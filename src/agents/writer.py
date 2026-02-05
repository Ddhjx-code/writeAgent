from typing import Dict, Any, List
import asyncio
from ..novel_types import AgentResponse
from ..config import Config
from .base import BaseAgent
from ..core.prompt_manager import prompt_manager, PromptTemplate


class WriterAgent(BaseAgent):
    """Writer agent that generates narrative content based on the story state."""

    def __init__(self, config: Config):
        super().__init__("writer", config)

    async def process(self, state: Dict[str, Any]) -> AgentResponse:
        """Write narrative content based on the current story state."""
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                # Build context for the writer
                context = self._build_context(state)

                # Get the prompt template with system and user messages
                prompt_template = prompt_manager.get_prompt_template(self.name)

                # Format the user prompt with context
                formatted_user_prompt = prompt_template.user_prompt.format(
                    title=state.get('title', 'Untitled'),
                    context=context,
                    chapter_outline=state.get('outline', {}).get('current_chapter_outline', ''),
                    world_building=state.get('world_details', {}),
                    characters=state.get('characters', {}),
                    current_content=state.get('current_chapter', ''),
                    previous_content=state.get('chapters', [])[-1]['content'] if state.get('chapters') else ''
                ) if prompt_template.user_prompt else f"Story: {state.get('title', 'Untitled')}. Context: {context}. Continue writing."

                # Format the system prompt with context
                formatted_system_prompt = prompt_template.system_prompt
                if '{' in formatted_system_prompt and '}' in formatted_system_prompt:
                    # If system prompt has placeholders, format them too
                    formatted_system_prompt = formatted_system_prompt.format(
                        title=state.get('title', 'Untitled'),
                        context=context,
                        world_building=state.get('world_details', {}),
                        characters=state.get('characters', {}),
                    )

                # Call the actual LLM with both system and user prompts
                response_content = await self.llm.call_with_system_user(
                    formatted_system_prompt,
                    formatted_user_prompt,
                    self.config.default_writer_model
                )

                # Validate response format/content - check if we got a reasonable response
                # If the content looks like error or MOCK response, try again
                if response_content and ("MOCK" not in response_content or "ERROR" not in response_content) and len(response_content.strip()) > 10:
                    return AgentResponse(
                        agent_name=self.name,
                        content=response_content,
                        reasoning="Generated narrative content based on story context, outline, character relationships, and world-building elements",
                        suggestions=[
                            "Consider adjusting tone for more dramatic effect",
                            "Could expand on character motivations",
                            "The setting details might need more clarity"
                        ],
                        status="success"
                    )
                else:
                    # If response is invalid, increase retry count and continue
                    retry_count += 1
                    if retry_count >= max_retries:
                        return AgentResponse(
                            agent_name=self.name,
                            content="",
                            reasoning=f"Failed to get valid response from LLM after {max_retries} attempts.",
                            status="failed"
                        )
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    return AgentResponse(
                        agent_name=self.name,
                        content="",
                        reasoning=f"Error in WriterAgent processing after {max_retries} attempts: {str(e)}",
                        status="failed"
                    )

        return AgentResponse(
            agent_name=self.name,
            content="",
            reasoning=f"Failed to generate content after {max_retries} retries",
            status="failed"
        )

    def get_prompt(self) -> str:
        """Return the old-style prompt for backward compatibility."""
        # Delegate to prompt_manager to load from external file
        template = prompt_manager.get_prompt_template(self.name)
        # Combine system and user prompts for backward compatibility
        if template.user_prompt:
            return f"{template.system_prompt}\n\n{template.user_prompt}"
        else:
            return template.system_prompt