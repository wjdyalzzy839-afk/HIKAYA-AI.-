import json
import re
import unicodedata
from pathlib import Path


def normalize(text):
    text = unicodedata.normalize("NFKC", str(text))
    text = re.sub(r"[\u064B-\u065F\u0670]", "", text)
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    text = text.replace("ى", "ي").replace("ة", "ه")
    return text.lower()


def tokenize(text):
    return set(re.findall(r"\w+", normalize(text), flags=re.UNICODE))


class KnowledgeSearch:
    def __init__(self, knowledge_path):
        self.path = Path(knowledge_path)
        self.records = json.loads(
            self.path.read_text(encoding="utf-8")
        )

        if not isinstance(self.records, list):
            raise ValueError("قاعدة المعرفة يجب أن تكون قائمة.")

    def search(self, query, top_k=5):
        query_words = tokenize(query)

        if not query_words:
            return []

        results = []

        for item in self.records:
            searchable = " ".join([
                item.get("fact", ""),
                item.get("category", ""),
                item.get("topic", "")
            ])

            record_words = tokenize(searchable)
            matched = query_words & record_words

            if not matched:
                continue

            results.append({
                "id": item.get("id"),
                "fact": item.get("fact"),
                "topic": item.get("topic", item.get("category", "")),
                "source": item.get("source", ""),
                "source_url": item.get("source_url", ""),
                "status": item.get("status", "unknown"),
                "verified": item.get("status") == "verified",
                "score": round(len(matched) / len(query_words), 3)
            })

        results.sort(
            key=lambda item: (item["score"], item["verified"]),
            reverse=True
        )

        return results[:max(0, top_k)]
