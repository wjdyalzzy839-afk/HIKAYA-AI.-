import json
import pytest
from hikaya_ai.knowledge_manager import KnowledgeManager


def create_manager(tmp_path, source_url="https://example.com"):
    path = tmp_path / "knowledge.json"
    path.write_text(json.dumps([{
        "id": "TEST-001",
        "fact": "معلومة تجريبية",
        "source_url": source_url,
        "status": "unverified"
    }]), encoding="utf-8")

    return KnowledgeManager(path), path


def test_list_and_get_records(tmp_path):
    manager, _ = create_manager(tmp_path)

    assert len(manager.list_records()) == 1
    assert manager.get_record("TEST-001")["fact"] == "معلومة تجريبية"


def test_update_status_and_save_audit(tmp_path):
    manager, _ = create_manager(tmp_path)

    result = manager.update_status(
        "TEST-001", "needs_review", "Reviewer", "مراجعة أولية"
    )

    assert result["success"] is True
    assert manager.get_record("TEST-001")["status"] == "needs_review"
    assert manager.audit_path.exists()


def test_verified_requires_explicit_confirmation(tmp_path):
    manager, _ = create_manager(tmp_path)

    with pytest.raises(ValueError):
        manager.update_status(
            "TEST-001", "verified", "Reviewer", "تمت المراجعة"
        )


def test_verified_requires_source(tmp_path):
    manager, _ = create_manager(tmp_path, source_url="")

    with pytest.raises(ValueError):
        manager.update_status(
            "TEST-001", "verified", "Reviewer",
            "مراجعة", confirm_review=True
        )


def test_unknown_record_is_rejected(tmp_path):
    manager, _ = create_manager(tmp_path)

    with pytest.raises(KeyError):
        manager.update_status(
            "UNKNOWN", "needs_review", "Reviewer", "مراجعة"
        )



def test_existing_source_review_status_is_supported(tmp_path):
    manager, _ = create_manager(tmp_path)

    manager.records[0]["status"] = "source_attached_needs_fact_review"

    assert len(manager.list_records(
        status="source_attached_needs_fact_review"
    )) == 1
