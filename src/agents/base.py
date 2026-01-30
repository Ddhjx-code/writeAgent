from typing import Dict, List, Any, Optional, Callable
from pydantic import BaseModel
from src.core.story_state import StoryState
try:
    from src.core.knowledge_base import KnowledgeBase  # Original full knowledge base
except ImportError:
    from src.core.knowledge_base_minimal import KnowledgeBase  # Fallback minimal version
import json


class AgentConfig(BaseModel):
    """Configuration for an agent"""
    name: str
    role: str
    llm_config: Dict[str, Any]
    system_message: str
    max_consecutive_auto_reply: int = 10
    human_input_mode: str = "NEVER"  # NEVER, TERMINATE, ALWAYS


class BaseAgent:
    """
    Base class for all agents in the novel writing system.
    Provides common functionality for interacting with story state and knowledge base.
    """

    def __init__(self, config: AgentConfig, knowledge_base: KnowledgeBase):
        self.config = config
        self.knowledge_base = knowledge_base
        self.name = config.name
        self.role = config.role
        self.llm_config = config.llm_config
        self.system_message = config.system_message
        self.max_consecutive_auto_reply = config.max_consecutive_auto_reply
        self.human_input_mode = config.human_input_mode

        # Agent-specific state
        self.message_history: List[Dict[str, Any]] = []

    def process(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the current state and context.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement the process method")

    def update_state(self, state: StoryState, updates: Dict[str, Any]) -> StoryState:
        """
        Update the story state with the provided changes.
        This is a helper method that should be used by all agents.
        """
        for key, value in updates.items():
            if hasattr(state, key):
                setattr(state, key, value)

        state.updated_at = state.__class__.model_fields['updated_at'].default_factory()
        return state

    def get_relevant_information(self, query: str, top_k: int = 5) -> List[str]:
        """Retrieve relevant information from the knowledge base"""
        if not self.knowledge_base:
            return []

        try:
            documents = self.knowledge_base.query(query, similarity_top_k=top_k)
            return [doc.text for doc in documents]
        except Exception as e:
            print(f"Error retrieving information: {e}")
            return []

    def log_message(self, message: str, message_type: str = "info"):
        """Log a message to the agent's message history"""
        self.message_history.append({
            "timestamp": self.get_current_time(),
            "type": message_type,
            "message": message,
            "agent_name": self.name
        })

    def get_current_time(self):
        from datetime import datetime
        return datetime.now()

    def verify_consistency(self, state: StoryState, content: str) -> Dict[str, Any]:
        """
        Common method for agents to verify consistency of their content
        with the story state and knowledge base.
        """
        # This is a placeholder implementation - to be filled in with actual verification logic
        return {
            "is_consistent": True,
            "issues": [],
            "suggestions": []
        }

    def format_response(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Format the agent's response in a standardized way
        """
        if metadata is None:
            metadata = {}

        return {
            "content": content,
            "agent_name": self.name,
            "agent_role": self.role,
            "timestamp": self.get_current_time().isoformat(),
            "metadata": metadata
        }