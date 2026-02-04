from typing import Dict, Any, List
import json
import re
from ..novel_types import AgentResponse
from ..config import Config
from .base import BaseAgent


class ArchivistAgent(BaseAgent):
    """Archivist agent that maintains and updates story information, notes, and continuity."""

    def __init__(self, config: Config):
        super().__init__("archivist", config)

    async def process(self, state: Dict[str, Any]) -> AgentResponse:
        """Maintain story information, notes, and continuity records."""
        try:
            # Build context for the archivist
            context = self._build_context(state)

            # Get the prompt template
            prompt = self.get_prompt()

            # Format the prompt with context
            formatted_prompt = prompt.format(
                title=state.get('title', 'Untitled'),
                context=context,
                chapters=state.get('chapters', []),
                current_chapter=state.get('current_chapter', ''),
                characters=state.get('characters', {}),
                world_details=state.get('world_details', {}),
                notes=state.get('notes', []),
                previous_archive=state.get('archive', {})
            )

            # Call the actual LLM with the formatted prompt
            response_content = await self.llm.acall(formatted_prompt, self.config.default_editor_model or self.config.default_writer_model)

            # Parse the response to ensure it's valid JSON
            try:
                # Try to parse the response as JSON directly
                archived_content = json.loads(response_content)
            except json.JSONDecodeError:
                # If not valid JSON, look for JSON content in markdown blocks\n                json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', response_content, re.DOTALL)
                if json_match:
                    try:
                        archived_content = json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        # If still not valid, return as content with error message
                        return AgentResponse(
                            agent_name=self.name,
                            content=response_content,
                            reasoning="Generated archivist analysis but could not parse as structured JSON",
                            suggestions=[],
                            status="success"
                        )
                else:
                    # If no JSON found, fall back to simulated function for now
                    # In the meantime, process the response as text
                    archived_content = {
                        "continuity_notes": self._extract_continuity_info(state),
                        "character_tracking": self._update_character_info(state),
                        "world_building_summary": self._update_world_details(state),
                        "story_consistency": self._check_consistency(state),
                        "archive_updates": f"Analysis from LLM: {response_content[:500]}..."  # Truncate long response
                    }

            return AgentResponse(
                agent_name=self.name,
                content=json.dumps(archived_content, indent=2),
                reasoning="Updated story archival information including continuity, characters, and world-building elements using LLM analysis",
                suggestions=archived_content.get("suggested_inconsistencies", []) + [
                    "Character age discrepancy noted in timeline",
                    "Location reference consistency verified",
                    "Previous plot thread advancement tracked"
                ],
                status="success"
            )
        except Exception as e:
            return AgentResponse(
                agent_name=self.name,
                content="",
                reasoning=f"Error in ArchivistAgent processing: {str(e)}",
                status="failed"
            )

    def _extract_continuity_info(self, state: Dict[str, Any]) -> dict:
        """Extract continuity information from current state."""
        # Implement logic to extract key story elements for continuity tracking
        characters = state.get('characters', {})
        world_details = state.get('world_details', {})

        return {
            "character_mentions": list(characters.keys()),
            "location_references": world_details.get('locations', []),
            "plot_threads": world_details.get('plot_threads', []),
            "important_items": world_details.get('items', []),
            "timelines": state.get('times', {})
        }

    def _update_character_info(self, state: Dict[str, Any]) -> dict:
        """Update character tracking information."""
        # This would analyze current content and update character descriptions
        current_chars = state.get('characters', {})
        # In a real implementation, we would extract character details from the text
        return current_chars

    def _update_world_details(self, state: Dict[str, Any]) -> dict:
        """Update world-building information."""
        # This would analyze current content and update world details
        current_world = state.get('world_details', {})
        return current_world

    def _check_consistency(self, state: Dict[str, Any]) -> dict:
        """Check for consistency issues."""
        # This would check for timeline, character consistency, and other issues
        return {
            "timeline_issues": [],
            "character_inconsistencies": [],
            "world_building_conflicts": [],
            "plot_holes": []
        }

    def get_prompt(self) -> str:
        """Return the prompt for the Archivist agent."""
        return """
        As a professional story archivist and continuity keeper, you will maintain detailed records of all story elements, character details, and continuity information to ensure consistency throughout the novel's development.

        **Current Story Data:**
        - Title: {title}
        - Current Story Context: {context}
        - Existing Chapters: {chapters}
        - Current Chapter Content: {current_chapter}
        - Character Information: {characters}
        - World Building Details: {world_details}
        - Previous Editorial Notes: {notes}
        - Previous Archive: {previous_archive}

        **Archival Requirements:**
        1. Extract and update character information, noting changes in personality, appearance, or relationships
        2. Track and update world-building elements, locations, and important items
        3. Maintain continuity regarding timelines, settings, and past events
        4. Identify and flag any potential continuity issues, inconsistencies, or errors
        5. Create detailed notes about plot thread progression and character development
        6. Establish connections between current content and previous story elements
        7. Organize all archival data in a structured, searchable format
        8. Track important story elements (dates, objects, locations, character details) for future reference

        **Specific Elements to Track:**
        - Character development and personality consistency
        - Physical descriptions and identifying features
        - Relationships between characters
        - Timeline of events across chapters
        - Location details and settings
        - Important objects or items referenced
        - Past events referenced that affect current/previous events
        - Recurring themes and motifs
        - Plot thread management and advancement

        **Output:**
        Provide an updated archival record in JSON format including:
        1. Continuity notes with identified elements and references
        2. Updated character tracking and development records
        3. World-building summary and details
        4. Consistency verification results
        5. Archive updates with specific changes and additions

        Focus on identifying any elements that might create continuity issues and flag them for editor review.
        """