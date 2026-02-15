"""
Lightweight RAG Engine for Revomate AI Consultant.
Uses JSON storage and Cosine Similarity to stay within Vercel's 250MB limit.
"""

import os
import json
import numpy as np
from typing import List, Dict, Any
from dotenv import load_dotenv
from groq import Groq

try:
    from .prompts import SYSTEM_PROMPT, format_prompt, GREETING_MESSAGE
except (ImportError, ValueError):
    from prompts import SYSTEM_PROMPT, format_prompt, GREETING_MESSAGE

load_dotenv()

class RevomateRAG:
    """Lightweight RAG system for Revomate AI Consultant."""
    
    def __init__(self):
        """Initialize RAG components."""
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.model_name = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")
        self.kb_path = os.getenv("KNOWLEDGE_BASE_PATH", "./data/knowledge_base.json")
        
        # Absolute path for reliability
        if not os.path.isabs(self.kb_path):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.kb_path = os.path.normpath(os.path.join(base_dir, self.kb_path))
            
        self.groq_client = Groq(api_key=self.groq_api_key)
        self.knowledge_base = self._load_kb()
        
        print(f"✅ Lightweight RAG Engine initialized. KB size: {len(self.knowledge_base)} chunks.")

    def _load_kb(self) -> List[Dict]:
        """Load knowledge base from JSON."""
        if os.path.exists(self.kb_path):
            with open(self.kb_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_kb(self):
        """Save knowledge base to JSON."""
        os.makedirs(os.path.dirname(self.kb_path), exist_ok=True)
        with open(self.kb_path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, indent=2)

    def _get_embedding(self, text: str) -> List[float]:
        """Deterministic hash-based embedding (384-dim)."""
        import hashlib
        import struct
        
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        embedding = []
        for i in range(0, 384):
            idx = i % len(hash_bytes)
            # Match the original hash logic for consistency
            val = struct.unpack('f', struct.pack('I', hash_bytes[idx] * (i + 1) % 256))[0]
            embedding.append(val)
        
        # Normalize
        norm = np.linalg.norm(embedding)
        return (np.array(embedding) / (norm + 1e-9)).tolist()

    def ingest_data(self, file_path: str):
        """Ingest text data and save to JSON knowledge base."""
        print(f"Ingesting data from {file_path}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        chunks = []
        chunk_parts = content.split('### 🧩 CHUNK')
        
        for i, part in enumerate(chunk_parts[1:], 1):
            lines = part.strip().split('\n', 1)
            if len(lines) >= 2:
                header = lines[0].strip()
                text = lines[1].strip().replace('---', '').strip()
                full_text = f"{header}\n{text}"
                
                chunks.append({
                    "id": f"chunk_{i:02d}",
                    "header": header,
                    "content": text,
                    "embedding": self._get_embedding(full_text)
                })
        
        self.knowledge_base = chunks
        self._save_kb()
        print(f"✅ Successfully ingested {len(chunks)} chunks.")

    def retrieve_context(self, query: str, top_k: int = 3) -> str:
        """Find most similar chunks using dot product (normalized vectors)."""
        if not self.knowledge_base:
            return ""
            
        query_vec = np.array(self._get_embedding(query))
        
        # Calculate scores (dot product is same as cosine sim for normalized vectors)
        scores = []
        for chunk in self.knowledge_base:
            score = np.dot(query_vec, np.array(chunk['embedding']))
            scores.append((score, chunk))
            
        # Sort by score descending
        scores.sort(key=lambda x: x[0], reverse=True)
        
        # Format results
        results = []
        for i, (score, chunk) in enumerate(scores[:top_k], 1):
            results.append(f"[Context {i}] {chunk['header']}\n{chunk['content']}\n")
            
        return "\n".join(results)

    def generate_response(self, query: str, chat_history: List[Dict] = None) -> Dict:
        """Generate AI response using RAG."""
        context = self.retrieve_context(query)
        prompt = format_prompt(context, query, chat_history)
        
        chat_completion = self.groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model_name,
            temperature=0.7,
            max_tokens=1024,
        )
        
        return {
            "response": chat_completion.choices[0].message.content,
            "context_used": context,
            "model": self.model_name
        }

    def get_greeting(self) -> str:
        return GREETING_MESSAGE

# Singleton
_instance = None
def get_rag_engine():
    global _instance
    if _instance is None:
        _instance = RevomateRAG()
    return _instance
