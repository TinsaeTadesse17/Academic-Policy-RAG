from __future__ import annotations

from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    def __init__(self, model_name: str) -> None:
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return [emb.tolist() for emb in embeddings]
