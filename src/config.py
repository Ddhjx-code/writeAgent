import os
from typing import Optional


class Config:
    """Configuration management for the novel writing system."""

    def __init__(self):
        # API Keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.mistral_api_key = os.getenv("MISTRAL_API_KEY")
        self.cohere_api_key = os.getenv("COHERE_API_KEY")

        # Model settings
        self.default_writer_model = os.getenv("WRITER_MODEL", "gpt-4")
        self.default_editor_model = os.getenv("EDITOR_MODEL", "gpt-4")
        self.default_planner_model = os.getenv("PLANNER_MODEL", "gpt-4")

        # Database settings
        self.chroma_persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")
        self.llamaindex_storage_dir = os.getenv("LLAMAINDEX_STORAGE_DIR", "./llamaindex_storage")

        # System settings
        self.max_iterations = int(os.getenv("MAX_ITERATIONS", "10"))
        self.max_retry_attempts = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))