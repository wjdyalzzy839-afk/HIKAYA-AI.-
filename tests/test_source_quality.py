import json
from hikaya_ai.source_quality import (
    validate_source_record,
    validate_source_file
)


def test_valid_source_is_ready_for_manual_review():
    record = {
        "id": "TEST-001",
        "fact": "معلومة تجريبية",
        "source": "مصدر تجريبي",
        "source_url": "https://example.com/page"
    }

    result = validate_source_record(record)

    assert result["valid"] is True
    assert result["ready_for_manual_review"] is True
    assert result["automatically_verified"] is False


def test_missing_source_is_rejected():
    record = {
        "id": "TEST-002",
        "fact": "معلومة تجريبية",
        "source": "",
        "source_url": "https://example.com"
    }

    result = validate_source_record(record)

    assert result["valid"] is False
    assert "اسم المصدر مفقود" in result["issues"]


def test_invalid_url_is_rejected():
    record = {
        "id": "TEST-003",
        "fact": "معلومة تجريبية",
        "source": "مصدر تجريبي",
        "source_url": "not-a-url"
    }

    result = validate_source_record(record)

    assert result["valid"] is False
    assert "رابط المصدر غير صالح" in result["issues"]


def test_source_file_validation(tmp_path):
    path = tmp_path / "knowledge.json"
    path.write_text(
        json.dumps([{
            "id": "TEST-004",
            "fact": "معلومة",
            "source": "مصدر",
            "source_url": "https://example.com"
        }]),
        encoding="utf-8"
    )

    results = validate_source_file(path)

    assert len(results) == 1
    assert results[0]["valid"] is True



def test_source_quality_report_counts(tmp_path):
    from hikaya_ai.source_quality import source_quality_report

    path = tmp_path / "knowledge.json"
    path.write_text(
        json.dumps([
            {
                "id": "TEST-001",
                "fact": "معلومة صحيحة الصيغة",
                "source": "مصدر",
                "source_url": "https://example.com"
            },
            {
                "id": "TEST-002",
                "fact": "معلومة بلا مصدر",
                "source": "",
                "source_url": ""
            }
        ]),
        encoding="utf-8"
    )

    report = source_quality_report(path)

    assert report["total"] == 2
    assert report["ready_for_review"] == 1
    assert report["needs_repair"] == 1
    assert report["verified"] == 0
