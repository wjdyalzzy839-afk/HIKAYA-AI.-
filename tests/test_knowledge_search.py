import json
from hikaya_ai.knowledge_search import KnowledgeSearch


def test_search_finds_matching_fact(tmp_path):
    data = [{
        "id": "TEST-001",
        "fact": "كانت سبأ مملكة قديمة في جنوب الجزيرة العربية.",
        "source_url": "https://example.com",
        "status": "source_attached_needs_fact_review"
    }]

    path = tmp_path / "knowledge.json"
    path.write_text(json.dumps(data), encoding="utf-8")

    search = KnowledgeSearch(path)
    results = search.search("مملكة سبأ")

    assert len(results) == 1
    assert results[0]["id"] == "TEST-001"


def test_unverified_fact_is_not_marked_verified(tmp_path):
    data = [{
        "id": "TEST-002",
        "fact": "تقع اليمن في جنوب غرب شبه الجزيرة العربية.",
        "source_url": "https://example.com",
        "status": "source_attached_needs_fact_review"
    }]

    path = tmp_path / "knowledge.json"
    path.write_text(json.dumps(data), encoding="utf-8")

    results = KnowledgeSearch(path).search("اليمن")

    assert len(results) == 1
    assert results[0]["verified"] is False


def test_empty_query_returns_no_results(tmp_path):
    path = tmp_path / "knowledge.json"
    path.write_text("[]", encoding="utf-8")

    assert KnowledgeSearch(path).search("   ") == []
