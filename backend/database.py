from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Iterable

import aiosqlite

from .config import settings


SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    path TEXT NOT NULL UNIQUE,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    token_estimate INTEGER NOT NULL,
    FOREIGN KEY(document_id) REFERENCES documents(id)
);
CREATE TABLE IF NOT EXISTS queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_text TEXT NOT NULL,
    mode TEXT NOT NULL,
    top_k INTEGER NOT NULL,
    max_retrieval_steps INTEGER NOT NULL,
    case_id TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS retrieval_traces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_id INTEGER NOT NULL,
    mode TEXT NOT NULL,
    model_unavailable INTEGER NOT NULL DEFAULT 0,
    trace_json TEXT NOT NULL,
    FOREIGN KEY(query_id) REFERENCES queries(id)
);
CREATE TABLE IF NOT EXISTS retrieval_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id INTEGER NOT NULL,
    step_index INTEGER NOT NULL,
    thought TEXT,
    subquery TEXT,
    action_json TEXT,
    retrieved_chunk_ids TEXT NOT NULL,
    latency_ms REAL NOT NULL,
    FOREIGN KEY(trace_id) REFERENCES retrieval_traces(id)
);
CREATE TABLE IF NOT EXISTS answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_id INTEGER NOT NULL,
    answer_text TEXT NOT NULL,
    citations_json TEXT NOT NULL,
    metrics_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(query_id) REFERENCES queries(id)
);
CREATE TABLE IF NOT EXISTS evaluation_cases (
    id TEXT PRIMARY KEY,
    question TEXT NOT NULL,
    expected_answer TEXT NOT NULL,
    expected_sources TEXT NOT NULL,
    tags TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS evaluation_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mode TEXT NOT NULL,
    summary_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS failure_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER,
    query_id INTEGER,
    failure_type TEXT NOT NULL,
    details TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS latency_traces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_id INTEGER,
    stage_json TEXT NOT NULL,
    total_time_ms REAL NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS trajectory_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_id INTEGER,
    metrics_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS embedding_diagnostics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    diagnostics_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS model_run_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_model TEXT NOT NULL,
    worker_model TEXT NOT NULL,
    embed_model TEXT NOT NULL,
    allow_external_apis INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def ensure_parent(path: Path | None = None) -> Path:
    db_path = path or settings.database_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


async def init_db(path: Path | None = None) -> None:
    db_path = ensure_parent(path)
    async with aiosqlite.connect(db_path) as db:
        await db.executescript(SCHEMA)
        await db.commit()


def init_db_sync(path: Path | None = None) -> None:
    db_path = ensure_parent(path)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA)
        conn.commit()


async def fetch_all(query: str, params: Iterable[Any] = ()) -> list[dict[str, Any]]:
    async with aiosqlite.connect(ensure_parent()) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(query, tuple(params))
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def fetch_one(query: str, params: Iterable[Any] = ()) -> dict[str, Any] | None:
    rows = await fetch_all(query, params)
    return rows[0] if rows else None


async def execute(query: str, params: Iterable[Any] = ()) -> int:
    async with aiosqlite.connect(ensure_parent()) as db:
        cursor = await db.execute(query, tuple(params))
        await db.commit()
        return int(cursor.lastrowid)
