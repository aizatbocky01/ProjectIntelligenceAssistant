"""
API routes for the FastAPI backend.
"""
import os
import shutil
import tempfile
import logging
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel

from app.rag.ingestion import load_pdf, load_csv, load_xlsx, process_and_chunk
from app.rag.vector_store import get_vector_store
from app.agents.graph import register_dataframe, build_graph

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize the LangGraph orchestration
agent_executor = build_graph()


class ChatRequest(BaseModel):
    query: str
    chat_history: Optional[List[dict]] = None


class ChatResponse(BaseModel):
    response: str
    sources: List[dict]


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint. Routes the query through the multi-agent system.
    """
    logger.info(f"Received query: {request.query}")
    try:
        initial_state = {
            "query": request.query,
            "chat_history": request.chat_history or [],
            "route": "",
            "context_docs": [],
            "dataframe_info": "",
            "answer": "",
            "sources": []
        }
        
        # Run the graph
        logger.info("Executing agent graph...")
        final_state = agent_executor.invoke(initial_state)
        
        logger.info(f"Graph execution complete. Routed to: {final_state.get('route')}")
        return ChatResponse(
            response=final_state.get("answer", "I could not generate an answer."),
            sources=final_state.get("sources", [])
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Endpoint to upload and ingest a document (PDF, CSV, or XLSX).
    """
    logger.info(f"Received upload request for file: {file.filename}")
    
    # Check file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".csv", ".xlsx"]:
        raise HTTPException(status_code=400, detail="Only PDF, CSV, and XLSX files are supported.")
        
    try:
        # Save to temp file because PyMuPDF and Pandas need a file path
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name

        documents = []
        df = None
        
        logger.info(f"Processing {file.filename}...")
        if ext == ".pdf":
            documents = load_pdf(temp_path)
            chunks = process_and_chunk(documents)
            get_vector_store().add_documents(chunks)
        elif ext == ".csv":
            df, documents = load_csv(temp_path)
            chunks = process_and_chunk(documents)
            get_vector_store().add_documents(chunks)
            # Register dataframe for data analysis agent
            df_info = f"Columns: {', '.join(df.columns.tolist())}\nRows: {len(df)}\nSample Data:\n{df.head(3).to_markdown()}"
            register_dataframe(file.filename, df_info)
        elif ext == ".xlsx":
            df, documents = load_xlsx(temp_path)
            chunks = process_and_chunk(documents)
            get_vector_store().add_documents(chunks)
            # Register dataframe
            df_info = f"Columns: {', '.join(df.columns.tolist())}\nRows: {len(df)}\nSample Data:\n{df.head(3).to_markdown()}"
            register_dataframe(file.filename, df_info)

        # Cleanup temp file
        os.remove(temp_path)
        logger.info(f"Successfully processed {file.filename}")
        
        return {"status": "success", "message": f"Processed {file.filename} successfully."}
    
    except Exception as e:
        logger.error(f"Error processing upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collection-info")
async def get_collection_info():
    """
    Returns basic info about the vector store.
    """
    try:
        vs = get_vector_store()
        collection = vs.client.get_collection(vs.client.get_collections().collections[0].name)
        return {
            "status": "success",
            "vectors_count": collection.vectors_count,
            "status_str": collection.status.value if collection.status else "unknown"
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@router.post("/client-log")
async def client_log(log_data: dict):
    """
    Receives logs from the frontend and forwards them to the client.log file.
    """
    frontend_logger = logging.getLogger("frontend")
    level_str = log_data.get("level", "info").upper()
    message = log_data.get("message", "")
    
    if hasattr(logging, level_str):
        level = getattr(logging, level_str)
        frontend_logger.log(level, message)
    else:
        frontend_logger.info(message)
        
    return {"status": "logged"}