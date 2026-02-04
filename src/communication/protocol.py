import logging
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from ..novel_types import AgentResponse
from .message import AgentMessage, MessageType
from ..config import Config


class CommunicationProtocol(str, Enum):
    """Available communication protocols."""
    AUTONOMIC = "autonomic"  # Each agent works independently
    HIERARCHICAL = "hierarchical"  # Structured communication with designated leader
    PEER_TO_PEER = "p2p"  # All agents communicate directly with each other
    HUB_AND_SPOKE = "hub_and_spoke"  # All communication through central coordinator
    HYBRID = "hybrid"  # Combination of different protocols


class CommunicationDirection(str, Enum):
    """Direction of communication flow."""
    ONE_WAY = "one_way"
    TWO_WAY = "two_way"
    BROADCAST = "broadcast"


class CommunicationManager:
    """Manages communication between agents using different protocols."""

    def __init__(self, protocol: CommunicationProtocol, config: Config):
        self.protocol = protocol
        self.config = config
        self.agents = {}  # agent_name -> agent_instance
        self.active_conversations = {}
        self.last_messages = {}
        self.communication_stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "conversations_count": 0
        }

    def register_agent(self, name: str, agent):
        """Register an agent with the communication manager."""
        self.agents[name] = agent

    async def send_message(self, sender: str, receivers: List[str], message: AgentMessage) -> bool:
        """Send a message from sender to receivers."""
        success_count = 0

        for receiver in receivers:
            if receiver in self.agents:
                # Add to statistics
                self.communication_stats["messages_sent"] += 1

                # In a real implementation, this would use the actual communication
                # method based on the protocol type
                if hasattr(self.agents[receiver], 'communicate'):
                    try:
                        response = await self.agents[receiver].communicate(message)
                        success_count += 1
                    except Exception as e:
                        logging.error(f"Error communicating with {receiver}: {e}")
                        continue
                else:
                    # Agent doesn't support direct communication, store for later retrieval
                    if receiver not in self.last_messages:
                        self.last_messages[receiver] = []
                    self.last_messages[receiver].append(message)
                    success_count += 1

        return success_count > 0

    async def broadcast_message(self, sender: str, message: AgentMessage, exclude: List[str] = None) -> bool:
        """Broadcast a message to all registered agents."""
        if exclude is None:
            exclude = []

        receivers = [name for name in self.agents.keys() if name not in exclude]
        return await self.send_message(sender, receivers, message)

    def get_new_messages(self, agent_name: str) -> List[AgentMessage]:
        """Get new messages for an agent."""
        self.communication_stats["messages_received"] += len(self.last_messages.get(agent_name, []))
        messages = self.last_messages.get(agent_name, [])
        # Clear messages after retrieval
        self.last_messages[agent_name] = []
        return messages

    def create_collaboration_cycle(self, agent_names: List[str], cycle_type: str = "sequential"):
        """Create a collaboration cycle between selected agents."""
        if cycle_type == "sequential":
            # In sequential mode, agents pass work to the next agent in the list
            for i, agent_name in enumerate(agent_names):
                next_agent = agent_names[(i + 1) % len(agent_names)]
                self.create_sequential_relationship(agent_name, next_agent)
        elif cycle_type == "iterative":
            # All agents review and add to each other's work
            for i, agent_name in enumerate(agent_names):
                others = [name for j, name in enumerate(agent_names) if j != i]
                for other in others:
                    self.create_review_relationship(agent_name, other)

    def create_sequential_relationship(self, sender: str, receiver: str):
        """Create a relationship where sender passes work to receiver."""
        relationship_key = f"{sender}_{receiver}_seq"
        self.active_conversations[relationship_key] = {
            "type": "sequential",
            "sender": sender,
            "receiver": receiver,
            "status": "active"
        }

    def create_review_relationship(self, reviewer: str, target: str):
        """Create a relationship where reviewer reviews target's work."""
        relationship_key = f"{reviewer}_{target}_review"
        self.active_conversations[relationship_key] = {
            "type": "review",
            "reviewer": reviewer,
            "target": target,
            "status": "active"
        }

    async def handle_feedback_loop(self, current_agent: str, feedback_agent: str, content: str) -> AgentResponse:
        """Handle a feedback loop between two agents."""
        # Get the agent responsible for providing feedback
        if feedback_agent not in self.agents:
            # Return original content if no feedback agent exists
            return AgentResponse(
                agent_name=current_agent,
                content=content,
                reasoning="No feedback agent available",
                status="success"
            )

        # Create a feedback message
        feedback_message = AgentMessage.from_content(
            sender=feedback_agent,
            receiver=current_agent,
            content=content,
            message_type=MessageType.FEEDBACK
        )

        # Send the feedback and return the result
        await self.send_message(
            sender=feedback_agent,
            receivers=[current_agent],
            message=feedback_message
        )

        # In a real implementation, we would wait for the updated agent response
        return AgentResponse(
            agent_name=current_agent,
            content=content,
            reasoning=f"Feedback sent to {current_agent} from {feedback_agent}",
            status="feedback_sent"
        )

    def get_communication_stats(self) -> Dict[str, Any]:
        """Get statistics about communication performance."""
        return self.communication_stats

    def get_active_conversations(self) -> List[Dict[str, Any]]:
        """Get list of active communication relationships."""
        return list(self.active_conversations.values())