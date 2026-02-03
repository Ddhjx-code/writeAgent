from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel
from ..novel_types import StoryState, AgentResponse
import json


class GraphState(BaseModel):
    """Represents the state of the LangGraph workflow for the novel writing system."""

    # Core story information
    title: str
    current_chapter: str = ""
    chapters: List[Dict[str, Any]] = []
    outline: Dict[str, Any] = {}
    characters: Dict[str, Any] = {}
    world_details: Dict[str, Any] = {}
    story_status: str = "draft"  # draft, in_progress, complete, etc.

    # System state tracking
    agent_responses: List[AgentResponse] = []
    story_notes: List[str] = []
    next_agent: str = "planner"  # Which agent should run next
    iteration_count: int = 0
    max_iterations: int = 50

    # Knowledge base integration
    knowledge_queries: List[str] = []
    retrieved_knowledge: List[Dict[str, Any]] = []

    # Workflow-specific tracking
    current_phase: str = "planning"  # planning, writing, editing, review
    error_count: int = 0
    last_error: Optional[str] = None

    # Human feedback integration
    human_feedback: List[Dict[str, Any]] = []
    needs_human_review: bool = False
    human_review_status: str = "pending"  # pending, approved, rejected, not_needed

    # Story-specific tracking
    completed_chapters: List[int] = []
    current_chapter_index: int = 0
    story_arc_progress: float = 0.0

    # Agent-specific information
    current_agent_output: Optional[str] = None
    agent_execution_log: List[Dict[str, Any]] = []

    def get_agent_context(self) -> Dict[str, Any]:
        """Return the current context for agents to work with."""
        return {
            "title": self.title,
            "current_chapter": self.current_chapter,
            "chapters": self.chapters,
            "outline": self.outline,
            "characters": self.characters,
            "world_details": self.world_details,
            "story_status": self.story_status,
            "story_notes": self.story_notes,
            "current_phase": self.current_phase,
            "agent_responses": [resp.dict() for resp in self.agent_responses],
            "retrieved_knowledge": self.retrieved_knowledge,
            "human_feedback": self.human_feedback
        }

    def to_story_state(self) -> StoryState:
        """Convert GraphState to StoryState for compatibility with agents."""
        return StoryState(
            title=self.title,
            current_chapter=self.current_chapter,
            chapters=self.chapters,
            outline=self.outline,
            characters=self.characters,
            world_details=self.world_details,
            story_status=self.story_status,
            notes=self.story_notes
        )

    def from_story_state(self, story_state: StoryState):
        """Update GraphState from StoryState."""
        self.title = story_state.title
        self.current_chapter = story_state.current_chapter
        self.chapters = story_state.chapters
        self.outline = story_state.outline
        self.characters = story_state.characters
        self.world_details = story_state.world_details
        self.story_status = story_state.story_status
        self.story_notes = story_state.notes

    def add_chapter(self, chapter_content: str, chapter_number: int, title: str):
        """Add a new chapter to the story."""
        chapter = {
            "number": chapter_number,
            "title": title,
            "content": chapter_content,
            "word_count": len(chapter_content.split()),
            "completed_at_iteration": self.iteration_count
        }
        if chapter_number > len(self.chapters):
            self.chapters.append(chapter)
        else:
            # Replace if it already exists
            for i, chap in enumerate(self.chapters):
                if chap["number"] == chapter_number:
                    self.chapters[i] = chapter
                    break
            else:
                self.chapters.append(chapter)

        self.completed_chapters.append(chapter_number)
        self.current_chapter_index = chapter_number

    def add_agent_response(self, response: AgentResponse):
        """Add an agent response to the history."""
        self.agent_responses.append(response)

    def has_error(self) -> bool:
        """Check if the current state contains an error."""
        return self.error_count > 0

    def should_continue(self) -> bool:
        """Determine if the workflow should continue iterating."""
        # Continue unless we exceed max iterations, complete the story, or have too many errors
        return (
            self.iteration_count < self.max_iterations and
            self.story_status != "complete" and
            self.error_count < 5  # Stop after 5 errors
        )