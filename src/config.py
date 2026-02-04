import os
from typing import Optional


class Config:
    """Configuration management for the novel writing system."""

    def __init__(self) -> None:
        # API Keys
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
        self.mistral_api_key: Optional[str] = os.getenv("MISTRAL_API_KEY")
        self.cohere_api_key: Optional[str] = os.getenv("COHERE_API_KEY")

        # API Base URLs
        self.openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")  # Default to OpenAI
        self.anthropic_base_url: str = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")  # Default to Anthropic
        self.mistral_base_url: str = os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai/v1")  # Default to Mistral
        self.cohere_base_url: str = os.getenv("COHERE_BASE_URL", "https://api.cohere.ai/v1")  # Default to Cohere

        # Model settings
        self.default_writer_model: str = os.getenv("WRITER_MODEL", "gpt-4")
        self.default_editor_model: str = os.getenv("EDITOR_MODEL", "gpt-4")
        self.default_planner_model: str = os.getenv("PLANNER_MODEL", "gpt-4")

        # Embedding model settings
        self.embedding_model: str = os.getenv("EMBEDDING_MODEL", "qwen3-embedding")  # Default to user's specified model

        # Database settings
        self.chroma_persist_dir: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")
        self.llamaindex_storage_dir: str = os.getenv("LLAMAINDEX_STORAGE_DIR", "./llamaindex_storage")

        # System settings
        self.max_iterations: int = int(os.getenv("MAX_ITERATIONS", "10"))
        self.max_retry_attempts: int = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))