from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel
from enum import Enum
from datetime import datetime


class MessageRole(str, Enum):
    """Enumeration of possible message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    AGENT = "agent"
    HUMAN_EDITOR = "human_editor"


class MessageType(str, Enum):
    """Enumeration of possible message types."""
    CONTENT_REQUEST = "content_request"
    CONTENT_RESPONSE = "content_response"
    FEEDBACK = "feedback"
    APPROVAL = "approval"
    REJECTION = "rejection"
    CONSISTENCY_CHECK = "consistency_check"
    KNOWLEDGE_UPDATE = "knowledge_update"
    QUERY_REQUEST = "query_request"
    QUERY_RESPONSE = "query_response"
    STATUS_UPDATE = "status_update"
    ERROR = "error"
    DEBUG = "debug"


class MessageStatus(str, Enum):
    """Enumeration of possible message statuses."""
    PENDING = "pending"
    SENT = "sent"
    RECEIVED = "received"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class AgentMessage(BaseModel):
    """Standardized message format for communication between agents."""

    # Core message identification
    id: str
    conversation_id: str
    timestamp: datetime

    # Sender and receiver
    sender: str
    receiver: str
    role: MessageRole

    # Message content and type
    message_type: MessageType
    content: str
    metadata: Optional[Dict[str, Any]] = {}

    # Status tracking
    status: MessageStatus = MessageStatus.PENDING
    priority: int = 1  # Lower is higher priority

    # Thread and context
    parent_id: Optional[str] = None
    thread_id: Optional[str] = None

    # Response tracking
    requires_response: bool = False
    response_timeout: Optional[int] = None  # In seconds

    # Additional fields for specialized message types
    agent_feedback: Optional[str] = None
    suggestions: Optional[List[str]] = []
    related_agents: Optional[List[str]] = []
    context_snapshot: Optional[Dict[str, Any]] = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format including string formatting for datetime."""
        result = self.dict()
        result['timestamp'] = self.timestamp.isoformat()
        return result

    @classmethod
    def from_content(cls,
                     sender: str,
                     receiver: str,
                     content: str,
                     message_type: MessageType = MessageType.CONTENT_REQUEST,
                     **kwargs) -> 'AgentMessage':
        """Create a message from basic content."""
        import uuid
        return cls(
            id=str(uuid.uuid4()),
            conversation_id=kwargs.get("conversation_id", str(uuid.uuid4())),
            timestamp=datetime.now(),
            sender=sender,
            receiver=receiver,
            role=kwargs.get("role", MessageRole.AGENT),
            message_type=message_type,
            content=content,
            **kwargs
        )