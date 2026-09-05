"""Deterministic synthetic fixtures for the Person 3 tampering module.

These are test artefacts, not identity documents or government records.
"""

import uuid
import cv2
import numpy as np
import pytest
from PIL import Image, PngImagePlugin

from app.schemas.document_context import DocumentContext
from app.modules.tampering import analyze as run_tampering
from app.modules.tampering import compression_analysis, copy_move, metadata_analysis, noise_analysis, photo_replacement, text_manipulation


def _context(path, **kwargs):
    return DocumentContext(screening_id=uuid.uuid4(), document_id=uuid.uuid4(), image_path=str(path), image_sha256="test", **kwargs)


def _clean_image(path):
    image = np.full((256, 384, 3), 220, dtype=np.uint8)
    cv2.rectangle(image, (20, 20), (364, 236), (180, 180, 180), 2)
    cv2.putText(image, "TEST DOCUMENT", (45, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (25, 25, 25), 2)
    cv2.putText(image, "123456789", (45, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (30, 30, 30), 2)
    cv2.imwrite(str(path), image)
    return image


def _polygon(x, y, width, height):
    return [[x, y], [x + width, y], [x + width, y + height], [x, y + height]]


def _p1_ocr(*boxes):
    return {
        "raw_lines": [
            {"text": f"LINE {index}", "confidence": 0.95, "bbox": box}
            for index, box in enumerate(boxes)
        ],
        "document_number": "A1234567",
        "extracted_fields": {"document_number": "A1234567"},
    }


def test_full_pipeline_clean_image_is_contract_conforming(tmp_path):
    path = tmp_path / "clean.png"
    _clean_image(path)
    result = run_tampering(_context(path))
    assert result.module == "tampering"
    assert result.status in {"SUCCESS", "PARTIAL", "INCONCLUSIVE"}
    assert result.processing_time_ms is not None
    assert all(item.module_name == "tampering" and 0 <= item.confidence <= 1 for item in result.evidence_items)


def test_copy_move_reports_metrics_for_controlled_repetition(tmp_path):
    path = tmp_path / "copy_move.png"
    image = _clean_image(path)
    patch = np.zeros((55, 55, 3), dtype=np.uint8)
    cv2.circle(patch, (27, 27), 20, (10, 10, 10), 2)
    cv2.line(patch, (5, 5), (50, 45), (10, 10, 10), 2)
    image[150:205, 45:100] = patch
    image[150:205, 240:295] = patch
    cv2.imwrite(str(path), image)
    _, status, metrics = copy_move.analyze(_context(path))
    assert status in {"SUCCESS", "INCONCLUSIVE"}
    assert metrics["keypoint_count"] >= 0
    assert "ransac_inlier_count" in metrics
    assert metrics["good_match_count"] > 0


def test_copy_move_blank_image_has_no_descriptors(tmp_path):
    path = tmp_path / "blank.png"
    cv2.imwrite(str(path), np.full((128, 128, 3), 220, dtype=np.uint8))
    items, status, metrics = copy_move.analyze(_context(path))
    assert status == "INCONCLUSIVE" and not items
    assert metrics["descriptor_count"] == 0


def test_tiny_image_is_inconclusive_for_spatial_detectors(tmp_path):
    path = tmp_path / "tiny.png"
    cv2.imwrite(str(path), np.zeros((12, 12, 3), dtype=np.uint8))
    _, copy_status, _ = copy_move.analyze(_context(path))
    _, noise_status, _ = noise_analysis.analyze(_context(path))
    assert copy_status == "INCONCLUSIVE"
    assert noise_status == "INCONCLUSIVE"


def test_noise_detector_measures_gaussian_and_wavelet_residuals(tmp_path):
    path = tmp_path / "noise.png"
    rng = np.random.default_rng(42)
    image = rng.integers(0, 256, size=(128, 128, 3), dtype=np.uint8)
    cv2.imwrite(str(path), image)
    _, status, metrics = noise_analysis.analyze(_context(path))
    assert status == "SUCCESS"
    assert metrics["gaussian_residual_variance"] > 0
    assert metrics["wavelet_residual_variance"] > 0
    assert metrics["wavelet"] == "haar"
    assert np.isfinite(metrics["max_combined_deviation"])


def test_wavelet_noise_path_is_safe_for_constant_image(tmp_path):
    path = tmp_path / "constant.png"
    cv2.imwrite(str(path), np.full((128, 128, 3), 127, dtype=np.uint8))
    items, status, metrics = noise_analysis.analyze(_context(path))
    assert status == "INCONCLUSIVE" and not items
    assert metrics["gaussian_residual_variance"] == 0
    assert metrics["wavelet_residual_variance"] == 0
    assert metrics["reason"] == "insufficient_noise_signal"


def test_missing_ocr_and_portrait_region_never_fabricate_boxes(tmp_path):
    path = tmp_path / "clean.png"
    _clean_image(path)
    context = _context(path)
    text_items, text_status, _ = text_manipulation.analyze(context)
    photo_items, photo_status, _ = photo_replacement.analyze(context)
    assert text_status == "INCONCLUSIVE" and not text_items
    assert photo_status == "INCONCLUSIVE" and not photo_items


def test_current_p1_raw_lines_polygon_contract_executes(tmp_path):
    path = tmp_path / "clean.png"
    _clean_image(path)
    ocr_result = _p1_ocr(
        _polygon(45, 45, 30, 18), _polygon(85, 45, 30, 18),
        _polygon(125, 45, 30, 18), _polygon(165, 45, 30, 18),
    )
    items, status, metrics = text_manipulation.analyze(_context(path, ocr_result=ocr_result))
    assert status == "SUCCESS" and not items
    assert metrics["valid_token_count"] == 4
    assert metrics["coordinate_system"] == "original_image_pixels_exif_oriented"
    assert metrics["mean_ocr_confidence"] == 0.95


def test_full_p3_executes_with_current_p1_shaped_metadata(tmp_path):
    path = tmp_path / "clean.png"
    _clean_image(path)
    ocr_result = _p1_ocr(
        _polygon(45, 45, 30, 18), _polygon(85, 45, 30, 18),
        _polygon(125, 45, 30, 18), _polygon(165, 45, 30, 18),
    )
    result = run_tampering(_context(path, ocr_result=ocr_result))
    assert result.status == "SUCCESS"
    assert result.metadata["detector_statuses"]["text_manipulation"] == "SUCCESS"
    assert result.metadata["detectors"]["text_manipulation"]["valid_token_count"] == 4


@pytest.mark.parametrize("bbox", [
    None,
    "not-a-box",
    [[10, 10], [20, 10], [20, 20]],
    [[10, 10], [20, 10], [20, float("nan")], [10, 20]],
    {"x": "bad", "y": 10, "width": 20, "height": 10},
])
def test_malformed_current_ocr_geometry_is_inconclusive(tmp_path, bbox):
    path = tmp_path / "clean.png"
    _clean_image(path)
    items, status, metrics = text_manipulation.analyze(_context(path, ocr_result=_p1_ocr(bbox)))
    assert status == "INCONCLUSIVE" and not items
    assert metrics["malformed_box_count"] == 1


@pytest.mark.parametrize("bbox", [
    _polygon(-1, 20, 20, 10), _polygon(20, -1, 20, 10),
    _polygon(375, 20, 20, 10), _polygon(20, 250, 20, 10),
])
def test_partially_out_of_image_polygons_are_rejected(tmp_path, bbox):
    path = tmp_path / "clean.png"
    _clean_image(path)
    items, status, metrics = text_manipulation.analyze(_context(path, ocr_result=_p1_ocr(bbox)))
    assert status == "INCONCLUSIVE" and not items
    assert metrics["out_of_image_box_count"] == 1
    assert metrics["image_width"] == 384 and metrics["image_height"] == 256


def test_oversized_and_duplicate_polygons_do_not_manufacture_geometry(tmp_path):
    path = tmp_path / "clean.png"
    _clean_image(path)
    oversized = _polygon(0, 0, 384, 256)
    duplicate = _polygon(45, 45, 30, 18)
    near_duplicate = _polygon(46, 45, 30, 18)
    items, status, metrics = text_manipulation.analyze(
        _context(path, ocr_result=_p1_ocr(oversized, duplicate, duplicate, near_duplicate))
    )
    assert status == "INCONCLUSIVE" and not items
    assert metrics["oversized_box_count"] == 1
    assert metrics["duplicate_overlap_box_count"] == 2
    assert metrics["valid_token_count"] == 1


def test_legitimate_overlapping_p1_polygons_remain_usable(tmp_path):
    path = tmp_path / "clean.png"
    _clean_image(path)
    boxes = [_polygon(45, 45, 40, 18), _polygon(75, 45, 40, 18), _polygon(105, 45, 40, 18), _polygon(135, 45, 40, 18)]
    items, status, metrics = text_manipulation.analyze(_context(path, ocr_result=_p1_ocr(*boxes)))
    assert status == "SUCCESS"
    assert metrics["valid_token_count"] == 4
    assert metrics["duplicate_overlap_box_count"] == 0
    assert all(item.category == "TEXT_MANIPULATION_CANDIDATE" for item in items)


def test_insufficient_valid_p1_lines_are_inconclusive(tmp_path):
    path = tmp_path / "clean.png"
    _clean_image(path)
    items, status, metrics = text_manipulation.analyze(
        _context(path, ocr_result=_p1_ocr(_polygon(45, 45, 30, 18), _polygon(85, 45, 30, 18)))
    )
    assert status == "INCONCLUSIVE" and not items
    assert metrics["valid_token_count"] == 2


def test_text_finding_is_only_review_candidate(tmp_path):
    path = tmp_path / "candidate.png"
    image = _clean_image(path)
    image[150:210, 250:290] = 0
    cv2.imwrite(str(path), image)
    boxes = [_polygon(45, 45, 30, 10), _polygon(85, 45, 30, 10), _polygon(125, 45, 30, 10), _polygon(250, 150, 40, 60)]
    items, status, _ = text_manipulation.analyze(_context(path, ocr_result=_p1_ocr(*boxes)))
    assert status == "SUCCESS" and len(items) == 1
    evidence = items[0]
    assert evidence.category == "TEXT_MANIPULATION_CANDIDATE"
    assert evidence.severity in {"LOW", "MEDIUM"}
    assert "manual review" in evidence.description.lower()
    assert all(word not in evidence.description.lower() for word in ("fake", "fraud", "forged"))


def test_metadata_editing_signature_is_only_low_supporting_evidence(tmp_path):
    path = tmp_path / "metadata.png"
    png_info = PngImagePlugin.PngInfo()
    png_info.add_text("Software", "Adobe Photoshop")
    Image.new("RGB", (80, 80), "white").save(path, pnginfo=png_info)
    items, status, metrics = metadata_analysis.analyze(_context(path))
    assert status == "SUCCESS"
    assert metrics["metadata_available"] is True
    assert items and items[0].severity == "LOW"


def test_corrupt_image_returns_failed_module_result(tmp_path):
    path = tmp_path / "corrupt.bin"
    path.write_bytes(b"not an image")
    result = run_tampering(_context(path))
    assert result.status == "FAILED"
    assert len(result.errors) == 7


def test_one_detector_failure_is_isolated(tmp_path, monkeypatch):
    path = tmp_path / "clean.png"
    _clean_image(path)
    import importlib
    module = importlib.import_module("app.modules.tampering.analyze")
    original = module._DETECTORS
    monkeypatch.setattr(module, "_DETECTORS", (("broken", lambda _: (_ for _ in ()).throw(RuntimeError("test failure"))),) + original[1:])
    result = module.analyze(_context(path))
    assert result.status == "PARTIAL"
    assert any("broken: test failure" in error for error in result.errors)


def test_returned_failed_status_controls_aggregate(tmp_path, monkeypatch):
    path = tmp_path / "clean.png"
    _clean_image(path)
    import importlib
    module = importlib.import_module("app.modules.tampering.analyze")
    failed = lambda _: ([], "FAILED", {"reason": "controlled"})
    monkeypatch.setattr(module, "_DETECTORS", (("failed", failed), ("ok", lambda _: ([], "SUCCESS", {}))))
    assert module.analyze(_context(path)).status == "PARTIAL"
    monkeypatch.setattr(module, "_DETECTORS", (("one", failed), ("two", failed)))
    assert module.analyze(_context(path)).status == "FAILED"


def test_compression_detector_returns_measured_metrics(tmp_path):
    path = tmp_path / "compression.png"
    image = _clean_image(path)
    cv2.rectangle(image, (250, 170), (340, 220), (0, 0, 255), -1)
    cv2.imwrite(str(path), image, [cv2.IMWRITE_JPEG_QUALITY, 45])
    _, status, metrics = compression_analysis.analyze(_context(path))
    assert status == "SUCCESS"
    assert metrics["mean_difference"] >= 0
    assert 0 <= metrics["suspicious_pixel_ratio"] <= 1
