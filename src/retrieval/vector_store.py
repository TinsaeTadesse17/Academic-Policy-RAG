from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.http import models


class VectorStore:
    def __init__(self, url: str, collection: str) -> None:
        self.client = QdrantClient(url=url)
        self.collection = collection

    def ensure_collection(self, vector_size: int) -> None:
        existing = self.client.get_collections().collections
        if any(col.name == self.collection for col in existing):
            return

        self.client.create_collection(
            collection_name=self.collection,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE,
            ),
        )

    def upsert(
        self,
        ids: list[int],
        vectors: list[list[float]],
        payloads: list[dict],
    ) -> None:
        points = [
            models.PointStruct(id=pid, vector=vec, payload=payload)
            for pid, vec, payload in zip(ids, vectors, payloads)
        ]
        self.client.upsert(collection_name=self.collection, points=points)

    def search(self, vector: list[float], limit: int) -> list[dict]:
        results = self.client.search(
            collection_name=self.collection,
            query_vector=vector,
            limit=limit,
            with_payload=True,
        )
        return [
            {
                "score": hit.score,
                "payload": hit.payload,
            }
            for hit in results
        ]
