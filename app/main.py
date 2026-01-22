from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.utils.config import load_settings
from src.retrieval.embeddings import EmbeddingModel
from src.retrieval.vector_store import VectorStore
from src.retrieval.retriever import Retriever
from src.generation.llm import LLMClient
from src.generation.answer import generate_answer


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    citations: list[dict]


app = FastAPI(title="University Policy RAG")
settings = load_settings()

embedding_model = EmbeddingModel(settings.embedding_model)
vector_store = VectorStore(settings.qdrant_url, settings.qdrant_collection)
retriever = Retriever(embedding_model, vector_store)
llm_client = LLMClient(settings.openai_api_key, settings.openai_model)


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question is required")

    retrieved = retriever.retrieve(request.question, settings.top_k)
    if not retrieved:
        return AskResponse(
            answer="I could not find that in the documents.",
            citations=[],
        )
    result = generate_answer(request.question, retrieved, llm_client)
    return AskResponse(**result)
