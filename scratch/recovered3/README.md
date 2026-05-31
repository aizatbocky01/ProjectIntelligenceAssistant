# Project Intelligence Assistant (Gamuda Assessment)

An AI-powered multi-agent RAG system designed to ingest project documents (PDFs, spreadsheets) and answer complex questions about project status, risks, and budgets.

## Features

- **Multi-Agent Architecture (LangGraph)**: Routes queries to specialized agents (Document Q&A vs Data Analysis).
- **Hybrid RAG**: Uses both dense vector embeddings (Gemini) and sparse keyword scoring (BM25) with Reciprocal Rank Fusion (RRF) for accurate retrieval.
- **Dual Data Pipeline**: Parses PDFs for qualitative Q&A and loads CSVs/Excel into memory for quantitative budget analysis.
- **Source Citations**: Grounded answers always provide the source document and page number.
- **Premium UI**: Modern React frontend with glassmorphism design.

## Prerequisites

- Node.js (v18+)
- Python (3.11+)
- Qdrant Vector DB (can run locally via Docker)
- Google Gemini API Key

## Setup Instructions

### 1. Start Qdrant (Vector Database)

You can run Qdrant quickly using Docker:

```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
```
(Alternatively, download the Qdrant binary for Windows/Mac).

### 2. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Set your environment variables (or create a `.env` file in `backend/app/core/`):
   ```bash
   export GOOGLE_API_KEY="your_gemini_api_key_here"
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### 3. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Open your browser to `http://localhost:3000`.

## Testing the System

1. The frontend application will load.
2. Drag and dr
<truncated 966 bytes>