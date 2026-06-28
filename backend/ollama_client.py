from __future__ import annotations

import hashlib
import math
from typing import Any

import httpx

from .config import settings


class OllamaClient:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")

    async def available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=0.3) as client:
                response = await client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    async def list_models(self) -> list[str]:
        try:
            async with httpx.AsyncClient(timeout=0.5) as client:
                response = await client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            return [item.get("name", "") for item in response.json().get("models", []) if item.get("name")]
        except httpx.HTTPError:
            return []

    async def generate(self, prompt: str, model: str | None = None) -> str | None:
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={"model": model or settings.chat_model, "prompt": prompt, "stream": False},
                )
            response.raise_for_status()
            return str(response.json().get("response", "")).strip()
        except httpx.HTTPError:
            return None

    async def embed(self, text: str, model: str | None = None) -> list[float] | None:
        try:
            async with httpx.AsyncClient(timeout=0.5) as client:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": model or settings.embed_model, "prompt": text},
                )
            response.raise_for_status()
            embedding = response.json().get("embedding")
            return [float(x) for x in embedding] if embedding else None
        except httpx.HTTPError:
            return None


def lexical_embedding(text: str, dims: int = 64) -> list[float]:
    vector = [0.0] * dims
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:2], "big") % dims
        sign = 1.0 if digest[2] % 2 == 0 else -1.0
        vector[idx] += sign
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


def cosine(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    size = min(len(a), len(b))
    dot = sum(a[i] * b[i] for i in range(size))
    na = math.sqrt(sum(a[i] * a[i] for i in range(size))) or 1.0
    nb = math.sqrt(sum(b[i] * b[i] for i in range(size))) or 1.0
    return dot / (na * nb)


def estimate_tokens(text: str) -> int:
    return max(1, len(text.split()))
