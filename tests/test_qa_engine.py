import json
from hikaya_ai.qa_engine import KnowledgeQA


def create_knowledge(path, records=None):
    path.write_text(
        json.dumps(records or [], ensure_ascii=False),
        encoding="utf-8"
    )
    return path


def test_qa_returns_matching_knowledge(tmp_path):
    path = create_knowledge(tmp_path / "knowledge.json", [{
        "id": "TEST-001",
        "fact": "تقع اليمن في جنوب غرب شبه الجزيرة العربية.",
        "source_url": "https://example.com",
        "status": "source_attached_needs_fact_review"
    }])

    qa = KnowledgeQA(path)
    result = qa.answer("أين تقع اليمن؟")

    assert result["success"] is True
    assert result["results"][0]["id"] == "TEST-001"
    assert result["results"][0]["verified"] is False


def test_qa_handles_unknown_question(tmp_path):
    path = create_knowledge(tmp_path / "knowledge.json")
    qa = KnowledgeQA(path)

    result = qa.answer("ما تاريخ مدينة غير موجودة؟")

    assert result["success"] is False
    assert result["results"] == []


def test_qa_rejects_empty_question(tmp_path):
    path = create_knowledge(tmp_path / "knowledge.json")
    qa = KnowledgeQA(path)

    result = qa.answer("   ")

    assert result["success"] is False


def test_qa_remembers_and_retrieves_information(tmp_path):
    path = create_knowledge(tmp_path / "knowledge.json")
    qa = KnowledgeQA(
        path,
        memory_path=tmp_path / "memory.db"
    )

    saved = qa.remember(
        "مملكة سبأ تاريخياً في جنوب الجزيرة العربية",
        category="تاريخ"
    )

    result = qa.answer("مملكة سبأ")

    assert saved["success"] is True
    assert result["success"] is True
    assert result["results"][0]["origin"] == "memory"


def test_memory_information_stays_unverified(tmp_path):
    path = create_knowledge(tmp_path / "knowledge.json")
    qa = KnowledgeQA(
        path,
        memory_path=tmp_path / "memory.db"
    )

    qa.remember("مدينة صنعاء تاريخية", category="تاريخ")
    result = qa.answer("صنعاء")

    assert result["results"][0]["verified"] is False


def test_remember_fails_when_memory_is_disabled(tmp_path):
    path = create_knowledge(tmp_path / "knowledge.json")
    qa = KnowledgeQA(path)

    result = qa.remember("معلومة جديدة")

    assert result["success"] is False



def test_memory_persists_after_recreating_qa(tmp_path):
    knowledge = create_knowledge(tmp_path / "knowledge.json")
    database = tmp_path / "memory.db"

    first = KnowledgeQA(knowledge, memory_path=database)
    first.remember("معلومة محفوظة", category="تاريخ")

    second = KnowledgeQA(knowledge, memory_path=database)
    result = second.answer("معلومة محفوظة")

    assert result["success"] is True
    assert result["results"][0]["fact"] == "معلومة محفوظة"
    assert result["results"][0]["verified"] is False
