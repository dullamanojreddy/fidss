"""Contract entry point for quality-gated document/selfie face verification."""
import os
import time
from app.schemas.document_context import DocumentContext
from app.schemas.evidence_item import BoundingBox, EvidenceItem
from app.schemas.module_result import ModuleResult
from .embedder import EmbeddingUnavailable, create_embedding
from .face_detector import crop_face, detect_faces, load_image
from .matcher import match_embeddings
from .quality_gate import assess_face_quality

def _result(started, status, outcome, *, errors=None, evidence=None, metadata=None):
    return ModuleResult(module="face", status=status, evidence_items=evidence or [], errors=errors or [], processing_time_ms=int((time.perf_counter()-started)*1000), metadata={"outcome":outcome, **(metadata or {})})

def analyze(context: DocumentContext) -> ModuleResult:
    started = time.perf_counter()
    if not context.selfie_path:
        return _result(started,"SUCCESS","SKIPPED",metadata={"reason":"SELFIE_NOT_PROVIDED","note":"Face verification skipped — no traveler selfie uploaded."})
    try:
        document, selfie = load_image(context.image_path), load_image(context.selfie_path)
        document_faces, selfie_faces = detect_faces(document), detect_faces(selfie)
    except Exception as exc:
        return _result(started,"FAILED","INCONCLUSIVE",errors=[f"Face detection failed: {exc}"],metadata={"reason":"DETECTION_ERROR"})
    counts = {"document_face_count":len(document_faces),"selfie_face_count":len(selfie_faces)}
    if not document_faces or not selfie_faces:
        missing = "DOCUMENT" if not document_faces else "SELFIE"
        return _result(started,"INCONCLUSIVE","NO_FACE",errors=[f"No face detected in {missing.lower()} image"],metadata={**counts,"reason":f"NO_{missing}_FACE"})
    if len(selfie_faces) > 1:
        return _result(started,"INCONCLUSIVE","MULTIPLE_FACES",errors=["Multiple faces detected in traveler selfie"],metadata={**counts,"reason":"MULTIPLE_SELFIE_FACES"})
    document_face, selfie_face = document_faces[0], selfie_faces[0]
    document_crop, selfie_crop = crop_face(document,document_face), crop_face(selfie,selfie_face)
    document_quality, selfie_quality = assess_face_quality(document_crop), assess_face_quality(selfie_crop)
    quality = {
        "document_quality":{"passed":document_quality.passed,"blur_score":round(document_quality.blur_score,2),"brightness":round(document_quality.brightness,2),"face_size":document_quality.face_size,"issues":list(document_quality.issues)},
        "selfie_quality":{"passed":selfie_quality.passed,"blur_score":round(selfie_quality.blur_score,2),"brightness":round(selfie_quality.brightness,2),"face_size":selfie_quality.face_size,"issues":list(selfie_quality.issues)},
    }
    if not document_quality.passed or not selfie_quality.passed:
        issues = sorted(set(document_quality.issues + selfie_quality.issues))
        return _result(started,"INCONCLUSIVE","INCONCLUSIVE",errors=["Face quality gate failed: "+", ".join(issues)],metadata={**counts,**quality,"reason":"QUALITY_GATE_FAILED"})
    try:
        threshold = float(os.getenv("FIDSS_FACE_SIMILARITY_THRESHOLD","0.45"))
        matched = match_embeddings(create_embedding(document_crop),create_embedding(selfie_crop),threshold)
    except EmbeddingUnavailable as exc:
        return _result(started,"INCONCLUSIVE","INCONCLUSIVE",errors=[str(exc)],metadata={**counts,**quality,"reason":"MODEL_UNAVAILABLE"})
    except Exception as exc:
        return _result(started,"FAILED","INCONCLUSIVE",errors=[f"Face matching failed: {exc}"],metadata={**counts,**quality,"reason":"MATCHING_ERROR"})
    metadata = {**counts,**quality,"similarity":round(matched.similarity,4),"similarity_percent":round(max(0.0,matched.similarity)*100,1),"threshold":matched.threshold,"detector_confidence":round(document_face.confidence,4)}
    evidence = []
    if matched.outcome == "MISMATCH":
        x,y,w,h = document_face.bbox
        evidence.append(EvidenceItem(screening_id=context.screening_id,module_name="face",category="FACE_MISMATCH",severity="HIGH",source="ArcFace cosine similarity",confidence=round(min(1.0,max(0.0,matched.threshold-matched.similarity+0.5)),4),description=f"Traveler selfie did not match the document portrait (similarity {matched.similarity:.3f}, threshold {matched.threshold:.3f}).",document_region=BoundingBox(x=x,y=y,width=w,height=h,label="document_portrait"),metrics={"similarity":round(matched.similarity,4),"threshold":matched.threshold}))
    return _result(started,"SUCCESS",matched.outcome,evidence=evidence,metadata=metadata)
