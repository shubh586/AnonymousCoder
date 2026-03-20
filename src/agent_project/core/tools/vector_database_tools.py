from typing import List

from langchain.tools import tool

from ...infrastructure.databases.vector_database import get_vector_store


@tool
def add_texts(texts: List[str]) -> str:
    """
    Add texts to the Qdrant vector store.
    
    Args:
        texts: List of text strings to add to the vector store
        
    Returns:
        Success message with count of added texts or error message
    """
    try:
        vector_store = get_vector_store()
        return vector_store.add_texts(texts)
    except Exception as e:
        return f"❌ Error: {e}"


@tool
def similarity_search(text: str, k: int = 2) -> str:
    """
    Search for similar texts in the vector store.
    
    Args:
        text: The text to search for similar matches
        k: Number of similar texts to return (default: 2)
        
    Returns:
        List of similar texts with their IDs or error message
    """
    try:
        vector_store = get_vector_store()
        return vector_store.similarity_search(text, k)
    except Exception as e:
        return f"❌ Error: {e}"


@tool
def update_text(point_id: str, new_text: str) -> str:
    """
    Update an existing text in the vector store.
    
    Args:
        point_id: The ID of the point to update
        new_text: The new text content
        
    Returns:
        Success message or error message
    """
    try:
        vector_store = get_vector_store()
        return vector_store.update_text(point_id, new_text)
    except Exception as e:
        return f"❌ Error: {e}"


@tool
def delete_text(point_id: str) -> str:
    """
    Delete a text from the vector store.
    
    Args:
        point_id: The ID of the point to delete
        
    Returns:
        Success message or error message
    """
    try:
        vector_store = get_vector_store()
        return vector_store.delete_text(point_id)
    except Exception as e:
        return f"❌ Error: {e}"