import google.generativeai as genai
from app.core.config import settings


class GeminiGenerationService:
    def __init__(self):
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is missing")

        genai.configure(api_key=settings.GOOGLE_API_KEY)

        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash"
        )

        print("✅ Gemini Service Initialized")

    def generate_response(
        self,
        question: str,
        context: str,
        language: str,
        personalization: str = ""
    ) -> str:

        prompt = f"""
You are Appna Bank AI, a friendly financial assistant.

Respond in {language}.

User Profile:
{personalization}

Context:
{context}

Question:
{question}

Rules:
1. Use simple language.
2. Explain like a 5th-grade student.
3. Use practical examples.
4. Keep answers short and useful.
5. Suggest emergency savings before risky investments.
6. Prefer government schemes when relevant.
"""

        try:
            response = self.model.generate_content(prompt)

            if hasattr(response, "text") and response.text:
                return response.text

            return "No response generated."

        except Exception as e:
            print(f"GEMINI ERROR: {str(e)}")
            return f"Gemini Error: {str(e)}"


gemini_service = GeminiGenerationService()
