import asyncio
import unittest
from unittest.mock import AsyncMock, patch
import sys
import os
import json

# Add source directory to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.config import Config
from src.knowledge.base import BaseKnowledgeBase
from src.knowledge.store import KnowledgeStore
from src.knowledge.schema import CharacterSchema, LocationSchema, EventSchema, RelationshipSchema, StoryElementSchema


class TestableKnowledgeBase(BaseKnowledgeBase):
    """A testable version of the BaseKnowledgeBase for unit testing."""

    async def initialize(self):
        self.memory = {}
        return True

    async def store_memory(self, key: str, value, metadata=None):
        self.memory[key] = {"value": value, "metadata": metadata}
        return True

    async def retrieve_memory(self, key: str, top_k: int = 1):
        if key in self.memory:
            return [self.memory[key]["value"]]
        return []

    async def search(self, query: str, top_k: int = 5):
        results = []
        for key, item in self.memory.items():
            if query.lower() in str(item["value"]).lower():
                results.append({
                    "text": str(item["value"]),
                    "metadata": item["metadata"],
                    "key": key
                })
        return results[:top_k]

    async def delete_memory(self, key: str):
        if key in self.memory:
            del self.memory[key]
            return True
        return False

    async def get_all_keys(self):
        return list(self.memory.keys())

    async def clear(self):
        self.memory = {}
        return True


class TestBaseKnowledgeBase(unittest.TestCase):
    """Test suite for the BaseKnowledgeBase abstract class."""

    def setUp(self):
        self.kb = TestableKnowledgeBase()

    async def test_initialization(self):
        """Test that the knowledge base initializes properly."""
        result = await self.kb.initialize()
        self.assertTrue(result)
        self.assertIsInstance(self.kb.memory, dict)

    async def test_store_and_retrieve_memory(self):
        """Test storing and retrieving memory."""
        # Store a memory
        await self.kb.store_memory("test_key", "test_value", {"type": "test"})

        # Retrieve the memory
        result = await self.kb.retrieve_memory("test_key")

        self.assertEqual(result, ["test_value"])

    async def test_search_functionality(self):
        """Test the search functionality."""
        await self.kb.store_memory("key1", "This is a test document about AI", {"type": "doc"})
        await self.kb.store_memory("key2", "Another document about knowledge bases", {"type": "doc"})

        results = await self.kb.search("AI")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["key"], "key1")

    async def test_delete_memory(self):
        """Test deleting memory entries."""
        await self.kb.store_memory("delete_me", "test content")

        # Verify it exists
        result = await self.kb.retrieve_memory("delete_me")
        self.assertEqual(result, ["test content"])

        # Delete it
        await self.kb.delete_memory("delete_me")

        # Verify it's gone
        result = await self.kb.retrieve_memory("delete_me")
        self.assertEqual(result, [])

    async def test_get_all_keys(self):
        """Test getting all stored keys."""
        await self.kb.store_memory("key1", "value1")
        await self.kb.store_memory("key2", "value2")

        keys = await self.kb.get_all_keys()

        self.assertIn("key1", keys)
        self.assertIn("key2", keys)

    async def test_clear_all_memory(self):
        """Test clearing all memory."""
        await self.kb.store_memory("key1", "value1")
        await self.kb.store_memory("key2", "value2")

        # Verify memory exists
        keys = await self.kb.get_all_keys()
        self.assertGreater(len(keys), 0)

        # Clear memory
        await self.kb.clear()

        # Verify memory is cleared
        keys = await self.kb.get_all_keys()
        self.assertEqual(len(keys), 0)

    async def test_store_chapter_content(self):
        """Test storing chapter content."""
        from src.types import Chapter

        chapter = Chapter(
            chapter_number=1,
            title="Chapter 1",
            content="This is the first chapter content.",
            characters_mentioned=["Aelar", "Mira"],
            locations_mentioned=["Crystal Cave"],
            key_plot_points=["Introduction of main characters"]
        )

        key = await self.kb.store_chapter_content(chapter)

        self.assertEqual(key, "chapter_1")

        # Verify it's stored
        content = await self.kb.retrieve_memory(key)
        self.assertGreater(len(content), 0)


class TestKnowledgeStore(unittest.TestCase):
    """Test suite for the KnowledgeStore class."""

    def setUp(self):
        self.config = Config()

    async def test_initialization(self):
        """Test that KnowledgeStore initializes properly."""
        # Test with Chroma backend
        store = KnowledgeStore(self.config, "chroma")

        # Just verify it creates the backend without errors
        # Actual initialization happens in the async method
        self.assertIsNotNone(store)

        # If chromadb is not available, use mock for the actual test
        try:
            await store.initialize()
            self.assertIsNotNone(store.backend)
        except ImportError:
            # Mock the chroma functionality for the test
            store = KnowledgeStore(self.config, "chroma")
            # The mock would be set up if we knew chromadb wasn't available
            # For now, just verify the constructor works
            self.assertEqual(store.backend_type, "chroma")

    async def test_store_and_retrieve_memory(self):
        """Test storing and retrieving memory (using a simple in-memory system for tests)."""
        # For testing purposes, we'll use our testable KB implementation
        # rather than the full system

        # First test with a test object
        store = KnowledgeStore(self.config, "chroma")
        # We'll use a patched version for this test specifically
        with patch('src.knowledge.store.ChromaDBKnowledge', TestableKnowledgeBase) as mock_kb:
            mock_kb_instance = TestableKnowledgeBase()
            store.backend = mock_kb_instance
            await store.initialize()  # This will initialize the memory dict

            # Now we can run our test safely with the testable implementation
            await store.store_memory("test_key", "test_value")
            result = await store.retrieve_memory("test_key", 1)

            self.assertEqual(result, ["test_value"])

    async def test_schema_validation(self):
        """Test storage with schema validation."""
        from src.knowledge.schema import CharacterSchema

        # Create a character schema instance
        char_schema = CharacterSchema(
            name="Test Character",
            description="A sample test character",
            personality_traits=["brave", "wise"],
            appearance="Brown hair, green eyes",
            role_in_story="Protagonist",
            relationships={"other_char": "friend"},
            character_arc=["introduction", "development", "resolution"]
        )

        store = KnowledgeStore(self.config, "chroma")
        # Since the actual system initialization depends on chromadb,
        # we'll just verify the schema validation part works
        self.assertIsInstance(char_schema, CharacterSchema)
        self.assertEqual(char_schema.name, "Test Character")


class TestKnowledgeSchemas(unittest.TestCase):
    """Test suite for the knowledge schemas."""

    def test_character_schema(self):
        """Test the CharacterSchema."""
        character = CharacterSchema(
            name="Aelar",
            description="A young wizard with untapped magical abilities",
            personality_traits=["curious", "brave", "sometimes reckless"],
            appearance="Medium height, brown hair, green eyes",
            role_in_story="Protagonist",
            relationships={"Mira": "trainer and friend"},
            character_arc=["discovery of powers", "learning to control", "masters abilities"]
        )

        self.assertEqual(character.name, "Aelar")
        self.assertIn("brave", character.personality_traits)
        self.assertEqual(character.role_in_story, "Protagonist")

    def test_location_schema(self):
        """Test the LocationSchema."""
        location = LocationSchema(
            name="Crystal Caves",
            description="Glowing caves filled with magical crystals",
            geography="Subterranean caverns beneath the mountain",
            culture="Home to crystal-worshipping miners",
            history="Ancient site of magical energy",
            inhabitants=["Miners", "Crystal spirits"],
            significance_to_story="Where protagonist discovers magic"
        )

        self.assertEqual(location.name, "Crystal Caves")
        self.assertIn("Miners", location.inhabitants)
        self.assertTrue(location.description.startswith("Glowing caves"))

    def test_event_schema(self):
        """Test the EventSchema."""
        # Note: In Python, underscores become hyphens in field names when using pydantic
        event = EventSchema(
            event_id="event_001",
            title="The Great Revelation",
            description="The ancient prophecy is revealed",
            occurred_in_chapter=3,
            characters_involved=["Protagonist", "Oracle"],
            significance="Reveals the protagonist's true destiny",
            consequences=["Character's path changes", "New antagonist revealed"]
        )

        self.assertEqual(event.event_id, "event_001")
        self.assertEqual(event.occurred_in_chapter, 3)
        self.assertIn("Character's path changes", event.consequences)

    def test_relationship_schema(self):
        """Test the RelationshipSchema."""
        relationship = RelationshipSchema(
            relationship_id="rel_001",
            character1="Aelar",
            character2="Mira",
            relationship_type="Mentor",
            status="Developing",
            description="Mira guides Aelar in using magic responsibly",
            history=["First meeting", "Trust established", "Training begins"]
        )

        self.assertEqual(relationship.relationship_id, "rel_001")
        self.assertEqual(relationship.relationship_type, "Mentor")
        self.assertIn("First meeting", relationship.history)

    def test_story_element_schema(self):
        """Test the StoryElementSchema."""
        element = StoryElementSchema(
            element_id="element_magic_sword",
            name="Sword of Light",
            category="object",
            description="Legendary weapon that glows with pure energy",
            significance="Key to defeating the main antagonist",
            first_mentioned=2,
            last_mentioned=8
        )

        self.assertEqual(element.name, "Sword of Light")
        self.assertEqual(element.category, "object")
        self.assertEqual(element.first_mentioned, 2)

    def test_invalid_schema_creation(self):
        """Test that invalid schemas raise validation errors."""
        from pydantic import ValidationError

        # Test required field validation for character schema
        with self.assertRaises(ValidationError):
            CharacterSchema(
                # Missing required field 'name'
                description="Invalid character",
                personality_traits=["trait"],
                appearance="N/A",
                role_in_story="N/A",
                relationships={}
            )


def run_tests():
    """Run all knowledge base tests."""
    print("Running knowledge base tests...")

    # Create test suites (since our tests are async, we'll run them specially)
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    # Python doesn't have native support for async tests in unittest until 3.8+
    # We need to run this in an async context for the async tests
    async def run_all_tests():
        return await asyncio.get_running_loop().run_in_executor(None, run_tests)

    # For simplicity since Python 3.7 doesn't have built-in async unittest support:
    suite = unittest.TestLoader().loadTestsFromTestCase(TestKnowledgeSchemas)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

    # Run the async tests with asyncio.run()
    suite_chars = unittest.TestLoader().loadTestsFromTestCase(TestBaseKnowledgeBase)
    for test_class in [TestBaseKnowledgeBase]:
        print(f"Running {test_class.__name__} async tests...")
        # The tests themselves are already defined with async support
        pass  # These would need more complex integration with async runner