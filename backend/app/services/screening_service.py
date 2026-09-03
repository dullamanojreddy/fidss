import json
import uuid
from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.screening import Screening
from app.models.document import Document
from app.models.document_field import DocumentField
from app.models.module_result import ModuleResultModel
from app.models.evidence_item import EvidenceItemModel
from app.models.user import User
from app.schemas.screening_result import ScreeningResultResponse, ScreeningListItem
from app.schemas.module_result import ModuleResult
from app.schemas.evidence_item import EvidenceItem, BoundingBox


class ScreeningService:
    @staticmethod
    def get_by_id(db: Session, screening_id: str) -> ScreeningResultResponse | None:
        screening = db.query(Screening).filter(Screening.id == screening_id).first()
        if not screening:
            return None

        # Fetch document
        doc = db.query(Document).filter(Document.screening_id == screening_id).first()
        doc_id = uuid.UUID(doc.id) if doc else uuid.UUID(screening.id)

        # Extracted fields
        fields_records = db.query(DocumentField).filter(DocumentField.screening_id == screening_id).all()
        extracted_fields = {f.field_name: f.field_value for f in fields_records}

        # Module results
        module_models = db.query(ModuleResultModel).filter(ModuleResultModel.screening_id == screening_id).all()
        module_results = []
        for m in module_models:
            errors = json.loads(m.errors_json) if m.errors_json else []
            meta = json.loads(m.metadata_json) if m.metadata_json else {}
            module_results.append(
                ModuleResult(
                    id=uuid.UUID(m.id),
                    module=m.module_name,
                    status=m.status,  # type: ignore
                    processing_time_ms=m.processing_time_ms,
                    errors=errors,
                    metadata=meta,
                )
            )

        # Evidence items
        ev_records = db.query(EvidenceItemModel).filter(EvidenceItemModel.screening_id == screening_id).all()
        key_findings = []
        for ev in ev_records:
            region = None
            if ev.region_json:
                try:
                    r_dict = json.loads(ev.region_json)
                    region = BoundingBox(**r_dict)
                except Exception:
                    pass
            metrics = json.loads(ev.metrics_json) if ev.metrics_json else {}
            key_findings.append(
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
                    metrics=metrics,
                    created_at=ev.created_at,
                )
            )

        creator_name = "Inspector Arjun"
        if screening.created_by:
            user = db.query(User).filter(User.id == screening.created_by).first()
            if user:
                creator_name = user.full_name

        return ScreeningResultResponse(
            id=uuid.UUID(screening.id),
            screening_number=screening.screening_number,
            status=screening.status,  # type: ignore
            document_type=screening.document_type,
            nationality=screening.nationality or "IND (India)",
            overall_risk_score=screening.overall_risk_score,
            screening_level=screening.screening_level,  # type: ignore
            recommendation_text=screening.recommendation_text,
            document_id=doc_id,
            document_preview_url=f"/api/documents/{doc_id}/file" if doc else None,
            submitted_by=creator_name,
            submitted_at=screening.created_at,
            completed_at=screening.completed_at,
            extracted_fields=extracted_fields,
            module_results=module_results,
            key_findings=key_findings[:4],
            total_evidence_count=len(key_findings),
            current_step=7 if screening.status == "COMPLETED" else 1,
        )

    @staticmethod
    def list_screenings(db: Session, limit: int = 20, offset: int = 0) -> list[ScreeningListItem]:
        screenings = (
            db.query(Screening)
            .order_by(Screening.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        items = []
        for s in screenings:
            items.append(
                ScreeningListItem(
                    id=uuid.UUID(s.id),
                    screening_number=s.screening_number,
                    document_type=s.document_type.capitalize(),
                    submitted_at=s.created_at,
                    screening_level=s.screening_level,  # type: ignore
                    overall_risk_score=s.overall_risk_score,
                    status=s.status,  # type: ignore
                    submitted_by="Inspector Arjun",
                )
            )
        return items

    @staticmethod
    def get_dashboard_metrics(db: Session) -> dict[str, Any]:
        total_count = db.query(func.count(Screening.id)).scalar() or 0
        clear_count = db.query(func.count(Screening.id)).filter(Screening.screening_level == "CLEAR").scalar() or 0
        review_count = (
            db.query(func.count(Screening.id))
            .filter(Screening.screening_level.in_(["REVIEW_RECOMMENDED", "ENHANCED_REVIEW_RECOMMENDED"]))
            .scalar()
            or 0
        )
        inconclusive_count = (
            db.query(func.count(Screening.id)).filter(Screening.screening_level == "INCONCLUSIVE").scalar() or 0
        )

        recent = ScreeningService.list_screenings(db, limit=5)

        return {
            "total_screenings": total_count,
            "clear_count": clear_count,
            "review_recommended_count": review_count,
            "inconclusive_count": inconclusive_count,
            "system_health": "Operational",
            "average_processing_time_ms": 284,
            "recent_screenings": [item.model_dump() for item in recent],
        }
