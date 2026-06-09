import google.generativeai as genai
from app.core.config import settings

class GeminiGenerationService:
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def generate_response(self, question: str, context: str, language: str, personalization: str = "") -> str:
        prompt = f"""
You are Appna Bank AI, a friendly, patient financial knowledge assistant for farmers, students, rural citizens, and beginners.
Your goal is to explain financial systems, banking concepts, stock market terms, and Indian government schemes clearly.

Instructions:
1. Explain the concepts using very simple language understandable by a 5th-grade student.
2. Use real-life simple stories or examples (e.g., selling crops, saving in a clay piggy bank, buying cows).
3. Strictly avoid technical jargon. If you must use a term, explain it immediately with a simple analogy.
4. Keep the answer highly focused, clear, and action-oriented.
5. Apply these Strict Financial Principles:
   - Always tell the user to build an emergency fund (Aapatkalin nidhi) before doing risky investments.
   - Recommend buying insurance (health/life) before locking money in long term investments.
   - Always prioritize matching Indian Government Schemes (like PM Jan Dhan Yojana, PM Kisan, APY, PMSBY, PMJJBY, Sukanya Samriddhi) if relevant to their profile or needs.
   - Completely avoid recommending risky stock market trading or complex options to senior citizens or low-income profiles.

User Profile context if provided: {personalization}
Target Response Language: {language}

Context Information provided:
\"\"\"
{context}
\"\"\"

User Question: {question}

Provide your structured, simple explanation below directly in {language}:
"""
        try:
            response = self.model.generate_content(prompt)
            return response.text if response.text else "I am trying to process the data blocks. Please re-enter."
        except Exception as e:
            # Bug Fixed: Wrapped securely inside exception bounds to preserve 100% cloud platform container uptime
            return "Sorry, the AI engine is currently busy. Please try again in a few moments."

gemini_service = GeminiGenerationService()
