from typing import List, Literal, Optional

from langchain_core.messages import BaseMessage
from pydantic import BaseModel


class AppState(BaseModel):
    query:str
    messages: List[BaseMessage]
    type: Optional[Literal["execution_node","scaffolding_node"]]

class TypeOutput(BaseModel):
    """Type of query"""
    type_of_query: Literal["execution_node", "scaffolding_node", "scaffolding_node"]

class Framework(BaseModel):
    framework:Literal['NONE']