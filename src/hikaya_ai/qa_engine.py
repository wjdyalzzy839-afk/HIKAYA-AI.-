import re

from .knowledge_search import KnowledgeSearch
from .memory_store import HikayaMemory


class KnowledgeQA:
    def __init__(self, knowledge_path, memory_path=None):
        self.search_engine = KnowledgeSearch(knowledge_path)
        self.memory = (
            HikayaMemory(memory_path)
            if memory_path is not None
            else None
        )

    def remember(self, content, category="عام", source="", source_url=""):
        if self.memory is None:
            return {
                "success": False,
                "message": "الذاكرة غير مفعلة."
            }

        result = self.memory.add_memory(
            content=content,
            category=category,
            source=source,
            source_url=source_url,
            status="unverified"
        )

        return {
            "success": True,
            "message": "تم حفظ المعلومة في الذاكرة.",
            "memory": result
        }

    def answer(self, question, top_k=5):
        if not isinstance(question, str) or not question.strip():
            return {
                "success": False,
                "message": "يرجى إدخال سؤال واضح.",
                "results": []
            }

        results = self.search_engine.search(question, top_k=top_k)

        for item in results:
            item["origin"] = "knowledge"

        if self.memory is not None:
            words = set(re.findall(r"\w+", question))

            found_memory = {}

            for word in words:
                for item in self.memory.search(word, limit=100):
                    found_memory[item["id"]] = item

            for item in found_memory.values():
                content_words = set(
                    re.findall(r"\w+", item["content"])
                )
                matched = words & content_words

                if not matched:
                    continue

                results.append({
                    "id": item["id"],
                    "fact": item["content"],
                    "topic": item["category"],
                    "source": item["source"],
                    "source_url": item["source_url"],
                    "status": item["status"],
                    "verified": item["status"] == "verified",
                    "score": round(len(matched) / len(words), 3),
                    "origin": "memory"
                })

        results.sort(
            key=lambda item: (
                item["score"],
                item["verified"]
            ),
            reverse=True
        )

        results = results[:max(0, top_k)]

        if not results:
            return {
                "success": False,
                "message": "لم أعثر على معلومات مطابقة.",
                "results": []
            }

        return {
            "success": True,
            "message": "تم العثور على معلومات من مصادر المعرفة والذاكرة.",
            "results": results
        }
