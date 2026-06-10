from typing import List

_model = None


def get_model():
    global _model

    if _model is None:
        from sentence_transformers import SentenceTransformer

        print("Loading embedding model...")

        _model = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )

        print("Embedding model loaded successfully")

    return _model


class MultilingualEmbedder:

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        try:
            model = get_model()

            embeddings = model.encode(
                texts,
                batch_size=16,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False
            )

            return embeddings.tolist()

        except Exception as e:
            print(f"Document Embedding Error: {e}")
            raise

    def embed_query(self, text: str) -> List[float]:
        try:
            model = get_model()

            embedding = model.encode(
                text,
                normalize_embeddings=True,
                convert_to_numpy=True
            )

            return embedding.tolist()

        except Exception as e:
            print(f"Query Embedding Error: {e}")
            raise


embedder = MultilingualEmbedder()
