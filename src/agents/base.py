from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..novel_types import AgentResponse, Message
from ..config import Config


class BaseAgent(ABC):
    """Base class for all agents in the novel writing system."""

    def __init__(self, name: str, config: Config):
        self.name = name
        self.config = config
        self._validate_config()

    def _validate_config(self):
        """Validate that required configuration is present."""
        if not hasattr(self.config, f"{self.name.lower()}_model"):
            # Default to a general model if specific model not set
            setattr(self.config, f"{self.name.lower()}_model", self.config.default_writer_model)

    @abstractmethod
    async def process(self, state: Dict[str, Any]) -> AgentResponse:
        """Process the current state and return a response."""
        pass

    @abstractmethod
    def get_prompt(self) -> str:
        """Return the prompt for this agent."""
        pass

    async def communicate(self, message: Message) -> Optional[Message]:
        """Handle communication with other agents."""
        # Implementation for communication protocol would go here
        # For now, just return a response acknowledging the message
        return Message(
            sender=self.name,
            receiver=message.sender,
            content=f"Received message from {message.sender}",
            message_type="ack",
            timestamp=message.timestamp
        )

    def _build_context(self, state: Dict[str, Any]) -> str:
        """Build context from state for agent processing."""
        return f"""
        Story Title: {state.get('title', 'N/A')}
        Current Chapter: {state.get('current_chapter', 'N/A')}
        Characters: {state.get('characters', {})}
        World Details: {state.get('world_details', {})}
        Story Outline: {state.get('outline', {})}
        """