import json
from pathlib import Path


def validate_knowledge(path):
    path = Path(path)
    records = json.loads(path.read_text(encoding="utf-8"))
    results = []

    for item in records:
        errors = []

        if not item.get("fact"):
            errors.append("المعلومة فارغة")

        if not item.get("source_url"):
            errors.append("المصدر مفقود")

        if item.get("status") != "verified":
            errors.append("المعلومة لم تعتمد بعد")

        results.append({
            "id": item.get("id"),
            "valid": len(errors) == 0,
            "errors": errors
        })

    return results
