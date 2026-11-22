from hikaya_ai.answer_evaluator import AnswerEvaluator


def test_verified_answer_gets_full_score():
    answer = {
        "success": True,
        "results": [{
            "fact": "معلومة",
            "source_url": "https://example.com",
            "verified": True
        }]
    }

    result = AnswerEvaluator().evaluate(answer)

    assert result["valid"] is True
    assert result["score"] == 100


def test_unverified_answer_is_rejected():
    answer = {
        "success": True,
        "results": [{
            "fact": "معلومة",
            "source_url": "https://example.com",
            "verified": False
        }]
    }

    result = AnswerEvaluator().evaluate(answer)

    assert result["valid"] is False
    assert "توجد معلومة غير موثقة" in result["issues"]


def test_empty_answer_is_rejected():
    result = AnswerEvaluator().evaluate({
        "success": False,
        "results": []
    })

    assert result["valid"] is False
    assert result["score"] == 60


def test_invalid_input_is_rejected():
    result = AnswerEvaluator().evaluate("نص")

    assert result["valid"] is False
    assert result["score"] == 0
