import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_user, require_admin_user
from app.schemas.auth import UserResponse
from app.schemas.settings import SystemSettingsUpdate, SystemSettingsResponse
from app.models.system_setting import SystemSetting
from app.models.model_registry import ModelRegistry
from app.services.audit.audit_service import AuditService

router = APIRouter(prefix="/settings", tags=["System Settings"])


@router.get("", response_model=SystemSettingsResponse)
def get_settings(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Read system settings and thresholds."""
    settings_records = db.query(SystemSetting).all()
    data = {}
    last_updated = None
    for s in settings_records:
        try:
            data[s.key] = json.loads(s.value_json)
        except Exception:
            data[s.key] = s.value_json
        if not last_updated or (s.updated_at and s.updated_at > last_updated):
            last_updated = s.updated_at

    return SystemSettingsResponse(
        settings=data,
        last_updated_at=last_updated,
        updated_by="System Administrator",
    )


@router.put("", response_model=SystemSettingsResponse)
def update_settings(
    settings_in: SystemSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_admin_user),
):
    """Admin-only update to thresholds and policy weights. Appends to audit log."""
    now = datetime.now(timezone.utc)
    updated_keys = []

    for k, v in settings_in.settings.items():
        existing = db.query(SystemSetting).filter(SystemSetting.key == k).first()
        val_str = json.dumps(v)
        if existing:
            existing.value_json = val_str
            existing.updated_at = now
            existing.updated_by = str(current_user.id)
        else:
            db.add(SystemSetting(
                key=k,
                value_json=val_str,
                description="Custom threshold update",
                updated_by=str(current_user.id),
                updated_at=now,
            ))
        updated_keys.append(k)

    db.commit()

    # Log to audit chain
    AuditService.log_event(
        db=db,
        event_type="SYSTEM_SETTING_CHANGED",
        event_payload={
            "updated_keys": updated_keys,
            "admin_id": str(current_user.id),
            "admin_name": current_user.full_name,
        },
        actor_id=str(current_user.id),
    )

    return get_settings(db, current_user)


@router.get("/models")
def list_registered_models(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """List registered detection models, runtimes, versions and checksums."""
    models = db.query(ModelRegistry).all()
    return models
