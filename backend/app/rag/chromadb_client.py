import chromadb
from app.core.config import settings
from app.rag.embedder import embedder

class ChromaDBManager:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)
        
    def get_or_create_collection(self, name: str):
        return self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"}
        )

    def query_collection(self, collection_name: str, query_text: str, n_results: int = 2):
        collection = self.get_or_create_collection(collection_name)
        query_vector = embedder.embed_query(query_text)
        
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=n_results
        )
        return results

chroma_manager = ChromaDBManager()
