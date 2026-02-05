"""Integration tests for LLM functionality using environment variables."""

import os
import unittest
import sys
from unittest.mock import patch

# Add source directory to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.config import Config
from src.llm.providers import LLMProvider
from src.core.prompt_manager import prompt_manager, PromptTemplate


class TestLLMIntegration(unittest.TestCase):
    """Integration tests for LLM functionality with real API keys."""

    def setUp(self):
        """Set up test fixtures using environment variables."""
        self.config = Config()

        # Get API key from environment (as we now only support OpenAI)
        self.openai_api_key = os.getenv('OPENAI_API_KEY')

        # Only proceed with tests if API key is present
        if not self.openai_api_key:
            self.skipTest("OpenAI API key not found in environment for integration tests")

    @unittest.skipIf(not os.getenv('OPENAI_API_KEY'), "OpenAI API key not provided")
    def test_openai_system_user_messages(self):
        """Test OpenAI API with both system and user messages."""
        # Initialize provider with config that includes API key
        self.config.openai_api_key = os.getenv('OPENAI_API_KEY')
        provider = LLMProvider(self.config)

        # Test with simple prompts
        system_msg = "You are a helpful assistant that answers in JSON format."
        user_msg = "What is 2+2? Respond in JSON form with an 'answer' field."

        response = self.run_async(provider.call_with_system_user(
            system_msg,
            user_msg,
            getattr(self.config, 'writer_model', 'gpt-3.5-turbo')
        ))

        # Validate response
        self.assertTrue(response, "Should receive a response from OpenAI API")
        self.assertTrue(len(response.strip()) > 0, "Response should not be empty")

        print(f"OpenAI response: {response}")
        # Store this response for future mock usage (simulating the requirement's intent)
        if '"' in response:
            # Verify it's valid JSON with answer key
            assert '"answer"' in response.lower(), f"Expected JSON with answer field, got: {response}"

    def run_async(self, coro):
        """Helper to run async functions syncronously for testing."""
        import asyncio
        return asyncio.run(coro)


class TestPromptManagerWithRealFiles(unittest.TestCase):
    """Test prompt manager with real prompt files."""

    def test_prompt_loading_from_real_files(self):
        """Test that prompt manager can load prompts from real files."""
        # Test if the prompt files exist as specified in requirements
        import os
        prompts_dir = "./prompts" if os.path.exists("./prompts") else os.path.join("..", "prompts")

        if not os.path.exists(prompts_dir):
            self.skipTest(f"Prompts directory {prompts_dir} not found")

        # Try to read the Writer prompt file
        template = prompt_manager.get_prompt_template("writer")

        self.assertIsInstance(template, PromptTemplate)
        self.assertIsInstance(template.system_prompt, str)
        self.assertIsInstance(template.user_prompt, str)

        # Verify the prompts were actually read from files
        self.assertIn("writer", template.system_prompt.lower() + template.user_prompt.lower() or "writing", "Should contain writing-related content")