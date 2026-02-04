import logging
from typing import Dict, Any, List, Optional
from ..agents.base import BaseAgent
from .message import AgentMessage, MessageType
from ..config import Config


class AutoGenWrapper:
    """Wrapper for AutoGen library to handle communication between agents."""

    def __init__(self, config: Config):
        self._config = config  # Store Config without direct dependency on autogen
        self._message_queue = []
        self._agent_registry = {}
        self._conversation_history = {}

    def register_agent(self, name: str, agent: BaseAgent):
        """Register an agent with the wrapper."""
        self._agent_registry[name] = agent

    def send_message(self, message: AgentMessage) -> bool:
        """Send a message to the recipient agent."""
        try:
            # Add message to queue for processing
            self._message_queue.append(message)

            # Process the message by calling the appropriate agent if it's registered
            if message.receiver in self._agent_registry:
                # Update message status
                message.status = "sent"
                return True
            else:
                # In a real implementation, we might need other communication channels
                message.status = "failed"
                return False
        except Exception as e:
            logging.error(f"Error sending message: {e}")
            if message:
                message.status = "failed"
            return False

    def broadcast_message(self, message: AgentMessage, exclude_list: List[str] = None):
        """Broadcast a message to all registered agents except those in the exclude list."""
        if exclude_list is None:
            exclude_list = []

        sent_count = 0
        for agent_name in self._agent_registry:
            if agent_name not in exclude_list:
                # Create a new message for each recipient
                new_message = AgentMessage(
                    id=message.id,
                    conversation_id=message.conversation_id,
                    timestamp=message.timestamp,
                    sender=message.sender,
                    receiver=agent_name,
                    role=message.role,
                    message_type=message.message_type,
                    content=message.content,
                    metadata=message.metadata,
                    parent_id=message.parent_id,
                    thread_id=message.thread_id,
                    requires_response=message.requires_response,
                    suggested_responses=message.suggestions
                )
                if self.send_message(new_message):
                    sent_count += 1

        return sent_count

    def get_new_messages(self, agent_name: str) -> List[AgentMessage]:
        """Get new messages for a specific agent."""
        messages_for_agent = []
        for message in self._message_queue:
            if message.receiver == agent_name and message.status in ["sent", "pending"]:
                messages_for_agent.append(message)

        # Mark messages as received
        for message in messages_for_agent:
            message.status = "received"

        return messages_for_agent

    def process_incoming_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process an incoming message and generate a response if appropriate."""
        try:
            # Look up the recipient agent
            target_agent = self._agent_registry.get(message.receiver)

            if target_agent is None:
                # If agent doesn't exist in registry, return None or handle differently
                return None

            # Convert message content to state format if needed
            state_like_dict = {
                "title": "Collaborative Novel",
                "current_chapter": message.content if message.message_type == MessageType.CONTENT_REQUEST else "",
                "chapters": [],
                "outline": {},
                "characters": {},
                "world_details": {},
                "story_status": "in_progress",
                "notes": [f"Message from {message.sender}: {message.content}"]
            }

            # Process the message content (in real implementation this would call the agent)
            # For this wrapper, we'll return a simple response
            response_content = f"Message received from {message.sender}. Content: {message.content[:100]}..."

            # Create a response message if required
            if message.requires_response:
                response_message = AgentMessage(
                    id=f"resp_{message.id}",
                    conversation_id=message.conversation_id,
                    timestamp=message.timestamp,
                    sender=message.receiver,  # Swapped sender and receiver
                    receiver=message.sender,
                    role="agent",
                    message_type=MessageType.CONTENT_RESPONSE,
                    content=response_content,
                    metadata=message.metadata
                )
                return response_message

            return None

        except Exception as e:
            logging.error(f"Error processing message: {e}")
            # Return an error message
            error_message = AgentMessage(
                id=f"error_{message.id}",
                conversation_id=message.conversation_id,
                timestamp=message.timestamp,
                sender="system",
                receiver=message.sender,
                role="agent",
                message_type=MessageType.ERROR,
                content=f"Error processing message: {str(e)}",
                metadata={}
            )
            return error_message

    def check_conversation_history(self, agent1: str, agent2: str) -> List[AgentMessage]:
        """Retrieve conversation history between two agents."""
        conversation_key = f"{agent1}-{agent2}" if agent1 < agent2 else f"{agent2}-{agent1}"
        return self._conversation_history.get(conversation_key, [])

    def cleanup_processed_messages(self):
        """Remove older messages that have been processed."""
        # In a real implementation, we'd have more sophisticated retention rules
        unprocessed_messages = []
        for message in self._message_queue:
            if message.status.value not in ["processed", "failed"]:
                unprocessed_messages.append(message)

        self._message_queue = unprocessed_messages