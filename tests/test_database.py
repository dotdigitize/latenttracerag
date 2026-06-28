from backend import database


async def test_database_tables_exist():
    rows = await database.fetch_all("SELECT name FROM sqlite_master WHERE type = 'table'")
    names = {row["name"] for row in rows}
    assert "documents" in names
    assert "retrieval_traces" in names
    assert "model_run_configs" in names
