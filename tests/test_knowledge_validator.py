import json
from hikaya_ai.knowledge_validator import validate_knowledge

def test_unverified_record_is_rejected(tmp_path):
    data = [{
        "id": "TEST-001",
        "fact": "معلومة تجريبية",
        "source_url": "https://example.com",
        "status": "source_attached_needs_fact_review"
    }]

    file = tmp_path / "knowledge.json"
    file.write_text(json.dumps(data), encoding="utf-8")

    result = validate_knowledge(file)

    assert result[0]["valid"] is False
    assert "المعلومة لم تعتمد بعد" in result[0]["errors"]

def test_verified_record_is_accepted(tmp_path):
    data = [{
        "id": "TEST-002",
        "fact": "معلومة تجريبية",
        "source_url": "https://example.com",
        "status": "verified"
    }]

    file = tmp_path / "knowledge.json"
    file.write_text(json.dumps(data), encoding="utf-8")

    result = validate_knowledge(file)

    assert result[0]["valid"] is True
