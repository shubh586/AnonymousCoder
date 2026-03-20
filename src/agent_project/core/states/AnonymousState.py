from typing import Annotated, List
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AnonymousState(TypedDict):
    """State schema for the AnonymousCoder LangGraph agent."""
    query: str
    messages: Annotated[List[BaseMessage], add_messages]
    type: str