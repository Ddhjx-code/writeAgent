from typing import Dict, Any, List
import json
from ..novel_types import AgentResponse
from ..config import Config
from .base import BaseAgent
from ..core.prompt_manager import prompt_manager


class HumanizerAgent(BaseAgent):
    """Humanizer agent that removes AI writing traces to make text sound more natural and human."""

    def __init__(self, config: Config):
        super().__init__("humanizer", config)

    async def process(self, state: Dict[str, Any]) -> AgentResponse:
        """Remove AI writing traces to make content sound more natural and human."""
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                # Build context for the humanizer
                context = self._build_context(state)

                # Get the content to humanize
                content_to_humanize = state.get('current_chapter', '') or state.get('content', '')

                if not content_to_humanize:
                    return AgentResponse(
                        agent_name=self.name,
                        content="",
                        reasoning="No content provided to humanize",
                        status="success"
                    )

                # Get the prompt template
                prompt_template = prompt_manager.get_prompt_template(self.name)

                # Format the user prompt with content
                formatted_user_prompt = prompt_template.user_prompt.format(
                    original_content=content_to_humanize
                ) if prompt_template.user_prompt else f"Please humanize this content: {content_to_humanize}"

                # Format the system prompt with context
                formatted_system_prompt = prompt_template.system_prompt
                if '{' in formatted_system_prompt and '}' in formatted_system_prompt:
                    # If system prompt has placeholders, format them too
                    formatted_system_prompt = formatted_system_prompt.format(
                        original_content=content_to_humanize
                    )

                # Call the actual LLM with the formatted prompts
                response_content = await self.llm.call_with_system_user(
                    formatted_system_prompt,
                    formatted_user_prompt,
                    self.config.default_writer_model
                )

                # The response should be the humanized content
                # We can apply basic checks to see if AI traces were removed
                original_length = len(content_to_humanize)
                humanized_length = len(response_content)
                changes_summary = []

                if original_length > humanized_length:
                    changes_summary.append("Reduced excessive content")

                return AgentResponse(
                    agent_name=self.name,
                    content=response_content,
                    reasoning="Applied humanization techniques to remove AI writing patterns and make text sound more natural using LLM analysis",
                    suggestions=changes_summary + ["AI text humanization applied via LLM processing"],
                    status="success"
                )
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    return AgentResponse(
                        agent_name=self.name,
                        content="",
                        reasoning=f"Error in HumanizerAgent processing after {max_retries} attempts: {str(e)}",
                        status="failed"
                    )

        return AgentResponse(
            agent_name=self.name,
            content="",
            reasoning=f"Failed to generate humanized content after {max_retries} retries",
            status="failed"
        )

    def _humanize_text(self, original_text: str) -> str:
        """Apply humanization techniques to remove AI writing traces."""
        if not original_text or not isinstance(original_text, str):
            return original_text

        # Import here to avoid circular dependencies in the final system
        import re

        # This is a simplified implementation - in a real system, we would implement all the techniques from Humanizer-zh.md
        processed_text = original_text

        # Remove common AI fillers and patterns
        patterns_to_remove = [
            # Remove "As a professional writer..." introductions
            r"(As an? [^,]+,? )|(This is a professional )",
            # Remove AI sign-off phrases
            r"(Hope this helps!?)|(Please let me know if you need any modifications)",
            # Remove generic phrases
            r"(In today's world)|(In the current landscape)",
        ]

        for pattern in patterns_to_remove:
            processed_text = re.sub(pattern, "", processed_text, flags=re.IGNORECASE)
            processed_text.replace(r"\s+", " ").strip()  # Clean up spaces after removals

        # In a real implementation, we would apply all techniques from Humanizer-zh.md here
        return processed_text.strip()

    def _analyze_changes(self, original: str, humanized: str) -> List[str]:
        """Analyze what changes were made during humanization."""
        changes = []

        # Simple comparison for this implementation
        original_length = len(original)
        humanized_length = len(humanized)

        if original_length > humanized_length:
            changes.append("Reduced excessive content")

        # Check for specific AI patterns removal
        import re
        ai_intro_patterns = [
            r"(As an? [^,]+,? )",
            r"(In today's world)",
            r"(It is important to note)"
        ]

        for pattern in ai_intro_patterns:
            if re.search(pattern, original, re.IGNORECASE) and not re.search(pattern, humanized, re.IGNORECASE):
                changes.append("Removed AI introduction patterns")

        return changes

    def get_prompt(self) -> str:
        """Return the old-style prompt for backward compatibility."""
        # Delegate to prompt_manager to load from external file
        template = prompt_manager.get_prompt_template(self.name)
        # Combine system and user prompts for backward compatibility
        if template.user_prompt:
            return f"{template.system_prompt}\n\n{template.user_prompt}"
        else:
            return template.system_prompt