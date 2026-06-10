import os
from pypdf import PdfReader
from app.rag.chromadb_client import chroma_manager
from app.rag.embedder import embedder


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    chunks = []
    if not text or not text.strip():
        return chunks
        
    # Safeguard against short text causing infinite loops
    if len(text) <= chunk_size:
        return [text.strip()]

    start = 0
    step = chunk_size - overlap
    
    # Absolute safety constraint
    if step <= 0:
        step = chunk_size

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += step

    return chunks


def build_and_seed_vector_database():
    print("\n===== STARTING KNOWLEDGE BASE INGESTION =====\n")

    pdf_sources = [
        {
            "file": "APPNA BANK AI KNOWLEDGE BASE.pdf",
            "collection": "banking_knowledge"
        },
        {
            "file": "Module 1_Introduction to Stock Markets.pdf",
            "collection": "stock_market_english"
        },
        {
            "file": "Module1_Hindi.pdf",
            "collection": "stock_market_hindi"
        },
        {
            "file": "No.docx pdf question for ai rag agent ok.pdf",
            "collection": "stock_market_bengali"
        },
        {
            "file": "Top 30 Questions for Appna Bank AI.pdf",
            "collection": "question_bank_reference"
        }
    ]

    # Explicit relative layout matching your repository target folder
    base_pdf_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../pdfs")
    )

    print(f"Target Absolute PDF Directory Path: {base_pdf_dir}")

    for source in pdf_sources:
        file_path = os.path.join(base_pdf_dir, source["file"])
        print(f"\nProcessing target document: {source['file']}")

        # Validate file existence before parsing
        if not os.path.exists(file_path):
            print(f"ERROR: Missing PDF file asset -> {file_path}")
            continue

        try:
            reader = PdfReader(file_path)
        except Exception as e:
            print(f"ERROR reading PDF {source['file']}: {str(e)}")
            continue

        full_text = ""

        # Extract text page-by-page safely
        try:
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
        except Exception as e:
            print(f"ERROR extracting text from {source['file']}: {str(e)}")
            continue

        if not full_text.strip():
            print(f"WARNING: No readable text found inside {source['file']}")
            continue

        chunks = chunk_text(full_text)

        if not chunks:
            print(f"WARNING: Zero vector chunks split out of {source['file']}")
            continue

        print(f"Generated {len(chunks)} structural context blocks.")

        # Mount target partition collection
        collection = chroma_manager.get_or_create_collection(
            source["collection"]
        )

        # Generate embeddings matrix via Gemini
        try:
            embeddings = embedder.embed_documents(chunks)
        except Exception as e:
            print(f"Embedding Generation Error: {str(e)}")
            continue

        # Clean IDs removing formatting dots or spaces 
        safe_file_name = source['file'].replace(' ', '_').replace('.', '_')
        ids = [
            f"{safe_file_name}_chunk_{i}"
            for i in range(len(chunks))
        ]

        metadatas = [
            {
                "source": source["file"],
                "collection": source["collection"],
                "chunk_index": i
            }
            for i in range(len(chunks))
        ]

        # Purge old identifiers to prevent duplicate leaks
        try:
            collection.delete(ids=ids)
        except Exception:
            pass

        # Insert fresh vector updates
        try:
            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas
            )
            print(f"SUCCESS: Tokenized and stored {len(chunks)} chunks into '{source['collection']}'.")
        except Exception as e:
            print(f"ChromaDB Persistent Engine Ingestion Fault: {str(e)}")

    print("\n===== INGESTION COMPLETED NATIVELY =====\n")


if __name__ == "__main__":
    build_and_seed_vector_database()
