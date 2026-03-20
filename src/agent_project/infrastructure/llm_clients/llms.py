import os
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, SecretStr, field_validator


class ModelProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    GOOGLE = "google"
    OLLAMA = "ollama"
    GROQ = "groq"


class ModelParameters(BaseModel):
    """Unified model parameters with validation."""
    # Optional just makes it possible to make the fields None even if there is a default when instantiating a Class
    max_retries: Optional[int] = Field(default=3, ge=1, le=10, description="Number of retries for the model if error occurs")
    max_tokens: Optional[int] = Field(default=4096, ge=1, le=1000000, description="Number of output tokens")
    temperature: float = Field(default=0.0, ge=0.0, le=2.0, description="The temperature of the model")
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Top-p sampling parameter")
    top_k: Optional[int] = Field(default=None, ge=1, le=100, description="Top-k sampling parameter")

class LLMConfig(BaseModel):
    """Configuration for LLM instances."""
    provider: ModelProvider
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    # this avoids sahring of the same instance of the class for each LLM instance
    # else with parameters=ModelParameters() it will share the same instance of the class for each LLM instance
    parameters: ModelParameters = Field(default_factory=ModelParameters)

    @field_validator('api_key',mode='before')
    def validate_api_key(cls,v):
        if v is None:
            raise ValueError("API key is required")
        return v

class BaseLLM(ABC):
    """Abstract class for creating LLM instances."""
    
    @abstractmethod
    def create_llm(self, config: LLMConfig) -> BaseChatModel:
        """Create an LLM instance based on configuration."""

class OpenAILLM(BaseLLM):
    
    def create_llm(self, config: LLMConfig) -> BaseChatModel:
        if not config.api_key:
            raise ValueError("OpenAI API key is required")
        
        api_key = config.api_key

        return ChatOpenAI(
            model=config.model_name,
            api_key=SecretStr(api_key),
            base_url=config.base_url,
            max_completion_tokens=config.parameters.max_tokens,
            temperature=config.parameters.temperature,
            top_p=config.parameters.top_p,
            max_retries=config.parameters.max_retries
        )

class GroqLLM(BaseLLM):
    def create_llm(self, config: LLMConfig) -> BaseChatModel:
        
        if not config.api_key and not os.getenv("GROQ_API_KEY"):
            raise ValueError("Groqq API key is required")
        
        api_key=config.api_key 
        return ChatGroq(
            model=config.model_name,
            api_key=SecretStr(str(api_key)),
            max_tokens=config.parameters.max_tokens,
        )    
        
class GoogleLLM(BaseLLM):
    
    def create_llm(self, config: LLMConfig) -> BaseChatModel:
        if not config.api_key and not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("Google API key is required")
        
        api_key = config.api_key or os.getenv("GOOGLE_API_KEY")
        
        return ChatGoogleGenerativeAI(
            model=config.model_name,
            google_api_key=api_key,
            max_output_tokens=config.parameters.max_tokens,
            temperature=config.parameters.temperature,
            top_p=config.parameters.top_p,
            top_k=config.parameters.top_k,
            max_retries=config.parameters.max_retries
        )


class OllamaLLM(BaseLLM):
    def create_llm(self, config: LLMConfig) -> BaseChatModel:
        base_url = config.base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        return ChatOllama(
            model=config.model_name,
            base_url=base_url,
            temperature=config.parameters.temperature,
            top_p=config.parameters.top_p,
            top_k=config.parameters.top_k,
            num_predict=config.parameters.max_tokens
        )

model_dict={
    ModelProvider.GOOGLE:GoogleLLM,
    ModelProvider.GROQ:GroqLLM,
    ModelProvider.OLLAMA:OllamaLLM,
    ModelProvider.OPENAI:OpenAILLM,
}
    
def get_llm(llmConfig: LLMConfig) -> BaseChatModel:
    llm_class = model_dict.get(llmConfig.provider)
    if not llm_class:
        raise ValueError(f"Unsupported provider: {llmConfig.provider}")
    return llm_class().create_llm(llmConfig)
