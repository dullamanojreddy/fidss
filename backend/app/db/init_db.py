import json
import uuid
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User
from app.models.system_setting import SystemSetting
from app.models.model_registry import ModelRegistry


def init_db(db: Session | None = None) -> None:
    """Initialize database tables and seed essential administrative records from environment variables.
    No static screenings or synthetic documents are created; all screenings must be created dynamically
    via authenticated screening upload requests.
    """
    Base.metadata.create_all(bind=engine)

    close_session = False
    if db is None:
        db = SessionLocal()
        close_session = True

    try:
        # Seed default Officer if not in DB (credentials from environment)
        officer = db.query(User).filter(User.username == settings.SEED_OFFICER_USERNAME).first()
        if not officer:
            officer = User(
                id=str(uuid.uuid4()),
                username=settings.SEED_OFFICER_USERNAME,
                hashed_password=get_password_hash(settings.SEED_OFFICER_PASSWORD),
                full_name="Inspector Arjun",
                role="OFFICER",
                is_active=True,
            )
            db.add(officer)

        # Seed default Admin if not in DB (credentials from environment)
        admin = db.query(User).filter(User.username == settings.SEED_ADMIN_USERNAME).first()
        if not admin:
            admin = User(
                id=str(uuid.uuid4()),
                username=settings.SEED_ADMIN_USERNAME,
                hashed_password=get_password_hash(settings.SEED_ADMIN_PASSWORD),
                full_name="System Administrator",
                role="ADMIN",
                is_active=True,
            )
            db.add(admin)

        db.commit()

        # Seed system settings if empty
        if not db.query(SystemSetting).first():
            default_settings = [
                ("face_similarity_threshold", json.dumps(0.65), "ArcFace Cosine Similarity Threshold"),
                ("quality_min_sharpness", json.dumps(85.0), "Minimum Laplacian Variance"),
                ("mrz_strict_checksum", json.dumps(True), "Enforce ICAO 9303 Checksum Validation"),
                ("tamper_sensitivity", json.dumps("STANDARD"), "Forensic ELA and Noise Sensitivity"),
            ]
            for k, v, desc in default_settings:
                db.add(SystemSetting(key=k, value_json=v, description=desc, updated_by=admin.id))
            db.commit()

        # Seed model registry if empty
        if not db.query(ModelRegistry).first():
            default_models = [
                ("PP-OCRv4", "4.0.0", "PaddleOCR-CPU", "sha256:d8a9f3b7..."),
                ("SCRFD-10G", "1.0.0", "ONNXRuntime-CPU", "sha256:e3b0c442..."),
                ("ArcFace-ResNet50", "2.1.0", "ONNXRuntime-CPU", "sha256:9f86d081..."),
                ("Forensic-CV-Suite", "1.4.2", "Classical-NumPy", "sha256:5e884898..."),
            ]
            for name, ver, rt, chk in default_models:
                db.add(ModelRegistry(
                    id=str(uuid.uuid4()),
                    model_name=name,
                    version=ver,
                    runtime=rt,
                    checksum=chk,
                    is_active=True,
                    metadata_json=json.dumps({"author": "FIDSS Engineering"}),
                ))
            db.commit()

    finally:
        if close_session:
            db.close()
