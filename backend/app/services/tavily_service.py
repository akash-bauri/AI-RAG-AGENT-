import requests
from app.core.config import settings

class TavilySearchService:
    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY
        self.url = "https://api.tavily.com/search"

    def search(self, query: str) -> str:
        """
        Fetches live data from the web when local PDFs do not contain the answer.
        """
        try:
            payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": "basic",
                "include_answer": True
            }
            response = requests.post(self.url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("answer", "No instant lookup details summarized.")
            return "Could not connect to external search indexes."
        except Exception as e:
            return f"Web crawling error: {str(e)}"

tavily_service = TavilySearchService()
