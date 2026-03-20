from typing import List

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from ..prompts.system_prompt import (get_execution_prompt, get_memory_prompt,
                                     get_plan_prompt, get_scaffolding_prompt,
                                     get_summarization_prompt,
                                     get_understanding_prompt)
from ..states.AppStates import AppState, TypeOutput
from ..tools import (FILE_SYS_TOOLS, MEMORY_TOOLS, POWERSHELL_TOOLS,
                     SHELL_TOOLS, ask_user_tool, get_framework_context)


class TypeOutput(BaseModel):
    """Structured output for query classification."""
    type_of_query: Literal['execution_node', 'scaffolding_node']


def get_memory_node(llm: BaseChatModel):
    def memory_node(state: AnonymousState):
        # Get the current user query
        query: str = state["query"]
        MEMORY_SYSTEM_PROMPT: str = get_memory_prompt()
        CONTEXT_INJECT_PROMPT: str = get_context_injection_prompt()

        # Step 1: Memory update agent — checks if query has memory-worthy info
        try:
            agent = create_react_agent(
                model=llm,
                tools=VECTOR_STORE_TOOLS,
                prompt=MEMORY_SYSTEM_PROMPT
            )
            agent.invoke({"messages": [HumanMessage(content=query)]})
        except Exception:
            pass  # Memory update is best-effort, don't block the pipeline

        # Step 2: Context injection agent — retrieves relevant memories
        enriched_query = query
        try:
            agent = create_react_agent(
                model=llm,
                tools=[similarity_search],
                prompt=CONTEXT_INJECT_PROMPT
            )
            output = agent.invoke({"messages": [HumanMessage(content=query)]})
            # Append retrieved context to the query
            ai_messages = [m for m in output.get("messages", []) if hasattr(m, 'content')]
            if ai_messages:
                last_response = ai_messages[-1].content
                if last_response and last_response.strip():
                    enriched_query = f"{query}\n\n[Retrieved Context]:\n{last_response}"
        except Exception:
            pass  # Context retrieval is best-effort

        return {
            "query": enriched_query,
        }
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
        messages = state["messages"]
        UNDERSTANDING_SYSTEM_PROMPT: str = get_understanding_prompt()

        # Build message list for classification
        classification_messages = messages + [
            SystemMessage(content=UNDERSTANDING_SYSTEM_PROMPT),
            HumanMessage(content=query)
        ]

        # Use structured output to classify the query
        understanding_chain = llm.with_structured_output(schema=TypeOutput)
        result = understanding_chain.invoke(classification_messages)

        return {
            "type": result.type_of_query,
        }

    return understanding_node


def get_execution_node(llm: BaseChatModel):
    def execution_node(state: AnonymousState):
        query = state["query"]
        messages = state["messages"]
        EXECUTION_SYSTEM_PROMPT: str = get_execution_prompt()

        agent = create_react_agent(
            model=llm,
            tools=FILE_SYS_TOOLS,
            prompt=EXECUTION_SYSTEM_PROMPT
        )

        # Invoke the ReAct agent with full message history + current query
        input_messages = list(messages) + [HumanMessage(content=query)]
        output = agent.invoke({"messages": input_messages})

        # Extract the final AI response
        ai_messages = [m for m in output.get("messages", []) if hasattr(m, 'type') and m.type == 'ai' and m.content]
        response_content = ai_messages[-1].content if ai_messages else "I completed the task."

        return {
            "messages": [SystemMessage(content=response_content)],
        }
    return execution_node


def get_scaffolding_node(llm: BaseChatModel):
    def scaffolding_node(state: AnonymousState):
        query = state["query"]
        messages = state["messages"]

        # Scaffolding uses the same execution agent but with a project-creation focus
        agent = create_react_agent(
            model=llm,
            tools=FILE_SYS_TOOLS,
            prompt=(
                "You are a project scaffolding assistant. The user wants to create "
                "a new project from scratch. Use the available file system tools to "
                "create the project structure, configuration files, and boilerplate code. "
                "Ask clarifying questions if the framework or stack is not clear."
            )
        )

        input_messages = list(messages) + [HumanMessage(content=query)]
        output = agent.invoke({"messages": input_messages})

        ai_messages = [m for m in output.get("messages", []) if hasattr(m, 'type') and m.type == 'ai' and m.content]
        response_content = ai_messages[-1].content if ai_messages else "Project scaffolding complete."

        return {
            "messages": [SystemMessage(content=response_content)],
        }
    return scaffolding_node