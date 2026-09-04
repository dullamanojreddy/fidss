"""Pure face-embedding comparison and decision logic."""
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class MatchResult:
    outcome: str
    similarity: float
    threshold: float

def cosine_similarity(first: np.ndarray, second: np.ndarray) -> float:
    first, second = np.asarray(first, dtype=np.float32).reshape(-1), np.asarray(second, dtype=np.float32).reshape(-1)
    if first.shape != second.shape or first.size == 0:
        raise ValueError("Embeddings must have the same non-zero shape")
    denominator = float(np.linalg.norm(first) * np.linalg.norm(second))
    if denominator == 0.0:
        raise ValueError("Embeddings must have non-zero magnitude")
    return float(np.clip(np.dot(first, second) / denominator, -1.0, 1.0))

def match_embeddings(first: np.ndarray, second: np.ndarray, threshold: float = 0.45) -> MatchResult:
    if not -1.0 <= threshold <= 1.0:
        raise ValueError("Similarity threshold must be between -1 and 1")
    similarity = cosine_similarity(first, second)
    return MatchResult("MATCH" if similarity >= threshold else "MISMATCH", similarity, threshold)
