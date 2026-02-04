from typing import Dict, Any, List
import json
from ..novel_types import AgentResponse
from ..config import Config
from .base import BaseAgent


class PacingAdvisorAgent(BaseAgent):
    """Pacing Advisor agent that analyzes story rhythm, tension, and narrative flow."""

    def __init__(self, config: Config):
        super().__init__("pacing_advisor", config)

    async def process(self, state: Dict[str, Any]) -> AgentResponse:
        """Analyze story rhythm, tension, and narrative flow."""
        try:
            # Build context for the pacing advisor
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
                all_chapters=state.get('chapters', []),
                genre=state.get('outline', {}).get('genre', ''),
                current_tension_level=state.get('outline', {}).get('current_tension', 'moderate'),
                overall_story_arc=state.get('outline', {}).get('arc', {})
            )

            # Call the actual LLM with the formatted prompt
            response_content = await self.llm.acall(formatted_prompt, self.config.default_editor_model or self.config.default_writer_model)

            # Parse the response to ensure it's valid JSON
            try:
                # Try to parse the response as JSON directly
                pacing_analysis = json.loads(response_content)
            except json.JSONDecodeError:
                # If not valid JSON, look for JSON content in markdown blocks
                import re
                json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', response_content, re.DOTALL)
                if json_match:
                    try:
                        pacing_analysis = json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        # If still not valid, return content with error message
                        return AgentResponse(
                            agent_name=self.name,
                            content=response_content,
                            reasoning="Generated pacing analysis but could not parse as structured JSON",
                            suggestions=[],
                            status="success"
                        )
                else:
                    # If no JSON found, extract recommendations from the response text
                    import re
                    # Extract potential recommendations from the response text
                    recommendation_pattern = r'(?:recommendations?:|suggestions?:|improvements?:)\s*(.*?)(?:\n\n|\n[A-Z][a-z]+:|$)'
                    match = re.search(recommendation_pattern, response_content, re.IGNORECASE | re.DOTALL)
                    recommendations = []
                    if match:
                        recommendations_text = match.group(1).strip()
                        # Try to split into individual recommendations
                        recommendations = [s.strip() for s in recommendations_text.split('\n') if s.strip().startswith(('-', '*', '•'))]
                        if not recommendations:
                            recommendations = [recommendations_text[:200]]  # Use first 200 chars as a recommendation if no bullets found

                    pacing_analysis = {
                        "pacing_recommendations": recommendations
                    }

            return AgentResponse(
                agent_name=self.name,
                content=json.dumps(pacing_analysis, indent=2),
                reasoning="Analyzed narrative rhythm, tension levels, and story flow using LLM analysis to ensure optimal pacing for reader engagement",
                suggestions=pacing_analysis.get("pacing_recommendations", []),
                status="success"
            )
        except Exception as e:
            return AgentResponse(
                agent_name=self.name,
                content="",
                reasoning=f"Error in PacingAdvisorAgent processing: {str(e)}",
                status="failed"
            )

    def get_prompt(self) -> str:
        """Return the prompt for the Pacing Advisor agent."""
        return """
        As a professional story structure and pacing editor, analyze the narrative rhythm, tension, and flow of the provided content according to pacing principles and genre standards.

        **Story Information:**
        - Title: {title}
        - Current Story Context: {context}
        - Current Chapter Content: {current_chapter}
        - Character Information: {characters}
        - World Building Details: {world_details}
        - Story Outline: {outline}
        - All Previous Chapters: {all_chapters}
        - Genre: {genre}
        - Current Tension Level: {current_tension_level}
        - Overall Story Arc: {overall_story_arc}

        **Pacing Analysis Areas:**

        1. **Rhythm Assessment:**
           - Sentence length variety (affecting reading pace)
           - Paragraph structure and flow
           - Balance between action scenes, dialogue, and descriptive passages
           - Use of white space and breaks for rhythmic effect
           - Rhythm changes that align with narrative purpose

        2. **Tension Analysis:**
           - Current tension level compared to story needs
           - Effectiveness of tension-building mechanisms
           - Identification of tension release points
           - Crescendo and climax effectiveness
           - Balance of tension vs. relief moments

        3. **Narrative Flow:**
           - Smoothness of transitions between scenes and time shifts
           - Logical content progression
           - Maintaining reader engagement
           - Maintaining narrative momentum
           - Integration of expository information without flow interruption

        4. **Structural Pacing:**
           - Chapter opening impact and forward pull
           - Mid-section energy and engagement maintenance
           - Ending effectiveness - closing current issues while creating forward momentum
           - Scene duration in relation to content importance
           - Pacing of plot revelation and character development

        5. **Reader Engagement:**
           - Assessment of points where readers might lose focus
           - Identification of most engaging passages
           - Pacing for maintaining genre-specific engagement
           - Assessment of information dumping vs. absorption time

        6. **Genre Comparison:**
           - Pacing compared to genre conventions
           - Tension curve adherence to genre standards
           - Rhythm matching similar successful works
           - Pace appropriate for story length and content

        **Special Attention:**
         - Look for long passages without action, dialogue, or plot advancement
         - Identify places where the story drags or where information dumps occur
         - Check for effective use of tension/release cycles
         - Note where reader attention might decrease due to pacing issues
         - Consider how pacing affects emotional arc
         - Identify opportunities to speed up or slow down in service to the narrative

        **Output Format:**
        Provide a comprehensive pacing analysis in this JSON structure:

        {{
          "rhythm_assessment": {{
            "sentence_length_variety": "...",
            "paragraph_structure": "...",
            "scene_vs_detailed_balance": "...",
            "rhythm_score": 1-10
          }},
          "tension_analysis": {{
            "current_tension_level": "...",
            "tension_building_mechanisms": [],
            "crescendo_effectiveness": "...",
            "tension_consistency": "..."
          }},
          "narrative_flow": {{
            "transition_smoothness": "...",
            "content_pacing": "...",
            "reader_engagement": "...",
            "flow_score": 1-10
          }},
          "structural_pacing": {{
            "chapter_beginning": "...",
            "mid_section_movement": "...",
            "ending_satisfaction": "..."
          }},
          "pacing_recommendations": [],
          "comparison_to_genre_standards": {{
            "pace_relative_to_genre": "...",
            "tension_distribution": "...",
            "engagement_patterns": "..."
          }}
        }}

        Rate rhythm and flow on a 1-10 scale and provide specific recommendations for pacing improvements.
        """