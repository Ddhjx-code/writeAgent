from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class StoryConfig(BaseModel):
    title: str
    genre: str
    description: str
    target_length: int
    outline: Optional[str] = None
    chapters_count: Optional[int] = 10
    pov_character: Optional[str] = None
    characters: Optional[List[Dict[str, Any]]] = []
    world_details: Optional[Dict[str, Any]] = {}
    themes: Optional[List[str]] = []
    notes: Optional[List[str]] = []

class CharacterInfo(BaseModel):
    id: str
    name: str
    role: str
    description: str
    personality_traits: Optional[List[str]] = []

class ChapterInfo(BaseModel):
    id: str
    number: int
    title: str
    content: str
    word_count: int
    status: str

class StoryStateResponse(BaseModel):
    id: str
    title: str
    description: str
    current_chapter: int
    total_chapters: int
    status: str
    characters: List[CharacterInfo]
    chapters: List[ChapterInfo]
    created_at: str
    updated_at: str

class AgentStatus(BaseModel):
    id: str
    name: str
    status: str
    role: str
    active: bool
    tasks: List[str]

class SystemStatus(BaseModel):
    engine_state: str
    is_running: bool
    current_story: Optional[str]
    knowledge_store_status: Optional[Dict[str, Any]]
    timestamp: str

class AgentMessage(BaseModel):
    agent_id: str
    agent_name: str
    message: str
    timestamp: str
    level: str = "info"  # info, warning, error

class StoryProgress(BaseModel):
    current_chapter: int
    total_chapters: int
    progress_percentage: float
    status: str
    current_phase: str
    last_updated: str