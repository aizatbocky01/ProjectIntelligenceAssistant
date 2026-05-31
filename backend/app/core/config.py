import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Project Intelligence Assistant"
    API_V1_STR: str = "/api/v1"
    
    # LLM Settings (Choose between 'gemini' or 'ollama')
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama") # Defaults to ollama as requested
    
    # Google Gemini Settings
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Ollama Settings
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_LLM_MODEL: str = os.getenv("OLLAMA_LLM_MODEL", "llama3") # Example default
    OLLAMA_EMBED_MODEL: str = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text") # Example default
    
    # Vector DB
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", 6333))
    QDRANT_VECTOR_SIZE: int = int(os.getenv("QDRANT_VECTOR_SIZE", 768)) # 768 for gemini and nomic-embed-text
    DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data")
    
    class Config:
        case_sensitive = True
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
