from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_model: str
    qdrant_url: str
    qdrant_collection: str
    embedding_model: str
    top_k: int
    chunk_words: int
    chunk_overlap: int


def load_settings() -> Settings:
    load_dotenv(PROJECT_ROOT / ".env")

    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        qdrant_collection=os.getenv("QDRANT_COLLECTION", "university_policies"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5"),
        top_k=int(os.getenv("TOP_K", "5")),
        chunk_words=int(os.getenv("CHUNK_WORDS", "350")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "50")),
    )
