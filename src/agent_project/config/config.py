from pydantic import BaseModel, Field


class AppSettings(BaseModel):
    """Complete configuration settings for the app to run"""
    
    TRACING: bool = Field(default=False)
    LANGFUSE_PUBLIC_KEY: str
    LANGFUSE_SECRET_KEY: str
    LANGFUSE_HOST: str
    QDRANT_HOST: str = Field(default="localhost:6333")
    QDRANT_API_KEY: str = Field(default="")
    QDRANT_COLLECTION: str = Field(default="app_documents")
    EMBEDDINGS_MODEL_NAME: str = Field(default="sentence-transformers/all-mpnet-base-v2")
    DEVICE: str = Field(default="cpu")
    AWS_REGION: str = Field(default="us-east-1")
    HISTORY_DB_FILE: str = Field(default="user_space/chats.db")
    LLM_NAME: str
    LOG_FILE: str = Field(default="user_space/logs.log")
    LOGGING: bool
    
    class Config:
        arbitrary_types_allowed = True