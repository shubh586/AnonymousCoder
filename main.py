import argparse
import os
import warnings

warnings.filterwarnings("ignore", message="Core Pydantic V1")

from dotenv import load_dotenv

load_dotenv()

from src.agent_project.application.app import Application
from src.agent_project.config.config import AppSettings


def main():
    parser = argparse.ArgumentParser(description="Anonymous Coder")
    parser.add_argument("--tui", action="store_true", help="Launch the Textual TUI instead of the CLI")
    args = parser.parse_args()

    # Get environment variables with defaults
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    langfuse_host = os.getenv("LANGFUSE_HOST", "http://localhost:3000")
    langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    qdrant_host = os.getenv("QDRANT_HOST", "http://localhost:6333")
    qdrant_api_key = os.getenv("QDRANT_API_KEY", "")
    
    if not langfuse_public_key or  not langfuse_secret_key:
        return
    
    settings = AppSettings(
        TRACING=False,
        AWS_REGION=aws_region,
        LANGFUSE_HOST=langfuse_host,
        LANGFUSE_SECRET_KEY=langfuse_secret_key,
        LANGFUSE_PUBLIC_KEY=langfuse_public_key,
        QDRANT_HOST=qdrant_host,
        QDRANT_API_KEY=qdrant_api_key,
        EMBEDDINGS_MODEL_NAME="sentence-transformers/all-mpnet-base-v2",
        QDRANT_COLLECTION="app_documents",
        DEVICE="cpu",
        LLM_NAME="amazon.nova-pro-v1:0",
        LOG_FILE="user_space/logs.log",
        LOGGING=True
    )
    
    # Create the application instance (initializes graph, db, etc.)
    app = Application(
        settings=settings,
        database=None,  # Will be set in model_post_init
        tracer=None,    # Will be set in model_post_init
        thread_id="",   # Will be set in model_post_init
        graph=None      # Will be set in model_post_init
    )
    
    if args.tui:
        from uuid import uuid4
        from src.agent_project.application.tui.app import AnonymousCoderApp

        # Build the same config the CLI uses
        thread_id = str(uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        if settings.TRACING and app.tracer:
            config["callbacks"] = [app.tracer]

        tui = AnonymousCoderApp(
            graph=app.graph,
            config=config,
            database=app.database,
        )
        tui.run()
    else:
        app.invoke()
    
if __name__ == "__main__":
    main()

