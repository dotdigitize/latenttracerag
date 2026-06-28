from backend.document_store import list_documents


async def test_documents_seeded():
    docs = await list_documents()
    assert len(docs) >= 10
    assert any("Finance Risk Controls" in doc["title"] for doc in docs)
