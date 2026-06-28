from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ["DATABASE_PATH"] = "data/test_latenttracerag.db"

from backend import database
from backend.seed_data import seed


@pytest.fixture(autouse=True)
async def prepared_db():
    path = Path("data/test_latenttracerag.db")
    if path.exists():
        path.unlink()
    await database.init_db(path)
    await seed()
    yield
