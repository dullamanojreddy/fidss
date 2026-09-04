# Face verification contract

`analyze(context: DocumentContext) -> ModuleResult` compares the largest detected document portrait with exactly one traveler-selfie face. Detection prefers a locally configured SCRFD ONNX model and otherwise uses OpenCV only for localization. Embeddings always require locally configured ArcFace weights; a missing model produces `INCONCLUSIVE`, never a fabricated comparison.

Environment configuration:

- `FIDSS_SCRFD_MODEL_PATH`: optional local SCRFD ONNX path.
- `FIDSS_ARCFACE_MODEL_PATH`: required local ArcFace ONNX path for matching.
- `FIDSS_FACE_SIMILARITY_THRESHOLD`: cosine threshold, default `0.45`.

Metadata includes `outcome` (`MATCH`, `MISMATCH`, `INCONCLUSIVE`, `NO_FACE`, or `MULTIPLE_FACES`), face counts, quality measurements, similarity, and threshold. Only a quality-gated mismatch emits a high-severity evidence item. Missing faces, poor quality, missing selfie, or unavailable weights remain inconclusive.
