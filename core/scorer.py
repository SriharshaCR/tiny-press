import numpy as np
from models.model_loader import get_embedder


def semantic_score(original: str, compressed: str) -> float:
    embedder = get_embedder()
    vecs = embedder.encode([original, compressed], convert_to_numpy=True)
    cos = float(
        np.dot(vecs[0], vecs[1]) / (np.linalg.norm(vecs[0]) * np.linalg.norm(vecs[1]))
    )
    return round(max(0.0, min(1.0, cos)), 4)
