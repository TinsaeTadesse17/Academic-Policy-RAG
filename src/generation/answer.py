from __future__ import annotations

from typing import Iterable

from src.generation.llm import LLMClient


def format_contexts(retrieved: Iterable[dict]) -> tuple[str, list[dict]]:
    context_blocks: list[str] = []
    citations: list[dict] = []
    for idx, item in enumerate(retrieved, start=1):
        payload = item.get("payload") or {}
        text = payload.get("text", "")
        source_pdf = payload.get("source_pdf", "unknown")
        page_number = payload.get("page_number", "unknown")
        chunk_id = payload.get("chunk_id", "unknown")
        citations.append(
            {
                "source_pdf": source_pdf,
                "page_number": page_number,
                "chunk_id": chunk_id,
            }
        )
        context_blocks.append(
            f"[{idx}] Source: {source_pdf} | Page: {page_number} | Chunk: {chunk_id}\n{text}"
        )
    return "\n\n".join(context_blocks), citations


def generate_answer(question: str, retrieved: list[dict], llm: LLMClient) -> dict:
    context_text, citations = format_contexts(retrieved)

    system_prompt = (
        "You are a university policy assistant. Answer only using the provided "
        "sources. If the sources do not contain the answer, say you cannot find "
        "it in the documents. Always include citations in the form [#]."
    )
    user_prompt = (
        f"Question: {question}\n\n"
        f"Sources:\n{context_text}\n\n"
        "Return a concise answer with citations."
    )

    answer = llm.chat(system_prompt=system_prompt, user_prompt=user_prompt)
    return {"answer": answer, "citations": citations}
