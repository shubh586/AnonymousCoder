from pydantic import BaseModel, Field


class AppSettings(BaseModel):
    """Complete configuration settings for the app to run"""
    # TODO: TO REMOVE IN PROD  
    TRACING: bool = Field(default=False)
    LOGGING: bool = Field(default=False)
    LANGFUSE_PUBLIC_KEY: str
    LANGFUSE_SECRET_KEY: str
    LANGFUSE_HOST: str
    #TODO:  QDRANT_HOST: str = Field(default="localhost:6333")
    #TODO: QDRANT_API_KEY: str = Field(default="")
    #TODO: QDRANT_COLLECTION: str = Field(default="app_documents")
    #TODO: TYPE THE ENTIRE SYSTEM TO ACCEPT THE DEFINED PROVIDERS
    LLM_PROVIDER:str
    LLM_NAME:str
    EMBEDDINGS_PROVIDER:str
    EMBEDDINGS_MODEL_NAME: str = Field(default="sentence-transformers/all-mpnet-base-v2")
    LLM_API_KEY: str
    EMBEDDINGS_API_KEY:str
    #TODO: VOICE_AGENTS
    #TODO: VOICE_MODE
    #TODO: ADD MCP SUPPORT
    HISTORY_DB_FILE: str = Field(default="user_space/threads.db")
    # TO REMOVE IN DEVELOPMENT
    LOG_FILE: str = Field(default="user_space/app.log")

    class Config:
        arbitrary_types_allowed = True