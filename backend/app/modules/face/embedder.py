"""ArcFace embedding using explicitly configured local model weights."""
from pathlib import Path
import os
import cv2
import numpy as np

class EmbeddingUnavailable(RuntimeError):
    pass

def create_embedding(face: np.ndarray) -> np.ndarray:
    model_path = os.getenv("FIDSS_ARCFACE_MODEL_PATH")
    if not model_path or not Path(model_path).is_file():
        raise EmbeddingUnavailable("ArcFace model is not configured (set FIDSS_ARCFACE_MODEL_PATH to a valid .onnx file)")
    try:
        from insightface.model_zoo import get_model
        model = get_model(model_path, providers=["CPUExecutionProvider"])
        model.prepare(ctx_id=-1)
        embedding = np.asarray(model.get_feat(cv2.resize(face, (112, 112)))).reshape(-1).astype(np.float32)
    except ImportError as exc:
        raise EmbeddingUnavailable("InsightFace runtime is not installed") from exc
    except Exception as exc:
        raise EmbeddingUnavailable(f"ArcFace inference failed: {exc}") from exc
    norm = float(np.linalg.norm(embedding))
    if not np.isfinite(norm) or norm == 0.0:
        raise EmbeddingUnavailable("ArcFace returned an invalid embedding")
    return embedding / norm
