from typing import Dict, Any, List
import json
from ..novel_types import AgentResponse
from ..config import Config
from .base import BaseAgent


class DialogueSpecialistAgent(BaseAgent):
    """Dialogue Specialist agent that analyzes and improves character dialogue and interactions."""

    def __init__(self, config: Config):
        super().__init__("dialogue_specialist", config)

    async def process(self, state: Dict[str, Any]) -> AgentResponse:
        """Analyze and improve character dialogue and interactions."""
        try:
            # Build context for the dialogue specialist
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
                dialogue_samples=state.get('current_chapter', '').split('\n') if state.get('current_chapter') else [],
                previous_dialogue_analysis=state.get('dialogue_notes', {})
            )

            # Call the actual LLM with the formatted prompt
            response_content = await self.llm.acall(formatted_prompt, self.config.default_editor_model or self.config.default_writer_model)

            # Parse the response to ensure it's valid JSON
            try:
                # Try to parse the response as JSON directly
                dialogue_analysis = json.loads(response_content)
            except json.JSONDecodeError:
                # If not valid JSON, look for JSON content in markdown blocks
                import re
                json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', response_content, re.DOTALL)
                if json_match:
                    try:
                        dialogue_analysis = json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        # If still not valid, return content with error message
                        return AgentResponse(
                            agent_name=self.name,
                            content=response_content,
                            reasoning="Generated dialogue analysis but could not parse as structured JSON",
                            suggestions=[],
                            status="success"
                        )
                else:
                    # If no JSON found, extract suggestions from response
                    import re
                    # Extract potential improvement suggestions from the response text
                    suggestion_pattern = r'(?:suggestions?:|improvements?:|recommendations:)\s*(.*?)(?:\n\n|\n[A-Z][a-z]+:|$)'
                    match = re.search(suggestion_pattern, response_content, re.IGNORECASE | re.DOTALL)
                    suggestions = []
                    if match:
                        suggestions_text = match.group(1).strip()
                        # Try to split into individual suggestions
                        suggestions = [s.strip() for s in suggestions_text.split('\n') if s.strip().startswith(('-', '*', '•'))]
                        if not suggestions:
                            suggestions = [suggestions_text[:200]]  # Use first 200 chars as a suggestion if no bullets found

                    dialogue_analysis = {
                        "improvement_suggestions": suggestions
                    }

            return AgentResponse(
                agent_name=self.name,
                content=json.dumps(dialogue_analysis, indent=2),
                reasoning="Analyzed dialogue patterns, character voices, and interaction quality using LLM analysis",
                suggestions=dialogue_analysis.get("improvement_suggestions", []),
                status="success"
            )
        except Exception as e:
            return AgentResponse(
                agent_name=self.name,
                content="",
                reasoning=f"Error in DialogueSpecialistAgent processing: {str(e)}",
                status="failed"
            )

    def get_prompt(self) -> str:
        """Return the prompt for the Dialogue Specialist agent."""
        return """
        As a professional dialogue editor and linguistics specialist, analyze the character dialogue and interactions in the provided content for quality, authenticity, and effectiveness.

        **Story Context:**
        - Title: {title}
        - Current Story Context: {context}
        - Current Chapter Content: {current_chapter}
        - Character Information: {characters}
        - World Building Details: {world_details}
        - Dialogue Samples from Current Chapter: {dialogue_samples}
        - Previous Dialogue Analysis: {previous_dialogue_analysis}

        **Analysis Requirements:**

        1. **Character Voice Consistency:**
           - Does each character have a distinctive voice?
           - Are individual speech patterns consistent across the story?
           - Is the character's vocabulary appropriate for their background and personality?
           - Do accents or speech quirks remain consistent?

        2. **Dialogue Quality Metrics:**
           - Does the dialogue sound natural and conversational?
           - Does each conversation serve a specific purpose (advance plot, reveal character, provide exposition)?
           - Is the dialogue well-balanced (not too much exposition vs. too little context)?
           - Does the dialogue effectively convey emotion?

        3. **Dialogue Technique Analysis:**
           - Is subtext properly used to add depth below the surface conversation?
           - Are dialogue tags varied and appropriately used or appropriately minimal?
           - Is attribution clear when multiple characters speak?
           - Are dialogue and action tags well-integrated?

        4. **Character Interaction Dynamics:**
           - Do conversations reveal the appropriate relationship dynamics?
           - Are characters' responses believable based on their personalities and situation?
           - Are internal and external conflicts properly conveyed through dialogue?
           - Are power dynamics within conversations clear and consistent?

        5. **Style and Authenticity:**
           - Does the vocabulary match the genre, setting, and character backgrounds?
           - Are conversational patterns natural to the time period/setting?
           - Do characters speak to each other in ways that feel authentic to their relationship?

        6. **Integration with Narrative:**
           - Does dialogue appropriately break up with narrative description?
           - Can readers follow conversation dynamics without confusion?
           - Does dialogue effectively shift narrative focus between characters?

        **Special Attention:**
         - Flag any dialogue that breaks character voice consistency
         - Identify instances where dialogue is too expository or "on the nose"
         - Note when characters seem to give each other information they both already know
         - Look for opportunities to convey information through subtext rather than direct statements
         - Analyze whether dialogue effectively conveys scene objectives

        **Output Format:**
        Provide a comprehensive dialogue analysis in this JSON structure:

        {{
          "character_voice_consistency": {{
            "distinctiveness_score": 1-10,
            "individual_voices": [],
            "voice_consistency": "..."
          }},
          "dialogue_quality_metrics": {{
            "naturalness_score": 1-10,
            "purposefulness": "...",
            "balance": "...",
            "authenticity": "..."
          }},
          "dialogue_technique_analysis": {{
            "subtext_effectiveness": "...",
            "dialogue_tags": "...",
            "attribution_consistency": "..."
          }},
          "character_interaction_dynamics": {{
            "relationship_progression": "...",
            "conflict_representation": "...",
            "emotional_arc": "..."
          }},
          "improvement_suggestions": [],
          "style_consistency": {{
            "vocabulary_choices": "...",
            "conversational_styles": "...",
            "formality_levels": "..."
          }}
        }}

        Rate key elements on a 1-10 scale and provide actionable improvement suggestions.
        """