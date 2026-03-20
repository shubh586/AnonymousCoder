import os
import warnings

warnings.filterwarnings("ignore", message="Core Pydantic V1")

from dotenv import load_dotenv

load_dotenv()

from dotenv import load_dotenv

from src.agent_project.application.app import Application
from src.agent_project.config.config import AppSettings
from src.agent_project.utilities.load_json import load_json


def main():
    try:    
        load_dotenv()
        # Get environment variables with defaults
        # This all will be set in the settings page of terminal
        # Model to use , its api key , Whether to use observatory or not 
        # User provided API keys
        
        # TODO: System default shipped with the product
        # halt for now untill indexing of cde base is needed 
        # qdrant_host = os.getenv("QDRANT_HOST")
        # qdrant_api_key = os.getenv("QDRANT_API_KEY")
            
        # load user settings
        user_settings=load_json(settings_path="user_space/settings.json")    
        settings = AppSettings(    
            TRACING=user_settings.get("TRACING",""),
            LOGGING=user_settings.get("LOGGING",""),
            LANGFUSE_HOST=os.getenv("LANGFUSE_HOST",""),
            LANGFUSE_SECRET_KEY=os.getenv("LANGFUSE_SECRET_KEY",""),
            LANGFUSE_PUBLIC_KEY= os.getenv("LANGFUSE_PUBLIC_KEY",""),
            EMBEDDINGS_MODEL_NAME=user_settings.get("EMBEDDINGS_MODEL_NAME"),
            LLM_PROVIDER=user_settings.get("LLM_PROVIDER"),
            LLM_NAME=user_settings.get("LLM_NAME"),
            EMBEDDINGS_PROVIDER=user_settings.get("EMBEDDINGS_PROVIDER"),
            LLM_API_KEY=os.getenv("LLM_API_KEY",""),
            EMBEDDINGS_API_KEY=os.getenv("EMBEDDINGS_API_KEY",""), 
        )
        
        # Create the application instance directly
        app = Application(
            settings=settings,
            database=None,  
            tracer=None,    
            thread_id="",   
            graph=None      
        )
        
        app.invoke()
    except Exception as e:
        print(e)
if __name__ == "__main__":
    main()
