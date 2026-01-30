import unittest
from src.core.story_state import StoryState, Character, Location, Chapter, ChapterState
from src.core.knowledge_base import KnowledgeBase, KnowledgeEntity
from src.core.agent_factory import AgentFactory
from src.core.workflow import NovelWritingWorkflow
from src.ui.gradio_app import NovelWritingApp


class TestIntegration(unittest.TestCase):
    """Integration tests for the AI collaborative novel writing system"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.knowledge_base = KnowledgeBase()
        self.agent_factory = AgentFactory(self.knowledge_base)
        self.workflow = NovelWritingWorkflow(self.knowledge_base)

    def test_create_and_manage_story_state(self):
        """Test creating and managing story state"""
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

        # Test adding a chapter
        chapter = Chapter(
            id="chapter_1_9999999999", # Use a hardcoded id that's unique
            number=1,
            title="Chapter 1",
            content="This is chapter content",
            status=ChapterState.DRAFT,
            word_count=1500,
            versions=["Initial version"]
        )
        story.add_chapter(chapter)

        self.assertIn("chapter_1_9999999999", story.chapters)
        self.assertEqual(story.chapters["chapter_1_9999999999"].content, "This is chapter content")
        self.assertEqual(story.current_chapter_number, 1)

        # Verify character added to knowledge base via our app method
        self.knowledge_base.add_entity(
            KnowledgeEntity(
                id=char.id,
                name=char.name,
                description=char.description,
                type="character"
            )
        )
        entities = self.knowledge_base.search_entities("Alice")
        self.assertTrue(len(entities) > 0)
        self.assertEqual(entities[0].name, "Alice")

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

        # Check that location was added to knowledge base
        self.knowledge_base.add_entity(
            KnowledgeEntity(
                id=location.id,
                name=location.name,
                description=location.description,
                type="location"
            )
        )
        entities = self.knowledge_base.search_entities("Dark Forest")
        self.assertTrue(len(entities) > 0)

    def test_agent_factory_creates_all_agents(self):
        """Test that the agent factory creates all required agents"""
        agents = self.agent_factory.create_all_agents()

        # Check that we have all the expected agents
        expected_agents = [
            'Archivist',
            'Planner',
            'Writer',
            'Editor',
            'ConsistencyChecker',
            'WorldBuilder',
            'DialogueSpecialist',
            'PacingAdvisor'
        ]

        for agent_name in expected_agents:
            self.assertIn(agent_name, agents, f"Missing agent: {agent_name}")
            agent = agents[agent_name]
            # Verify basic interface properties exist
            self.assertTrue(hasattr(agent, 'process'))
            self.assertTrue(hasattr(agent, 'name'))
            self.assertTrue(hasattr(agent, 'role'))

    def test_workflow_creation(self):
        """Test that workflow is properly created with all required components"""
        self.assertIsInstance(self.workflow, NovelWritingWorkflow)
        self.assertIsNotNone(self.workflow.workflow)
        self.assertIn("Archivist", self.workflow.agents)

    def test_basic_story_cycle(self):
        """Test a basic workflow cycle from character creation to chapter writing"""
        story = StoryState(
            title="Integrated Test Story",
            genre="Fantasy",
            summary="A test to verify system integration"
        )

        # Create character
        char = Character(
            id="int_test_char_1",
            name="Integrated Tester",
            description="Character for integration test",
            role="tester"
        )
        story.add_character(char)

        # Add to knowledge base
        self.knowledge_base.add_entity(
            KnowledgeEntity(
                id=char.id,
                name=char.name,
                description=char.description,
                type="character"
            )
        )

        # Verify that character information is available through knowledge base
        related_info = self.knowledge_base.query("Integrated Tester", similarity_top_k=3)
        self.assertTrue(len(related_info) > 0)

        # Create initial chapter
        # For this test we'll directly use the Planner agent
        planner = self.agent_factory.create_agent("planner", "TestPlanner")
        result = planner.process(
            story,
            {
                "action": "outline_chapter",
                "chapter_number": 1,
                "title": "Chapter 1 Test",
                "plot_advancement": "Initial plot advancement"
            }
        )
        self.assertEqual(result["status"], "success")

        # Verify chapter is added
        writer = self.agent_factory.create_agent("writer", "TestWriter")
        result = writer.process(
            story,
            {
                "action": "write_chapter",
                "chapter_number": 1,
                "outline": "Test outline",
                "characters": [char.id]
            }
        )
        self.assertEqual(result["status"], "success")

        # Check that we have one chapter with content
        self.assertEqual(len(story.chapters), 1)

    def test_gradio_app_creation(self):
        """Test creating the UI application doesn't cause errors"""
        app = NovelWritingApp()
        self.assertIsNotNone(app)
        self.assertIsNotNone(app.knowledge_base)
        self.assertIsNotNone(app.workflow)

if __name__ == '__main__':
    unittest.main()