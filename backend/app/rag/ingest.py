import os
from pypdf import PdfReader
from app.rag.chromadb_client import chroma_manager
from app.rag.embedder import embedder

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - overlap)
    return chunks

def build_and_seed_vector_database():
    print("--- STARTING KNOWLEDGE BASE INGESTION ---")
    
    # Tracked PDF items mapped exactly to your uploaded filenames
    pdf_sources = [
        {"file": "APPNA BANK AI KNOWLEDGE BASE.pdf", "collection": "banking_knowledge"},
        {"file": "Module 1_Introduction to Stock Markets.pdf", "collection": "stock_market_english"},
        {"file": "Module1_Hindi.pdf", "collection": "stock_market_hindi"},
        {"file": "No.docx pdf question for ai rag agent ok.pdf", "collection": "stock_market_bengali"},
        {"file": "Top 30 Questions for Appna Bank AI.pdf", "collection": "question_bank_reference"}
    ]

    base_pdf_dir = "./pdfs"

    for source in pdf_sources:
        path = os.path.join(base_pdf_dir, source["file"])
        coll = chroma_manager.get_or_create_collection(source["collection"])
        
        # Bug Fixed: Explicitly abort if the file doesn't exist. No more fake mock data insertion!
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Required PDF not found: '{path}'. Please upload it before running ingestion."
            )
            
        print(f"Reading file: {source['file']}...")
        reader = PdfReader(path)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
        
        chunks = chunk_text(full_text)
        if not chunks:
            print(f"Skipping empty document: {source['file']}")
            continue

        embeddings = embedder.embed_documents(chunks)
        ids = [f"{source['file'].replace(' ', '_')}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": source["file"]} for _ in chunks]

        coll.upsert(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
        print(f"Stored {len(chunks)} fragments into [{source['collection']}] collection.")

if __name__ == "__main__":
    build_and_seed_vector_database()
