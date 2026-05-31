# Design Decisions

This document explains the key architectural and technical decisions made for the Project Intelligence Assistant.

---

## 1. LLM Choice: Dual Provider Support (Gemini + Ollama)

**Decision**: Support both Google Gemini and local Ollama models, switchable via a single `LLM_PROVIDER` environment variable.

**Rationale**:
- **Flexibility**: Allows running fully offline (privacy-first) or with a cloud model (speed-first)
- **Gemini**: Fast inference, native embedding model, generous free tier, good LangChain integration
- **Ollama**: Full data privacy, no API costs, works on-premise with models like `qwen3:4b` and `nomic-embed-text`

**Trade-offs**:
- Local Ollama models are significantly slower than Gemini on hardware without a dedicated GPU
- Embedding dimensions must match between the LLM model and the Qdrant collection (configured via `QDRANT_VECTOR_SIZE`)

---

## 2. Vector Database: Qdrant (Local File-Based)

**Decision**: Use Qdrant with local file-based storage instead of ChromaDB or Pinecone (and without requiring Docker).

**Rationale**:
- **Native hybrid search support** — Qdrant supports both dense and sparse vectors natively
- **No cloud dependency** — runs fully locally for the assessment
- **No Docker required** — Qdrant's Python client supports a `path=` argument for purely file-based storage, making local setup trivial
- **Production-ready** — unlike ChromaDB which is designed for prototyping

**Trade-offs**:
- File-based storage is slower than a running Qdrant server for large corpora
- ChromaDB would have been simpler but lacks native hybrid search

---

## 3. Advanced RAG: Hybrid Search with Reciprocal Rank Fusion

**Decision**: Implement Hybrid Search (Dense + BM25 Sparse) with RRF fusion instead of naive similarity search.

**Rationale**:
- **Assessment requirement**: Must implement "at least one technique beyond naive similarity search"
- Dense search (semantic) catches paraphrased queries
- Sparse search (BM25) catches exact terms like project names ("Project Alpha"), risk IDs ("RSK-001"), and financial figures
- **RRF** is a proven fusion method that doesn't require tuning score distributions

**Alternatives considered**:
- **HyDE (Hypothetical Document Embeddings)**: More complex, adds latency from extra LLM call
- **Re-ranking with Cross-Encoder**: Would be a good addition but adds dependency and latency
- **Parent Document Retrieval**: Useful for long documents but adds complexity

**Trade-offs**:
- BM25 is computed at query time over all documents (O(n)) — fine for assessment scale, would need an inverted index for production
- RRF weights (0.7 dense / 0.3 sparse) are defaults — could be tuned per query type

---

## 4. Multi-Agent Architecture: LangGraph StateGraph

**Decision**: Use LangGraph's StateGraph for agent orchestration instead of LangChain's AgentExecutor or CrewAI.

**Rationale**:
- **Assessment requires multi-agent**: LangGraph is LangChain's official multi-agent framework
- **Explicit control flow**: StateGraph provides deterministic routing (Router → Specialist → END) rather than open-ended tool use
- **Shared state**: AgentState TypedDict cleanly passes context between agents
- **Debuggable**: Each node's input/output can be inspected via LangSmith

**Architecture**:
```
Router Agent → classify intent
  ├── document_qa  → Hybrid Search → LLM answer with citations
  ├── data_analysis → DataFrame analysis → LLM answer
  └── general      → Direct LLM response
```

**Trade-offs**:
- Simpler than a ReAct loop or tool-calling agent — but more predictable
- Adding new agent types is easy (just add a node + edge)

---

## 5. Document Processing: PyMuPDF + Pandas

**Decision**: Use PyMuPDF (fitz) for PDFs and Pandas for CSVs.

**Rationale**:
- **PyMuPDF** is the fastest Python PDF library and handles messy layouts well
- **Pandas** provides powerful data analysis capabilities and natural integration with the Data Analysis agent
- CSVs are **dual-indexed**: stored as text chunks in the vector DB AND as DataFrames for computation

**Trade-offs**:
- PyMuPDF doesn't handle scanned PDFs (would need OCR for production)
- Pandas DataFrames are kept in memory — would need a database for production scale

---

## 6. Frontend: React + Vite (No TailwindCSS)

**Decision**: Use React with Vite and custom CSS instead of TailwindCSS.

**Rationale**:
- Assessment requires "JavaScript with React"
- Vite provides fast HMR and modern build tooling
- Custom CSS gives full control over the glassmorphism/dark theme design
- Minimal dependencies: only React, Axios, and react-markdown

**Trade-offs**:
- More CSS to write vs Tailwind utility classes
- More design control and uniqueness

---

## 7. Evaluation: RAGAS with 4 Difficulty Levels

**Decision**: Create 8 test queries spanning easy, medium, hard, and adversarial categories.

**Rationale**:
- **Easy** (2): Direct factual lookups — validates basic retrieval
- **Medium** (2): Multi-source reasoning — validates cross-document retrieval
- **Hard** (2): Comparison and inference — validates agent routing and analysis
- **Adversarial** (2): Out-of-scope queries — validates graceful handling of missing info

**Metrics**:
- **Faithfulness**: Does the answer stay grounded in the retrieved context?
- **Answer Relevancy**: Does the answer actually address the question?

---

## 8. Synthetic Data Design

**Decision**: Create intentionally messy synthetic data to simulate real-world conditions.

**Details**:
- **Inconsistent formats**: One report has an "Executive Summary" section, another doesn't
- **Missing fields**: Some CSV notes are blank
- **Mixed document types**: PDFs (status reports, risk register) + CSV (financial summary) + XLSX (portfolio summary)
- **Cross-referencing**: Risk register references projects mentioned in status reports

This tests the system's ability to handle imperfect, real-world data.

---

## 9. Logging: File-Based with Startup Hook

**Decision**: Implement file-based logging for both backend (Python) and frontend (React), with setup deferred to a FastAPI `@app.on_event("startup")` hook.

**Rationale**:
- **Observability**: Having persistent log files (`logs/backend/app.log`, `logs/frontend/client.log`) is essential for debugging in production
- **Windows compatibility**: Uvicorn's `--reload` mode spawns multiple processes. Opening `FileHandler` at module import time causes file-locking conflicts on Windows (`ECONNRESET`). Deferring to the startup event ensures only the worker process holds the file handle
- **Frontend logs**: React runs in the browser so cannot write files directly. Logs are forwarded to a `/api/v1/client-log` endpoint and written server-side

**Trade-offs**:
- For production, a structured logging service (e.g., Datadog, Loki) would replace flat files

