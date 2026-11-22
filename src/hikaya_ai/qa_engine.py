from .knowledge_search import KnowledgeSearch


class KnowledgeQA:
    def __init__(self, knowledge_path):
        self.search_engine = KnowledgeSearch(knowledge_path)

    def answer(self, question, top_k=5):
        if not isinstance(question, str) or not question.strip():
            return {
                "success": False,
                "message": "يرجى إدخال سؤال واضح.",
                "results": []
            }

        results = self.search_engine.search(question, top_k=top_k)

        if not results:
            return {
                "success": False,
                "message": "لم أعثر على معلومات مطابقة في قاعدة المعرفة.",
                "results": []
            }

        return {
            "success": True,
            "message": "تم العثور على معلومات. راجع حالة التوثيق والمصادر.",
            "results": results
        }
