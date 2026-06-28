from backend.retriever import Retriever


async def test_retriever_returns_ranked_chunks():
    results = await Retriever().retrieve("severity one support incidents acknowledged", top_k=2)
    assert len(results) == 2
    assert results[0].score >= results[1].score
