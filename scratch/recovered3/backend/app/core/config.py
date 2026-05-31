import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Project Intelligence Assistant"
    API_V1_STR: str = "/api/v1"
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", 6333))
    DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data")
    
    class Config:
        case_sensitive = True

settings = Settings()
