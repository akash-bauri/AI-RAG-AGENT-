import google.generativeai as genai

from app.core.config import settings


class GeminiGenerationService:

    def __init__(self):

        genai.configure(
            api_key=settings.GOOGLE_API_KEY
        )

        self.model = genai.GenerativeModel(
            "gemini-1.5-flash"
        )

        print("✅ Gemini Initialized")

    def generate_response(
        self,
        question: str,
        context: str,
        language: str,
        personalization: str = ""
    ) -> str:

        prompt = f"""
Answer in {language}

Context:
{context}

Profile:
{personalization}

Question:
{question}
"""

        try:

            response = self.model.generate_content(
                prompt
            )

            if response.text:
                return response.text

            return "No response generated."

        except Exception as e:

            print(f"GEMINI ERROR: {e}")

            return f"Gemini Error: {str(e)}"


gemini_service = GeminiGenerationService()
