from __future__ import annotations

from sentence_transformers import SentenceTransformer
import torch


class EmbeddingModel:
    def __init__(self, model_name: str) -> None:
        # Force CPU to reduce memory usage
        device = "cpu"
        # Load model with CPU device
        self.model = SentenceTransformer(model_name, device=device)
        # Set model to evaluation mode and disable gradient computation
        self.model.eval()
        # Disable gradient tracking to save memory
        for param in self.model.parameters():
            param.requires_grad = False

    def encode(self, texts: list[str]) -> list[list[float]]:
        # Use no_grad context to save memory
        with torch.no_grad():
            embeddings = self.model.encode(
                texts, 
                normalize_embeddings=True,
                show_progress_bar=False,
                batch_size=8  # Smaller batch size to reduce memory
            )
        return [emb.tolist() for emb in embeddings]
