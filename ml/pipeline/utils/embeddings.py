"""
Sentence-transformer embedding utility.
Single instance shared across the pipeline — never instantiate inline.
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Union

import numpy as np

_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
_EMBEDDING_DIM = 384  # matches all-MiniLM-L6-v2


@lru_cache(maxsize=1)
def _get_model():
    """Lazy-load model once and cache. Thread-safe via GIL for inference."""
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(_MODEL_NAME)
    except ImportError as e:
        raise ImportError(
            "sentence-transformers not installed. Run: pip install sentence-transformers"
        ) from e


def embed_texts(texts: list[str]) -> np.ndarray:
    """
    Returns a (N, 384) float32 array of embeddings.
    Handles empty input gracefully.
    """
    if not texts:
        return np.zeros((0, _EMBEDDING_DIM), dtype=np.float32)
    model = _get_model()
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return np.array(embeddings, dtype=np.float32)


def embed_single(text: str) -> np.ndarray:
    """Returns a (384,) embedding vector."""
    return embed_texts([text])[0]


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two normalized vectors."""
    a = a / (np.linalg.norm(a) + 1e-10)
    b = b / (np.linalg.norm(b) + 1e-10)
    return float(np.dot(a, b))


def batch_cosine_similarity(query: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """
    Compute cosine similarities between a query vector and a matrix of vectors.
    Returns a (N,) array of similarity scores.
    """
    query = query / (np.linalg.norm(query) + 1e-10)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10
    normed = matrix / norms
    return normed @ query


def cluster_texts(texts: list[str], n_clusters: int = 5) -> tuple[np.ndarray, np.ndarray]:
    """
    Cluster texts into n_clusters using KMeans on sentence embeddings.
    Returns (labels, centroids).
    Used by Hackability extractor for use-case diversity indexing.
    """
    if len(texts) < n_clusters:
        n_clusters = max(1, len(texts))

    from sklearn.cluster import KMeans

    embeddings = embed_texts(texts)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(embeddings)
    return labels, kmeans.cluster_centers_


EMBEDDING_DIM = _EMBEDDING_DIM
