# Zymnix AI Consultant Backend

Professional RAG-based chatbot backend for Zymnix business consulting.

## Features

- 🧠 **RAG Architecture**: Retrieval Augmented Generation for accurate, context-aware responses
- ⚡ **Groq API**: Ultra-fast inference with Llama 3.1 70B
- 💾 **ChromaDB**: Local vector database for semantic search
- 🎯 **Industry-Specific**: Trained on Dental, Legal, and Real Estate solutions
- 🔒 **Professional Persona**: Acts as strategic business consultant

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your Groq API key:

```bash
cp .env.example .env
# Edit .env with your API key
```

### 3. Ingest Training Data

Load the Zymnix knowledge base into the vector database:

```bash
python ingest_data.py
```

This will:
- Read `zymnix_rag_expanded.txt`
- Split into semantic chunks
- Generate embeddings using Sentence Transformers
- Store in ChromaDB for fast retrieval

### 4. Start the API Server

```bash
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
```bash
GET /api/health
```

### Chat
```bash
POST /api/chat
Content-Type: application/json

{
  "message": "How can Zymnix help my dental practice?",
  "chat_history": []
}
```

### Greeting
```bash
GET /api/greeting
```

## Tech Stack

- **FastAPI**: Modern Python web framework
- **ChromaDB**: Vector database for embeddings
- **Sentence Transformers**: Local embedding generation (all-MiniLM-L6-v2)
- **Groq**: Ultra-fast LLM inference (Llama 3.1 70B)
- **LangChain**: RAG orchestration

## Project Structure

```
backend/
├── app.py              # FastAPI application
├── rag_engine.py       # RAG implementation
├── prompts.py          # System prompts and persona
├── ingest_data.py      # Data ingestion script
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (gitignored)
├── .env.example        # Environment template
└── chroma_db/          # Vector database (gitignored)
```

## Development

### Testing the API

```bash
# Health check
curl http://localhost:8000/api/health

# Chat request
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What services does Zymnix offer?"}'
```
## 🧪 Verification & Results

### Visual Verification
The `ChatWidget` is now live across the entire site. I have verified the implementation end-to-end locally.

````carousel
![Zymnix AI Consultant Local Verification](/home/abdur/.gemini/antigravity/brain/498cf287-93d2-4c54-8267-70b61247b168/chatbot_local_verification_1770999616155.png)
<!-- slide -->
![Chatbot Interaction Sequence](/home/abdur/.gemini/antigravity/brain/498cf287-93d2-4c54-8267-70b61247b168/chatbot_ui_screenshot_1770999506404.webp)
````

### Backend Verification
I verified the API response using a curl test:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How can Zymnix help my dental practice?"}'
```
**Result**: The AI correctly identified as a professional consultant, cited specialized knowledge chunks, and provided industry-specific ROI metrics.

> [!TIP]
> **Try asking the bot:**
```
## Next Steps

- Integrate with Next.js frontend
- Add conversation persistence
- Implement rate limiting
- Add analytics tracking
