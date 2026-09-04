"""Face detection helpers with an optional local InsightFace SCRFD model."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os
import cv2
import numpy as np

@dataclass(frozen=True)
class FaceDetection:
    bbox: tuple[int, int, int, int]
    confidence: float
    landmarks: np.ndarray | None = None
    @property
    def area(self) -> int:
        return self.bbox[2] * self.bbox[3]

class FaceDetectionError(RuntimeError):
    pass

def load_image(path: str) -> np.ndarray:
    image = cv2.imread(str(Path(path)))
    if image is None:
        raise FaceDetectionError(f"Unable to read image: {path}")
    return image

def _insightface_detections(image: np.ndarray) -> list[FaceDetection] | None:
    """Use configured local SCRFD weights; never download a model implicitly."""
    model_path = os.getenv("FIDSS_SCRFD_MODEL_PATH")
    if not model_path or not Path(model_path).is_file():
        return None
    try:
        from insightface.model_zoo import get_model
        model = get_model(model_path, providers=["CPUExecutionProvider"])
        model.prepare(ctx_id=-1, input_size=(640, 640), det_thresh=0.5)
        boxes, landmarks = model.detect(image, max_num=0)
    except (ImportError, RuntimeError, ValueError):
        return None
    return [FaceDetection((int(b[0]), int(b[1]), int(b[2]-b[0]), int(b[3]-b[1])), float(b[4]), landmarks[i] if landmarks is not None else None) for i, b in enumerate(boxes)]

def _opencv_detections(image: np.ndarray) -> list[FaceDetection]:
    cascade = cv2.CascadeClassifier(str(Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"))
    if cascade.empty():
        raise FaceDetectionError("OpenCV face detector is unavailable")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    boxes = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
    return [FaceDetection(tuple(map(int, box)), 0.75) for box in boxes]

def detect_faces(image: np.ndarray) -> list[FaceDetection]:
    detections = _insightface_detections(image)
    return sorted(_opencv_detections(image) if detections is None else detections, key=lambda face: face.area, reverse=True)

def crop_face(image: np.ndarray, detection: FaceDetection, margin: float = 0.15) -> np.ndarray:
    x, y, width, height = detection.bbox
    pad_x, pad_y = int(width * margin), int(height * margin)
    return image[max(0,y-pad_y):min(image.shape[0],y+height+pad_y), max(0,x-pad_x):min(image.shape[1],x+width+pad_x)].copy()
