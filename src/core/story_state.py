from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import json


class ChapterState(str, Enum):
    """Enum representing the state of a chapter"""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION = "revision"
    COMPLETED = "completed"


class Character(BaseModel):
    """Represents a character in the story"""
    id: str
    name: str
    description: str
    role: str = ""
    personality_traits: List[str] = Field(default_factory=list)
    background: str = ""
    relationships: Dict[str, str] = Field(default_factory=dict)  # {other_character_id: relationship_type}
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Location(BaseModel):
    """Represents a location in the story"""
    id: str
    name: str
    description: str
    type: str = ""
    features: List[str] = Field(default_factory=list)
    significance: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PlotPoint(BaseModel):
    """Represents a significant plot point"""
    id: str
    title: str
    description: str
    type: str  # "inciting_incident", "rising_action", "climax", "resolution", etc.
    chapter: int
    order: int  # Order within the chapter
    consequences: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Chapter(BaseModel):
    """Represents a chapter in the story"""
    id: str
    number: int
    title: str
    content: str
    status: ChapterState
    word_count: int = 0
    characters_in_chapter: List[str] = Field(default_factory=list)  # Character IDs
    locations_in_chapter: List[str] = Field(default_factory=list)  # Location IDs
    plot_points: List[str] = Field(default_factory=list)  # Plot point IDs
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    versions: List[str] = Field(default_factory=list)  # List of content versions
    notes: str = ""


class StoryState(BaseModel):
    """
    Central state management for the novel writing process
    Stores all story elements, chapter data, and workflow state
    """
    id: str = Field(default_factory=lambda: f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    title: str = ""
    genre: str = ""
    summary: str = ""
    status: str = "planning"  # planning, writing, revising, completed

    # Story elements
    characters: Dict[str, Character] = Field(default_factory=dict)
    locations: Dict[str, Location] = Field(default_factory=dict)
    plot_points: Dict[str, PlotPoint] = Field(default_factory=dict)

    # Chapter management
    chapters: Dict[str, Chapter] = Field(default_factory=dict)
    current_chapter_number: int = 0
    target_chapter_count: int = 0

    # Timeline and pacing
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    # Workflow state
    current_stage: str = "planning"
    agent_work_queue: List[str] = Field(default_factory=list)  # List of agent IDs waiting to work
    revision_history: List[Dict[str, Any]] = Field(default_factory=list)

    # Meta information
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    version: int = 1

    def add_character(self, character: Character) -> str:
        """Add a character to the story state"""
        self.characters[character.id] = character
        self.updated_at = datetime.now()
        return character.id

    def get_character(self, character_id: str) -> Optional[Character]:
        """Get a character by ID"""
        return self.characters.get(character_id)

    def update_character(self, character_id: str, character: Character) -> bool:
        """Update an existing character"""
        if character_id in self.characters:
            self.characters[character_id] = character
            self.updated_at = datetime.now()
            return True
        return False

    def remove_character(self, character_id: str) -> bool:
        """Remove a character from the story"""
        if character_id in self.characters:
            del self.characters[character_id]
            self.updated_at = datetime.now()
            return True
        return False

    def add_location(self, location: Location) -> str:
        """Add a location to the story state"""
        self.locations[location.id] = location
        self.updated_at = datetime.now()
        return location.id

    def get_location(self, location_id: str) -> Optional[Location]:
        """Get a location by ID"""
        return self.locations.get(location_id)

    def update_location(self, location_id: str, location: Location) -> bool:
        """Update an existing location"""
        if location_id in self.locations:
            self.locations[location_id] = location
            self.updated_at = datetime.now()
            return True
        return False

    def add_plot_point(self, plot_point: PlotPoint) -> str:
        """Add a plot point to the story state"""
        self.plot_points[plot_point.id] = plot_point
        self.updated_at = datetime.now()
        return plot_point.id

    def add_chapter(self, chapter: Chapter) -> str:
        """Add a chapter to the story"""
        self.chapters[chapter.id] = chapter
        if chapter.number > self.current_chapter_number:
            self.current_chapter_number = chapter.number
        self.updated_at = datetime.now()
        return chapter.id

    def get_chapter(self, chapter_id: str) -> Optional[Chapter]:
        """Get a chapter by ID"""
        return self.chapters.get(chapter_id)

    def update_chapter_content(self, chapter_id: str, content: str) -> bool:
        """Update the content of a chapter"""
        chapter = self.chapters.get(chapter_id)
        if chapter:
            # Save current version to history
            chapter.versions.append(chapter.content)
            # Update content
            chapter.content = content
            chapter.word_count = len(content.split())
            chapter.updated_at = datetime.now()
            self.updated_at = datetime.now()
            return True
        return False

    def set_chapter_status(self, chapter_id: str, status: ChapterState) -> bool:
        """Update the status of a chapter"""
        chapter = self.chapters.get(chapter_id)
        if chapter:
            # Log the status change
            self.revision_history.append({
                "type": "chapter_status_update",
                "chapter_id": chapter_id,
                "old_status": chapter.status,
                "new_status": status,
                "timestamp": datetime.now()
            })

            chapter.status = status
            chapter.updated_at = datetime.now()
            self.updated_at = datetime.now()
            return True
        return False

    def get_characters_in_chapter(self, chapter_id: str) -> List[Character]:
        """Get all characters that appear in a specific chapter"""
        chapter = self.chapters.get(chapter_id)
        if not chapter:
            return []

        return [self.characters[chr_id] for chr_id in chapter.characters_in_chapter if chr_id in self.characters]

    def get_locations_in_chapter(self, chapter_id: str) -> List[Location]:
        """Get all locations that appear in a specific chapter"""
        chapter = self.chapters.get(chapter_id)
        if not chapter:
            return []

        return [self.locations[loc_id] for loc_id in chapter.locations_in_chapter if loc_id in self.locations]

    def to_json(self) -> str:
        """Serialize the story state to JSON"""
        return self.model_dump_json(indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'StoryState':
        """Create a StoryState instance from JSON string"""
        data = json.loads(json_str)
        return cls.model_validate(data)

    def get_chapters_by_status(self, status: ChapterState) -> List[Chapter]:
        """Get all chapters with a specific status"""
        return [chapter for chapter in self.chapters.values() if chapter.status == status]

    def get_next_chapter_number(self) -> int:
        """Get the next sequential chapter number"""
        return self.current_chapter_number + 1

    def increment_version(self):
        """Increment the state version"""
        self.version += 1
        self.updated_at = datetime.now()