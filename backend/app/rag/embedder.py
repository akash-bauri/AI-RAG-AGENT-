import google.generativeai as genai
from app.core.config import settings
from typing import List


class GeminiEmbedder:
    def __init__(self):
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is missing")

        genai.configure(api_key=settings.GOOGLE_API_KEY)

        self.model_name = "models/text-embedding-004"

        print("✅ Gemini Embedder Initialized")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        try:
            embeddings = []

            for text in texts:
                response = genai.embed_content(
                    model=self.model_name,
                    content=text,
                    task_type="retrieval_document"
                )

                embeddings.append(response["embedding"])

            return embeddings

        except Exception as e:
            print(f"❌ Document Embedding Error: {str(e)}")
            raise

    def embed_query(self, text: str) -> List[float]:
        try:
            response = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type="retrieval_query"
            )

            return response["embedding"]

        except Exception as e:
            print(f"❌ Query Embedding Error: {str(e)}")
            raise


embedder = GeminiEmbedder()
