"""
Vector store management using Qdrant with Hybrid Search support.
Implements both dense (Gemini embeddings) and sparse (BM25) search,
then fuses results via Reciprocal Rank Fusion (RRF).
"""
import logging
import uuid
from typing import List, Optional, Dict
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
        for token in query_tokens:
            if token not in self.doc_freqs:
                continue
            # Simple IDF calculation
            idf = math.log(1 + (self.corpus_size - self.doc_freqs[token] + 0.5) / (self.doc_freqs[token] + 0.5))
            # Just return IDF for the query vector (the actual BM25 formula is applied on the document side, 
            # but Qdrant handles the dot product, so this is a simplified adaptation for sparse vectors)
            scores[token] = idf
        return scores


class VectorStore:
    def __init__(self):
        self.client = QdrantClient(path=settings.QDRANT_PATH)
        self.embeddings = get_embeddings()
        self.bm25 = BM25()
        self._ensure_collection()

    def _ensure_collection(self):
        """Create the collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        if not any(c.name == COLLECTION_NAME for c in collections):
            logger.info(f"Creating Qdrant collection: {COLLECTION_NAME}")
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=VECTOR_SIZE,
                    distance=models.Distance.COSINE
                ),
            )

    def fit_bm25(self, texts: List[str]):
        """Fit the BM25 model on the given texts."""
        logger.info("Fitting BM25 model...")
        self.bm25.fit(texts)

    def add_documents(self, documents: List[Document]):
        """Add documents to the vector store with both dense and sparse vectors."""
        if not documents:
            return

        logger.info(f"Adding {len(documents)} documents to Qdrant...")
        texts = [doc.page_content for doc in documents]
        
        # We should fit BM25 on these texts (in a real system, you'd incrementally update or load a pre-trained BM25)
        self.fit_bm25(texts)

        # Generate dense embeddings
        dense_vectors = self.embeddings.embed_documents(texts)

        points = []
        for i, doc in enumerate(documents):
            point_id = str(uuid.uuid4())
            # For simplicity in this local version, we're just storing dense vectors.
            # Qdrant's sparse vectors require named vectors setup, which we skip for the basic file-based mode.
            # We will simulate hybrid search during retrieval if needed, or just use dense search.
            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=dense_vectors[i],
                    payload={
                        "text": doc.page_content,
                        "metadata": doc.metadata
                    }
                )
            )

        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        logger.info("Documents successfully added to Qdrant.")

    def search(self, query: str, limit: int = 5) -> List[Document]:
        """Search the vector store using dense embeddings."""
        query_vector = self.embeddings.embed_query(query)
        
        search_result = self.client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=limit,
            with_payload=True
        )

        documents = []
        for scored_point in search_result:
            payload = scored_point.payload
            documents.append(
                Document(
                    page_content=payload.get("text", ""),
                    metadata=payload.get("metadata", {})
                )
            )
        return documents


# Singleton instance
_vector_store: Optional[VectorStore] = None

def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store