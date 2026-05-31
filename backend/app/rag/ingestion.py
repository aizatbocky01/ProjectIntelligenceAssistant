"""
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
import openpyxl

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
            row_text = "; ".join([f"{c}: {row[c]}" for c in columns])
            documents.append(
                Document(
                    page_content=row_text,
                    metadata={
                        "source": os.path.basename(file_path),
                        "row": idx,
                        "file_type": "csv",
                    },
                )
            )
        return df, documents
    except Exception as e:
        logger.error(f"Error loading CSV {file_path}: {e}")
        raise

def load_xlsx(file_path: str) -> Tuple[pd.DataFrame, List[Document]]:
    """
    Load an XLSX file into a Pandas DataFrame AND create LangChain Documents
    from it for the vector store.
    """
    try:
        df = pd.read_excel(file_path, engine="openpyxl")
        logger.info(f"Loaded Excel with {len(df)} rows from {file_path}")

        documents = []
        columns = df.columns.tolist()
        for idx, row in df.iterrows():
            row_text = "; ".join([f"{c}: {row[c]}" for c in columns])
            documents.append(
                Document(
                    page_content=row_text,
                    metadata={
                        "source": os.path.basename(file_path),
                        "row": idx,
                        "file_type": "xlsx",
                    },
                )
            )
        return df, documents
    except Exception as e:
        logger.error(f"Error loading Excel {file_path}: {e}")
        raise


def process_and_chunk(documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
    """
    Split documents into smaller chunks for optimal RAG performance.
    """
    logger.info(f"Chunking {len(documents)} documents...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Created {len(chunks)} chunks.")
    return chunks