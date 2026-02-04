"""Ollama embedding utilities for the novel writing system."""

import os
import logging
from typing import List, Union
import ollama
from ..config import Config

class OllamaEmbeddingProvider:
    """Ollama embedding provider for generating text embeddings."""

    def __init__(self, config: Config):
        self.config = config
        # Use the qwen3-embedding model as specified by user
        self.model = os.getenv("EMBEDDING_MODEL", "qwen3-embedding")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts using Ollama."""
        try:
            embeddings = []
            for text in texts:
                response = ollama.embed(
                    model=self.model,
                    input=text
                )
                embeddings.append(response['embeddings'][0] if response['embeddings'] else [])
            return embeddings
        except Exception as e:
            logging.error(f"Error generating embeddings with Ollama: {e}")
            # Return empty embeddings list in case of error
            return [[] for _ in texts]

    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query text."""
        try:
            response = ollama.embed(
                model=self.model,
                input=text
            )
            return response['embeddings'][0] if response['embeddings'] else []
        except Exception as e:
            logging.error(f"Error generating embedding with Ollama: {e}")
            return []