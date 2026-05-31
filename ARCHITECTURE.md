# Architecture

## System Overview

The **Project Intelligence Assistant** is a multi-agent RAG system built with **LangChain/LangGraph** (Python) and **React** (JavaScript). It ingests project documents (PDFs, CSVs) and answers complex questions about project status, risks, and budgets using specialized AI agents.

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                       │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  Upload UI  │  │   Chat UI    │  │  Source Cite   │  │
│  └──────┬──────┘  └──────┬───────┘  └───────────────┘  │
└─────────┼────────────────┼──────────────────────────────┘
          │                │
          ▼                ▼
┌─────────────────────────────────────────────────────────┐
│               FastAPI Backend (Python)                  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │            LangGraph Orchestrator                │   │
│  │                                                  │   │
│  │  ┌──────────┐     ┌──────────────┐               │   │
│  │  │  Router  │────►│ Document Q&A │──► Hybrid RAG │   │
│  │  │  Agent   │     │    Agent     │               │   │
│  │  │          │     └──────────────┘               │   │
│  │  │          │     ┌──────────────┐               │   │
│  │  │          │────►│Data Analysis │──► DataFrame  │   │
│  │  │          │     │    Agent     │               │   │
│  │  │          │     └──────────────┘               │   │
│  │  │          │     ┌──────────────┐               │   │
│  │  │          │────►│   General    │               │   │
│  │  │          │     │    Agent     │               │   │
│  │  └──────────┘     └──────────────┘               │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌────────────────┐    ┌─────────────────────────────┐  │
│  │ Data Ingestion │    │     Qdrant Vector DB        │  │
│  │ (PyMuPDF +     │───►│  Dense (Gemini Embeddings)  │  │
│  │  Pandas)       │    │  + BM25 Sparse Scoring      │  │
│  └────────────────┘    └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Data Ingestion Pipeline (`app/rag/ingestion.py`)
- **PDFs**: Extracted page-by-page using PyMuPDF for accurate text extraction
- **CSVs**: Loaded into Pandas DataFrames AND converted to text documents for dual indexing
- **Chunking**: RecursiveCharacterTextSplitter (1000 chars, 200 overlap) preserving metadata

### 2. Hybrid Search (`app/rag/vector_store.py`)
- **Dense Search**: Configurable embedding model (Gemini `embedding-001` or Ollama `nomic-embed-text`) stored in Qdrant, searched via cosine similarity
- **Sparse Search**: BM25 scoring computed at query time for keyword matching
- **Fusion**: Reciprocal Rank Fusion (RRF) with configurable weights (default 0.7 dense, 0.3 sparse)
- **Storage**: Qdrant runs as a local file-based store — no Docker required for development

This hybrid approach ensures both semantic understanding (dense) and exact keyword matching (sparse), which is critical for finding specific project names, risk IDs, and financial figures.

### 3. Multi-Agent System (`app/agents/graph.py`)
Built as a LangGraph StateGraph:
- **Router Agent**: Zero-shot classification of query intent → `document_qa` | `data_analysis` | `general`
- **Document Q&A Agent**: Retrieves context via Hybrid Search and generates cited answers
- **Data Analysis Agent**: Analyzes financial DataFrames and performs calculations
- **General Agent**: Handles greetings and meta-questions

### 4. Evaluation (`evaluate.py`)
RAGAS evaluation with 8 test queries:
- 2 Easy (direct factual lookups)
- 2 Medium (multi-source reasoning)
- 2 Hard (cross-document comparison and inference)
- 2 Adversarial (out-of-scope and edge cases)

Metrics: **Faithfulness** and **Answer Relevancy**

## Data Flow

1. **Upload** → PDF/CSV/XLSX → Ingestion Pipeline → Chunks → Embeddings → Qdrant
2. **Query** → Router Agent → Specialist Agent → (Hybrid Search | DataFrame) → LLM → Answer with Citations

## LLM Provider Configuration

The system supports two LLM providers, switchable via the `LLM_PROVIDER` environment variable:

| Provider | LLM | Embeddings | Use Case |
|---|---|---|---|
| `ollama` | Any Ollama model (e.g. `qwen3:4b`, `llama3`) | `nomic-embed-text` | Offline / private deployments |
| `gemini` | `gemini-2.0-flash` | `embedding-001` | Fast cloud inference |

## Logging Architecture

- **Backend**: All application logs (requests, agent routing, errors) are written to `backend/logs/backend/app.log` via Python's `logging` module, initialised in a FastAPI `@startup` event to avoid Windows file-locking issues with Uvicorn.
- **Frontend**: Key events and errors from the React app are sent to the `/api/v1/client-log` endpoint and written to `backend/logs/frontend/client.log`.
