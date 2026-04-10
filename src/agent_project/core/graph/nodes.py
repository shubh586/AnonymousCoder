from typing import List, Literal

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel

from ..prompts.system_prompt import (get_context_injection_prompt,
                                     get_execution_prompt, get_memory_prompt,
                                     get_summarization_prompt,
                                     get_understanding_prompt)
from ..states.AnonymousState import AnonymousState
from ..tools import FILE_SYS_TOOLS
from ..tools.vector_database_tools import VECTOR_STORE_TOOLS, similarity_search


class TypeOutput(BaseModel):
    """Structured output for query classification."""
    type_of_query: Literal['execution_node', 'scaffolding_node']


def get_memory_node(llm: BaseChatModel):
    def memory_node(state: AnonymousState):
        # Get the current user query
        query: str = state["query"]
        try:
            # Skip memory operations if vector store is not available
            from ...infrastructure.databases.vector_database import get_vector_store
            try:
                get_vector_store()
            except RuntimeError:
                # Vector store not initialized — skip memory entirely
                return {"query": query}

            MEMORY_SYSTEM_PROMPT: str = get_memory_prompt()
            CONTEXT_INJECT_PROMPT: str = get_context_injection_prompt()

            # Step 1: Memory update agent — checks if query has memory-worthy info
            try:
                agent = create_react_agent(
                    model=llm,
                    tools=VECTOR_STORE_TOOLS,
                    prompt=MEMORY_SYSTEM_PROMPT,
                    version="v1",
                )
                agent.invoke({"messages": [HumanMessage(content=query)]})
            except Exception:
                pass  # best-effort

            # Step 2: Context injection agent — retrieves relevant memories
            enriched_query = query
            try:
                agent = create_react_agent(
                    model=llm,
                    tools=[similarity_search],
                    prompt=CONTEXT_INJECT_PROMPT,
                    version="v1",
                )
                output = agent.invoke({"messages": [HumanMessage(content=query)]})

                # Append retrieved context to the query
                ai_messages = [m for m in output.get("messages", []) if hasattr(m, "content")]
                if ai_messages:
                    last_response = ai_messages[-1].content
                    if last_response and last_response.strip():
                        enriched_query = f"{query}\n\n[Retrieved Context]:\n{last_response}"
            except Exception:
                pass  # best-effort

            return {"query": enriched_query}
        except Exception:
            # Never fail the whole graph because memory enrichment is flaky.
            return {"query": query}

    return memory_node


def get_summarization_node(llm: BaseChatModel):
    def summarization_node(state: AnonymousState):
        messages = list(state["messages"])
        SUMMARIZATION_PROMPT: str = get_summarization_prompt()

        if len(messages) >= 4 and isinstance(messages[3], SystemMessage):
            # Discard very old summaries
            del messages[1:3]
        elif len(messages) >= 8:
            # Create summaries of older messages
            messages_to_summarize: List[BaseMessage] = [SystemMessage(content=SUMMARIZATION_PROMPT)] + messages[1:9]
            result = llm.invoke(messages_to_summarize)
            messages[1:9] = [SystemMessage(content=result.content)]

        return {
            "messages": messages
        }
    return summarization_node


def get_understanding_node(llm: BaseChatModel):
    def understanding_node(state: AnonymousState):
        query = state["query"]
        # Avoid strict tool-based structured output (some providers error if a tool
        # isn't called). This is a lightweight classifier that's "good enough".
        q = (query or "").lower()
        project_like = any(
            k in q
            for k in (
                "scaffold",
                "scaffolding",
                "create a new project",
                "from scratch",
                "project structure",
                "new project",
                "setup",
                "initialize project",
                "build a new project",
            )
        )

        return {"type": "scaffolding_node" if project_like else "execution_node"}
    return understanding_node


def get_execution_node(llm: BaseChatModel):
    def execution_node(state: AnonymousState):
        query = state["query"]
        messages = state["messages"]
        EXECUTION_SYSTEM_PROMPT: str = get_execution_prompt()
        try:
            agent = create_react_agent(
                model=llm,
                tools=FILE_SYS_TOOLS,
                prompt=EXECUTION_SYSTEM_PROMPT,
                version="v1",
            )

            # Invoke the ReAct agent with full message history + current query
            input_messages = list(messages) + [HumanMessage(content=query)]
            output = agent.invoke({"messages": input_messages})

            # Extract the final AI response
            ai_messages = [
                m
                for m in output.get("messages", [])
                if hasattr(m, "type") and m.type == "ai" and getattr(m, "content", None)
            ]
            response_content = ai_messages[-1].content if ai_messages else "Task completed."

            return {"messages": [AIMessage(content=response_content)]}
        except Exception as e:
            # If tool calling fails, don't crash the graph.
            return {"messages": [AIMessage(content=f"❌ Error: {e}")]}
    return execution_node


def get_scaffolding_node(llm: BaseChatModel):
    def scaffolding_node(state: AnonymousState):
        query = state["query"]
        messages = state["messages"]

        # Scaffolding uses the same execution agent but with a project-creation focus
        try:
            agent = create_react_agent(
                model=llm,
                tools=FILE_SYS_TOOLS,
                prompt=(
                    "You are a project scaffolding assistant. The user wants to create "
                    "a new project from scratch. Use the available file system tools to "
                    "create the project structure, configuration files, and boilerplate code. "
                    "Ask clarifying questions if the framework or stack is not clear."
                ),
                version="v1",
            )

            input_messages = list(messages) + [HumanMessage(content=query)]
            output = agent.invoke({"messages": input_messages})

            ai_messages = [
                m
                for m in output.get("messages", [])
                if hasattr(m, "type") and m.type == "ai" and getattr(m, "content", None)
            ]
            response_content = (
                ai_messages[-1].content if ai_messages else "Project scaffolding complete."
            )

            return {"messages": [AIMessage(content=response_content)]}
        except Exception as e:
            return {"messages": [AIMessage(content=f"❌ Error: {e}")]}
    return scaffolding_node