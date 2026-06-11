from google import genai
from app.core.config import settings


class GeminiGenerationService:

    def __init__(self):

        self.client = genai.Client(
            api_key=settings.GOOGLE_API_KEY
        )

        print("✅ Gemini Client Initialized")

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

            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )

            if hasattr(response, "text"):
                return response.text

            return str(response)

        except Exception as e:

            print(f"❌ GEMINI ERROR: {e}")

            return (
                "Sorry, I am unable to generate a response right now."
            )


gemini_service = GeminiGenerationService()
