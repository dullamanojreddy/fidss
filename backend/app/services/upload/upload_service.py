import os
import uuid
import hashlib
from pathlib import Path
from fastapi import UploadFile
from app.core.config import settings
from app.core.exceptions import FileValidationException

ALLOWED_MIME_TYPES = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/webp": [b"RIFF"],
}
MAX_FILE_BYTES = settings.MAX_UPLOAD_MB * 1024 * 1024


class UploadService:
    @staticmethod
    async def validate_and_save(file: UploadFile) -> dict:
        content = await file.read()
        if not content:
            raise FileValidationException("Uploaded file is empty.")

        if len(content) > MAX_FILE_BYTES:
            raise FileValidationException(
                f"File size exceeds allowed limit of {settings.MAX_UPLOAD_MB} MB."
            )

        # Validate magic bytes
        detected_mime = None
        for mime, signatures in ALLOWED_MIME_TYPES.items():
            for sig in signatures:
                if content.startswith(sig):
                    detected_mime = mime
                    break
            if detected_mime:
                break

        if not detected_mime:
            # Check for webp after RIFF offset
            if len(content) > 12 and content[:4] == b"RIFF" and content[8:12] == b"WEBP":
                detected_mime = "image/webp"

        if not detected_mime:
            raise FileValidationException(
                "Invalid image format. Allowed formats are JPEG, PNG, and WebP."
            )

        # Compute SHA-256
        sha256_hash = hashlib.sha256(content).hexdigest()

        # Secure unique filename
        ext = ".jpg" if "jpeg" in detected_mime else (".png" if "png" in detected_mime else ".webp")
        safe_filename = f"{uuid.uuid4()}{ext}"
        save_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

        with open(save_path, "wb") as f:
            f.write(content)

        return {
            "original_filename": file.filename or safe_filename,
            "storage_path": save_path,
            "file_size": len(content),
            "mime_type": detected_mime,
            "sha256_hash": sha256_hash,
        }
