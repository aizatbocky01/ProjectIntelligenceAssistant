
Vector store management using Qdrant with Hybrid Search support.
Implements both dense (Gemini embeddings) and sparse (BM25) search,
then fuses results via Reciprocal Rank Fusion (RRF).
"""
import logging
import uuid
from typing import List, Optional
import math
import re
from collections import Counter

from qdrant_client import QdrantClient, models
from langchain.schema import Document

from app.core.llm import get_embeddings
from app.core.config import settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "project_documents"
VECTOR_SIZE = 768  # Gemini embedding-001 outputs 768 dimensions


class BM25:
    """
    Simple BM25 implementation for generating sparse scores.
    Used to complement dense vector search for hybrid retrieval.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = 0
        self.avgdl = 0
        self.doc_freqs: Counter = Counter()
        self.doc_len: List[int] = []

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Simple whitespace + lowercase tokenization."""
        return re.findall(r"\w+", text.lower())

    def fit(self, corpus: List[str]):
        """Fit BM25 on the corpus to compute IDF values."""
        self.corpus_size = len(corpus)
        total_len = 0
        for doc in corpus:
            tokens = self.tokenize(doc)
            self.doc_len.append(len(tokens))
            total_len += len(tokens)
            unique_tokens = set(tokens)
            for token in unique_tokens:
                self.doc_freqs[token] += 1
        self.avgdl = total_len / self.corpus_size if self.corpus_size else 0

    def get_scores(self, query: str) -> dict:
        """
        Return a dict of {token: weight} representing a sparse vector
        for the given query based on IDF.
        """
        query_tokens = self.tokenize(query)
        scores = {}
        for token in qu
<truncated 7519 bytes>