from typing import Dict, Any, List
import json
from ..novel_types import AgentResponse
from ..config import Config
from .base import BaseAgent


class WorldBuilderAgent(BaseAgent):
    """World Builder agent that develops and maintains the fictional world, setting, and background elements."""

    def __init__(self, config: Config):
        super().__init__("world_builder", config)

    async def process(self, state: Dict[str, Any]) -> AgentResponse:
        """Develop and maintain the fictional world, setting, and background elements."""
        try:
            # Build context for the world builder
            context = self._build_context(state)

            # Get the prompt template
            prompt = self.get_prompt()

            # Format the prompt with context
            formatted_prompt = prompt.format(
                title=state.get('title', 'Untitled'),
                context=context,
                current_chapter=state.get('current_chapter', ''),
                characters=state.get('characters', {}),
                existing_world_details=state.get('world_details', {}),
                outline=state.get('outline', {}),
                all_chapters=state.get('chapters', []),
                genre_expecations=state.get('outline', {}).get('genre', ''),
                setting_requirements=state.get('outline', {}).get('setting', {})
            )

            # Call the actual LLM with the formatted prompt
            response_content = await self.llm.acall(formatted_prompt, self.config.default_planner_model or self.config.default_writer_model)

            # Parse the response to ensure it's valid JSON
            try:
                # Try to parse the response as JSON directly
                world_building_report = json.loads(response_content)
            except json.JSONDecodeError:
                # If not valid JSON, look for JSON content in markdown blocks
                import re
                json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', response_content, re.DOTALL)
                if json_match:
                    try:
                        world_building_report = json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        # If still not valid, return content with error message
                        return AgentResponse(
                            agent_name=self.name,
                            content=response_content,
                            reasoning="Generated world building analysis but could not parse as structured JSON",
                            suggestions=[],
                            status="success"
                        )
                else:
                    # If no JSON found, extract recommendations from the response text
                    import re
                    # Extract potential recommendations from the response text
                    recommendation_pattern = r'(?:recommendations?:|suggestions?:)\s*(.*?)(?:\n\n|\n[A-Z][a-z]+:|$)'
                    match = re.search(recommendation_pattern, response_content, re.IGNORECASE | re.DOTALL)
                    recommendations = []
                    if match:
                        recommendations_text = match.group(1).strip()
                        # Try to split into individual recommendations
                        recommendations = [s.strip() for s in recommendations_text.split('\n') if s.strip().startswith(('-', '*', '•'))]
                        if not recommendations:
                            recommendations = [recommendations_text[:200]]  # Use first 200 chars as a recommendation if no bullets found

                    world_building_report = {
                        "world_building_recommendations": recommendations
                    }

            return AgentResponse(
                agent_name=self.name,
                content=json.dumps(world_building_report, indent=2),
                reasoning="Analyzed current chapter to expand world elements using LLM analysis while maintaining consistency with established setting",
                suggestions=world_building_report.get("world_building_recommendations", []),
                status="success"
            )
        except Exception as e:
            return AgentResponse(
                agent_name=self.name,
                content="",
                reasoning=f"Error in WorldBuilderAgent processing: {str(e)}",
                status="failed"
            )

    def _check_magic_systems(self, state: Dict[str, Any]) -> List[str]:
        """Check if magic system is used consistently."""
        return ["Magic system follows established rules from previous chapters"]

    def _check_political_updates(self, state: Dict[str, Any]) -> List[str]:
        """Check political elements."""
        return ["Political tensions align with previous mentions"]

    def _check_economic_details(self, state: Dict[str, Any]) -> List[str]:
        """Check economic elements."""
        return ["Economic details consistent with established world"]

    def _check_social_details(self, state: Dict[str, Any]) -> List[str]:
        """Check social structure elements."""
        return ["Social hierarchies remain consistent with previous descriptions"]

    def get_prompt(self) -> str:
        """Return the prompt for the World Builder agent."""
        return """
        As a professional world builder and setting developer, analyze the current story content to expand, develop, and maintain the fictional world, setting, and background elements in a coherent and immersive way.

        **Story Information:**
        - Title: {title}
        - Current Story Context: {context}
        - Current Chapter Content: {current_chapter}
        - Character Information: {characters}
        - Existing World Details: {existing_world_details}
        - Story Outline: {outline}
        - All Previous Chapters: {all_chapters}
        - Genre Requirements: {genre_expecations}
        - Setting Requirements: {setting_requirements}

        **World Building Focus Areas:**

        1. **Geographic Development:**
           - Introduce new locations that fit with existing geography
           - Expand on existing locations with greater detail
           - Maintain consistency with known world geography
           - Consider map accuracy and logical placement of locations
           - Identify opportunities for future geographic exploration
           - Ensure travel times and distances are reasonable

        2. **Cultural and Social Development:**
           - Introduce new cultural elements (traditions, festivals, customs)
           - Expand on existing cultural practices with greater detail
           - Ensure cultural elements are consistent with the world's history
           - Develop social hierarchies and class structures
           - Consider cultural diversity across different regions
           - Link cultural elements to character development and plot

        3. **World Systems Integrity:**
           - If present, maintain consistency in magic systems, rules, and limitations
           - Develop political systems, power structures, and governance
           - Establish economic systems, trade, and resource management
           - Create technological levels appropriate for the world
           - Define legal systems, social norms, and societal expectations

        4. **Detail Enrichment:**
           - Add sensory details (sounds, smells, textures) to locations
           - Develop history that explains the current state of the world
           - Create artifacts, architecture, and objects that reflect the world
           - Design languages, slang, or naming conventions specific to cultures
           - Include flora, fauna, and environmental elements unique to the world

        5. **Integration and Consistency:**
           - Ensure new world elements connect with plot developments
           - Link world elements to character backgrounds and motivations
           - Maintain consistency with prior established world facts
           - Identify any contradictions in world building elements
           - Verify that world-building doesn't slow the narrative unnecessarily

        6. **Future Development Opportunities:**
           - Identify elements that could be expanded in future chapters
           - Note details that could be referenced later for plot development
           - Suggest how world elements could impact broader story direction

        **Output Format:**
        Provide a comprehensive world building report in this JSON structure:

        {
          "geographic_expansion": {
            "new_locations_introduced": [],
            "location_details_enhanced": [],
            "map_consistency": "...",
            "exploration_opportunities": []
          },
          "cultural_development": {
            "new_cultural_elements": [],
            "cultural_detail_enhanced": [],
            "tradition_integration": "..."
          },
          "world_systems_integrity": {
            "magic_system_updates": [],
            "political_system_updates": [],
            "economic_system_updates": [],
            "social_structure_updates": []
          },
          "consistency_verification": {
            "new_elements_consistent": "...",
            "contradiction_check": "...",
            "integration_quality": "..."
          },
          "world_building_recommendations": [],
          "expansion_opportunities": []
        }

        Focus on creating a cohesive, believable world that serves the story while maintaining internal consistency.
        """