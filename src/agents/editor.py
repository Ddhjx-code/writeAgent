from typing import Dict, Any, List
import json
import re
from ..novel_types import AgentResponse
from ..config import Config
from .base import BaseAgent


class EditorAgent(BaseAgent):
    """Editor agent that reviews and improves written content for quality and consistency."""

    def __init__(self, config: Config):
        super().__init__("editor", config)

    async def process(self, state: Dict[str, Any]) -> AgentResponse:
        """Review and improve written content."""
        try:
            # Build context for the editor
            context = self._build_context(state)

            # Get the prompt template
            prompt = self.get_prompt()

            # Format the prompt with context
            formatted_prompt = prompt.format(
                title=state.get('title', 'Untitled'),
                context=context,
                current_chapter=state.get('current_chapter', ''),
                characters=state.get('characters', {}),
                world_details=state.get('world_details', {}),
                outline=state.get('outline', {}),
                chapters=state.get('chapters', []),
                previous_edits=state.get('editor_notes', [])
            )

            # Call the actual LLM with the formatted prompt
            response_content = await self.llm.acall(formatted_prompt, self.config.default_editor_model)

            # Check if this is a MOCK response from the LLM provider first
            if response_content.startswith(("MOCK RESPONSE:", "MOCK ANTHROPIC RESPONSE:", "MOCK MISTRAL RESPONSE:", "MOCK COHERE RESPONSE:")):
                # For MOCK responses, create a minimal JSON structure instead of failing
                edit_recommendations = {"status": "mock_response", "message": "MOCK response processed successfully"}
            else:
                # Parse the response to ensure it's valid JSON
                try:
                    # Try to parse the response as JSON directly
                    edit_recommendations = json.loads(response_content)
                except json.JSONDecodeError:
                    # If not valid JSON, look for JSON content in markdown blocks
                    json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', response_content, re.DOTALL)
                    if json_match:
                        try:
                            edit_recommendations = json.loads(json_match.group(1))
                        except json.JSONDecodeError:
                            # If still not valid, create a simple default structure
                            edit_recommendations = {"message": "No JSON content in response"}
                    else:
                        # For other non-JSON responses create simple structure
                        edit_recommendations = {"message": "No structured content returned"}

            return AgentResponse(
                agent_name=self.name,
                content=json.dumps(edit_recommendations, indent=2),
                reasoning="Reviewed current chapter content according to writing standards for pacing, style, and narrative effectiveness",
                suggestions=edit_recommendations.get("suggested_revisions", []),
                status="success"
            )
        except Exception as e:
            return AgentResponse(
                agent_name=self.name,
                content="",
                reasoning=f"Error in EditorAgent processing: {str(e)}",
                suggestions=[],
                status="failed"
            )

    def get_prompt(self) -> str:
        """Return the prompt for the Editor agent."""
        return """
        As a professional developmental and copy editor, review the following chapter content with attention to narrative effectiveness, style, coherence, character development, plot advancement, and general writing quality.

        **Story Context:**
        - Title: {title}
        - Current Story Context: {context}
        - Current Chapter Content: {current_chapter}
        - Character Information: {characters}
        - World Building Details: {world_details}
        - Story Outline: {outline}
        - Existing Chapters: {chapters}
        - Previous Editor Notes: {previous_edits}

        **Editing Focus Areas:**
        1. **Narrative Structure and Pacing:**
           - Check for strong opening hook
           - Evaluate pacing - appropriate for genre and chapter position
           - Verify smooth transitions between scenes
           - Assess ending satisfaction and forward momentum

        2. **Character Development:**
           - Ensure character consistency with previous chapters
           - Verify character motivations are clear
           - Assess dialogue authenticity and voice consistency
           - Check character agency and impact on plot

        3. **Plot and Story Elements:**
           - Verify plot advancement for this chapter
           - Check for plot hole identification
           - Assess subplot integration
           - Confirm alignment with overall story outline

        4. **Style and Prose:**
           - Evaluate sentence variety and paragraph flow
           - Identify repetitive word usage or sentence structures
           - Ensure tone consistency throughout
           - Verify description effectiveness (show versus tell balance)

        5. **World Building:**
           - Ensure consistency with established world details
           - Verify world-building elements feel natural, not forced
           - Check for appropriate use of world-building in narrative

        6. **Continuity:**
           - Check for continuity with previous chapters
           - Identify any timeline inconsistencies
           - Verify character knowledge matches prior scenes
           - Confirm setting details remain consistent

        **Output Format:**
        Provide detailed feedback in the following JSON structure:
        {{
          "structural_feedback": {{
            "pacing_issues": [],
            "plot_advancement": "...",
            "character_development": "..."
          }},
          "style_feedback": {{
            "sentence_variety": "...",
            "vocabulary": "...",
            "tone_consistency": "..."
          }},
          "continuity_check": {{
            "character_appearances": "...",
            "world_building": "...",
            "plot_threads": "..."
          }},
          "suggested_revisions": [],
          "overall_score": 1-10,
          "recommendations_summary": "..."
        }}
        """