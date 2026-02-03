import asyncio
import unittest
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Add source directory to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.config import Config
from src.novel_types import StoryState
from src.agents.writer import WriterAgent
from src.agents.planner import PlannerAgent
from src.agents.archivist import ArchivistAgent
from src.agents.editor import EditorAgent
from src.agents.consistency_checker import ConsistencyCheckerAgent
from src.agents.dialogue_specialist import DialogueSpecialistAgent
from src.agents.world_builder import WorldBuilderAgent
from src.agents.pacing_advisor import PacingAdvisorAgent


class TestWriterAgent(unittest.TestCase):
    """Test suite for the WriterAgent class."""

    def setUp(self):
        self.config = Config()
        self.agent = WriterAgent(self.config)

    def test_agent_initialization(self):
        """Test that WriterAgent initializes properly with config."""
        self.assertEqual(self.agent.name, "writer")
        self.assertIsNotNone(self.agent.config)

    def test_get_prompt_method(self):
        """Test that get_prompt method returns a non-empty string."""
        prompt = self.agent.get_prompt()
        self.assertIsInstance(prompt, str)
        self.assertTrue(len(prompt) > 0)

    @patch('src.agents.writer.asyncio.sleep', new=AsyncMock())
    def test_process_method_with_empty_state(self):
        """Test the process method with an empty state."""
        state = {
            'title': 'Test Story',
            'current_chapter': '',
            'chapters': [],
            'outline': {},
            'characters': {},
            'world_details': {},
            'story_status': 'draft'
        }

        result = asyncio.run(self.agent.process(state))

        self.assertIsNotNone(result)
        self.assertEqual(result.agent_name, 'writer')
        self.assertEqual(result.status, 'success')
        self.assertIsNotNone(result.content)
        self.assertTrue(len(result.content) > 0)


class TestPlannerAgent(unittest.TestCase):
    """Test suite for the PlannerAgent class."""

    def setUp(self):
        self.config = Config()
        self.agent = PlannerAgent(self.config)

    def test_agent_initialization(self):
        """Test that PlannerAgent initializes properly with config."""
        self.assertEqual(self.agent.name, "planner")
        self.assertIsNotNone(self.agent.config)

    def test_get_prompt_method(self):
        """Test that get_prompt method returns a non-empty string."""
        prompt = self.agent.get_prompt()
        self.assertIsInstance(prompt, str)
        self.assertTrue(len(prompt) > 0)

    def test_process_method_with_minimal_state(self):
        """Test the process method with a minimal state."""
        state = {
            'title': 'Test Story',
            'current_chapter': '',
            'chapters': [],
            'outline': {},
            'characters': {},
            'world_details': {},
            'story_status': 'draft'
        }

        result = asyncio.run(self.agent.process(state))

        self.assertIsNotNone(result)
        self.assertEqual(result.agent_name, 'planner')
        self.assertEqual(result.status, 'success')
        self.assertIsNotNone(result.content)
        # Check that content is valid JSON
        import json
        try:
            parsed = json.loads(result.content)
            self.assertIsInstance(parsed, dict)
        except json.JSONDecodeError:
            self.fail("Planner agent output is not valid JSON")


class TestArchivistAgent(unittest.TestCase):
    """Test suite for the ArchivistAgent class."""

    def setUp(self):
        self.config = Config()
        self.agent = ArchivistAgent(self.config)

    def test_agent_initialization(self):
        """Test that ArchivistAgent initializes properly with config."""
        self.assertEqual(self.agent.name, "archivist")
        self.assertIsNotNone(self.agent.config)

    def test_get_prompt_method(self):
        """Test that get_prompt method returns a non-empty string."""
        prompt = self.agent.get_prompt()
        self.assertIsInstance(prompt, str)
        self.assertTrue(len(prompt) > 0)

    def test_continuity_functions(self):
        """Test the continuity checking helper functions."""
        self.assertIsInstance(self.agent._extract_continuity_info({}), dict)
        self.assertIsInstance(self.agent._update_character_info({}), dict)
        self.assertIsInstance(self.agent._update_world_details({}), dict)
        self.assertIsInstance(self.agent._check_consistency({}), dict)

    def test_process_method(self):
        """Test the process method."""
        state = {
            'title': 'Test Story',
            'current_chapter': 'This is the first chapter content.',
            'chapters': [],
            'outline': {},
            'characters': {
                'Protagonist': {'name': 'Test Protagonist', 'description': 'A test character'}
            },
            'world_details': {
                'location': 'Test world',
                'rules': 'Magic exists'
            },
            'story_status': 'draft',
            'archive': {}
        }

        result = asyncio.run(self.agent.process(state))

        self.assertIsNotNone(result)
        self.assertEqual(result.agent_name, 'archivist')
        self.assertEqual(result.status, 'success')
        self.assertIsNotNone(result.content)


class TestEditorAgent(unittest.TestCase):
    """Test suite for the EditorAgent class."""

    def setUp(self):
        self.config = Config()
        self.agent = EditorAgent(self.config)

    def test_agent_initialization(self):
        """Test that EditorAgent initializes properly with config."""
        self.assertEqual(self.agent.name, "editor")
        self.assertIsNotNone(self.agent.config)

    def test_get_prompt_method(self):
        """Test that get_prompt method returns a non-empty string."""
        prompt = self.agent.get_prompt()
        self.assertIsInstance(prompt, str)
        self.assertTrue(len(prompt) > 0)

    def test_process_method(self):
        """Test the process method."""
        state = {
            'title': 'Test Story',
            'current_chapter': 'This is the chapter text for editing.',
            'chapters': [],
            'outline': {},
            'characters': {},
            'world_details': {},
            'story_status': 'draft',
            'editor_notes': []
        }

        result = asyncio.run(self.agent.process(state))

        self.assertIsNotNone(result)
        self.assertEqual(result.agent_name, 'editor')
        self.assertEqual(result.status, 'success')
        self.assertIsNotNone(result.content)

        import json
        try:
            parsed = json.loads(result.content)
            self.assertIsInstance(parsed, dict)
        except json.JSONDecodeError:
            self.fail("Editor agent output is not valid JSON")


class TestConsistencyCheckerAgent(unittest.TestCase):
    """Test suite for the ConsistencyCheckerAgent class."""

    def setUp(self):
        self.config = Config()
        self.agent = ConsistencyCheckerAgent(self.config)

    def test_agent_initialization(self):
        """Test that ConsistencyCheckerAgent initializes properly with config."""
        self.assertEqual(self.agent.name, "consistency_checker")
        self.assertIsNotNone(self.agent.config)

    def test_get_prompt_method(self):
        """Test that get_prompt method returns a non-empty string."""
        prompt = self.agent.get_prompt()
        self.assertIsInstance(prompt, str)
        self.assertTrue(len(prompt) > 0)

    def test_process_method(self):
        """Test the process method."""
        state = {
            'title': 'Test Story',
            'current_chapter': 'This is the chapter text to check for consistency.',
            'chapters': [],
            'outline': {},
            'characters': {
                'Character1': {'name': 'Char 1', 'age': 30}
            },
            'world_details': {
                'time_period': 'modern',
                'magic_system': 'rules here'
            },
            'story_status': 'draft',
            'inconsistency_log': []
        }

        result = asyncio.run(self.agent.process(state))

        self.assertIsNotNone(result)
        self.assertEqual(result.agent_name, 'consistency_checker')
        self.assertEqual(result.status, 'success')
        self.assertIsNotNone(result.content)

        import json
        try:
            parsed = json.loads(result.content)
            self.assertIsInstance(parsed, dict)
        except json.JSONDecodeError:
            self.fail("Consistency checker agent output is not valid JSON")


class TestDialogueSpecialistAgent(unittest.TestCase):
    """Test suite for the DialogueSpecialistAgent class."""

    def setUp(self):
        self.config = Config()
        self.agent = DialogueSpecialistAgent(self.config)

    def test_agent_initialization(self):
        """Test that DialogueSpecialistAgent initializes properly with config."""
        self.assertEqual(self.agent.name, "dialogue_specialist")
        self.assertIsNotNone(self.agent.config)

    def test_get_prompt_method(self):
        """Test that get_prompt method returns a non-empty string."""
        prompt = self.agent.get_prompt()
        self.assertIsInstance(prompt, str)
        self.assertTrue(len(prompt) > 0)

    def test_process_method(self):
        """Test the process method."""
        state = {
            'title': 'Test Story',
            'current_chapter': 'Character 1: "Hello there," said Character 1 to Character 2.',
            'chapters': [],
            'outline': {},
            'characters': {'Character 1': {'name': 'First'}},
            'world_details': {},
            'story_status': 'draft',
            'dialogue_notes': []
        }

        result = asyncio.run(self.agent.process(state))

        self.assertIsNotNone(result)
        self.assertEqual(result.agent_name, 'dialogue_specialist')
        self.assertEqual(result.status, 'success')
        self.assertIsNotNone(result.content)


class TestWorldBuilderAgent(unittest.TestCase):
    """Test suite for the WorldBuilderAgent class."""

    def setUp(self):
        self.config = Config()
        self.agent = WorldBuilderAgent(self.config)

    def test_agent_initialization(self):
        """Test that WorldBuilderAgent initializes properly with config."""
        self.assertEqual(self.agent.name, "world_builder")
        self.assertIsNotNone(self.agent.config)

    def test_get_prompt_method(self):
        """Test that get_prompt method returns a non-empty string."""
        prompt = self.agent.get_prompt()
        self.assertIsInstance(prompt, str)
        self.assertTrue(len(prompt) > 0)

    def test_process_method(self):
        """Test the process method."""
        state = {
            'title': 'Test Story',
            'current_chapter': 'The characters are in a magical forest.',
            'chapters': [],
            'outline': {'genre': 'Fantasy'},
            'characters': {},
            'world_details': {'magic_system': 'elemental magic'},
            'story_status': 'draft'
        }

        result = asyncio.run(self.agent.process(state))

        self.assertIsNotNone(result)
        self.assertEqual(result.agent_name, 'world_builder')
        self.assertEqual(result.status, 'success')
        self.assertIsNotNone(result.content)


class TestPacingAdvisorAgent(unittest.TestCase):
    """Test suite for the PacingAdvisorAgent class."""

    def setUp(self):
        self.config = Config()
        self.agent = PacingAdvisorAgent(self.config)

    def test_agent_initialization(self):
        """Test that PacingAdvisorAgent initializes properly with config."""
        self.assertEqual(self.agent.name, "pacing_advisor")
        self.assertIsNotNone(self.agent.config)

    def test_get_prompt_method(self):
        """Test that get_prompt method returns a non-empty string."""
        prompt = self.agent.get_prompt()
        self.assertIsInstance(prompt, str)
        self.assertTrue(len(prompt) > 0)

    def test_process_method(self):
        """Test the process method."""
        state = {
            'title': 'Test Story',
            'current_chapter': 'This chapter has various scenes with different pacing.',
            'chapters': [],
            'outline': {'genre': 'Thriller'},
            'characters': {},
            'world_details': {},
            'story_status': 'draft'
        }

        result = asyncio.run(self.agent.process(state))

        self.assertIsNotNone(result)
        self.assertEqual(result.agent_name, 'pacing_advisor')
        self.assertEqual(result.status, 'success')
        self.assertIsNotNone(result.content)


if __name__ == '__main__':
    unittest.main()