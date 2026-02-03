from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from ..novel_types import Chapter


class BaseKnowledgeBase(ABC):
    """Base class for all knowledge base implementations in the novel writing system."""

    @abstractmethod
    async def initialize(self):
        """Initialize the knowledge base."""
        pass

    @abstractmethod
    async def store_memory(self, key: str, value: Any, metadata: Optional[Dict] = None):
        """Store a memory in the knowledge base."""
        pass

    @abstractmethod
    async def retrieve_memory(self, key: str, top_k: int = 1) -> List[Any]:
        """Retrieve memories from the knowledge base."""
        pass

    @abstractmethod
    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant information in the knowledge base."""
        pass

    @abstractmethod
    async def delete_memory(self, key: str):
        """Delete a memory from the knowledge base."""
        pass

    @abstractmethod
    async def get_all_keys(self) -> List[str]:
        """Get all stored memory keys."""
        pass

    @abstractmethod
    async def clear(self):
        """Clear all memories from the knowledge base."""
        pass

    async def store_chapter_content(self, chapter: Chapter) -> str:
        """Store chapter content in the knowledge base."""
        content_summary = f"""
        Chapter {chapter.chapter_number}: {chapter.title}
        Content: {chapter.content}
        Characters mentioned: {', '.join(chapter.characters_mentioned)}
        Locations mentioned: {', '.join(chapter.locations_mentioned)}
        Key plot points: {', '.join(chapter.key_plot_points)}
        """
        await self.store_memory(f"chapter_{chapter.chapter_number}", content_summary)
        return f"chapter_{chapter.chapter_number}"

    async def store_character_info(self, character_name: str, character_info: Dict[str, Any]):
        """Store character information in the knowledge base."""
        await self.store_memory(f"character_{character_name}", character_info)

    async def store_world_building_info(self, aspect_name: str, aspect_info: Dict[str, Any]):
        """Store world building information in the knowledge base."""
        await self.store_memory(f"world_{aspect_name}", aspect_info)

    async def store_story_outline(self, outline: Dict[str, Any]):
        """Store the story outline in the knowledge base."""
        await self.store_memory("story_outline", outline)