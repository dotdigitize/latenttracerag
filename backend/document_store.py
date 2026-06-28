from __future__ import annotations

from pathlib import Path

from . import database
from .ollama_client import estimate_tokens


def chunk_text(text: str, max_words: int = 110) -> list[str]:
    words = text.split()
    chunks: list[str] = []
    for start in range(0, len(words), max_words):
        chunk = " ".join(words[start : start + max_words]).strip()
        if chunk:
            chunks.append(chunk)
    return chunks or [text.strip()]


async def upsert_document(path: Path) -> int:
    content = path.read_text(encoding="utf-8").strip()
    title = path.stem.replace("_", " ").title()
    existing = await database.fetch_one("SELECT id FROM documents WHERE path = ?", (str(path),))
    if existing:
        document_id = int(existing["id"])
        await database.execute("UPDATE documents SET title = ?, content = ? WHERE id = ?", (title, content, document_id))
        await database.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
    else:
        document_id = await database.execute(
            "INSERT INTO documents (title, path, content) VALUES (?, ?, ?)",
            (title, str(path), content),
        )
    for idx, chunk in enumerate(chunk_text(content)):
        await database.execute(
            "INSERT INTO chunks (document_id, chunk_index, text, token_estimate) VALUES (?, ?, ?, ?)",
            (document_id, idx, chunk, estimate_tokens(chunk)),
        )
    return document_id


async def seed_reference_corpus(root: Path = Path("corpus/reference")) -> int:
    await database.init_db()
    count = 0
    for path in sorted(root.glob("*.txt")):
        await upsert_document(path)
        count += 1
    return count


async def list_documents() -> list[dict]:
    return await database.fetch_all(
        "SELECT id, title, path, length(content) AS content_length, created_at FROM documents ORDER BY title"
    )


async def get_document(document_id: int) -> dict | None:
    document = await database.fetch_one("SELECT * FROM documents WHERE id = ?", (document_id,))
    if not document:
        return None
    chunks = await database.fetch_all(
        "SELECT id, chunk_index, text, token_estimate FROM chunks WHERE document_id = ? ORDER BY chunk_index",
        (document_id,),
    )
    document["chunks"] = chunks
    return document
