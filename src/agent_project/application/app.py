import os
import platform
from typing import Any, Optional
from uuid import uuid4

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langfuse.langchain.CallbackHandler import LangchainCallbackHandler
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel, Field

from src.agent_project.core.graph.graph import create_graph
from src.agent_project.core.prompts.system_prompt import get_system_prompt
from src.agent_project.core.states.AnonymousState import AnonymousState

from ..config.config import AppSettings
from ..infrastructure.databases.sql_database import (DataBaseManager,
                                                     get_database_manager)
from ..infrastructure.databases.vector_database import initialize_vector_store
from ..infrastructure.llm_clients.llms import GroqLLM, LLMConfig, ModelProvider
from ..infrastructure.monitoring.tracing import get_langfuse_handler
from ..utilities.logger import init_logger


class Application(BaseModel):
    settings: AppSettings
    database: Optional[DataBaseManager] = Field(default=None)
    tracer: Optional[LangchainCallbackHandler] = Field(default=None)
    thread_id: str = Field(default="")
    graph: Optional[CompiledStateGraph] = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    def model_post_init(self, __context: Any) -> None:
        log = init_logger(enable_logging=self.settings.LOGGING, log_file=self.settings.LOG_FILE)
        log.info("Warming up...")

        # Initialize chats db
        self.database = get_database_manager(self.settings.HISTORY_DB_FILE)

        # Initialize vector store with error handling
        try:
            embedding_model = HuggingFaceEmbeddings(
                model_name=self.settings.EMBEDDINGS_MODEL_NAME,
                model_kwargs={"device": self.settings.DEVICE}
            )
            initialize_vector_store(
                host=self.settings.QDRANT_HOST,
                api_key=self.settings.QDRANT_API_KEY,
                embeddings=embedding_model,
                collection_name=self.settings.QDRANT_COLLECTION
            )
            log.info("Qdrant vector store initialized successfully")
        except Exception as e:
            log.warning(f"Could not initialize Qdrant vector store: {e}")
            log.info("Continuing without vector store functionality")

        # Create LLM
        try:
            llm_config = LLMConfig(
                provider=ModelProvider.GROQ,
                model_name=self.settings.LLM_NAME,
                api_key=self.settings.GROQ_API_KEY
            )
            llm = GroqLLM().create_llm(config=llm_config)
            log.info("LLM initialized successfully")
        except Exception as e:
            log.error(f"Could not initialize LLM: {e}")
            log.info("Continuing without LLM functionality")
            llm = None

        self.tracer = get_langfuse_handler(
            LANGFUSE_SECRET_KEY=self.settings.LANGFUSE_SECRET_KEY,
            LANGFUSE_HOST=self.settings.LANGFUSE_HOST,
            LANGFUSE_PUBLIC_KEY=self.settings.LANGFUSE_PUBLIC_KEY
        )

        self.thread_id = str(uuid4())

        # Create Graph
        if llm:
            self.graph = create_graph(llm=llm)
            log.info("Graph created successfully")
        else:
            log.warning("Could not create graph due to LLM initialization failure")
            self.graph = None

        log.info("Running the AI hamsters...")

    def invoke(self):
        """Start the chat loop."""
        self._chat()

    def _chat(self):
        thread_id = str(uuid4())

        # Build runnable config
        if self.settings.TRACING and self.tracer:
            config: RunnableConfig = {
                "callbacks": [self.tracer],
                "configurable": {"thread_id": thread_id}
            }
        else:
            config: RunnableConfig = {
                "configurable": {"thread_id": thread_id}
            }

        # System prompt for the first message
        system_prompt = get_system_prompt(
            os=platform.system(),
            path=os.getcwd()
        )
        first_chat = True

        while True:
            # User input
            try:
                query = input("\n🟢 You: ")
            except (EOFError, KeyboardInterrupt):
                print("\nExiting the world... :(")
                break

            if not query.strip():
                continue

            # Generate a message id and store in DB
            message_id = str(uuid4())
            if self.database:
                try:
                    self.database.create_thread(thread_id=thread_id, title=query[:50])
                    self.database.add_human_message(
                        thread_id=thread_id,
                        message_id=message_id,
                        content=query
                    )
                except Exception:
                    pass  # DB storage is best-effort

            if query.lower() in {"bye", "exit"}:
                print("Exiting the world... :(")
                break

            if not self.graph:
                print("❌ LLM not available. Please check your configuration.")
                continue

            # Build the input state
            if first_chat:
                first_chat = False
                input_state = {
                    "query": query,
                    "messages": [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=query)
                    ],
                    "type": ""
                }
            else:
                input_state = {
                    "query": query,
                    "messages": [HumanMessage(content=query)],
                    "type": ""
                }

            # Invoke the graph
            try:
                output = self.graph.invoke(input_state, config)

                # Extract the AI response from the output
                messages = output.get("messages", [])
                if messages:
                    # Get the last non-human message
                    for msg in reversed(messages):
                        if hasattr(msg, 'type') and msg.type != 'human':
                            print(f"\n🤖 Anonymous Coder: {msg.content}")
                            # Store AI response in DB
                            if self.database:
                                try:
                                    ai_message_id = str(uuid4())
                                    self.database.add_ai_message(
                                        thread_id=thread_id,
                                        message_id=ai_message_id,
                                        content=str(msg.content)
                                    )
                                except Exception:
                                    pass
                            break
                    else:
                        print("\n🤖 Anonymous Coder: Task completed.")
                else:
                    print("\n🤖 Anonymous Coder: Task completed.")

            except Exception as e:
                print(f"\n❌ Error: {e}")

        print("=" * 60)