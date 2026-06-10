import chromadb
from app.core.config import settings
from app.rag.embedder import embedder


class ChromaDBManager:
    def __init__(self):
        try:
            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_DB_DIR
            )

            print(
                f"✅ ChromaDB Connected: {settings.CHROMA_DB_DIR}"
            )

        except Exception as e:
            print(f"❌ ChromaDB Initialization Error: {str(e)}")
            raise

    def get_or_create_collection(self, name: str):
        try:
            return self.client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )

        except Exception as e:
            print(
                f"❌ Collection Creation Error [{name}]: {str(e)}"
            )
            raise

    def query_collection(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = 3
    ):
        try:
            collection = self.get_or_create_collection(
                collection_name
            )

            query_vector = embedder.embed_query(
                query_text
            )

            results = collection.query(
                query_embeddings=[query_vector],
                n_results=n_results
            )

            return results

        except Exception as e:
            print(
                f"❌ Query Error [{collection_name}]: {str(e)}"
            )
            raise


chroma_manager = ChromaDBManager()
