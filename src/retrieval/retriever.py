from __future__ import annotations

from src.retrieval.embeddings import EmbeddingModel
from src.retrieval.vector_store import VectorStore


class Retriever:
    def __init__(self, embedding_model: EmbeddingModel, store: VectorStore) -> None:
        self.embedding_model = embedding_model
        self.store = store

    def retrieve(self, query: str, top_k: int) -> list[dict]:
        vector = self.embedding_model.encode([query])[0]
        return self.store.search(vector=vector, limit=top_k)
