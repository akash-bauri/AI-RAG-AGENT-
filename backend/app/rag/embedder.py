from sentence_transformers import SentenceTransformer
from typing import List


class MultilingualEmbedder:
    def __init__(self):
        self.model = SentenceTransformer(
            "paraphrase-multilingual-MiniLM-L12-v2"
        )

        print("✅ Lightweight Multilingual Embedder Initialized")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True
        )

        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
            convert_to_numpy=True
        )

        return embedding.tolist()


embedder = MultilingualEmbedder()
