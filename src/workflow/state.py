from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, validator
from ..novel_types import StoryState, AgentResponse
import json


class GraphState(BaseModel):
    """Represents the state of the LangGraph workflow for the novel writing system."""

    # Core story information
    title: str
    current_chapter: str = ""
    chapters: List[Dict[str, Any]] = []
    outline: Dict[str, Any] = {}
    characters: Dict[str, Any] = {}
    world_details: Dict[str, Any] = {}
    story_status: str = "draft"  # draft, in_progress, complete, etc.

    # System state tracking
    agent_responses: List[AgentResponse] = []
    story_notes: List[str] = []
    next_agent: str = "planner"  # Which agent should run next
    iteration_count: int = 0
    max_iterations: int = 50

    # Knowledge base integration
    knowledge_queries: List[str] = []
    retrieved_knowledge: List[Dict[str, Any]] = []

    # Workflow-specific tracking
    current_phase: str = "planning"  # planning, writing, editing, review
    error_count: int = 0
    last_error: Optional[str] = None

    # Hierarchical workflow tracking (NEW FIELDS)
    current_hierarchical_phase: Literal["macro", "mid", "micro"] = "macro"
    macro_progress: float = 0.0  # Progress in macro phase (0.0-1.0)
    mid_progress: float = 0.0    # Progress in mid phase (0.0-1.0)
    micro_progress: float = 0.0  # Progress in micro phase (0.0-1.0)
    macro_phase_data: Dict[str, Any] = {}  # State data specific to macro phase
    mid_phase_data: Dict[str, Any] = {}    # State data specific to mid phase
    micro_phase_data: Dict[str, Any] = {}  # State data specific to micro phase
    target_macro_completion: int = 1       # Number of major story sections to complete
    target_mid_completion: int = 10        # Number of chapters/chapter sections to complete
    macro_completion_criteria: Dict[str, Any] = {}  # Criteria to complete macro phase
    mid_completion_criteria: Dict[str, Any] = {}    # Criteria to complete mid phase
    micro_completion_criteria: Dict[str, Any] = {}  # Criteria to complete micro phase

    # Human feedback integration
    human_feedback: List[Dict[str, Any]] = []
    needs_human_review: bool = False
    human_review_status: str = "pending"  # pending, approved, rejected, not_needed

    # Story-specific tracking
    completed_chapters: List[int] = []
    current_chapter_index: int = 0
    story_arc_progress: float = 0.0

    # Agent-specific information
    current_agent_output: Optional[str] = None
    agent_execution_log: List[Dict[str, Any]] = []

    # Cycle detection and execution tracking
    cycle_detection_metrics: Dict[str, int] = {}  # Track agent execution patterns
    execution_sequence: List[str] = []  # Track sequence of agent executions
    agent_iteration_counts: Dict[str, int] = {}  # Track individual agent iterations
    forced_transitions_count: int = 0  # Count number of forced transitions
    debug_mode: bool = False  # Enable debug features

    @validator('macro_progress', 'mid_progress', 'micro_progress')
    def validate_progress(cls, v):
        """Validate that progress values are between 0.0 and 1.0"""
        if not 0.0 <= v <= 1.0:
            raise ValueError('Progress must be between 0.0 and 1.0')
        return v

    def log_current_step(self, step_data: Dict[str, Any]):
        """Log the current execution step for debugging and cycle detection."""
        step_log = {
            "iteration": self.iteration_count,
            "agent": self.next_agent,
            "phase": self.current_hierarchical_phase,
            "timestamp": self.iteration_count,  # Using iteration as timestamp
            **step_data
        }
        self.agent_execution_log.append(step_log)

        # Update execution sequence for cycle detection
        self.execution_sequence.append(self.next_agent)

        # Update agent iteration counts
        if self.next_agent not in self.agent_iteration_counts:
            self.agent_iteration_counts[self.next_agent] = 0
        self.agent_iteration_counts[self.next_agent] += 1

        # Update cycle detection metrics
        if self.next_agent not in self.cycle_detection_metrics:
            self.cycle_detection_metrics[self.next_agent] = 0
        self.cycle_detection_metrics[self.next_agent] += 1

    def detect_cycle(self, max_repeats: Optional[int] = None) -> Optional[str]:
        """Detect potential cycles in the execution sequence."""
        from .config import WorkflowConfig
        config = WorkflowConfig()
        threshold = max_repeats or config.max_related_nodes_sequence

        # Check if the last N elements of the execution sequence are the same
        if len(self.execution_sequence) < threshold * 2:
            return None

        # Check for repeated patterns within the last sequence
        recent_executions = self.execution_sequence[-threshold:]
        if len(recent_executions) == threshold and len(set(recent_executions)) == 1:
            return f"Potential cycle detected: {recent_executions[0]} executed {threshold} times in succession"

        # Check for shorter repetitive patterns
        if len(self.execution_sequence) >= 6:
            last_6 = self.execution_sequence[-6:]
            if last_6[:3] == last_6[3:]:  # First three equal last three
                return f"Potential 3-agent cycle detected: {last_6[:3]}"

        # Check for high iteration counts in individual agents
        for agent, count in self.agent_iteration_counts.items():
            if count > threshold:
                return f"Agent {agent} has run {count} times - potential infinite loop"

        return None

    def mark_forced_transition(self):
        """Mark that a forced transition has occurred to help track cycle-breaking events."""
        self.forced_transitions_count += 1

    def get_agent_context(self) -> Dict[str, Any]:
        """Return the current context for agents to work with."""
        return {
            "title": self.title,
            "current_chapter": self.current_chapter,
            "chapters": self.chapters,
            "outline": self.outline,
            "characters": self.characters,
            "world_details": self.world_details,
            "story_status": self.story_status,
            "story_notes": self.story_notes,
            "current_phase": self.current_phase,
            "agent_responses": [resp.dict() for resp in self.agent_responses],
            "retrieved_knowledge": self.retrieved_knowledge,
            "human_feedback": self.human_feedback
        }

    def to_story_state(self) -> StoryState:
        """Convert GraphState to StoryState for compatibility with agents."""
        return StoryState(
            title=self.title,
            current_chapter=self.current_chapter,
            chapters=self.chapters,
            outline=self.outline,
            characters=self.characters,
            world_details=self.world_details,
            story_status=self.story_status,
            notes=self.story_notes
        )

    def from_story_state(self, story_state: StoryState):
        """Update GraphState from StoryState."""
        self.title = story_state.title
        self.current_chapter = story_state.current_chapter
        self.chapters = story_state.chapters
        self.outline = story_state.outline
        self.characters = story_state.characters
        self.world_details = story_state.world_details
        self.story_status = story_state.story_status
        self.story_notes = story_state.notes

    def add_chapter(self, chapter_content: str, chapter_number: int, title: str):
        """Add a new chapter to the story."""
        chapter = {
            "number": chapter_number,
            "title": title,
            "content": chapter_content,
            "word_count": len(chapter_content.split()),
            "completed_at_iteration": self.iteration_count
        }
        if chapter_number > len(self.chapters):
            self.chapters.append(chapter)
        else:
            # Replace if it already exists
            for i, chap in enumerate(self.chapters):
                if chap["number"] == chapter_number:
                    self.chapters[i] = chapter
                    break
            else:
                self.chapters.append(chapter)

        self.completed_chapters.append(chapter_number)
        self.current_chapter_index = chapter_number

    def add_agent_response(self, response: AgentResponse):
        """Add an agent response to the history."""
        self.agent_responses.append(response)

    def has_error(self) -> bool:
        """Check if the current state contains an error."""
        return self.error_count > 0

    def should_continue(self) -> bool:
        """Determine if the workflow should continue iterating."""
        # Continue unless we exceed max iterations, complete the story, or have too many errors
        base_continuation = (
            self.iteration_count < self.max_iterations and
            self.story_status != "complete" and
            self.error_count < 5  # Stop after 5 errors
        )

        # If base conditions are not met, don't continue
        if not base_continuation:
            return False

        # Check hierarchical phase-specific continuation criteria
        # If no specific criteria are defined for a phase, continue normally
        if self.current_hierarchical_phase == "macro":
            # For macro, continue if we have not set specific completion criteria or not yet met them
            if len(self.macro_completion_criteria) == 0:
                return base_continuation  # Continue if base conditions met but no specific criteria set
            else:
                # If criteria exist, continue until they're met
                is_complete = self.macro_progress >= 1.0
                return not is_complete
        elif self.current_hierarchical_phase == "mid":
            # For mid, continue if we have not set specific completion criteria or not yet met them
            if len(self.mid_completion_criteria) == 0:
                return base_continuation  # Continue if base conditions met but no specific criteria set
            else:
                # If criteria exist, continue until they're met
                is_complete = self.mid_progress >= 1.0
                return not is_complete
        else:  # micro
            # For micro, continue if we have not set specific completion criteria or not yet met them
            if len(self.micro_completion_criteria) == 0:
                return base_continuation  # Continue if base conditions met but no specific criteria set
            else:
                # If criteria exist, continue until they're met
                is_complete = self.micro_progress >= 1.0
                return not is_complete

    def can_transition_to_phase(self, target_phase: Literal["macro", "mid", "micro"]) -> bool:
        """Check if a transition to the target hierarchical phase is allowed."""
        current = self.current_hierarchical_phase

        if target_phase == current:
            return True  # Already in the target phase

        # Define hierarchical phase transition rules
        # Allowed transitions: macro -> mid, mid -> macro, mid -> micro, micro -> mid
        allowed_transitions = {
            "macro": ["mid"],
            "mid": ["macro", "micro"],
            "micro": ["mid"]
        }

        return target_phase in allowed_transitions.get(current, [])

    def should_transition_to_phase(self, target_phase: Literal["macro", "mid", "micro"]) -> bool:
        """Determine if the workflow should transition to a different hierarchical phase."""
        if not self.can_transition_to_phase(target_phase):
            return False

        # Define conditions that might trigger a phase transition
        if target_phase == "macro":
            # Return to macro when story structure needs re-planning
            needs_replan = (not self.outline or
                          self.story_status in ["replan", "restart"] or
                          len(self.chapters) >= self.target_mid_completion)
            return needs_replan

        elif target_phase == "mid":
            # Transition back from macro once initial outline is created
            macro_done = ("story_outline" in self.macro_phase_data and
                          len(self.outline.get("chapters", [])) > 0)

            # Or transition from micro once current chapter is substantially complete
            micro_done = (self.current_chapter and
                         len(self.current_chapter.strip()) > 100 and  # Some minimal content threshold
                         self.micro_progress >= 1.0)
            return macro_done or micro_done

        elif target_phase == "micro":
            # Transition when mid phase has sufficient chapter details to proceed to content creation
            mid_ready = ("chapter_details" in self.mid_phase_data and
                        self.current_chapter_index < len(self.chapters) + 1)
            return mid_ready

        return False