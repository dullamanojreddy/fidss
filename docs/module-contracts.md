# FIDSS Module Contracts Specification

Every detection module authored by Persons 1–4 must implement an `analyze(context: DocumentContext) -> ModuleResult` function adhering strictly to the shared schemas.

## 1. Input Contract: `DocumentContext`
```python
class DocumentContext(BaseModel):
    screening_id: UUID
    document_id: UUID
    image_path: str
    document_type: str  # passport, visa, national_id, etc.
    image_sha256: str
    quality_result: QualityResult | None = None
    ocr_result: dict[str, Any] | None = None
    mrz_result: dict[str, Any] | None = None
    validation_result: dict[str, Any] | None = None
    selfie_path: str | None = None
    allowed_outputs: dict[str, Any] = {}
```

## 2. Output Contract: `ModuleResult`
```python
class ModuleResult(BaseModel):
    module: str  # "ocr", "quality", "validation", "tampering", "face", "fusion"
    status: Literal["SUCCESS", "PARTIAL", "FAILED", "INCONCLUSIVE"]
    evidence_items: list[EvidenceItem] = []
    processing_time_ms: int | None = None
    errors: list[str] = []
    metadata: dict[str, Any] = {}
```

## 3. Evidence Contract: `EvidenceItem`
```python
class EvidenceItem(BaseModel):
    id: UUID | None = None
    screening_id: UUID
    module_name: str
    module_result_id: UUID | None = None
    category: str
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    source: str
    confidence: float
    description: str
    document_region: BoundingBox | None = None
    metrics: dict[str, float | str] = {}
```

## 4. Contract Violation Protocol
If a module throws an unhandled exception or returns a dictionary that fails schema instantiation:
1. `ModuleDispatcher` catches the error.
2. `ModuleResult(status="FAILED", errors=[str(exc)])` is synthesized.
3. The screening status is set to `REVIEW_RECOMMENDED` or `INCONCLUSIVE`.
4. Under NO circumstances does Person 5 rewrite the underlying module algorithm.
