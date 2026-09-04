"""ORB, ratio-test, and RANSAC-based copy-move evidence."""

import cv2
import numpy as np
from app.schemas.document_context import DocumentContext
from app.schemas.evidence_item import EvidenceItem, BoundingBox


def analyze(context: DocumentContext) -> tuple[list[EvidenceItem], str, dict]:
    image = cv2.imread(context.image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("Unable to decode image for copy-move analysis")
    if min(image.shape) < 64:
        return [], "INCONCLUSIVE", {"reason": "image_too_small", "keypoint_count": 0}
    keypoints, descriptors = cv2.ORB_create(nfeatures=1600, fastThreshold=10).detectAndCompute(image, None)
    metrics = {"keypoint_count": len(keypoints), "descriptor_count": 0 if descriptors is None else len(descriptors), "candidate_match_count": 0, "good_match_count": 0, "ransac_inlier_count": 0, "inlier_ratio": 0.0}
    if descriptors is None or len(descriptors) < 8:
        return [], "INCONCLUSIVE", {**metrics, "reason": "insufficient_orb_features"}
    pairs = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False).knnMatch(descriptors, descriptors, k=3)
    good = []
    for candidates in pairs:
        if len(candidates) < 3:
            continue
        first, second, _ = candidates
        if first.queryIdx != first.trainIdx and first.distance < 0.72 * second.distance:
            p1, p2 = keypoints[first.queryIdx].pt, keypoints[first.trainIdx].pt
            if np.hypot(p1[0] - p2[0], p1[1] - p2[1]) > 24:
                good.append(first)
    metrics["candidate_match_count"] = len(pairs)
    metrics["good_match_count"] = len(good)
    if len(good) < 8:
        return [], "INCONCLUSIVE", {**metrics, "reason": "insufficient_ratio_test_matches"}
    source = np.float32([keypoints[m.queryIdx].pt for m in good])
    destination = np.float32([keypoints[m.trainIdx].pt for m in good])
    _, inlier_mask = cv2.estimateAffinePartial2D(source, destination, method=cv2.RANSAC, ransacReprojThreshold=3.0)
    inliers = np.flatnonzero(inlier_mask.ravel()) if inlier_mask is not None else np.array([], dtype=int)
    metrics["ransac_inlier_count"] = int(len(inliers))
    metrics["inlier_ratio"] = round(float(len(inliers) / len(good)), 5) if good else 0.0
    if len(inliers) < 8 or metrics["inlier_ratio"] < 0.45:
        return [], "INCONCLUSIVE", {**metrics, "reason": "no_geometrically_consistent_cluster"}
    points = source[inliers]
    x, y, w, h = cv2.boundingRect(points.astype(np.float32))
    confidence = min(0.85, 0.4 + metrics["inlier_ratio"] * 0.4 + min(len(inliers) / 80, 0.15))
    return [EvidenceItem(
        screening_id=context.screening_id, module_name="tampering", category="COPY_MOVE_CANDIDATE", severity="MEDIUM",
        source="tampering.copy_move", confidence=round(confidence, 4),
        description="Repeated ORB features form a geometrically consistent copy-move candidate; manual review is required.",
        document_region=BoundingBox(x=int(x), y=int(y), width=int(w), height=int(h), label="copy_move_source"), metrics=metrics,
    )], "SUCCESS", metrics
