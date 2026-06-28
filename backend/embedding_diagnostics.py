from __future__ import annotations

import json
from statistics import mean
from typing import Any

from . import database
from .ollama_client import cosine, lexical_embedding


async def compute_embedding_diagnostics() -> dict[str, Any]:
    rows = await database.fetch_all("SELECT text FROM chunks ORDER BY id LIMIT 100")
    vectors = [lexical_embedding(row["text"]) for row in rows]
    if len(vectors) < 2:
        result = {
            "mean_vector_similarity": 0.0,
            "embedding_spread_score": 0.0,
            "anisotropy_warning": False,
            "nearest_neighbor_stability": 0.0,
            "warning": "Not enough chunks for diagnostics.",
        }
    else:
        sims = [cosine(vectors[i], vectors[i + 1]) for i in range(len(vectors) - 1)]
        mean_sim = mean(sims)
        result = {
            "mean_vector_similarity": round(mean_sim, 4),
            "embedding_spread_score": round(1.0 - abs(mean_sim), 4),
            "anisotropy_warning": abs(mean_sim) > 0.85,
            "nearest_neighbor_stability": round(sum(1 for score in sims if score > 0.1) / len(sims), 4),
            "warning": "Using deterministic lexical embedding fallback unless local Ollama embeddings are configured.",
        }
    await database.execute("INSERT INTO embedding_diagnostics (diagnostics_json) VALUES (?)", (json.dumps(result),))
    return result
