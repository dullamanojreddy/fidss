from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.schemas.auth import UserResponse
from app.models.audit_log import AuditLog
from app.services.audit.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["Audit Trail"])


@router.get("/logs")
def list_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieve chronological audit trail blocks."""
    events = (
        db.query(AuditLog)
        .order_by(AuditLog.timestamp.desc(), AuditLog.id.desc())
        .limit(limit)
        .all()
    )
    return events


@router.post("/{screening_id}/verify")
def verify_screening_audit_chain(
    screening_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Cryptographically verify all audit chain links for a specific screening."""
    from app.models.screening import Screening
    s = db.query(Screening).filter(Screening.screening_number == screening_id).first()
    target_id = s.id if s else screening_id

    result = AuditService.verify_screening_chain(db, target_id)
    return result


@router.post("/verify-system")
def verify_system_audit_chain(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Cryptographically verify the entire global audit hash chain."""
    result = AuditService.verify_system_chain(db)
    return result


@router.post("/tamper-demo")
def demonstrate_tamper_detection(
    screening_id: str = Query("SID-2026-05-21-00124"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Controlled demonstration endpoint for SIH presentation (Demo Script Steps 14-15).
    Deliberately modifies an audit row payload to trigger AUDIT_INTEGRITY_FAILURE on next verification.
    """
    from app.models.screening import Screening
    s = db.query(Screening).filter(Screening.screening_number == screening_id).first()
    target_id = s.id if s else screening_id

    res = AuditService.tamper_demo_record(db, target_id)
    return res
