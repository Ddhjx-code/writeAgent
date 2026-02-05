from typing import Dict, Any, List
import json
from ..novel_types import AgentResponse
from ..config import Config
from .base import BaseAgent
from ..core.prompt_manager import prompt_manager


class DialogueSpecialistAgent(BaseAgent):
    """Dialogue Specialist agent that analyzes and improves character dialogue and interactions."""

    def __init__(self, config: Config):
        super().__init__("dialogue_specialist", config)

    async def process(self, state: Dict[str, Any]) -> AgentResponse:
        """Analyze and improve character dialogue and interactions."""
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                # Build context for the dialogue specialist
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
                    dialogue_samples=state.get('current_chapter', '').split('\n') if state.get('current_chapter') else [],
                    previous_dialogue_analysis=state.get('dialogue_notes', {})
                ) if prompt_template.user_prompt else f"Analyze dialogue for story: {state.get('title', 'Untitled')}. Content: {context}. Current Chapter: {state.get('current_chapter', '')}"

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
                        dialogue_samples=state.get('current_chapter', '').split('\n') if state.get('current_chapter') else [],
                        previous_dialogue_analysis=state.get('dialogue_notes', {})
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
                    dialogue_analysis = json.loads(response_content)
                except json.JSONDecodeError:
                    # If not valid JSON, look for JSON content in markdown blocks
                    import re
                    json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', response_content, re.DOTALL)
                    if json_match:
                        try:
                            dialogue_analysis = json.loads(json_match.group(1))
                        except json.JSONDecodeError:
                            # If still not valid, return content with error message after retry
                            retry_count += 1
                            if retry_count >= max_retries:
                                # If no JSON found, extract suggestions from response
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
                                    reasoning=f"Failed to extract structured JSON after {max_retries} attempts",
                                    suggestions=dialogue_analysis.get("improvement_suggestions", []),
                                    status="success_with_warnings"
                                )
                            continue  # retry
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
                retry_count += 1
                if retry_count >= max_retries:
                    return AgentResponse(
                        agent_name=self.name,
                        content="",
                        reasoning=f"Error in DialogueSpecialistAgent processing after {max_retries} attempts: {str(e)}",
                        status="failed"
                    )

        return AgentResponse(
            agent_name=self.name,
            content="",
            reasoning=f"Failed to generate dialogue analysis after {max_retries} retries",
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