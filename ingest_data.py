"""
Ingestion script for the lightweight Revomate RAG engine.
"""

import os
from rag_engine import RevomateRAG

def main():
    """Ingest training data into JSON knowledge base."""
    # Initialize RAG engine
    rag = RevomateRAG()
    
    # Get paths from env
    data_path = os.getenv("DATA_PATH", "./data/revomate_rag_expanded.txt")
    
    if not os.path.exists(data_path):
        # Try finding it relative to this file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "data", "revomate_rag_expanded.txt")

    if not os.path.exists(data_path):
        print(f"❌ Error: Data file not found at {data_path}")
        return

    # Run ingestion
    rag.ingest_data(data_path)
    print("✅ Ingestion complete.")

if __name__ == "__main__":
    main()
