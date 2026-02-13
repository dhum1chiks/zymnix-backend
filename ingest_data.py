"""
Data ingestion script for Zymnix RAG system.
Run this once to populate the vector database.
"""

import os
try:
    from .rag_engine import ZymnixRAG
except (ImportError, ValueError):
    from rag_engine import ZymnixRAG

def main():
    """Ingest training data into vector database."""
    # Get data path from environment
    data_path = os.getenv("DATA_PATH", "./data/zymnix_rag_expanded.txt")
    
    # Resolve relative path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, data_path)
    full_path = os.path.normpath(full_path)
    
    if not os.path.exists(full_path):
        print(f"❌ Error: Data file not found at {full_path}")
        print("Please update DATA_PATH in .env or place zymnix_rag_expanded.txt in the correct location.")
        return
    
    print("=" * 60)
    print("ZYMNIX RAG DATA INGESTION")
    print("=" * 60)
    print(f"Data source: {full_path}\n")
    
    # Initialize RAG engine
    rag = ZymnixRAG()
    
    # Ingest data
    rag.ingest_data(full_path)
    
    print("\n" + "=" * 60)
    print("✅ DATA INGESTION COMPLETE")
    print("=" * 60)
    print(f"Total documents in database: {rag.collection.count()}")
    print("\nYou can now start the API server with: uvicorn app:app --reload")


if __name__ == "__main__":
    main()
