"""
RAG Engine for Zymnix AI Consultant chatbot.
Handles document ingestion, embedding, retrieval, and response generation.
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from groq import Groq
try:
    from .prompts import SYSTEM_PROMPT, format_prompt, GREETING_MESSAGE
except (ImportError, ValueError):
    from prompts import SYSTEM_PROMPT, format_prompt, GREETING_MESSAGE

load_dotenv()


class ZymnixRAG:
    """RAG system for Zymnix AI Consultant."""
    
    def __init__(self):
        """Initialize RAG components."""
        # Environment config
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.model_name = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")
        self.vector_db_path = os.getenv("VECTOR_DB_PATH", "./chroma_db")
        
        # Groq client
        self.groq_client = Groq(api_key=self.groq_api_key)
        
        # Robust absolute path for serverless/read-only compatibility
        if not os.path.isabs(self.vector_db_path):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.vector_db_path = os.path.normpath(os.path.join(base_dir, self.vector_db_path))
            
        print(f"Initializing vector database at {self.vector_db_path}...")
        self.chroma_client = chromadb.PersistentClient(path=self.vector_db_path)
        
        # Get or create collection (using Groq for embeddings)
        self.collection = self.chroma_client.get_or_create_collection(
            name="zymnix_knowledge",
            metadata={"description": "Zymnix business knowledge base"}
        )
        
        print(f"✅ RAG Engine initialized. Collection has {self.collection.count()} documents.")
    
    def _get_embedding(self, text: str) -> List[float]:
        """
        Get embedding using simple hash-based approach for demo.
        For production, use proper embedding model.
        """
        # Simple hash-based embedding for demo purposes
        # In production, use OpenAI embeddings or sentence-transformers
        import hashlib
        import struct
        
        # Create a deterministic embedding from text
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to 384-dimensional vector
        embedding = []
        for i in range(0, 384):
            idx = i % len(hash_bytes)
            embedding.append(struct.unpack('f', struct.pack('I', hash_bytes[idx] * (i + 1) % 256))[0])
        
        # Normalize
        norm = sum(x**2 for x in embedding) ** 0.5
        embedding = [x / (norm + 1e-9) for x in embedding]
        
        return embedding
    
    def ingest_data(self, file_path: str):
        """
        Ingest and chunk data from the training file.
        
        Args:
            file_path: Path to the zymnix_rag_expanded.txt file
        """
        print(f"Reading data from {file_path}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by chunk markers
        chunks = []
        chunk_parts = content.split('### 🧩 CHUNK')
        
        for i, part in enumerate(chunk_parts[1:], 1):  # Skip intro text
            # Extract chunk number and content
            lines = part.strip().split('\n', 1)
            if len(lines) >= 2:
                chunk_header = lines[0].strip()
                chunk_content = lines[1].strip()
                
                # Clean up chunk content
                chunk_content = chunk_content.replace('---', '').strip()
                
                chunk = {
                    'id': f'chunk_{i:02d}',
                    'header': chunk_header,
                    'content': chunk_content,
                    'metadata': {'chunk_number': i}
                }
                chunks.append(chunk)
        
        print(f"Found {len(chunks)} chunks. Generating embeddings...")
        
        # Generate embeddings
        texts = [f"{chunk['header']}\n{chunk['content']}" for chunk in chunks]
        embeddings = [self._get_embedding(text) for text in texts]
        
        # Store in ChromaDB
        self.collection.add(
            ids=[chunk['id'] for chunk in chunks],
            embeddings=embeddings,
            documents=texts,
            metadatas=[{'chunk_number': chunk['metadata']['chunk_number'], 
                       'header': chunk['header']} for chunk in chunks]
        )
        
        print(f"✅ Ingested {len(chunks)} chunks into vector database.")
    
    def retrieve_context(self, query: str, top_k: int = 3) -> str:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: User query
            top_k: Number of chunks to retrieve
        
        Returns:
            Formatted context string
        """
        # Generate query embedding
        query_embedding = self._get_embedding(query)
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.collection.count())
        )
        
        # Format context
        context_parts = []
        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
            context_parts.append(f"[Context {i}] {metadata['header']}\n{doc}\n")
        
        return "\n".join(context_parts)
    
    def generate_response(
        self, 
        query: str, 
        chat_history: List[Dict[str, str]] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate a response using RAG.
        
        Args:
            query: User query
            chat_history: Previous conversation messages
            temperature: LLM temperature
        
        Returns:
            Dict with response and metadata
        """
        # Retrieve relevant context
        context = self.retrieve_context(query)
        
        # Format prompt with context and history
        prompt = format_prompt(context, query, chat_history)
        
        # Generate response with Groq
        chat_completion = self.groq_client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model=self.model_name,
            temperature=temperature,
            max_tokens=1024,
        )
        
        response_text = chat_completion.choices[0].message.content
        
        return {
            "response": response_text,
            "context_used": context,
            "model": self.model_name,
            "tokens": {
                "prompt": chat_completion.usage.prompt_tokens,
                "completion": chat_completion.usage.completion_tokens,
                "total": chat_completion.usage.total_tokens
            }
        }
    
    def get_greeting(self) -> str:
        """Get the greeting message."""
        return GREETING_MESSAGE


# Singleton instance
_rag_instance = None

def get_rag_engine() -> ZymnixRAG:
    """Get or create RAG engine singleton."""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = ZymnixRAG()
    return _rag_instance
