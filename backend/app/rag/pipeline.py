from langdetect import detect
from app.rag.chromadb_client import chroma_manager
from app.services.tavily_service import tavily_service
from app.services.gemini_service import gemini_service
from typing import Dict, Any

class HybridRAGPipeline:
    def __init__(self):
        self.collections = [
            "banking_knowledge", 
            "stock_market_english", 
            "stock_market_hindi", 
            "stock_market_bengali", 
            "question_bank_reference"
        ]
        # Bug Fixed: Increased to 0.65 threshold to stop poor quality lookups from polluting context blocks!
        self.RAG_THRESHOLD = 0.65

    def detect_language(self, text: str) -> str:
        try:
            lang = detect(text)
            return lang if lang in ['hi', 'bn'] else 'en'
        except Exception:
            return 'en'

    def process_query(self, question: str, profile_data: Dict[str, Any] = None) -> Dict[str, Any]:
        detected_lang = self.detect_language(question)
        lang_mapping = {"en": "English", "hi": "Hindi", "bn": "Bengali"}
        target_lang_name = lang_mapping.get(detected_lang, "English")

        best_context = ""
        best_source_name = "None"
        best_source_type = "fallback"
        highest_confidence = -1.0 

        for col_name in self.collections:
            res = chroma_manager.query_collection(col_name, question, n_results=2)
            if res and res['documents'] and res['documents'][0]:
                distance = res['distances'][0][0] if 'distances' in res and res['distances'] else 1.0
                similarity = 1.0 - distance

                if similarity > highest_confidence:
                    highest_confidence = similarity
                    best_context = "\n".join(res['documents'][0])
                    if res['metadatas'] and res['metadatas'][0] and 'source' in res['metadatas'][0][0]:
                        best_source_name = res['metadatas'][0][0]['source']
                    else:
                        best_source_name = col_name
                    best_source_type = "pdf"

        # If context match is below 0.65 accuracy, switch to live web crawling automatically
        if highest_confidence < self.RAG_THRESHOLD:
            best_context = tavily_service.search(question)
            best_source_type = "tavily"
            best_source_name = "Tavily Live Search Web Index"

        personalization = ""
        if profile_data:
            personalization = f"Age: {profile_data.get('age')}, Income: ₹{profile_data.get('monthly_income')}, Goal: {profile_data.get('goal')}"

        answer = gemini_service.generate_response(
            question=question, 
            context=best_context, 
            language=target_lang_name, 
            personalization=personalization
        )

        return {
            "answer": answer,
            "source_type": best_source_type,
            "source_name": best_source_name,
            "detected_language": detected_lang
        }

rag_pipeline = HybridRAGPipeline()
