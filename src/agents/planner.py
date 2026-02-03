from typing import Dict, Any, List
import json
from ..novel_types import AgentResponse
from ..config import Config
from .base import BaseAgent


class PlannerAgent(BaseAgent):
    """Planner agent that creates and updates story outlines and narrative direction."""

    def __init__(self, config: Config):
        super().__init__("planner", config)

    async def process(self, state: Dict[str, Any]) -> AgentResponse:
        """Create or update the story plan based on the current state."""
        try:
            # Build context for the planner
            context = self._build_context(state)

            # Get the prompt template
            prompt = self.get_prompt()

            # Format the prompt with context
            formatted_prompt = prompt.format(
                title=state.get('title', 'Untitled'),
                context=context,
                chapters=state.get('chapters', []),
                current_outline=state.get('outline', {}),
                current_chapter=state.get('current_chapter', ''),
                story_status=state.get('story_status', 'draft')
            )

            # For now, simulate planning generation
            # In a real implementation, this would call an LLM and include more detailed planning
            planned_content = {
                "current_chapter_outline": {
                    "chapter_number": len(state.get('chapters', [])) + 1,
                    "title": f"Chapter {len(state.get('chapters', [])) + 1}",
                    "content_goals": [
                        "Introduce main conflict",
                        "Develop key relationships",
                        "Advance overarching plot",
                        "Establish character motivation"
                    ],
                    "key_scenes": [
                        "Opening scene establishing setting and mood",
                        "Character interaction revealing personality",
                        "Inciting incident that drives chapter",
                        "Closing that connects to wider story"
                    ],
                    "character_appearances": list(state.get('characters', {}).keys()) if state.get('characters') else [],
                    "world_building_elements": state.get('world_details', {})
                },
                "overall_arc": {
                    "current_progress": f"Chapter {len(state.get('chapters', [])) + 1}/{state.get('outline', {}).get('total_chapters', 10)}",
                    "next_milestones": ["midpoint crisis", "pre-climax tension", "climax", "resolution"],
                    "themes_to_develop": ["character growth", "central conflict", "world exploration"]
                }
            }

            return AgentResponse(
                agent_name=self.name,
                content=json.dumps(planned_content, indent=2),
                reasoning="Generated chapter plan and story arc considering the current story state and progression",
                suggestions=[
                    "Consider adjusting pacing based on reader engagement metrics",
                    "Ensure character development goals align with story requirements",
                    "Reassess chapter count based on story complexity"
                ],
                status="success"
            )
        except Exception as e:
            return AgentResponse(
                agent_name=self.name,
                content="",
                reasoning=f"Error in PlannerAgent processing: {str(e)}",
                status="failed"
            )

    def get_prompt(self) -> str:
        """Return the prompt for the Planner agent."""
        return """
        As a professional story planner and narrative architect, you will create a detailed outline and plan for the current story based on the provided information.

        **Story Information:**
        - Title: {title}
        - Current Story Context: {context}
        - Existing Chapters: {chapters}
        - Current Story Outline: {current_outline}
        - Current Chapter Content: {current_chapter}
        - Story Status: {story_status}

        **Planning Requirements:**
        1. Create a detailed chapter-by-chapter outline if no outline exists
        2. Update and refine the outline based on actual content written so far
        3. Ensure pacing, flow, and cohesion across the entire narrative
        4. Identify character development arcs and plot progression
        5. Specify world-building elements to be introduced or expanded
        6. Set clear goals for upcoming chapters while maintaining flexibility
        7. Consider genre conventions and reader expectations

        **Chapter Outline Format:**
        - Chapter number and title
        - Primary goals for the content
        - Key scenes to be included
        - Characters that should appear
        - World-building elements to incorporate
        - Plot advancement requirements
        - Character development milestones

        **Overall Story Arc:**
        - Current progress through the story
        - Upcoming major milestones
        - Thematic consistency across chapters
        - Expected total length
        - Pacing requirements

        **Output:**
        Provide a structured JSON format with both the current chapter's outline and the overall story arc, ensuring that all elements work together to create a cohesive and engaging narrative.
        """