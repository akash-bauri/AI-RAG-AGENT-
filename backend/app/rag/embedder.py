import google.generativeai as genai
from app.core.config import settings
from typing import List

class GeminiEmbedder:
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model_name = "models/text-embedding-004"

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        response = genai.embed_content(
            model=self.model_name,
            content=texts,
            task_type="retrieval_document"
        )
        return response['embedding']

    def embed_query(self, text: str) -> List[float]:
        response = genai.embed_content(
            model=self.model_name,
            content=text,
            task_type="retrieval_query"
        )
        return response['embedding']

embedder = GeminiEmbedder()
