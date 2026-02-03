from typing import Literal, Union, Dict, Any, List
from enum import Enum
from pydantic import BaseModel


class NodeType(str, Enum):
    """Enumeration of all possible node types in the workflow."""
    PLANNER = "planner"
    WRITER = "writer"
    ARCHIVIST = "archivist"
    EDITOR = "editor"
    CONSISTENCY_CHECKER = "consistency_checker"
    DIALOGUE_SPECIALIST = "dialogue_specialist"
    WORLD_BUILDER = "world_builder"
    PACING_ADVISOR = "pacing_advisor"
    HUMANIZER = "humanizer"
    HUMAN_REVIEW = "human_review"
    # Additional nodes that might be added in the future
    GLOBAL_PLANNING = "global_planning"  # For system-level planning
    GLOBAL_PACING_SETUP = "global_pacing_setup"  # For overall pacing
    PROCESS_CHAPTER = "process_chapter"  # For chapter-specific processing
    INTEGRATE_FULL_STORY = "integrate_full_story"  # For integration steps


class WorkflowStatus(str, Enum):
    """Enumeration of possible workflow states."""
    NOT_STARTED = "not_started"
    PLANNING = "planning"
    WRITING = "writing"
    EDITING = "editing"
    CONSISTENCY_CHECK = "consistency_check"
    REFINING = "refining"
    COMPLETED = "completed"
    ERROR = "error"
    PAUSED = "paused"
    WAITING_FOR_INPUT = "waiting_for_input"


class WorkflowEvent(str, Enum):
    """Events that can happen during workflow execution."""
    NODE_STARTED = "node_started"
    NODE_COMPLETED = "node_completed"
    NODE_FAILED = "node_failed"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    HUMAN_INPUT_REQUESTED = "human_input_requested"
    ITERATION_COMPLETED = "iteration_completed"


class WorkflowConfig(BaseModel):
    """Configuration for workflow execution."""
    max_iterations: int = 100
    max_errors: int = 10
    save_frequency: int = 10  # How often to persist state
    human_review_enabled: bool = True
    debug: bool = False


class WorkflowStep(BaseModel):
    """Represents a single step in the workflow."""
    node_type: NodeType
    execution_order: int
    required_inputs: List[str]
    outputs_generated: List[str]
    estimated_duration: int  # Estimated duration in seconds
    priority: int = 1  # Lower is higher priority


class AgentMessage(BaseModel):
    """Message format for communication between agents."""
    from_agent: str
    to_agent: str
    message_type: str  # request, response, notification, error
    content: Union[Dict[str, Any], str]
    timestamp: float
    metadata: Dict[str, Any] = {}


class WorkflowSignal(BaseModel):
    """Signal that can be sent to change workflow behavior."""
    signal_type: Literal["pause", "resume", "skip_node", "restart"]
    target: str  # Target node or process
    reason: str
    data: Dict[str, Any] = {}


class ChapterResult(BaseModel):
    """Result format for chapter generation."""
    chapter_number: int
    title: str
    content: str
    word_count: int
    generated_at_iteration: int
    agent_feedback: List[Dict[str, Any]]
    status: Literal["draft", "revised", "approved", "rejected"]


class StoryProgress(BaseModel):
    """Track the progress of the entire story."""
    total_chapters_planned: int
    chapters_completed: int
    chapters_approved: int
    current_chapter: int
    story_completion_percentage: float
    words_written: int
    estimated_completion_chapters: int
    estimated_days_remaining: int