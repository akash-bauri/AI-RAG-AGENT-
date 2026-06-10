from sentence_transformers import SentenceTransformer
from typing import List


class MultilingualEmbedder:
    def __init__(self):
        """
        Multilingual embedding model supporting:
        - English
        - Hindi
        - Bengali
        """

        self.model = SentenceTransformer(
            "intfloat/multilingual-e5-base"
        )

        print("✅ Multilingual E5 Embedder Initialized")

    def embed_documents(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        """
        Generate embeddings for document chunks.
        """

        try:
            embeddings = self.model.encode(
                texts,
                normalize_embeddings=True,
                convert_to_numpy=True
            )

            return embeddings.tolist()

        except Exception as e:
            print(
                f"❌ Document Embedding Error: {str(e)}"
            )
            raise

    def embed_query(
        self,
        text: str
    ) -> List[float]:
        """
        Generate embedding for user query.
        """

        try:
            embedding = self.model.encode(
                text,
                normalize_embeddings=True,
                convert_to_numpy=True
            )

            return embedding.tolist()

        except Exception as e:
            print(
                f"❌ Query Embedding Error: {str(e)}"
            )
            raise


# Singleton Instance
embedder = MultilingualEmbedder()
