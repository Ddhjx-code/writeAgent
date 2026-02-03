from typing import Dict, Any, List, Optional
import json
import os
import asyncio
from datetime import datetime
from ..novel_types import StoryState
from ..workflow.state import GraphState


def format_chapter_for_display(chapter: Dict[str, Any]) -> str:
    """Format a chapter for display in the interface."""
    if isinstance(chapter, dict):
        chapter_num = chapter.get('number', 'N/A')
        title = chapter.get('title', 'Untitled')
        content = chapter.get('content', '')
        word_count = chapter.get('word_count', 0)

        formatted = f"Chapter {chapter_num}: {title}\n"
        formatted += f"Word Count: {word_count}\n"
        formatted += f"Content:\n{content}"

        return formatted
    else:
        return str(chapter)


def format_character_for_display(character: Dict[str, Any]) -> str:
    """Format a character for display in the interface."""
    if isinstance(character, dict):
        name = character.get('name', 'Unknown')
        role = character.get('role', 'N/A')
        description = character.get('description', 'No description')

        formatted = f"Name: {name}\n"
        formatted += f"Role: {role}\n"
        formatted += f"Description: {description}\n"

        return formatted
    else:
        return str(character)


def serialize_story_state(state: StoryState) -> Dict[str, Any]:
    """Convert StoryState to JSON-serializable dictionary."""
    return {
        "title": state.title,
        "current_chapter": state.current_chapter,
        "chapters": state.chapters,
        "outline": state.outline,
        "characters": state.characters,
        "world_details": state.world_details,
        "story_status": state.story_status,
        "notes": state.notes
    }


def deserialize_story_state(data: Dict[str, Any]) -> StoryState:
    """Convert dictionary back to StoryState."""
    return StoryState(
        title=data.get('title', ''),
        current_chapter=data.get('current_chapter', ''),
        chapters=data.get('chapters', []),
        outline=data.get('outline', {}),
        characters=data.get('characters', {}),
        world_details=data.get('world_details', {}),
        story_status=data.get('story_status', 'draft'),
        notes=data.get('notes', [])
    )


def serialize_graph_state(state: GraphState) -> Dict[str, Any]:
    """Convert GraphState to JSON-serializable dictionary."""
    # Convert AgentResponse objects to dictionaries
    agent_responses = []
    for response in state.agent_responses:
        if hasattr(response, 'dict'):
            agent_responses.append(response.dict())
        else:
            agent_responses.append(response)

    return {
        "title": state.title,
        "current_chapter": state.current_chapter,
        "chapters": state.chapters,
        "outline": state.outline,
        "characters": state.characters,
        "world_details": state.world_details,
        "story_status": state.story_status,
        "story_notes": state.story_notes,
        "next_agent": state.next_agent,
        "iteration_count": state.iteration_count,
        "max_iterations": state.max_iterations,
        "knowledge_queries": state.knowledge_queries,
        "retrieved_knowledge": state.retrieved_knowledge,
        "current_phase": state.current_phase,
        "error_count": state.error_count,
        "last_error": state.last_error,
        "human_feedback": state.human_feedback,
        "needs_human_review": state.needs_human_review,
        "human_review_status": state.human_review_status,
        "completed_chapters": state.completed_chapters,
        "current_chapter_index": state.current_chapter_index,
        "story_arc_progress": state.story_arc_progress,
        "current_agent_output": state.current_agent_output,
        "agent_execution_log": state.agent_execution_log,
        "agent_responses": agent_responses
    }


def validate_story_data(data: Dict[str, Any]) -> bool:
    """Validate if the provided data represents valid story information."""
    required_fields = ['title']
    for field in required_fields:
        if field not in data:
            return False
        if not data[field]:
            return False  # Title shouldn't be empty

    return True


def sanitize_user_input(text: str) -> str:
    """Sanitize user input to prevent any potential issues."""
    if not text:
        return ""

    # Remove any potentially problematic characters or patterns
    sanitized = text.replace('<script', '&lt;script').replace('javascript:', 'javascript-')
    # Remove null bytes
    sanitized = sanitized.replace('\x00', '')
    # Limit length to reasonable size
    return sanitized[:10000]  # Limit to 10k characters


def calculate_story_metrics(state: GraphState) -> Dict[str, Any]:
    """Calculate various metrics about the story for display purposes."""
    total_words = sum(chapter.get('word_count', len(chapter.get('content', '').split()))
                      for chapter in state.chapters)

    total_chapters = len(state.chapters)

    # Calculate progress based on completed chapters vs. planned chapters
    planned_chapters = state.outline.get('total_chapters', 10)
    progress = min(100.0, (total_chapters / planned_chapters) * 100) if planned_chapters > 0 else 0

    # Other metrics
    character_count = len(state.characters)
    world_building_elements = len(state.world_details) if state.world_details else 0
    notes_count = len(state.story_notes)

    return {
        "total_words": total_words,
        "total_chapters": total_chapters,
        "story_progress": progress,
        "character_count": character_count,
        "world_building_count": world_building_elements,
        "notes_count": notes_count,
        "estimated_completion_days": calculate_estimated_completion(total_words, progress)
    }


def calculate_estimated_completion(current_words: int, progress: float) -> int:
    """Estimate days to completion based on current progress."""
    if progress <= 0:
        return 0

    # Assume 1000 words per day as a baseline for estimation
    baseline_daily = 1000
    daily_target = baseline_daily  # Could be adjusted based on project needs

    remaining_percentage = 100 - progress
    if remaining_percentage <= 0:
        return 0

    # Estimate remaining words
    estimated_total = current_words / (progress / 100) if progress > 0 else current_words * 2
    remaining_words = estimated_total - current_words

    # Days remaining
    days_remaining = remaining_words / daily_target

    # Round up to nearest day
    import math
    return math.ceil(days_remaining)


def export_story_to_format(state: GraphState, format_type: str = "json") -> str:
    """Export story to various formats."""
    if format_type.lower() == "json":
        story_data = serialize_graph_state(state)
        return json.dumps(story_data, indent=2)
    elif format_type.lower() == "txt":
        # Create a plain text format
        output = f"Title: {state.title}\n"
        output += f"Status: {state.story_status}\n\n"

        for chapter in state.chapters:
            output += f"Chapter {chapter.get('number', '')} - {chapter.get('title', '')}\n"
            output += f"{'='*50}\n{chapter.get('content', '')}\n\n"

        output += "Characters:\n"
        for name, details in state.characters.items():
            output += f"- {name}: {details}\n"

        return output
    elif format_type.lower() == "markdown":
        # Create a markdown format
        output = f"# {state.title}\n\n"
        output += f"**Status**: {state.story_status}\n\n"

        for chapter in state.chapters:
            output += f"## Chapter {chapter.get('number', '')} - {chapter.get('title', '')}\n\n"
            output += f"{chapter.get('content', '')}\n\n"

        output += "## Characters\n\n"
        for name, details in state.characters.items():
            output += f"- **{name}**: {details}\n\n"

        return output
    else:
        raise ValueError(f"Unsupported format: {format_type}")


def import_story_from_json(json_str: str) -> GraphState:
    """Import story from JSON string."""
    data = json.loads(json_str)
    return GraphState(**data)


def create_sample_story_data() -> GraphState:
    """Create sample story data for testing."""
    return GraphState(
        title="Sample Story",
        current_chapter="This is a sample chapter to demonstrate the UI functionality.",
        chapters=[
            {
                "number": 1,
                "title": "The Beginning",
                "content": "It was a bright cold day in April, and the clocks were striking thirteen...",
                "word_count": 1000,
                "completed_at_iteration": 1
            }
        ],
        outline={
            "initial_outline": "A short story for interface testing",
            "current_chapter_outline": {"chapter_number": 1, "title": "The Beginning"},
            "total_chapters": 3
        },
        characters={
            "Protagonist": {"name": "Sample Protagonist", "role": "Main Character"}
        },
        world_details={"locations": ["Test Location"], "culture": "Test Culture"},
        story_status="in_progress",
        story_notes=["Sample note for testing interfaces"],
        current_phase="writing"
    )