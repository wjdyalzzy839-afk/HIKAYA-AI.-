class AnswerEvaluator:
    def evaluate(self, answer):
        if not isinstance(answer, dict):
            return {
                "valid": False,
                "score": 0,
                "issues": ["صيغة الإجابة غير صحيحة"]
            }

        results = answer.get("results", [])
        issues = []

        if not answer.get("success"):
            issues.append("لم يتم العثور على معلومات")

        if not results:
            issues.append("لا توجد نتائج")

        for item in results:
            if not item.get("fact"):
                issues.append("توجد معلومة فارغة")

            if not item.get("source_url"):
                issues.append("توجد معلومة بلا مصدر")

            if item.get("verified") is not True:
                issues.append("توجد معلومة غير موثقة")

        score = 100 if not issues else max(0, 100 - len(issues) * 20)

        return {
            "valid": len(issues) == 0,
            "score": score,
            "issues": issues
        }
