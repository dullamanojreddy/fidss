"""Quality gates that prevent poor captures from becoming false mismatches."""
from dataclasses import dataclass
import cv2
import numpy as np

@dataclass(frozen=True)
class FaceQuality:
    passed: bool
    blur_score: float
    brightness: float
    face_size: int
    issues: tuple[str, ...]

def assess_face_quality(face: np.ndarray, minimum_size: int = 80) -> FaceQuality:
    if face.size == 0:
        return FaceQuality(False, 0.0, 0.0, 0, ("EMPTY_FACE_CROP",))
    gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    blur, brightness, face_size = float(cv2.Laplacian(gray, cv2.CV_64F).var()), float(gray.mean()), min(gray.shape[:2])
    issues = []
    if face_size < minimum_size: issues.append("FACE_TOO_SMALL")
    if blur < 35.0: issues.append("FACE_BLURRY")
    if brightness < 35.0: issues.append("FACE_TOO_DARK")
    elif brightness > 225.0: issues.append("FACE_OVEREXPOSED")
    return FaceQuality(not issues, blur, brightness, face_size, tuple(issues))
