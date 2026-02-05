"""LLM provider utilities for the novel writing system."""

import asyncio
from typing import Optional, Dict, Any
import urllib.parse
import logging
from ..config import Config

logger = logging.getLogger(__name__)

class LLMProvider:
    """LLM provider for OpenAI only."""

    def __init__(self, config: Config):
        self.config = config
        self.openai_client = None  # Initialize as instance variable
        self._setup_client()

    def _setup_client(self) -> None:
        """Setup OpenAI client with security validation."""
        # Setup OpenAI client if API key provided - use the modern approach
        if self.config.openai_api_key:
            try:
                from openai import AsyncOpenAI
                # Create the client instance
                base_url = self.config.openai_base_url
                if base_url:
                    self._validate_and_set_base_url(base_url)
                self.openai_client = AsyncOpenAI(
                    api_key=self.config.openai_api_key,
                    base_url=base_url
                )
            except ImportError:
                logger.warning("OpenAI library not installed")
                self.openai_client = None
            except Exception as e:
                logger.warning(f"OpenAI client initialization failed: {type(e).__name__}")
                self.openai_client = None

    def _validate_and_set_base_url(self, base_url: str) -> None:
        """Validate base URL to prevent SSRF vulnerabilities."""
        try:
            parsed = urllib.parse.urlparse(base_url)
            if not parsed.scheme or parsed.scheme not in ('https', 'http'):
                raise ValueError(f"Invalid scheme in base URL: {parsed.scheme}")
            if not parsed.netloc:
                raise ValueError(f"Invalid netloc in base URL: {parsed.netloc}")
            # Additional validation to ensure it's a properly formatted URL
        except Exception as e:
            logger.error(f"Invalid base URL: {base_url}. Error: {e}")
            raise

    async def acall(self, prompt: str, model: str, **kwargs) -> str:
        """Make an async call to the LLM with the given prompt and model (backward compatibility)."""
        # This maintains backward compatibility - treat single prompt as user prompt
        # Check if prompt contains both system and user components - for now, treat as user prompt
        return await self._call_openai(prompt, model, **kwargs)

    async def call_with_system_user(self, system_prompt: str, user_prompt: str, model: str, **kwargs) -> str:
        """Make an async call to the LLM with both system and user prompts."""
        # OpenAI only implementation
        return await self._call_openai_with_system_user(system_prompt, user_prompt, model, **kwargs)

    async def _call_openai(self, prompt: str, model: str, **kwargs) -> str:
        """Call OpenAI with the given prompt (backward compatibility)."""
        # For backward compatibility, treat the single prompt as a user prompt with empty system
        return await self._call_openai_with_system_user("", prompt, model, **kwargs)

    async def _call_openai_with_system_user(self, system_prompt: str, user_prompt: str, model: str, **kwargs) -> str:
        """Call OpenAI with both system and user messages."""
        if not self.openai_client:
            # Return mock response if not configured
            return f"MOCK RESPONSE: System: {system_prompt[:100]}... User: {user_prompt[:150]}..."

        try:
            messages = []
            if system_prompt and system_prompt.strip():
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_prompt})

            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            # Sanitize error message to prevent API key exposure
            error_msg = str(e)
            if self.config.openai_api_key:
                error_msg = error_msg.replace(self.config.openai_api_key, "[REDACTED_API_KEY]")
            logger.error(f"OpenAI API error: {error_msg}")
            # Return mock response to allow continued processing
            return f"MOCK OPENAI RESPONSE due to error: {error_msg[:200]}..."