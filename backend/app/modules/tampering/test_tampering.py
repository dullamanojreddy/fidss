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


def test_tiny_image_is_inconclusive_for_spatial_detectors(tmp_path):
    path = tmp_path / "tiny.png"
    cv2.imwrite(str(path), np.zeros((12, 12, 3), dtype=np.uint8))
    _, copy_status, _ = copy_move.analyze(_context(path))
    _, noise_status, _ = noise_analysis.analyze(_context(path))
    assert copy_status == "INCONCLUSIVE"
    assert noise_status == "INCONCLUSIVE"


def test_missing_ocr_and_portrait_region_never_fabricate_boxes(tmp_path):
    path = tmp_path / "clean.png"
    _clean_image(path)
    context = _context(path)
    text_items, text_status, _ = text_manipulation.analyze(context)
    photo_items, photo_status, _ = photo_replacement.analyze(context)
    assert text_status == "INCONCLUSIVE" and not text_items
    assert photo_status == "INCONCLUSIVE" and not photo_items


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


def test_compression_detector_returns_measured_metrics(tmp_path):
    path = tmp_path / "compression.png"
    image = _clean_image(path)
    cv2.rectangle(image, (250, 170), (340, 220), (0, 0, 255), -1)
    cv2.imwrite(str(path), image, [cv2.IMWRITE_JPEG_QUALITY, 45])
    _, status, metrics = compression_analysis.analyze(_context(path))
    assert status == "SUCCESS"
    assert metrics["mean_difference"] >= 0
    assert 0 <= metrics["suspicious_pixel_ratio"] <= 1
