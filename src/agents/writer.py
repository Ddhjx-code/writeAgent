from typing import Dict, Any, List
import asyncio
from ..novel_types import AgentResponse
from ..config import Config
from .base import BaseAgent


class WriterAgent(BaseAgent):
    """Writer agent that generates narrative content based on the story state."""

    def __init__(self, config: Config):
        super().__init__("writer", config)

    async def process(self, state: Dict[str, Any]) -> AgentResponse:
        """Write narrative content based on the current story state."""
        try:
            # Build context for the writer
            context = self._build_context(state)

            # Get the prompt template
            prompt = self.get_prompt()

            # Format the prompt with context
            formatted_prompt = prompt.format(
                title=state.get('title', 'Untitled'),
                context=context,
                chapter_outline=state.get('outline', {}).get('current_chapter_outline', ''),
                world_building=state.get('world_details', {}),
                characters=state.get('characters', {}),
                current_content=state.get('current_chapter', ''),
                previous_content=state.get('chapters', [])[-1]['content'] if state.get('chapters') else ''
            )

            # For now, simulate content generation
            # In a real implementation, this would call an LLM
            simulated_content = f"""
            Chapter Content:

            The morning sun cast long shadows across the landscape as our protagonist began their journey. The world was vast and full of possibilities, each decision leading down a different path of discovery.

            The characters, each with their own distinct personality and motivations, moved through the vividly described world, interacting with the environment and each other in ways that revealed their inner thoughts and relationships.

            As the narrative progressed, the plot thickened, revealing clues and hints about the larger story while advancing the immediate goals of the characters and the overarching themes of the tale.
            """

            return AgentResponse(
                agent_name=self.name,
                content=simulated_content,
                reasoning="Generated narrative content based on story context, outline, character relationships, and world-building elements",
                suggestions=[
                    "Consider adjusting tone for more dramatic effect",
                    "Could expand on character motivations",
                    "The setting details might need more clarity"
                ],
                status="success"
            )
        except Exception as e:
            return AgentResponse(
                agent_name=self.name,
                content="",
                reasoning=f"Error in WriterAgent processing: {str(e)}",
                status="failed"
            )

    def get_prompt(self) -> str:
        """Return the prompt for the Writer agent."""
        # For a real implementation, this would read from a file or configuration
        # This is a simplified version that follows common story writing patterns
        return """
        As a professional creative writer, you will be tasked with generating the next portion of a novel based on the provided context and information.

        **Story Information:**
        - Title: {title}
        - Current Story Context: {context}
        - Chapter Outline: {chapter_outline}
        - World Building Details: {world_building}
        - Character Descriptions: {characters}
        - Current Chapter: {current_content}
        - Previous Chapter Content (for continuity): {previous_content}

        **Writing Instructions:**
        1. Follow the narrative structure and style consistent with the story's genre
        2. Develop characters authentically, showing their growth and responding to events
        3. Maintain world consistency and use details from provided world-building info
        4. Advance the plot based on the provided outline and character motivations
        5. Keep the narrative engaging and maintain pacing appropriate for the story
        6. Ensure narrative flow with the previous content when possible
        7. Focus on vivid scene-setting and compelling dialogue when appropriate

        **Output:**
        Generate the next portion of the novel that fits within the overarching story arc, maintaining stylistic consistency with the genre and tone established in the prior content. Make the writing engaging and purposeful while advancing the plot and character development.

        Begin writing from the following draft:
        {current_content}
        """