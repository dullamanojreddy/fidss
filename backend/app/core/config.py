import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "FIDSS"
    APP_ENV: str = "development"  # production, development, demo
    DEBUG: bool = True

    # Database: In production, MySQL 8 is used. In dev/demo, SQLite or MySQL can be targeted.
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./fidss_app.db")

    # Security & JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "fidss-secure-secret-key-change-in-production-2026")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12

    # Storage
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    UPLOAD_DIR: str = str(BASE_DIR / "storage" / "uploads")
    MAX_UPLOAD_MB: int = 10

    # Seed Passwords (Driven by environment variables, never hardcoded in production)
    SEED_ADMIN_USERNAME: str = os.getenv("SEED_ADMIN_USERNAME", "admin")
    SEED_ADMIN_PASSWORD: str = os.getenv("SEED_ADMIN_PASSWORD", "AdminSecure2026!")
    SEED_OFFICER_USERNAME: str = os.getenv("SEED_OFFICER_USERNAME", "arjun")
    SEED_OFFICER_PASSWORD: str = os.getenv("SEED_OFFICER_PASSWORD", "OfficerArjun2026!")

    # System Thresholds
    FACE_SIMILARITY_THRESHOLD: float = 0.65
    WATCHLIST_PROVIDER: str = "local"
    AUDIT_PROVIDER: str = "local"


settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
