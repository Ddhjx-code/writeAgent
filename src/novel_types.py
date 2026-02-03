from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class StoryState(BaseModel):
    """Current state of the story being written."""
    title: str
    current_chapter: str
    chapters: List[Dict[str, Any]]
    outline: Dict[str, Any]  # Story outline
    characters: Dict[str, Any]  # Character definitions
    world_details: Dict[str, Any]  # World building details
    story_status: str  # draft, in_progress, complete, etc.
    notes: List[str]  # Editorial notes


class AgentResponse(BaseModel):
    """Standardized response from an agent."""
    agent_name: str
    content: str
    reasoning: Optional[str] = None
    suggestions: Optional[List[str]] = None
    status: str  # success, failed, pending
    metadata: Optional[Dict[str, Any]] = None


class Message(BaseModel):
    """Standardized message format for communication."""
    sender: str
    receiver: str
    content: str
    message_type: str  # info, request, response, error
    timestamp: float
    metadata: Optional[Dict[str, Any]] = None


class Chapter(BaseModel):
    """Representation of a novel chapter."""
    chapter_number: int
    title: str
    content: str
    characters_mentioned: List[str]
    locations_mentioned: List[str]
    key_plot_points: List[str]