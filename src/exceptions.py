class NovelWritingException(Exception):
    """Base exception for the novel writing system."""
    pass


class AgentException(NovelWritingException):
    """Exception raised when an agent encounters an error."""
    pass


class WorkflowException(NovelWritingException):
    """Exception raised when a workflow encounters an error."""
    pass


class KnowledgeBaseException(NovelWritingException):
    """Exception raised when the knowledge base encounters an error."""
    pass


class CommunicationException(NovelWritingException):
    """Exception raised when communication between agents fails."""
    pass


class ConfigurationException(NovelWritingException):
    """Exception raised when there's a configuration error."""
    pass