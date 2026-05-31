# AI-Powered Project Intelligence Assistant - Implementation Plan

This plan details the architecture and implementation strategy for the Gamuda Senior AI Engineer take-home assessment.

## User Review Required

> [!WARNING]
> **Framework Constraint vs Upsonic**
> You mentioned exploring the **Upsonic** framework. While Upsonic is a great agentic framework, the assessment PDF explicitly states: 
> **"Note: You must use Python with LangChain for the backend, and JavaScript with React for the frontend."**
> To ensure you do not get disqualified for not following the instructions, I strongly recommend using **LangChain** and its multi-agent extension **LangGraph** for the orchestration instead of Upsonic. LangGraph is built specifically for creating multi-agent systems within the LangChain ecosystem. Do you agree to proceed with LangChain/LangGraph to strictly adhere to the requirements?

## Proposed Architecture

### 1. Technology Stack
*   **Backend:** Python 3.11+, FastAPI (REST API), LangChain + LangGraph (Agent Orchestration)
*   **Frontend:** React.js (Vite), TailwindCSS, Axios
*   **LLM & Embeddings:** Google Gemini (Free Tier) via `langchain-google-genai`
*   **Vector Database:** Qdrant (Local/Docker) - chosen because it has excellent native support for Hybrid Search, fulfilling the "advanced RAG" requirement.
*   **Observability:** LangSmith (Free Tier) for tracing agent calls and debugging.

### 2. Multi-Agent Orchestration (LangGraph)
We will build a state graph with the following agents:
*   **Router Agent:** Analyzes the user's query and routes it to the appropriate sub-agent based on intent.
*   **Document Q&A Agent:** Handles questions about Project Status and Risks. It uses Hybrid Search (Dense Embeddings + BM25 Sparse vectors) on the Qdrant Vector DB to retrieve PDF chunks and generates an answer with source citations.
*   **Data Analysis Agent:** Handles quantitative and budget questions. It will use a LangChain Pandas/Python execution tool to programmatically analyze 
<truncated 2633 bytes>