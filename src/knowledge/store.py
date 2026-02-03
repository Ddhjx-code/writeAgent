from typing import Any, Dict, List, Optional, Union
from abc import abstractmethod
from .base import BaseKnowledgeBase
from .llamaindex_db import LlamaIndexKnowledge
from .chroma_db import ChromaDBKnowledge
from .schema import (
    CharacterSchema, LocationSchema, EventSchema,
    RelationshipSchema, StoryElementSchema, ChapterIndexSchema,
    StoryIndexSchema, QuerySchema, SearchResultSchema
)
from ..novel_types import Chapter
from ..config import Config


class KnowledgeStore:
    """Main knowledge store interface that handles multiple knowledge base backends."""

    def __init__(self, config: Config, backend_type: str = "chroma"):
        self.config = config
        self.backend_type = backend_type
        self.backend = self._initialize_backend(backend_type)

    async def initialize(self):
        """Initialize the selected knowledge base backend."""
        await self.backend.initialize()

    def _initialize_backend(self, backend_type: str) -> BaseKnowledgeBase:
        """Initialize the appropriate knowledge base backend."""
        if backend_type.lower() == "llamaindex":
            return LlamaIndexKnowledge(self.config)
        elif backend_type.lower() == "chroma":
            return ChromaDBKnowledge(self.config)
        else:
            raise ValueError(f"Unsupported backend type: {backend_type}")

    async def store_memory(self, key: str, value: Any, metadata: Optional[Dict] = None):
        """Store a memory in the knowledge base."""
        await self.backend.store_memory(key, value, metadata)

    async def retrieve_memory(self, key: str, top_k: int = 1) -> List[Any]:
        """Retrieve memories from the knowledge base."""
        return await self.backend.retrieve_memory(key, top_k)

    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant information in the knowledge base."""
        return await self.backend.search(query, top_k)

    async def delete_memory(self, key: str):
        """Delete a memory from the knowledge base."""
        await self.backend.delete_memory(key)

    async def get_all_keys(self) -> List[str]:
        """Get all stored memory keys."""
        return await self.backend.get_all_keys()

    async def clear(self):
        """Clear all memories from the knowledge base."""
        await self.backend.clear()

    async def store_chapter_content(self, chapter: Chapter) -> str:
        """Store chapter content in the knowledge base."""
        return await self.backend.store_chapter_content(chapter)

    # Specialized storage methods for the writing process
    async def store_character_info(self, character_schema: CharacterSchema):
        """Store character information with validation."""
        import json
        character_dict = character_schema.dict()
        await self.store_memory(f"character_{character_schema.name}", character_dict)

    async def store_location_info(self, location_schema: LocationSchema):
        """Store location information with validation."""
        import json
        location_dict = location_schema.dict()
        await self.store_memory(f"location_{location_schema.name}", location_dict)

    async def store_event_info(self, event_schema: EventSchema):
        """Store event information with validation."""
        import json
        event_dict = event_schema.dict()
        await self.store_memory(f"event_{event_schema.event_id}", event_dict)

    async def store_relationship_info(self, relationship_schema: RelationshipSchema):
        """Store relationship information with validation."""
        import json
        relationship_dict = relationship_schema.dict()
        await self.store_memory(f"relationship_{relationship_schema.relationship_id}", relationship_dict)

    async def store_story_element_info(self, story_element_schema: StoryElementSchema):
        """Store story element information with validation."""
        import json
        element_dict = story_element_schema.dict()
        key = f"element_{story_element_schema.element_id}"
        if story_element_schema.category:
            key = f"{story_element_schema.category}_{story_element_schema.name}"
        await self.store_memory(key, element_dict)

    async def store_chapter_index(self, chapter_index_schema: ChapterIndexSchema):
        """Store chapter index with validation."""
        import json
        index_dict = chapter_index_schema.dict()
        await self.store_memory(f"chapter_index_{chapter_index_schema.chapter_number}", index_dict)

    async def update_story_index(self, story_index_schema: StoryIndexSchema):
        """Update the overall story index."""
        import json
        index_dict = story_index_schema.dict()
        await self.store_memory(f"story_index_{story_index_schema.title.replace(' ', '_').lower()}", index_dict)

    # Retrieval methods
    async def get_character_info(self, character_name: str) -> Union[CharacterSchema, None]:
        """Retrieve character information."""
        results = await self.retrieve_memory(f"character_{character_name}")
        if results:
            import json
            try:
                return CharacterSchema(**json.loads(results[0]))
            except (json.JSONDecodeError, TypeError):
                # If it's already a dict-like structure
                pass
        return None

    async def get_location_info(self, location_name: str) -> Union[LocationSchema, None]:
        """Retrieve location information."""
        results = await self.retrieve_memory(f"location_{location_name}")
        if results:
            import json
            try:
                return LocationSchema(**json.loads(results[0]))
            except (json.JSONDecodeError, TypeError):
                # If it's already a dict-like structure
                pass
        return None

    async def search_by_category(self, category: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for items by category."""
        if category == "characters":
            return await self.search(query, top_k)
        elif category == "locations":
            return await self.search(query, top_k)
        # Additional categories can be added here
        else:
            return await self.search(query, top_k)

    # Search with filtering support for ChromaDB backend
    async def advanced_search(self, query_schema: QuerySchema) -> SearchResultSchema:
        """Perform advanced search with filters."""
        import time
        start_time = time.time()

        results = await self.search(query_schema.query_text, query_schema.top_k)

        query_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Apply any additional filtering based on filters in query_schema
        if query_schema.filters:
            # This would apply additional filtering based on the backend's capabilities
            # For now we use a basic implementation
            if self.backend_type == "chroma":
                try:
                    # ChromaDB supports metadata based searching
                    filtered_results = await self.backend.search_by_metadata(
                        query_schema.filters,
                        query_schema.top_k
                    )
                    results = filtered_results
                except AttributeError:
                    # If backend doesn't support metadata search, skip for now
                    pass

        return SearchResultSchema(
            query=query_schema,
            results=results,
            total_found=len(results),
            query_time_ms=query_time
        )

    async def get_backend_status(self) -> Dict[str, str]:
        """Get status information about the active backend."""
        if self.backend_type == "chroma":
            return {
                "backend": "ChromaDB",
                "status": "active",
                "persist_dir": self.config.chroma_persist_dir,
                "total_records": len(await self.get_all_keys())
            }
        elif self.backend_type == "llamaindex":
            return {
                "backend": "LlamaIndex",
                "status": "active",
                "persist_dir": self.config.llamaindex_storage_dir,
                "total_records": len(await self.get_all_keys())
            }
        else:
            return {
                "backend": "Unknown",
                "status": "inactive",
                "total_records": 0
            }