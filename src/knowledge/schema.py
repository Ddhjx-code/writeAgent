from typing import Dict, List, Optional
from pydantic import BaseModel
from typing import Any
from pydantic import BaseModel


class CharacterSchema(BaseModel):
    """Schema for character information stored in the knowledge base."""
    name: str
    description: str
    personality_traits: List[str]
    appearance: str
    role_in_story: str
    relationships: Dict[str, str]  # Relationship description to other characters
    character_arc: Optional[List[str]] = None  # Major changes throughout the story


class LocationSchema(BaseModel):
    """Schema for location/world building information."""
    name: str
    description: str
    geography: str
    culture: str
    history: str
    inhabitants: List[str]
    significance_to_story: str


class EventSchema(BaseModel):
    """Schema for significant story events."""
    event_id: str
    title: str
    description: str
    occurred_in_chapter: Optional[int]
    characters_involved: List[str]
    significance: str  # Importance to overall story
    consequences: List[str]  # What changes as a result


class RelationshipSchema(BaseModel):
    """Schema for character relationships."""
    relationship_id: str
    character1: str
    character2: str
    relationship_type: str  # friend, enemy, romantic, family, etc.
    status: str  # current status of the relationship
    description: str
    history: List[str]  # Major developments in the relationship


class StoryElementSchema(BaseModel):
    """Schema for general story elements like objects, concepts, etc."""
    element_id: str
    name: str
    category: str  # 'object', 'concept', 'ability', etc.
    description: str
    significance: str
    first_mentioned: Optional[int]  # Chapter number
    last_mentioned: Optional[int]  # Chapter number


class ChapterIndexSchema(BaseModel):
    """Schema for chapter-level information in the knowledge base."""
    chapter_number: int
    title: str
    word_count: int
    characters_mentioned: List[str]
    locations_mentioned: List[str]
    key_events: List[str]
    themes_explored: List[str]
    pov_characters: List[str]
    chapter_summary: str
    related_chapters: List[int]  # Chapter numbers that are closely related


class StoryIndexSchema(BaseModel):
    """Schema for overall story indexing."""
    title: str
    author: str
    status: str  # draft, in_progress, completed, etc.
    genre: str
    total_chapters: int
    total_words: int
    characters: List[str]
    locations: List[str]
    themes: List[str]
    major_plot_lines: List[str]
    creation_date: str
    last_updated: str


class QuerySchema(BaseModel):
    """Schema for knowledge base queries."""
    query_type: str  # 'character', 'location', 'event', 'content', etc.
    query_text: str
    filters: Optional[Dict[str, Any]] = None
    top_k: int = 5


class SearchResultSchema(BaseModel):
    """Schema for knowledge base search results."""
    query: QuerySchema
    results: List[Dict[str, Any]]
    total_found: int
    query_time_ms: float