import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.services.audit.hash_chain import compute_event_hash, canonical_json, AuditHashChain


class AuditService:
    @staticmethod
    def log_event(
        db: Session,
        event_type: str,
        event_payload: dict,
        screening_id: str | None = None,
        actor_id: str = "system",
    ) -> AuditLog:
        """Append an event to the cryptographic SHA-256 hash chain with strict block sequence."""
        latest_event = (
            db.query(AuditLog)
            .order_by(AuditLog.block_index.desc())
            .first()
        )

        next_block_index = (latest_event.block_index + 1) if (latest_event and latest_event.block_index is not None) else 0
        previous_hash = latest_event.current_hash if latest_event else None
        now = datetime.now(timezone.utc).replace(microsecond=0)

        current_hash = compute_event_hash(previous_hash, event_payload, now)

        audit_entry = AuditLog(
            id=str(uuid.uuid4()),
            block_index=next_block_index,
            screening_id=screening_id,
            previous_hash=previous_hash,
            current_hash=current_hash,
            event_type=event_type,
            event_payload_json=canonical_json(event_payload),
            timestamp=now,
            actor_id=actor_id,
        )

        db.add(audit_entry)
        db.commit()
        db.refresh(audit_entry)
        return audit_entry

    @staticmethod
    def verify_screening_chain(db: Session, screening_id: str) -> dict:
        """Verify the integrity of all audit events for a specific screening."""
        events = (
            db.query(AuditLog)
            .filter(AuditLog.screening_id == screening_id)
            .order_by(AuditLog.block_index.asc())
            .all()
        )
        return AuditHashChain.verify_chain(events, is_subchain=True)

    @staticmethod
    def verify_system_chain(db: Session) -> dict:
        """Verify the complete system-wide audit chain."""
        events = (
            db.query(AuditLog)
            .order_by(AuditLog.block_index.asc())
            .all()
        )
        return AuditHashChain.verify_chain(events, is_subchain=False)

    @staticmethod
    def tamper_demo_record(db: Session, screening_id: str) -> dict:
        """Deliberately modify a payload in an existing audit row without updating its hash.
        This provides a live demonstration that the cryptographic verifier catches unauthorized database manipulation.
        """
        event = (
            db.query(AuditLog)
            .filter(AuditLog.screening_id == screening_id)
            .order_by(AuditLog.block_index.desc())
            .first()
        )
        if not event:
            return {"error": "No audit records found to tamper for demonstration."}

        event.event_payload_json = canonical_json({
            "tampered": True,
            "forged_by": "unauthorized_sql_injection",
            "original_note": "Risk level altered directly in database",
        })
        db.commit()

        return {
            "status": "TAMPERED",
            "tampered_block_id": event.id,
            "tampered_block_index": event.block_index,
            "tampered_event_type": event.event_type,
            "message": "Audit row payload was deliberately altered in database. Running verify will now fail.",
        }
