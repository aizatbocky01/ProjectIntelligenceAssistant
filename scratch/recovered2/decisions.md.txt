# Design Decisions

This document explains the key architectural and technical decisions made for the Project Intelligence Assistant.

---

## 1. LLM Choice: Google Gemini (gemini-2.0-flash)

**Decision**: Use Google Gemini via `langchain-google-genai` instead of OpenAI GPT.

**Rationale**:
- **Free tier** with generous rate limits for the assessment
- **Fast inference** (flash model) — suitable for multi-agent routing + generation
- **Native embedding model** (embedding-001) — avoids mixing providers
- **LangChain integration** is mature and well-documented

**Trade-offs**:
- Gemini's structured output support is less mature than GPT-4o
- Worked around this by using simple text classification for routing

---

## 2. Vector Database: Qdrant (Local)

**Decision**: Use Qdrant running locally (or Docker) instead of ChromaDB or Pinecone.

**Rationale**:
- **Native hybrid search support** — Qdrant supports both dense and sparse vectors natively
- **No cloud dependency** — runs fully locally for the assessment
- **Production-ready** — unlike ChromaDB which is designed for prototyping
- **REST + gRPC APIs** — good performance characteristics

**Trade-offs**:
- Requires Docker or local binary (added setup step)
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
- **R
<truncated 3715 bytes>