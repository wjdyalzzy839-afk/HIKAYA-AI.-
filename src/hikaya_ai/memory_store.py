import sqlite3
import hashlib
import unicodedata
from pathlib import Path
from datetime import datetime, timezone


class HikayaMemory:
    def __init__(self, database_path="data/hikaya_memory.db"):
        self.path = Path(database_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self):
        return sqlite3.connect(self.path)

    def initialize(self):
        with self.connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT DEFAULT '',
                    source_url TEXT DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'unverified',
                    created_at TEXT NOT NULL
                )
            """)

            db.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_category
                ON memories(category)
            """)

    def add_memory(
        self,
        content,
        category="عام",
        source="",
        source_url="",
        status="unverified"
    ):
        if not isinstance(content, str) or not content.strip():
            raise ValueError("محتوى الذاكرة لا يمكن أن يكون فارغاً.")

        if status not in ("unverified", "needs_review", "verified"):
            raise ValueError("حالة التوثيق غير معروفة.")

        normalized = unicodedata.normalize(
            "NFKC", content.strip()
        ).casefold()

        memory_id = hashlib.sha256(
            (category + "|" + normalized).encode("utf-8")
        ).hexdigest()

        with self.connect() as db:
            cursor = db.execute("""
                INSERT OR IGNORE INTO memories
                (id, category, content, source, source_url, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                memory_id,
                category,
                content.strip(),
                source,
                source_url,
                status,
                datetime.now(timezone.utc).isoformat()
            ))

            return {
                "success": True,
                "inserted": cursor.rowcount == 1,
                "id": memory_id,
                "status": status
            }

    def search(self, query, limit=10):
        if not isinstance(query, str) or not query.strip():
            return []

        limit = max(1, min(int(limit), 100))
        term = "%" + query.strip() + "%"

        with self.connect() as db:
            db.row_factory = sqlite3.Row

            rows = db.execute("""
                SELECT *
                FROM memories
                WHERE content LIKE ? OR category LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (term, term, limit)).fetchall()

            return [dict(row) for row in rows]

    def count(self):
        with self.connect() as db:
            return db.execute(
                "SELECT COUNT(*) FROM memories"
            ).fetchone()[0]
