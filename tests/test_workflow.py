import asyncio
import unittest
from unittest.mock import AsyncMock, patch
import sys
import os
import json

# Add source directory to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.config import Config
from src.workflow.state import GraphState
from src.workflow.graph import NovelWritingGraph
from src.workflow.nodes import NodeManager
from src.knowledge.store import KnowledgeStore


class TestGraphState(unittest.TestCase):
    """Test suite for the GraphState class."""

    def setUp(self):
        self.config = Config()

    def test_initialization_defaults(self):
        """Test that GraphState initializes with proper defaults."""
        state = GraphState(title="Test Story")

        self.assertEqual(state.title, "Test Story")
        self.assertEqual(state.story_status, "draft")
        self.assertEqual(state.current_phase, "planning")
        self.assertEqual(state.iteration_count, 0)
        self.assertEqual(state.error_count, 0)
        self.assertIsInstance(state.chapters, list)
        self.assertIsInstance(state.characters, dict)
        self.assertIsInstance(state.agent_responses, list)

    def test_add_chapter(self):
        """Test adding chapters to the state."""
        state = GraphState(title="Test Story")

        state.add_chapter("Chapter content here", 1, "Chapter 1")

        self.assertEqual(len(state.chapters), 1)
        self.assertEqual(state.chapters[0]["number"], 1)
        self.assertEqual(state.chapters[0]["title"], "Chapter 1")
        self.assertEqual(state.chapters[0]["content"], "Chapter content here")
        self.assertIn(1, state.completed_chapters)

    def test_get_agent_context(self):
        """Test the get_agent_context method."""
        state = GraphState(
            title="Test Story",
            current_chapter="Test chapter content",
            story_status="in_progress"
        )

        context = state.get_agent_context()

        self.assertIsInstance(context, dict)
        self.assertEqual(context["title"], "Test Story")
        self.assertEqual(context["current_chapter"], "Test chapter content")

    def test_to_from_story_state(self):
        """Test conversion between GraphState and StoryState."""
        from src.novel_types import StoryState

        graph_state = GraphState(
            title="Converted Story",
            current_chapter="Converted content"
        )

        story_state = graph_state.to_story_state()

        self.assertIsInstance(story_state, StoryState)
        self.assertEqual(story_state.title, "Converted Story")
        self.assertEqual(story_state.current_chapter, "Converted content")

        # Test the reverse - from StoryState to GraphState
        new_graph_state = GraphState(title="New Story")
        new_graph_state.from_story_state(story_state)

        self.assertEqual(new_graph_state.title, "Converted Story")
        self.assertEqual(new_graph_state.current_chapter, "Converted content")

    def test_should_continue_method(self):
        """Test the should_continue method."""
        state = GraphState(title="Test Story", story_status="in_progress")

        # Should continue under normal conditions
        self.assertTrue(state.should_continue())

        # Should not continue if max iterations reached
        state.iteration_count = 51
        self.assertFalse(state.should_continue())

        # Should not continue if too many errors
        state.iteration_count = 0
        state.error_count = 6
        self.assertFalse(state.should_continue())

        # Should not continue if story completed
        state.error_count = 0
        state.story_status = "complete"
        self.assertFalse(state.should_continue())


class TestNodeManager(unittest.TestCase):
    """Test suite for the NodeManager class."""

    def setUp(self):
        self.config = Config()
        # We'll use a mock for the knowledge store in tests
        self.knowledge_store = AsyncMock()
        self.node_manager = NodeManager(self.config, self.knowledge_store)

    @patch('src.agents.planner.PlannerAgent.process')
    def test_planner_node(self, mock_planner_process):
        """Test the planner_node method."""
        # Use AsyncMock for the async process method
        from src.novel_types import AgentResponse
        from unittest.mock import AsyncMock

        # Mock the planner response
        mock_response = AgentResponse(
            agent_name="planner",
            content='{"test": "outline_data"}',
            status="success"
        )
        mock_planner_process.return_value = AsyncMock(return_value=mock_response)

        async def run_test():
            initial_state = GraphState(title="Test Story")
            result = await self.node_manager.planner_node(initial_state)

            # Verify the result is a GraphState and has the updated outline
            self.assertIsInstance(result, GraphState)
            self.assertEqual(result.title, "Test Story")
            # The knowledge store should have been called
            self.knowledge_store.store_memory.assert_called_once()

        # Run the async function
        asyncio.run(run_test())

    @patch('src.agents.writer.WriterAgent.process')
    def test_writer_node(self, mock_writer_process):
        """Test the writer_node method."""
        from src.novel_types import AgentResponse
        from unittest.mock import AsyncMock

        # Mock the writer response
        mock_response = AgentResponse(
            agent_name="writer",
            content="This is the generated chapter content.",
            status="success"
        )
        mock_writer_process.return_value = AsyncMock(return_value=mock_response)

        async def run_test():
            initial_state = GraphState(title="Test Story")
            result = await self.node_manager.writer_node(initial_state)

            # Verify the result has the written content
            self.assertIsInstance(result, GraphState)
            self.assertEqual(result.current_chapter, "This is the generated chapter content.")
            self.assertEqual(result.current_phase, "editing")
            # Chapter should be stored in knowledge base
            self.knowledge_store.store_chapter_content.assert_called_once()

        # Run the async function
        asyncio.run(run_test())


class TestNovelWritingGraph(unittest.TestCase):
    """Test suite for the NovelWritingGraph class."""

    def setUp(self):
        self.config = Config()

    def test_initialization(self):
        """Test that NovelWritingGraph initializes properly."""
        graph = NovelWritingGraph(self.config)

        # Just testing that it doesn't throw an error during initialization
        # The actual initialization happens inside the async method
        self.assertIsNotNone(graph)
        self.assertEqual(graph.config, self.config)

    def test_graph_compilation(self):
        """Test that the graph compiles without errors."""
        graph = NovelWritingGraph(self.config)

        async def run_test():
            await graph.initialize()
            # Get the compiled graph
            compiled = graph.get_graph()
            self.assertIsNotNone(compiled)

        asyncio.run(run_test())

    def test_run_workflow(self):
        """Test running a simple workflow."""
        graph = NovelWritingGraph(self.config)

        async def run_test():
            await graph.initialize()

            initial_state = GraphState(title="Workflow Test")

            # Run the workflow - this should complete without errors
            final_state = await graph.run_workflow(initial_state)

            # The final state should still be a GraphState
            self.assertIsInstance(final_state, GraphState)
            self.assertEqual(final_state.title, "Workflow Test")

        asyncio.run(run_test())


def run_tests():
    """Run all workflow tests."""
    print("Running workflow tests...")

    # Create a test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    # Run the tests directly if this file is executed
    asyncio.run(run_tests())