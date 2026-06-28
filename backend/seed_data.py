from __future__ import annotations

import asyncio
import json
from pathlib import Path

from . import database
from .config import settings
from .document_store import seed_reference_corpus
from .embedding_diagnostics import compute_embedding_diagnostics
from .reporting import write_reports


async def seed() -> dict:
    await database.init_db()
    document_count = await seed_reference_corpus()
    cases = _load_cases()
    for case in cases:
        await database.execute(
            """
            INSERT OR REPLACE INTO evaluation_cases (id, question, expected_answer, expected_sources, tags)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                case["id"],
                case["question"],
                case["expected_answer"],
                json.dumps(case["expected_sources"]),
                json.dumps(case.get("tags", [])),
            ),
        )
    await database.execute(
        "INSERT INTO model_run_configs (chat_model, worker_model, embed_model, allow_external_apis) VALUES (?, ?, ?, ?)",
        (settings.chat_model, settings.worker_model, settings.embed_model, int(settings.allow_external_apis)),
    )
    diagnostics = await compute_embedding_diagnostics()
    summary = {"mode": "seed", "case_count": len(cases), "document_count": document_count, "embedding_diagnostics": diagnostics, "metrics": {}}
    await write_reports(summary)
    return summary


def _load_cases() -> list[dict]:
    path = Path("corpus/evaluation/eval_cases.jsonl")
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    result = asyncio.run(seed())
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
