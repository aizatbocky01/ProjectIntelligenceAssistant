
RAGAS Evaluation Script for the Project Intelligence Assistant.

Runs 8 predefined queries (easy, medium, hard, adversarial) against the
system and evaluates answers using Faithfulness and Answer Relevancy metrics.
"""
import os
import sys
import json
import asyncio
import logging

# Add parent dir to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.rag.ingestion import load_pdf, load_csv, chunk_documents
from app.rag.vector_store import get_vector_store
from app.agents.graph import get_graph, register_dataframe

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Test queries spanning difficulty levels
# --------------------------------------------------------------------------- #
TEST_QUERIES = [
    # Easy
    {
        "id": 1,
        "difficulty": "easy",
        "query": "What is the current status of Project Alpha?",
        "ground_truth": "Project Alpha is in the execution phase. The core infrastructure upgrade is 60% complete with minor delays due to supply chain issues.",
    },
    {
        "id": 2,
        "difficulty": "easy",
        "query": "Who is the author of the Project Beta status report?",
        "ground_truth": "Jane Smith is the author of the Project Beta monthly status report.",
    },
    # Medium
    {
        "id": 3,
        "difficulty": "medium",
        "query": "What are all the open risks across all projects?",
        "ground_truth": "There are three open risks: RSK-001 (Hardware supply chain disruption for Project Alpha, High severity), RSK-003 (Legacy database connection timeout for Project Beta, Low severity), and RSK-004 (Regulatory compliance changes for Project Gamma, High severity).",
    },
    {
        "id": 4,
        "difficulty": "medium",
        "quer
<truncated 7683 bytes>