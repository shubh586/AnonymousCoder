from typing import List
from uuid import uuid4

from langchain_core.embeddings import Embeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

_instance = None

class QdrantVectorStore:
    _instance = None
    collection_name = "app_collection"
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, host: str, api_key: str, embeddings: Embeddings) -> None:
        if not hasattr(self, "_initialized"):
            self.client = QdrantClient(url=host, api_key=api_key)
            self.embeddings = embeddings
            self._initialized = True
            
            # Initialize collection with sample embedding to get dimension
            sample_embedding = self.embeddings.embed_query("sample text")
            self._post_init(len(sample_embedding))
    
    def _post_init(self, size: int):
        if not self.client.collection_exists(collection_name=self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=size, distance=Distance.COSINE)
            )
    
    def add_texts(self, texts: List[str]):
        if not texts:
            return "No texts provided"
            
        encoded: List[tuple] = []
        for text in texts:
            embedding = self.embeddings.embed_query(text)
            encoded.append((text, embedding))
        
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=str(uuid4()),
                        vector=embedding,
                        payload={"text": text}
                    )
                    for text, embedding in encoded
                ]
            )
            return f"Successfully added {len(texts)} new memories"
        except Exception as e:
            return f"Error occurred while adding texts: {e}"
    
    def similarity_search(self, text: str, k: int = 2):
        if not text:
            return "No search text provided"
            
        try:
            encoded: List[float] = self.embeddings.embed_query(text)
            hits = self.client.search(
                collection_name=self.collection_name,
                query_vector=encoded,
                limit=k
            )
            
            if not hits:
                return "No similar texts found"
                
            output = []
            for hit in hits:
                output.append(f"ID: {hit.id}, Text: {hit.payload.get('text')}")
            return "\n".join(output)
        except Exception as e:
            return f"Error occurred during similarity search: {e}"

    def update_text(self, point_id: str, new_text: str):
        if not point_id or not new_text:
            return "Point ID and new text are required"
            
        try:
            new_embedding = self.embeddings.embed_query(new_text)
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=new_embedding,
                        payload={"text": new_text}
                    )
                ]
            )
            return f"Point {point_id} updated successfully"
        except Exception as e:
            return f"Error updating point {point_id}: {e}"

    def delete_text(self, point_id: str):
        if not point_id:
            return "Point ID is required"
            
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[point_id]
            )
            return f"Point {point_id} deleted successfully"
        except Exception as e:
            return f"Error deleting point {point_id}: {e}"


def initialize_vector_store(host: str, api_key: str, embeddings: Embeddings, collection_name: str = "app_collection"):
    """Initialize the vector store singleton instance."""
    global _instance
    _instance = QdrantVectorStore(host=host, api_key=api_key, embeddings=embeddings)
    if collection_name != "app_collection":
        _instance.collection_name = collection_name
        # Re-initialize collection with new name if needed
        sample_embedding = _instance.embeddings.embed_query("sample text")
        _instance._post_init(len(sample_embedding))
    return _instance


def get_vector_store():
    """Get the initialized vector store instance."""
    global _instance
    if _instance is None:
        raise RuntimeError("Vector store not initialized. Call initialize_vector_store() first.")
    return _instance