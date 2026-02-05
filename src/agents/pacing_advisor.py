from typing import Dict, Any, List
import json
from ..novel_types import AgentResponse
from ..config import Config
from .base import BaseAgent
from ..core.prompt_manager import prompt_manager

class PacingAdvisorAgent(BaseAgent):
    """Pacing Advisor agent that analyzes story rhythm, tension, and narrative flow."""

    def __init__(self, config: Config):
        super().__init__("pacing_advisor", config)

    async def process(self, state: Dict[str, Any]) -> AgentResponse:
        """Analyze story rhythm, tension, and narrative flow."""
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                # Build context for the pacing advisor
                context = self._build_context(state)

                # Get the prompt template with system and user messages
                prompt_template = prompt_manager.get_prompt_template(self.name)

                # Format the user prompt with context
                formatted_user_prompt = prompt_template.user_prompt.format(
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
                ) if prompt_template.user_prompt else f"Analyze pacing for story: {state.get('title', 'Untitled')}. Content: {context}. Current Chapter: {state.get('current_chapter', '')}"

                # Format the system prompt with context
                formatted_system_prompt = prompt_template.system_prompt
                if '{' in formatted_system_prompt and '}' in formatted_system_prompt:
                    # If system prompt has placeholders, format them too
                    formatted_system_prompt = formatted_system_prompt.format(
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

                # Call the actual LLM with both system and user prompts
                response_content = await self.llm.call_with_system_user(
                    formatted_system_prompt,
                    formatted_user_prompt,
                    self.config.default_editor_model or self.config.default_writer_model
                )

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
                            # If still not valid, return content with error message after retry
                            retry_count += 1
                            if retry_count >= max_retries:
                                # If no JSON found, extract recommendations from the response text
                                recommendation_pattern = r'(?:recommendations?:|suggestions?:|improvements?:)\s*(.*?)(?:\n\n|\n[A-Z][a-z]+:|$)'
                                match = re.search(recommendation_pattern, response_content, re.IGNORECASE | re.DOTALL)
                                recommendations = []
                                if match:
                                    recommendations_text = match.group(1).strip()
                                    # Try to split into individual recommendations
                                    recommendations = [s.strip() for s in recommendations_text.split('\n') if s.strip().startswith(('-', '*', '•'))]
                                    if not recommendations:
                                        recommendations = [recommendations_text[:200]]  # Use first 200 chars as a recommendation if no bulbs found

                                pacing_analysis = {
                                    "pacing_recommendations": recommendations
                                }
                                return AgentResponse(
                                    agent_name=self.name,
                                    content=json.dumps(pacing_analysis, indent=2),
                                    reasoning=f"Failed to extract structured JSON after {max_retries} attempts",
                                    suggestions=pacing_analysis.get("pacing_recommendations", []),
                                    status="success_with_warnings"
                                )
                            continue  # retry
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
                                recommendations = [recommendations_text[:200]]  # Use first 200 chars as a recommendation if no bulbs found

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
                retry_count += 1
                if retry_count >= max_retries:
                    return AgentResponse(
                        agent_name=self.name,
                        content="",
                        reasoning=f"Error in PacingAdvisorAgent processing after {max_retries} attempts: {str(e)}",
                        status="failed"
                    )

        return AgentResponse(
            agent_name=self.name,
            content="",
            reasoning=f"Failed to generate pacing analysis after {max_retries} retries",
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