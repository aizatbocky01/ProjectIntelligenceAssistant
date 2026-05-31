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
│  │  │  Router  │────►│ Document Q&A │──► Hybrid RAG │   
<truncated 3761 bytes>