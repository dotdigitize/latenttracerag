from __future__ import annotations

from dataclasses import dataclass

from . import database
from .ollama_client import OllamaClient, cosine, lexical_embedding


@dataclass
class RetrievedChunk:
    chunk_id: int
    document_id: int
    title: str
    text: str
    score: float


class Retriever:
    def __init__(self, client: OllamaClient | None = None) -> None:
        self.client = client or OllamaClient()

    async def retrieve(self, query: str, top_k: int = 3) -> list[RetrievedChunk]:
        rows = await database.fetch_all(
            """
            SELECT chunks.id AS chunk_id, chunks.document_id, documents.title, chunks.text
            FROM chunks JOIN documents ON documents.id = chunks.document_id
            """
        )
        query_embedding = await self.client.embed(query) or lexical_embedding(query)
        scored: list[RetrievedChunk] = []
        for row in rows:
            embedding = lexical_embedding(f"{row['title']} {row['text']}")
            lexical_bonus = self._keyword_overlap(query, row["text"]) * 0.08
            scored.append(
                RetrievedChunk(
                    chunk_id=int(row["chunk_id"]),
                    document_id=int(row["document_id"]),
                    title=str(row["title"]),
                    text=str(row["text"]),
                    score=round(cosine(query_embedding, embedding) + lexical_bonus, 6),
                )
            )
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]

    @staticmethod
    def _keyword_overlap(query: str, text: str) -> float:
        q = {token.strip(".,:;()").lower() for token in query.split() if len(token) > 3}
        t = {token.strip(".,:;()").lower() for token in text.split() if len(token) > 3}
        return len(q & t) / max(1, len(q))
