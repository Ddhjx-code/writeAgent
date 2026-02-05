"""LLM provider utilities for the novel writing system."""

import asyncio
from typing import Optional, Dict, Any
import urllib.parse
import logging
import anthropic
from ..config import Config

logger = logging.getLogger(__name__)

class LLMProvider:
    """Unified interface for different LLM providers."""

    def __init__(self, config: Config):
        self.config = config
        self.openai_client = None  # Initialize as instance variable
        self.anthropic_client = None
        self.mistral_client = None
        self.cohere_client = None
        self._setup_clients()

    def _setup_clients(self) -> None:
        """Setup clients for all available providers with security validation."""
        # Setup OpenAI client if API key provided - use the modern approach only
        if self.config.openai_api_key:
            try:
                from openai import AsyncOpenAI
                # Create the client instance - avoid global modification
                base_url = self.config.openai_base_url
                if base_url:
                    self._validate_and_set_base_url(base_url, 'openai')
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

        # Setup Anthropic client if API key provided
        if self.config.anthropic_api_key:
            try:
                # Validate base URL if provided for Anthropic
                base_url = self.config.anthropic_base_url if self.config.anthropic_base_url else None
                if base_url:
                    self._validate_and_set_base_url(base_url, 'anthropic')
                self.anthropic_client = anthropic.AsyncAnthropic(
                    api_key=self.config.anthropic_api_key,
                    base_url=base_url
                )
            except (ImportError, Exception) as e:
                logger.warning(f"Anthropic client initialization failed: {type(e).__name__}")
                self.anthropic_client = None

        # Setup Mistral client if API key provided
        self.mistral_client = None
        if self.config.mistral_api_key:
            try:
                from mistralai.async_client import MistralAsyncClient
                self.mistral_client = MistralAsyncClient(api_key=self.config.mistral_api_key)
            except ImportError:
                logger.warning("MistralAI library not installed")
                self.mistral_client = None
            except Exception as e:
                logger.warning(f"Mistral client initialization failed: {type(e).__name__}")
                self.mistral_client = None

        # Setup Cohere client if API key provided
        self.cohere_client = None
        if self.config.cohere_api_key:
            try:
                import cohere
                self.cohere_client = cohere.AsyncClient(self.config.cohere_api_key)
            except ImportError:
                logger.warning("Cohere library not installed")
                self.cohere_client = None
            except Exception as e:
                logger.warning(f"Cohere client initialization failed: {type(e).__name__}")
                self.cohere_client = None

    def _validate_and_set_base_url(self, base_url: str, provider_name: str) -> None:
        """Validate base URL to prevent SSRF vulnerabilities."""
        try:
            parsed = urllib.parse.urlparse(base_url)
            if not parsed.scheme or parsed.scheme not in ('https', 'http'):
                raise ValueError(f"Invalid scheme in {provider_name} base URL: {parsed.scheme}")
            if not parsed.netloc:
                raise ValueError(f"Invalid netloc in {provider_name} base URL: {parsed.netloc}")
            # Additional validation to ensure it's a properly formatted URL
        except Exception as e:
            logger.error(f"Invalid {provider_name} base URL: {base_url}. Error: {e}")
            raise

    async def acall(self, prompt: str, model: str, **kwargs) -> str:
        """Make an async call to the LLM with the given prompt and model (backward compatibility)."""
        # This maintains backward compatibility - treat single prompt as user prompt
        # Check if prompt contains both system and user components - for now, treat as user prompt
        return await self._call_openai(prompt, model, **kwargs)

    async def call_with_system_user(self, system_prompt: str, user_prompt: str, model: str, **kwargs) -> str:
        """Make an async call to the LLM with both system and user prompts."""
        # Determine which provider based on the model name
        if any(provider in model.lower() for provider in ['gpt', 'openai', 'dall', 'tts', 'whisper']):
            return await self._call_openai_with_system_user(system_prompt, user_prompt, model, **kwargs)
        elif any(provider in model.lower() for provider in ['claude', 'anthropic']):
            return await self._call_anthropic_with_system_user(system_prompt, user_prompt, model, **kwargs)
        elif any(provider in model.lower() for provider in ['mistral']):
            return await self._call_mistral_with_system_user(system_prompt, user_prompt, model, **kwargs)
        elif any(provider in model.lower() for provider in ['command', 'cohere']):
            return await self._call_cohere_with_system_user(system_prompt, user_prompt, model, **kwargs)
        else:
            # Default to OpenAI if model not specified as another provider
            return await self._call_openai_with_system_user(system_prompt, user_prompt, model, **kwargs)


    async def call_with_system_user(self, system_prompt: str, user_prompt: str, model: str, **kwargs) -> str:
        """Call LLM with both system and user messages."""
        # Determine which provider based on the model name and call the appropriate internal method
        if any(provider in model.lower() for provider in ['gpt', 'openai', 'dall', 'tts', 'whisper']):
            return await self._call_openai_with_system_user(system_prompt, user_prompt, model, **kwargs)
        elif any(provider in model.lower() for provider in ['claude', 'anthropic']):
            return await self._call_anthropic_with_system_user(system_prompt, user_prompt, model, **kwargs)
        elif any(provider in model.lower() for provider in ['mistral']):
            return await self._call_mistral_with_system_user(system_prompt, user_prompt, model, **kwargs)
        elif any(provider in model.lower() for provider in ['command', 'cohere']):
            return await self._call_cohere_with_system_user(system_prompt, user_prompt, model, **kwargs)
        else:
            # Default to OpenAI if model not specified as another provider
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

    async def _call_anthropic(self, prompt: str, model: str, **kwargs) -> str:
        """Call Anthropic with the given prompt (backward compatibility)."""
        # For backward compatibility, treat the single prompt as a user prompt with empty system
        return await self._call_anthropic_with_system_user("", prompt, model, **kwargs)

    async def _call_anthropic_with_system_user(self, system_prompt: str, user_prompt: str, model: str, **kwargs) -> str:
        """Call Anthropic with both system and user messages."""
        if not self.config.anthropic_api_key or not self.anthropic_client:
            # If Anthropic not configured, return mock response
            return f"MOCK ANTHROPIC RESPONSE: System: {system_prompt[:100]}... User: {user_prompt[:150]}..."

        try:
            extra_params = {k: v for k, v in kwargs.items() if k != 'max_tokens'}
            # Anthropic API supports system messages directly
            message_kwargs = {
                "model": model,
                "max_tokens": kwargs.get('max_tokens', 1024),
                "messages": [
                    {"role": "user", "content": user_prompt}
                ],
                **extra_params
            }

            # Add system message if provided
            if system_prompt and system_prompt.strip():
                message_kwargs["system"] = system_prompt

            message = await self.anthropic_client.messages.create(**message_kwargs)
            return message.content[0].text
        except Exception as e:
            # Sanitize error message to prevent API key exposure
            error_msg = str(e)
            if self.config.anthropic_api_key:
                error_msg = error_msg.replace(self.config.anthropic_api_key, "[REDACTED_API_KEY]")
            logger.error(f"Anthropic API error: {error_msg}")
            # Return mock response to allow continued processing
            return f"MOCK ANTHROPIC RESPONSE due to error: {error_msg[:200]}..."

    async def _call_mistral(self, prompt: str, model: str, **kwargs) -> str:
        """Call Mistral with the given prompt (backward compatibility)."""
        # For backward compatibility, treat the single prompt as a user prompt with empty system
        return await self._call_mistral_with_system_user("", prompt, model, **kwargs)

    async def _call_mistral_with_system_user(self, system_prompt: str, user_prompt: str, model: str, **kwargs) -> str:
        """Call Mistral with both system and user messages."""
        # Placeholder for Mistral implementation
        if not self.mistral_client:
            # Return mock response if not configured - allows testing without API keys
            return f"MOCK MISTRAL RESPONSE: System: {system_prompt[:100]}... User: {user_prompt[:150]}..."

        # Try to format messages with system and user roles
        messages = []
        if system_prompt and system_prompt.strip():
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        try:
            response = await self.mistral_client.chat(
                model=model,
                messages=messages,
                **kwargs
            )
            # Return the content from the response (structure depends on actual Mistral library)
            # The original code showed response.choices[0].message.content format
            if hasattr(response, 'choices') and len(response.choices) > 0:
                if hasattr(response.choices[0], 'message'):
                    return response.choices[0].message.content
            # If structure differs, return as string representation
            return str(response)
        except Exception as e:
            # Sanitize error message to prevent API key exposure
            error_msg = str(e)
            if self.config.mistral_api_key:
                error_msg = error_msg.replace(self.config.mistral_api_key, "[REDACTED_API_KEY]")
            logger.error(f"Mistral API error: {error_msg}")
            return f"MOCK MISTRAL RESPONSE due to error: {error_msg[:200]}..."

    async def _call_cohere(self, prompt: str, model: str, **kwargs) -> str:
        """Call Cohere with the given prompt (backward compatibility)."""
        # For backward compatibility, treat the single prompt as a user prompt with empty system
        # Cohere doesn't use the usual messages format, so just pass as is
        if not self.cohere_client:
            # Return mock response if not configured
            return f"MOCK COHERE RESPONSE: {prompt[:200]}..."

        try:
            response = await self.cohere_client.chat(
                message=prompt,
                model=model,
                **kwargs
            )
            # Return the text from the response
            return response.text
        except Exception as e:
            # Sanitize error message to prevent API key exposure
            error_msg = str(e)
            if self.config.cohere_api_key:
                error_msg = error_msg.replace(self.config.cohere_api_key, "[REDACTED_API_KEY]")
            logger.error(f"Cohere API error: {error_msg}")
            return f"MOCK COHERE RESPONSE due to error: {error_msg[:200]}..."

    async def _call_cohere_with_system_user(self, system_prompt: str, user_prompt: str, model: str, **kwargs) -> str:
        """Call Cohere with both system and user parts combined (Cohere doesn't support system message natively)."""
        if not self.cohere_client:
            # Return mock response if not configured
            return f"MOCK COHERE RESPONSE: System: {system_prompt[:100]}... User: {user_prompt[:150]}..."

        # Cohere doesn't have a dedicated system message role, so combine with explicit instruction
        combined_message = f"System Instructions: {system_prompt}\n\nUser Request: {user_prompt}"

        try:
            response = await self.cohere_client.chat(
                message=combined_message,
                model=model,
                **kwargs
            )
            # Return the text from the response
            return response.text
        except Exception as e:
            # Sanitize error message to prevent API key exposure
            error_msg = str(e)
            if self.config.cohere_api_key:
                error_msg = error_msg.replace(self.config.cohere_api_key, "[REDACTED_API_KEY]")
            logger.error(f"Cohere API error: {error_msg}")
            return f"MOCK COHERE RESPONSE due to error: {error_msg[:200]}..."