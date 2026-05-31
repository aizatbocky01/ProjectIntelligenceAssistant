
Multi-agent orchestration using LangGraph.

Implements a state machine with:
1. Router Agent - classifies the query intent
2. Document Q&A Agent - answers qualitative questions via Hybrid RAG
3. Data Analysis Agent - answers quantitative questions using DataFrames
4. General Agent - handles greetings and meta-questions
"""
import logging
from typing import TypedDict, List, Optional, Annotated
import operator

from langchain.schema import Document, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from app.core.llm import get_llm
from app.rag.vector_store import get_vector_store
from app.agents.prompts import (
    ROUTER_SYSTEM_PROMPT,
    DOCUMENT_QA_SYSTEM_PROMPT,
    DATA_ANALYSIS_SYSTEM_PROMPT,
    GENERAL_SYSTEM_PROMPT,
)

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# State definition
# --------------------------------------------------------------------------- #
class AgentState(TypedDict):
    """State shared across all nodes in the graph."""
    query: str
    route: str
    context_docs: List[Document]
    dataframe_info: str
    answer: str
    sources: List[dict]
    chat_history: List[dict]


# --------------------------------------------------------------------------- #
# DataFrames registry (populated at upload time)
# --------------------------------------------------------------------------- #
_dataframes: dict = {}


def register_dataframe(name: str, df_info: str):
    """Register a DataFrame summary for the Data Analysis agent."""
    _dataframes[name] = df_info


def get_dataframes_info() -> str:
    """Get all registered DataFrame summaries."""
    if not _dataframes:
        return "No financial data has been uploaded yet."
    return "\
\
".join(
        [f"--- {name} ---\
{info}" for name, info in _dataframes.items()]
    )


# ---------------------------------------------------------------------
<truncated 5762 bytes>