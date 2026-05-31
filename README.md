# Project Intelligence Assistant

An AI-powered **multi-agent RAG system** designed to ingest project documents (PDFs, spreadsheets) and answer complex questions about project status, risks, and budgets.

## Features

- **Multi-Agent Architecture (LangGraph)**: Routes queries to specialized agents (Document Q&A vs Data Analysis).
- **Hybrid RAG**: Combines dense vector embeddings with sparse BM25 keyword scoring fused via Reciprocal Rank Fusion (RRF).
- **Dual LLM Support**: Works with both **Google Gemini** (cloud) and **local Ollama models** (fully offline). Switch with a single `.env` variable.
- **Dual Data Pipeline**: Parses PDFs for qualitative Q&A and loads CSVs/Excel into Pandas DataFrames for quantitative budget analysis.
- **Source Citations**: Grounded answers always cite the source document and page number.
- **File Logging**: Backend logs to `logs/backend/app.log` and frontend events to `logs/frontend/client.log`.
- **Premium UI**: Modern React frontend with glassmorphism design.

## Prerequisites

- **Python** 3.11+
- **Node.js** v18+
- **Ollama** (if using local models) — or a Google Gemini API Key

> **No Docker required.** Qdrant runs using local file-based storage automatically.

## Quick Start

### 1. Configure Environment

Create a `.env` file in the **project root** (`gamuda/.env`). Copy the appropriate section:

**Option A — Local Ollama models (recommended for privacy):**
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3
OLLAMA_EMBED_MODEL=nomic-embed-text:latest
```

**Option B — Google Gemini (faster, cloud-based):**
```env
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open your browser to **http://localhost:3000**.

## Usage

1. Drag and drop your project documents (PDF, CSV, XLSX) into the upload panel.
2. Wait for the files to show as `INDEXED`.
3. Ask questions. Examples:
   - *"What is the status of Project Alpha?"* → Document Q&A Agent
   - *"Which project is over budget?"* → Data Analysis Agent
   - *"What are the major risks?"* → Document Q&A Agent
   - *"What is the total budget across all projects?"* → Data Analysis Agent

## Logs

After the backend starts, logs are written to:
- `backend/logs/backend/app.log` — all API and agent activity
- `backend/logs/frontend/client.log` — frontend events proxied to the backend

## Evaluation

Run the RAGAS evaluation script (8 test queries across 4 difficulty levels):

```bash
cd backend
python evaluate.py
```

## Docker Deployment (Optional)

For a fully containerised deployment:

```bash
# Copy and edit .env first
docker-compose up -d
```

The frontend will be available on port **80**, backend on **8000**.
