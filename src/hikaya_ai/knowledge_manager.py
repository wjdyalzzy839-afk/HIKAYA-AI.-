import json
from pathlib import Path
from datetime import datetime, timezone


ALLOWED_STATUSES = {
    "unverified",
    "source_attached_needs_fact_review",
    "needs_review",
    "verified"
}


class KnowledgeManager:
    def __init__(self, knowledge_path, audit_path=None):
        self.path = Path(knowledge_path)
        self.audit_path = Path(
            audit_path or self.path.parent / "knowledge_audit.jsonl"
        )

        if not self.path.exists():
            raise FileNotFoundError("قاعدة المعرفة غير موجودة.")

        self._load()

    def _load(self):
        self.records = json.loads(
            self.path.read_text(encoding="utf-8")
        )

        if not isinstance(self.records, list):
            raise ValueError("قاعدة المعرفة يجب أن تكون قائمة.")

        ids = [item.get("id") for item in self.records]

        if None in ids or len(ids) != len(set(ids)):
            raise ValueError("معرّفات المعلومات مفقودة أو مكررة.")

    def list_records(self, status=None):
        if status is not None and status not in ALLOWED_STATUSES:
            raise ValueError("حالة التوثيق غير معروفة.")

        return [
            dict(item)
            for item in self.records
            if status is None or item.get("status") == status
        ]

    def get_record(self, record_id):
        for item in self.records:
            if item.get("id") == record_id:
                return dict(item)

        return None

    def update_status(
        self,
        record_id,
        new_status,
        reviewer,
        note,
        confirm_review=False
    ):
        if new_status not in ALLOWED_STATUSES:
            raise ValueError("حالة التوثيق غير مسموحة.")

        if not isinstance(reviewer, str) or not reviewer.strip():
            raise ValueError("اسم المراجع مطلوب.")

        if not isinstance(note, str) or not note.strip():
            raise ValueError("سبب التعديل مطلوب.")

        target = next(
            (item for item in self.records
             if item.get("id") == record_id),
            None
        )

        if target is None:
            raise KeyError("المعلومة غير موجودة.")

        if new_status == "verified":
            if confirm_review is not True:
                raise ValueError("اعتماد المعلومة يتطلب تأكيد المراجعة.")

            if not target.get("source_url"):
                raise ValueError("لا يمكن اعتماد معلومة بلا رابط مصدر.")

        old_status = target.get("status", "unverified")
        timestamp = datetime.now(timezone.utc).isoformat()

        updated = dict(target)
        updated["status"] = new_status
        updated["reviewed_by"] = reviewer.strip()
        updated["review_note"] = note.strip()
        updated["reviewed_at"] = timestamp

        new_records = [
            updated if item.get("id") == record_id else item
            for item in self.records
        ]

        audit_entry = {
            "record_id": record_id,
            "old_status": old_status,
            "new_status": new_status,
            "reviewer": reviewer.strip(),
            "note": note.strip(),
            "timestamp": timestamp
        }

        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(new_records, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        temporary.replace(self.path)

        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        with self.audit_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(audit_entry, ensure_ascii=False) + "\n")

        self.records = new_records

        return {
            "success": True,
            "record_id": record_id,
            "old_status": old_status,
            "new_status": new_status,
            "audit_saved": True
        }
