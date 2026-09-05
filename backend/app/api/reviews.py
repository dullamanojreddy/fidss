import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.schemas.auth import UserResponse
from app.schemas.review import OfficerReviewCreate, OfficerReviewResponse
from app.models.screening import Screening
from app.models.officer_review import OfficerReview
from app.models.user import User
from app.services.audit.audit_service import AuditService

router = APIRouter(prefix="/screenings", tags=["Officer Reviews"])


@router.post("/{screening_id}/review", response_model=OfficerReviewResponse, status_code=status.HTTP_201_CREATED)
def submit_officer_review(
    screening_id: str,
    review_in: OfficerReviewCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    screening = db.query(Screening).filter(Screening.id == screening_id).first()
    if not screening:
        # Try screening_number
        screening = db.query(Screening).filter(Screening.screening_number == screening_id).first()
    if not screening:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Screening not found.")

    # Check if review already exists
    existing_review = db.query(OfficerReview).filter(OfficerReview.screening_id == screening.id).first()
    now = datetime.now(timezone.utc)

    if existing_review:
        existing_review.decision = review_in.decision
        existing_review.reason = review_in.reason
        existing_review.notes = review_in.notes
        existing_review.created_at = now
        review_obj = existing_review
    else:
        review_obj = OfficerReview(
            id=str(uuid.uuid4()),
            screening_id=screening.id,
            officer_id=str(current_user.id),
            decision=review_in.decision,
            reason=review_in.reason,
            notes=review_in.notes,
            created_at=now,
        )
        db.add(review_obj)

    if review_in.decision == "ESCALATE":
        screening.status = "ESCALATED_TO_SECONDARY"
    elif review_in.decision == "ACCEPT":
        screening.status = "CLEARED"
    elif review_in.decision == "REJECT":
        screening.status = "REJECTED"

    db.commit()
    db.refresh(review_obj)

    # Append to cryptographic SHA-256 audit chain
    AuditService.log_event(
        db=db,
        event_type="OFFICER_REVIEWED",
        event_payload={
            "screening_id": screening.id,
            "decision": review_in.decision,
            "reason": review_in.reason,
            "notes": review_in.notes,
            "officer_name": current_user.full_name,
        },
        screening_id=screening.id,
        actor_id=str(current_user.id),
    )

    return OfficerReviewResponse(
        id=uuid.UUID(review_obj.id),
        screening_id=uuid.UUID(review_obj.screening_id),
        officer_id=uuid.UUID(review_obj.officer_id),
        officer_name=current_user.full_name,
        decision=review_obj.decision,  # type: ignore
        reason=review_obj.reason,
        notes=review_obj.notes,
        created_at=review_obj.created_at,
    )


@router.get("/{screening_id}/review", response_model=OfficerReviewResponse | None)
def get_officer_review(
    screening_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    screening = db.query(Screening).filter(Screening.id == screening_id).first()
    if not screening:
        screening = db.query(Screening).filter(Screening.screening_number == screening_id).first()
    if not screening:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Screening not found.")

    review = db.query(OfficerReview).filter(OfficerReview.screening_id == screening.id).first()
    if not review:
        return None

    officer = db.query(User).filter(User.id == review.officer_id).first()
    return OfficerReviewResponse(
        id=uuid.UUID(review.id),
        screening_id=uuid.UUID(review.screening_id),
        officer_id=uuid.UUID(review.officer_id),
        officer_name=officer.full_name if officer else "Border Officer",
        decision=review.decision,  # type: ignore
        reason=review.reason,
        notes=review.notes,
        created_at=review.created_at,
    )
