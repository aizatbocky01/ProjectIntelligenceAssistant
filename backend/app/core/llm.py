"""
LLM and Embeddings setup using Google Gemini.
"""
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from app.core.config import settings


def get_llm(temperature: float = 0.1, model: str = "gemini-2.0-flash") -> ChatGoogleGenerativeAI:
    """
    Returns a configured Gemini LLM instance.
    Uses gemini-2.0-flash for a good balance of speed, cost, and quality.
    """
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=temperature,
        convert_system_message_to_human=True,
    )


def get_embeddings(model: str = "models/embedding-001") -> GoogleGenerativeAIEmbeddings:
    """
    Returns a configured Gemini Embeddings instance.
    """
    return GoogleGenerativeAIEmbeddings(
        model=model,
        google_api_key=settings.GOOGLE_API_KEY,
    )
