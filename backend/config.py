from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    chat_model: str = os.getenv("CHAT_MODEL", "gemma4:e4b")
    worker_model: str = os.getenv("WORKER_MODEL", "gemma4:e2b")
    embed_model: str = os.getenv("EMBED_MODEL", "embeddinggemma:latest")
    database_path: Path = Path(os.getenv("DATABASE_PATH", "data/latenttracerag.db"))
    top_k: int = int(os.getenv("TOP_K", "3"))
    max_retrieval_steps: int = int(os.getenv("MAX_RETRIEVAL_STEPS", "4"))
    allow_external_apis: bool = os.getenv("ALLOW_EXTERNAL_APIS", "false").lower() == "true"


settings = Settings()
