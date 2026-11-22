from pathlib import Path
from urllib.parse import urlsplit
import json


def validate_source_record(record):
    issues = []

    fact = record.get("fact")
    source = record.get("source")
    source_url = record.get("source_url")

    if not isinstance(fact, str) or not fact.strip():
        issues.append("المعلومة مفقودة")

    if not isinstance(source, str) or not source.strip():
        issues.append("اسم المصدر مفقود")

    valid_url = False

    if isinstance(source_url, str) and source_url.strip():
        try:
            parsed = urlsplit(source_url.strip())
            valid_url = (
                parsed.scheme in ("http", "https")
                and bool(parsed.hostname)
                and not parsed.username
                and not parsed.password
            )
        except ValueError:
            valid_url = False

    if not valid_url:
        issues.append("رابط المصدر غير صالح")

    ready = len(issues) == 0

    return {
        "id": record.get("id"),
        "valid": ready,
        "ready_for_manual_review": ready,
        "automatically_verified": False,
        "issues": issues
    }


def validate_source_file(path):
    path = Path(path)

    records = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(records, list):
        raise ValueError("قاعدة المعرفة يجب أن تكون قائمة.")

    return [
        validate_source_record(record)
        for record in records
    ]



def source_quality_report(path):
    results = validate_source_file(path)

    return {
        "total": len(results),
        "ready_for_review": sum(
            item["ready_for_manual_review"] for item in results
        ),
        "needs_repair": sum(
            not item["valid"] for item in results
        ),
        "verified": sum(
            item["automatically_verified"] for item in results
        ),
        "records": results
    }
