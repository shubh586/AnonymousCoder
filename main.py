import os
import warnings

warnings.filterwarnings("ignore", message="Core Pydantic V1")

from dotenv import load_dotenv

load_dotenv()

from src.agent_project.application.app import Application
from src.agent_project.config.config import AppSettings


def main():
    # Get environment variables with defaults
    groq_api_key = os.getenv("GROQ_API_KEY", "dummy_key_for_testing")
    langfuse_host = os.getenv("LANGFUSE_HOST", "http://localhost:3000")
    langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    qdrant_host = os.getenv("QDRANT_HOST", "localhost:6333")
    qdrant_api_key = os.getenv("QDRANT_API_KEY", "")
    
    if not langfuse_public_key or  not langfuse_secret_key:
        return
    
    settings = AppSettings(
        TRACING=False,
        GROQ_API_KEY=groq_api_key,
        LANGFUSE_HOST=langfuse_host,
        LANGFUSE_SECRET_KEY=langfuse_secret_key,
        LANGFUSE_PUBLIC_KEY=langfuse_public_key,
        QDRANT_HOST=qdrant_host,
        QDRANT_API_KEY=qdrant_api_key,
        EMBEDDINGS_MODEL_NAME="sentence-transformers/all-mpnet-base-v2",
        QDRANT_COLLECTION="app_documents",
        DEVICE="cpu",
        LLM_NAME="openai/gpt-oss-120b",
        LOG_FILE="user_space/logs.log",
        LOGGING=True
    )
    
    # Create the application instance directly
    app = Application(
        settings=settings,
        database=None,  # Will be set in model_post_init
        tracer=None,    # Will be set in model_post_init
        thread_id="",   # Will be set in model_post_init
        graph=None      # Will be set in model_post_init
    )
    
    app.invoke()
    
if __name__ == "__main__":
    main()
