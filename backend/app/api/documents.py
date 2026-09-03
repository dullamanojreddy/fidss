import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.document import Document
from app.models.screening import Screening

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/{document_id}")
def get_document_metadata(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        # Check if passed screening_id
        doc = db.query(Document).filter(Document.screening_id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    return {
        "id": doc.id,
        "screening_id": doc.screening_id,
        "original_filename": doc.original_filename,
        "file_size": doc.file_size,
        "mime_type": doc.mime_type,
        "sha256_hash": doc.sha256_hash,
        "document_type": doc.document_type,
        "created_at": doc.created_at,
    }


@router.get("/{document_id}/file")
def get_document_file(document_id: str, db: Session = Depends(get_db)):
    """Serve the document image for viewing in Document Preview."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        doc = db.query(Document).filter(Document.screening_id == document_id).first()

    if not doc or not os.path.exists(doc.storage_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image file not found on disk.")

    return FileResponse(doc.storage_path, media_type=doc.mime_type)
