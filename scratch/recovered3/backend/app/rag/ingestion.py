
Document ingestion pipeline.
Handles loading PDFs and CSVs, chunking text, and upserting into the vector store.
"""
import os
import logging
from typing import List, Tuple

import fitz  # PyMuPDF
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

logger = logging.getLogger(__name__)


def load_pdf(file_path: str) -> List[Document]:
    """
    Load a PDF file using PyMuPDF and return a list of LangChain Documents.
    Each page becomes a separate document with metadata.
    """
    documents = []
    try:
        doc = fitz.open(file_path)
        for page_num, page in enumerate(doc):
            text = page.get_text("text")
            if text.strip():
                documents.append(
                    Document(
                        page_content=text,
                        metadata={
                            "source": os.path.basename(file_path),
                            "page": page_num + 1,
                            "file_type": "pdf",
                        },
                    )
                )
        doc.close()
        logger.info(f"Loaded {len(documents)} pages from {file_path}")
    except Exception as e:
        logger.error(f"Error loading PDF {file_path}: {e}")
        raise
    return documents


def load_csv(file_path: str) -> Tuple[pd.DataFrame, List[Document]]:
    """
    Load a CSV file into a Pandas DataFrame AND create LangChain Documents
    from it for the vector store. Returns both the DataFrame (for the Data
    Analysis Agent) and the Documents (for RAG indexing).
    """
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Loaded CSV with {len(df)} rows from {file_path}")

        # Create a textual representation for each row for RAG indexing
        documents = []
        columns = df.columns.tolist()
        for idx, row in df.iterrows():
            row_text = "; ".join([f"{c
<truncated 1818 bytes>