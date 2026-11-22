import json
from hikaya_ai.qa_engine import KnowledgeQA


def test_qa_returns_matching_knowledge(tmp_path):
    data = [{
        "id": "TEST-001",
        "fact": "تقع اليمن في جنوب غرب شبه الجزيرة العربية.",
        "source_url": "https://example.com",
        "status": "source_attached_needs_fact_review"
    }]

    path = tmp_path / "knowledge.json"
    path.write_text(json.dumps(data), encoding="utf-8")

    qa = KnowledgeQA(path)
    result = qa.answer("أين تقع اليمن؟")

    assert result["success"] is True
    assert result["results"][0]["id"] == "TEST-001"
    assert result["results"][0]["verified"] is False


def test_qa_handles_unknown_question(tmp_path):
    path = tmp_path / "knowledge.json"
    path.write_text("[]", encoding="utf-8")

    qa = KnowledgeQA(path)
    result = qa.answer("ما تاريخ مدينة غير موجودة؟")

    assert result["success"] is False
    assert result["results"] == []


def test_qa_rejects_empty_question(tmp_path):
    path = tmp_path / "knowledge.json"
    path.write_text("[]", encoding="utf-8")

    qa = KnowledgeQA(path)
    result = qa.answer("   ")

    assert result["success"] is False
