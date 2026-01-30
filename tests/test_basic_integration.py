import unittest
from src.core.story_state import StoryState, Character, Location, Chapter, ChapterState
from src.core.agent_factory import AgentFactory
from src.ui.gradio_app import NovelWritingApp


class TestBasicIntegration(unittest.TestCase):
    """Basic integration tests that don't require external dependencies"""

    def test_create_and_manage_story_state(self):
        """Test creating and managing story state without external dependencies"""
        # Create a story state
        story = StoryState(
            title="Test Story",
            genre="Fantasy",
            summary="A fantasy adventure",
            target_chapter_count=3
        )

        # Test initial state
        self.assertEqual(story.title, "Test Story")
        self.assertEqual(story.genre, "Fantasy")
        self.assertEqual(story.summary, "A fantasy adventure")
        self.assertEqual(story.target_chapter_count, 3)

        # Test adding a character
        char = Character(
            id="char_1",
            name="Alice",
            description="Main hero",
            role="protagonist"
        )
        story.add_character(char)

        self.assertIn("char_1", story.characters)
        self.assertEqual(story.characters["char_1"].name, "Alice")

        # Test updating a character
        char.description = "Main hero and dragon slayer"
        story.update_character("char_1", char)
        self.assertEqual(story.characters["char_1"].description, "Main hero and dragon slayer")

        # Test adding and managing chapters
        chapter = Chapter(
            id="chapter_1_99999",
            number=1,
            title="Chapter 1",
            content="This is chapter content",
            status=ChapterState.DRAFT,
            word_count=1500,
            versions=["Initial version"]
        )
        story.add_chapter(chapter)

        self.assertIn("chapter_1_99999", story.chapters)
        self.assertEqual(story.chapters["chapter_1_99999"].content, "This is chapter content")
        self.assertEqual(story.current_chapter_number, 1)

        # Test chapter status updates
        story.set_chapter_status("chapter_1_99999", ChapterState.COMPLETED)
        self.assertEqual(story.chapters["chapter_1_99999"].status, ChapterState.COMPLETED)

    def test_create_locations(self):
        """Test creating and managing locations"""
        story = StoryState()

        # Add a location
        location = Location(
            id="loc_1",
            name="Dark Forest",
            description="A mysterious forest",
            type="forest",
            significance="Main setting"
        )
        story.add_location(location)

        # Check that location was added
        self.assertIn("loc_1", story.locations)
        self.assertEqual(story.locations["loc_1"].name, "Dark Forest")
        self.assertEqual(story.locations["loc_1"].description, "A mysterious forest")

    def test_agent_factory_basic(self):
        """Test creating agents with minimal dependencies"""
        from src.core.knowledge_base import KnowledgeBase
        knowledge_base = KnowledgeBase()
        agent_factory = AgentFactory(knowledge_base)

        # Test creation of agents with mock LLM configuration
        planner = agent_factory.create_agent(
            "planner",
            "TestPlanner",
            role="Planner Agent",
            llm_config={},
            system_message="Test Planner System Message"
        )

        self.assertIsNotNone(planner)
        self.assertEqual(planner.name, "TestPlanner")

        writer = agent_factory.create_agent(
            "writer",
            "TestWriter",
            role="Writer Agent",
            llm_config={},
            system_message="Test Writer System Message"
        )

        self.assertIsNotNone(writer)
        self.assertEqual(writer.name, "TestWriter")

    def test_gradio_app_creation(self):
        """Test creating the UI application doesn't cause immediate errors with basic components"""
        try:
            app = NovelWritingApp()
            self.assertIsNotNone(app)
            self.assertIsNotNone(app.current_story_state)  # Should have default story state
        except ImportError as e:
            # If there's an import issue with Gradio specifically
            print(f"Import issue: {e}")
            self.fail(f"Failed to create NovelWritingApp: {e}")

    def test_comprehensive_story_creation(self):
        """Test using all core modules together in a story creation workflow"""
        story = StoryState(
            title="Comprehensive Test",
            genre="Science Fiction",
            summary="A story testing all core components working together"
        )

        # Add multiple characters
        characters_data = [
            {"id": "protag", "name": "Alex", "role": "Protagonist", "desc": "Main character"},
            {"id": "antag", "name": "Valerie", "role": "Antagonist", "desc": "Main opponent"},
            {"id": "mentor", "name": "Dr. Chen", "role": "Mentor", "desc": "Wise advisor"}
        ]

        for char_data in characters_data:
            character = Character(
                id=char_data["id"],
                name=char_data["name"],
                description=char_data["desc"],
                role=char_data["role"]
            )
            story.add_character(character)

        # Add locations
        locations_data = [
            {"id": "city", "name": "Neo-Tokyo", "type": "city", "desc": "Futuristic metropolis"},
            {"id": "lab", "name": "Research Lab", "type": "facility", "desc": "Secret research facility"}
        ]

        for loc_data in locations_data:
            location = Location(
                id=loc_data["id"],
                name=loc_data["name"],
                description=loc_data["desc"],
                type=loc_data["type"],
                significance="Important to plot"
            )
            story.add_location(location)

        # Verify all elements are in place
        self.assertEqual(len(story.characters), 3)
        self.assertIn("protag", story.characters)
        self.assertEqual(story.characters["protag"].name, "Alex")

        self.assertEqual(len(story.locations), 2)
        self.assertIn("city", story.locations)
        self.assertEqual(story.locations["city"].name, "Neo-Tokyo")

        # Add some chapters
        chapter = Chapter(
            id="cpt_sci_fi_1",
            number=1,
            title="First Contact",
            content="In the neon-lit streets of Neo-Tokyo, Alex encountered the first signs of alien life.",
            status=ChapterState.DRAFT
        )
        story.add_chapter(chapter)

        self.assertEqual(story.current_chapter_number, 1)
        self.assertIn("cpt_sci_fi_1", story.chapters)

        # Update chapter status
        story.set_chapter_status("cpt_sci_fi_1", ChapterState.APPROVED)
        self.assertEqual(
            story.chapters["cpt_sci_fi_1"].status,
            ChapterState.APPROVED
        )

        # Verify story properties
        self.assertEqual(story.title, "Comprehensive Test")
        self.assertEqual(story.genre, "Science Fiction")
        self.assertEqual(story.status, "planning")  # Default initial status


if __name__ == '__main__':
    unittest.main()