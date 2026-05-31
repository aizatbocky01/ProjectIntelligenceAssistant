
API routes for document upload and chat.
"""
import os
import logging
import shutil
import tempfile
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.rag.ingestion import load_pdf, load_csv, chunk_documents
from app.rag.vector_store import get_vector_store
from app.agents.graph import get_graph, register_dataframe
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


# --------------------------------------------------------------------------- #
# Request / Response models
# --------------------------------------------------------------------------- #
class ChatRequest(BaseModel):
    query: str
    chat_history: Optional[List[dict]] = []


class SourceInfo(BaseModel):
    document: str
    page: str
    file_type: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]
    route: str


class UploadResponse(BaseModel):
    message: str
    files_processed: List[str]
    total_chunks: int


class CollectionInfoResponse(BaseModel):
    name: str
    vectors_count: int
    points_count: int


# --------------------------------------------------------------------------- #
# Endpoints
# --------------------------------------------------------------------------- #
@router.post("/upload", response_model=UploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload one or more documents (PDF or CSV) for processing.
    PDFs are chunked and indexed in the vector store.
    CSVs are loaded as DataFrames for the Data Analysis agent AND indexed.
    """
    vector_store = get_vector_store()
    processed_files = []
    total_chunks = 0

    for file in files:
        filename = file.filename or "unknown"
        file_ext = os.path.splitext(filename)[1].lower()

        # Save uploaded file to a temp location
        try:
            with temp
<truncated 5167 bytes>