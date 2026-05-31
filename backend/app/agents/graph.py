"""
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
    return "\n\n".join(
        [f"--- {name} ---\n{info}" for name, info in _dataframes.items()]
    )


# --------------------------------------------------------------------------- #
# Nodes
# --------------------------------------------------------------------------- #
def route_query(state: AgentState) -> AgentState:
    """Determine the nature of the query and set the route."""
    llm = get_llm(temperature=0.0)
    messages = [
        SystemMessage(content=ROUTER_SYSTEM_PROMPT),
        HumanMessage(content=state["query"])
    ]
    response = llm.invoke(messages)
    
    # Simple extraction of the route name from the LLM response
    route = response.content.strip().upper()
    valid_routes = ["DOCUMENT_QA", "DATA_ANALYSIS", "GENERAL"]
    
    if route not in valid_routes:
        # Fallback to document QA if it doesn't strictly follow format
        if "data" in route.lower() or "financial" in route.lower():
            route = "DATA_ANALYSIS"
        elif "hello" in route.lower() or "hi" in route.lower():
            route = "GENERAL"
        else:
            route = "DOCUMENT_QA"
            
    logger.info(f"Router decided route: {route}")
    return {"route": route}


def retrieve_documents(state: AgentState) -> AgentState:
    """Retrieve documents using Hybrid Search (Dense + BM25)."""
    vs = get_vector_store()
    logger.info("Retrieving documents for Q&A...")
    # Retrieve top 5 most relevant chunks
    docs = vs.search(state["query"], limit=5)
    return {"context_docs": docs}


def gather_dataframe_info(state: AgentState) -> AgentState:
    """Gather available DataFrame schemas and samples."""
    logger.info("Gathering dataframe metadata for Data Analysis...")
    df_info = get_dataframes_info()
    return {"dataframe_info": df_info}


def document_qa_agent(state: AgentState) -> AgentState:
    """Answer qualitative questions using the retrieved documents."""
    llm = get_llm(temperature=0.1)
    
    # Format context
    context_str = "\n\n".join([
        f"[Source: {doc.metadata.get('source', 'Unknown')}, Page/Row: {doc.metadata.get('page', doc.metadata.get('row', 'N/A'))}]\n{doc.page_content}"
        for doc in state["context_docs"]
    ])
    
    messages = [
        SystemMessage(content=DOCUMENT_QA_SYSTEM_PROMPT),
        HumanMessage(content=f"Context:\n{context_str}\n\nQuestion:\n{state['query']}")
    ]
    
    logger.info("Generating Document Q&A answer...")
    response = llm.invoke(messages)
    
    # Extract sources for the frontend
    sources = [
        {
            "source": doc.metadata.get('source', 'Unknown'),
            "page": doc.metadata.get('page'),
            "row": doc.metadata.get('row')
        }
        for doc in state["context_docs"]
    ]
    
    # Deduplicate sources based on filename
    unique_sources = []
    seen = set()
    for s in sources:
        if s["source"] not in seen:
            seen.add(s["source"])
            unique_sources.append(s)
            
    return {"answer": response.content, "sources": unique_sources}


def data_analysis_agent(state: AgentState) -> AgentState:
    """Answer quantitative questions using DataFrame schemas/samples."""
    llm = get_llm(temperature=0.1)
    
    messages = [
        SystemMessage(content=DATA_ANALYSIS_SYSTEM_PROMPT),
        HumanMessage(content=f"Available Data:\n{state['dataframe_info']}\n\nQuestion:\n{state['query']}")
    ]
    
    logger.info("Generating Data Analysis answer...")
    response = llm.invoke(messages)
    
    sources = [{"source": name} for name in _dataframes.keys()]
    return {"answer": response.content, "sources": sources}


def general_agent(state: AgentState) -> AgentState:
    """Handle conversational queries (greetings, 'what can you do')."""
    llm = get_llm(temperature=0.7)
    
    messages = [
        SystemMessage(content=GENERAL_SYSTEM_PROMPT),
        HumanMessage(content=state["query"])
    ]
    
    logger.info("Generating General conversation answer...")
    response = llm.invoke(messages)
    return {"answer": response.content, "sources": []}


# --------------------------------------------------------------------------- #
# Edge logic
# --------------------------------------------------------------------------- #
def route_after_classification(state: AgentState) -> str:
    return state["route"]


# --------------------------------------------------------------------------- #
# Graph Construction
# --------------------------------------------------------------------------- #
def build_graph() -> StateGraph:
    """Build and compile the LangGraph workflow."""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("router", route_query)
    workflow.add_node("retrieve_docs", retrieve_documents)
    workflow.add_node("gather_df", gather_dataframe_info)
    
    workflow.add_node("DOCUMENT_QA", document_qa_agent)
    workflow.add_node("DATA_ANALYSIS", data_analysis_agent)
    workflow.add_node("GENERAL", general_agent)
    
    # Entry point
    workflow.set_entry_point("router")
    
    # Conditional routing after the router node
    workflow.add_conditional_edges(
        "router",
        route_after_classification,
        {
            "DOCUMENT_QA": "retrieve_docs",
            "DATA_ANALYSIS": "gather_df",
            "GENERAL": "GENERAL"
        }
    )
    
    # Sequential execution for specialized paths
    workflow.add_edge("retrieve_docs", "DOCUMENT_QA")
    workflow.add_edge("gather_df", "DATA_ANALYSIS")
    
    # End points
    workflow.add_edge("DOCUMENT_QA", END)
    workflow.add_edge("DATA_ANALYSIS", END)
    workflow.add_edge("GENERAL", END)
    
    return workflow.compile()