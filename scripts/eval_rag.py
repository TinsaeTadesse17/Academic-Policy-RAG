from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.utils.config import load_settings, PROJECT_ROOT
from src.retrieval.embeddings import EmbeddingModel
from src.retrieval.vector_store import VectorStore
from src.retrieval.retriever import Retriever
from src.generation.llm import LLMClient
from src.generation.answer import generate_answer, format_contexts


def load_questions(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("eval_questions.json must be a list of questions")
    return data


def grade_with_sources(llm: LLMClient, question: str, answer: str, sources: str) -> str:
    system_prompt = "You are grading answer quality. Return one word: PASS or FAIL."
    user_prompt = (
        f"Question: {question}\n\nAnswer: {answer}\n\nSources:\n{sources}\n\n"
        "Does the answer align with the sources?"
    )
    result = llm.chat(system_prompt=system_prompt, user_prompt=user_prompt).strip()
    return result


def main() -> None:
    settings = load_settings()
    eval_path = PROJECT_ROOT / "data" / "eval_questions.json"
    if not eval_path.exists():
        raise FileNotFoundError("data/eval_questions.json not found")

    llm = LLMClient(settings.openai_api_key, settings.openai_model)
    embedder = EmbeddingModel(settings.embedding_model)
    store = VectorStore(settings.qdrant_url, settings.qdrant_collection)
    retriever = Retriever(embedder, store)

    rows = []
    for question in load_questions(eval_path):
        rag_retrieved = retriever.retrieve(question, settings.top_k)
        rag_result = generate_answer(question, rag_retrieved, llm)
        rag_sources, _ = format_contexts(rag_retrieved)

        llm_only = llm.chat(
            system_prompt="Answer the question as best you can.",
            user_prompt=question,
        )

        rows.append(
            {
                "question": question,
                "llm_only_answer": llm_only,
                "rag_answer": rag_result["answer"],
                "rag_has_citations": "[" in rag_result["answer"],
                "rag_grade": grade_with_sources(llm, question, rag_result["answer"], rag_sources),
            }
        )

    output_path = PROJECT_ROOT / "data" / "eval_results.csv"
    pd.DataFrame(rows).to_csv(output_path, index=False)


if __name__ == "__main__":
    main()
