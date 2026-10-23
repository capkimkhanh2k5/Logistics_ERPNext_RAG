"""Validate dense vector dimensions, finiteness and normalization."""

import numpy as np


def validate_vectors(vectors: np.ndarray, count: int) -> np.ndarray:
    vectors = np.asarray(vectors, dtype=np.float32)
    if vectors.shape != (count, 1024) or not np.isfinite(vectors).all():
        raise ValueError(f"Invalid dense vectors: {vectors.shape}")
    norm = np.linalg.norm(vectors, axis=1, keepdims=True)
    if (norm < 1e-8).any():
        raise ValueError("Zero embedding vector")
    return vectors / norm
