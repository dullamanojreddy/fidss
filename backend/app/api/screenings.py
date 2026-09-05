from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.schemas.auth import UserResponse
from app.schemas.screening_result import ScreeningResultResponse, ScreeningListItem
from app.schemas.evidence_item import EvidenceItem
from app.services.orchestrator import ScreeningOrchestrator
from app.services.screening_service import ScreeningService
from app.services.audit.audit_service import AuditService

router = APIRouter(prefix="/screenings", tags=["Screenings"])


@router.post("", response_model=ScreeningResultResponse, status_code=status.HTTP_201_CREATED)
async def create_screening(
    document: UploadFile = File(..., description="Document image to screen (JPEG/PNG/WebP)"),
    selfie: Optional[UploadFile] = File(None, description="Optional face photo/selfie"),
    document_type: str = Form("passport"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Execute complete 12-step screening pipeline on uploaded document."""
    res = await ScreeningOrchestrator.execute_screening(
        db=db,
        document_file=document,
        selfie_file=selfie,
        document_type=document_type.lower(),
        officer_id=str(current_user.id),
    )
    return res


@router.get("", response_model=list[ScreeningListItem])
def list_screenings(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieve list of recent screenings."""
    return ScreeningService.list_screenings(db, limit=limit, offset=offset)


@router.get("/escalated/list")
def list_escalated_screenings(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieve all screenings escalated to Senior Officer."""
    from app.models.screening import Screening
    from app.models.officer_review import OfficerReview
    from app.models.document_field import DocumentField
    from app.models.user import User

    reviews = (
        db.query(OfficerReview)
        .filter(OfficerReview.decision == "ESCALATE")
        .order_by(OfficerReview.created_at.desc())
        .all()
    )
    results = []
    for rev in reviews:
        screening = db.query(Screening).filter(Screening.id == rev.screening_id).first()
        if not screening:
            continue
        officer = db.query(User).filter(User.id == rev.officer_id).first()
        fields_records = db.query(DocumentField).filter(DocumentField.screening_id == screening.id).all()
        extracted_fields = {f.field_name: f.field_value for f in fields_records}

        doc_name = (
            extracted_fields.get("name")
            or extracted_fields.get("Full Name")
            or f"{extracted_fields.get('Given Name', '')} {extracted_fields.get('Surname', '')}".strip()
        )
        doc_num = extracted_fields.get("document_number") or extracted_fields.get("Passport Number") or "N/A"

        results.append({
            "screening_id": screening.id,
            "screening_number": screening.screening_number,
            "document_type": screening.document_type,
            "nationality": screening.nationality,
            "overall_risk_score": screening.overall_risk_score,
            "screening_level": screening.screening_level,
            "recommendation_text": screening.recommendation_text,
            "document_preview_url": f"/api/documents/{screening.id}/file",
            "traveler_name": doc_name or "Unknown Traveler",
            "document_number": doc_num,
            "extracted_fields": extracted_fields,
            "escalated_by": officer.full_name if officer else "Inspector Arjun",
            "escalation_reason": rev.reason,
            "escalation_notes": rev.notes,
            "escalated_at": rev.created_at.isoformat(),
            "status": screening.status,
        })
    return results


@router.get("/{screening_id}", response_model=ScreeningResultResponse)
def get_screening(
    screening_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieve full screening details by ID or Screening Number."""
    res = ScreeningService.get_by_id(db, screening_id)
    if not res:
        # Also check by screening_number (e.g. SID-2026-05-21-00124)
        from app.models.screening import Screening
        s = db.query(Screening).filter(Screening.screening_number == screening_id).first()
        if s:
            res = ScreeningService.get_by_id(db, s.id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screening '{screening_id}' not found.",
        )
    return res


@router.get("/{screening_id}/evidence", response_model=list[EvidenceItem])
def get_screening_evidence(
    screening_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieve all normalized evidence items for a screening."""
    screening = ScreeningService.get_by_id(db, screening_id)
    if not screening:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Screening not found.")
    
    from app.models.evidence_item import EvidenceItemModel
    import json
    from app.schemas.evidence_item import BoundingBox
    import uuid

    records = db.query(EvidenceItemModel).filter(EvidenceItemModel.screening_id == str(screening.id)).all()
    results = []
    for ev in records:
        region = None
        if ev.region_json:
            try:
                region = BoundingBox(**json.loads(ev.region_json))
            except Exception:
                pass
        results.append(
            EvidenceItem(
                id=uuid.UUID(ev.id),
                screening_id=uuid.UUID(ev.screening_id),
                module_name=ev.module_name,
                module_result_id=uuid.UUID(ev.module_result_id) if ev.module_result_id else None,
                category=ev.category,
                severity=ev.severity,  # type: ignore
                source=ev.source,
                confidence=ev.confidence,
                description=ev.description,
                document_region=region,
                metrics=json.loads(ev.metrics_json) if ev.metrics_json else {},
                created_at=ev.created_at,
            )
        )
    return results


@router.get("/{screening_id}/audit")
def get_screening_audit(
    screening_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieve cryptographic audit logs for a specific screening."""
    from app.models.audit_log import AuditLog
    events = (
        db.query(AuditLog)
        .filter(AuditLog.screening_id == screening_id)
        .order_by(AuditLog.timestamp.asc())
        .all()
    )
    return events
