from backend.evaluator import evaluate_answer


def test_evaluator_scores_citations():
    metrics = evaluate_answer(
        "Severity one incidents are acknowledged within fifteen minutes.",
        [{"title": "Customer Support Policy Reference"}],
        "Severity one incidents are acknowledged within fifteen minutes.",
        ["Customer Support Policy Reference"],
    )
    assert metrics["citation_recall"] == 1.0
    assert metrics["unsupported_answer_flag"] is False
