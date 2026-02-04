"""LLM module for the novel writing system."""

from .providers import LLMProvider
from .embeddings import OllamaEmbeddingProvider

__all__ = ['LLMProvider', 'OllamaEmbeddingProvider']