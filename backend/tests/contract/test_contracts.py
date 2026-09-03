import uuid
from app.schemas.document_context import DocumentContext
from app.schemas.quality_result import QualityResult
from app.schemas.module_result import ModuleResult
from app.schemas.evidence_item import EvidenceItem, BoundingBox
from app.services.module_dispatcher import ModuleDispatcher


def test_document_context_schema():
    ctx = DocumentContext(
        screening_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        image_path="/storage/test.png",
        document_type="passport",
        image_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    )
    assert ctx.document_type == "passport"
    assert ctx.quality_result is None


def test_evidence_item_provenance():
    s_id = uuid.uuid4()
    m_id = uuid.uuid4()
    item = EvidenceItem(
        screening_id=s_id,
        module_name="ocr",
        module_result_id=m_id,
        category="TEXT_CHECK",
        severity="LOW",
        source="PP-OCRv4",
        confidence=0.95,
        description="Text clear",
        document_region=BoundingBox(x=10, y=20, width=100, height=30),
        metrics={"field_count": 5},
    )
    assert item.module_name == "ocr"
    assert item.module_result_id == m_id
    assert item.severity == "LOW"


def test_module_dispatcher_quality_contract():
    ctx = DocumentContext(
        screening_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        image_path="/storage/test.png",
        image_sha256="test-hash",
    )
    res = ModuleDispatcher.run_quality(ctx)
    assert isinstance(res, QualityResult)
    assert res.status in ["PASS", "WARNING", "FAIL"]


def test_module_dispatcher_ocr_contract():
    ctx = DocumentContext(
        screening_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        image_path="/storage/test.png",
        image_sha256="test-hash",
    )
    res, extracted = ModuleDispatcher.run_ocr(ctx)
    assert isinstance(res, ModuleResult)
    assert res.module == "ocr"
    assert "Passport Number" in extracted


def test_fusion_invariant_never_clear_on_failure():
    ctx = DocumentContext(
        screening_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        image_path="/storage/test.png",
        image_sha256="test-hash",
    )
    q_pass = QualityResult(status="PASS")
    # Simulate failed tampering module
    failed_mod = ModuleResult(
        module="tampering",
        status="FAILED",
        errors=["Inference timeout"],
    )
    score, level, rec = ModuleDispatcher.run_fusion(ctx, q_pass, [failed_mod])
    # Must NOT be CLEAR!
    assert level != "CLEAR"
    assert level in ["REVIEW_RECOMMENDED", "INCONCLUSIVE"]
