from langdetect import detect
from app.services.gemini_service import gemini_service
from typing import Dict, Any


class HybridRAGPipeline:

    def detect_language(self, text: str) -> str:
        try:
            lang = detect(text)

            if lang in ["hi", "bn"]:
                return lang

            return "en"

        except Exception:
            return "en"

    def process_query(
        self,
        question: str,
        profile_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:

        detected_lang = self.detect_language(question)

        lang_mapping = {
            "en": "English",
            "hi": "Hindi",
            "bn": "Bengali"
        }

        target_lang_name = lang_mapping.get(
            detected_lang,
            "English"
        )

        personalization = ""

        if profile_data:
            personalization = (
                f"Age: {profile_data.get('age')}, "
                f"Income: ₹{profile_data.get('monthly_income')}, "
                f"Goal: {profile_data.get('goal')}"
            )

        answer = gemini_service.generate_response(
            question=question,
            context="Financial education assistant for banking, savings, SIP, FD, RD, insurance, government schemes and stock market basics.",
            language=target_lang_name,
            personalization=personalization
        )

        return {
            "answer": answer,
            "source_type": "gemini",
            "source_name": "Gemini 2.5 Flash",
            "detected_language": detected_lang
        }


rag_pipeline = HybridRAGPipeline()
