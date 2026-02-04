"""Hierarchical Phase Manager for the Novel Writing System."""

from typing import Literal, Dict, Any, Optional, List
from .state import GraphState


class HierarchicalPhaseManager:
    """Manages transitions between macro, mid, and micro hierarchical phases in the workflow."""

    def __init__(self):
        # Define the conditions that might trigger transitions between phases
        self.transition_rules = {
            "macro_to_mid": {
                "outline_substantiated": True,  # When we have a basic story outline
                "world_building_complete": False,  # World building could be optional in transition
            },
            "mid_to_macro": {
                "needs_restructure": False,  # When story needs restructuring
                "outline_inadequate": False,  # When current outline is insufficient
            },
            "mid_to_micro": {
                "chapter_details_planned": True,  # When we have details for the chapter we're creating
                "characters_developed": True,  # Sufficient character development for current chapter
            },
            "micro_to_mid": {
                "chapter_completion_threshold": 0.9,  # When chapter is 90% complete
                "needs_integration": True,  # When need to integrate with other chapters or re-plan
            }
        }

    def update_phase_progress(self, state: GraphState) -> GraphState:
        """Update progress metrics for the current phase."""
        updated_state = state.copy()

        if state.current_hierarchical_phase == "macro":
            # Calculate macro phase progress based on story structure setup
            progress = 0.0
            if state.outline and len(state.outline) > 0:
                progress += 0.3  # Outline complete

            if state.world_details and len(state.world_details) > 0:
                progress += 0.2  # World details

            if state.characters and len(state.characters) > 0:
                progress += 0.2  # Character creation complete

            # Additional factors that might influence progress
            if "story_arc" in state.outline:
                progress += 0.3

            updated_state.macro_progress = min(1.0, progress)

        elif state.current_hierarchical_phase == "mid":
            # Calculate mid phase progress based on chapter planning
            progress = 0.0
            if state.outline.get("chapters"):
                progress = min(1.0, len(state.chapters) / max(state.target_mid_completion, 1))

            updated_state.mid_progress = progress

        else:  # micro phase
            # Calculate micro phase progress based on current chapter completion
            current_content_length = len(state.current_chapter or "")
            progress = min(1.0, current_content_length / 5000)  # Normalized against 5000 chars per chapter

            # Also consider how many chapters are complete
            chapter_completion = len(state.chapters) / max(state.target_mid_completion, 1) if state.target_mid_completion > 0 else 0.0
            progress = max(progress, chapter_completion)

            updated_state.micro_progress = progress

        return updated_state

    def should_transition_to_phase(self, state: GraphState, target_phase: Literal["macro", "mid", "micro"]) -> bool:
        """Determine if the system should transition to the specified hierarchical phase."""
        # Check if the transition is allowed based on current state
        current = state.current_hierarchical_phase

        if current == target_phase:
            return False  # Already in this phase

        # Allowable transitions
        allowed_transitions = {
            "macro": ["mid"],
            "mid": ["macro", "micro"],
            "micro": ["mid"]
        }

        if target_phase not in allowed_transitions.get(current, []):
            return False

        # Check specific conditions for each transition
        if current == "macro" and target_phase == "mid":
            # Transition from macro to mid when structure is adequately defined
            return len(state.outline) > 0 and state.title.strip() != ""

        elif current == "mid" and target_phase == "macro":
            # Transition from mid back to macro when story needs re-planning
            needs_replan = (state.story_status in ["replan", "restart", "restructure"]
                           or not state.outline.get("chapters"))
            return needs_replan

        elif current == "mid" and target_phase == "micro":
            # Transition from mid to micro when we have chapter details to create
            return (len(state.chapters) < state.target_mid_completion and
                   bool(state.outline.get("chapters")))

        elif current == "micro" and target_phase == "mid":
            # Transition from micro to mid when current chapter is complete
            return (state.micro_progress >= 1.0 or
                   len(state.chapters) >= state.target_mid_completion)

        return False

    def prepare_phase_transition(self, state: GraphState, target_phase: Literal["macro", "mid", "micro"]) -> GraphState:
        """Prepare the state for a transition to the target phase."""
        updated_state = state.copy()

        # Update the phase
        updated_state.current_hierarchical_phase = target_phase

        # Set up phase-specific data and initialization
        if target_phase == "macro":
            # Prepare for macro-level world building and story architecture
            if not updated_state.macro_phase_data:
                updated_state.macro_phase_data = {
                    "world_building_status": "pending",
                    "story_arc_status": "pending",
                    "character_framework_status": "pending",
                    "planning_iteration": 0
                }
            updated_state.macro_phase_data["planning_iteration"] += 1

        elif target_phase == "mid":
            # Prepare for mid-level chapter organization
            if not updated_state.mid_phase_data:
                updated_state.mid_phase_data = {
                    "chapter_planning_progress": 0,
                    "character_integration": 0,
                    "world_detail_integration": 0,
                    "planning_iteration": 0
                }
            updated_state.mid_phase_data["planning_iteration"] += 1

        else:  # target_phase == "micro"
            # Prepare for micro-level content creation
            if not updated_state.micro_phase_data:
                updated_state.micro_phase_data = {
                    "writing_progress": 0,
                    "editing_cycle": 0,
                    "content_refinement": 0,
                    "creation_iteration": 0
                }
            updated_state.micro_phase_data["creation_iteration"] += 1

        return updated_state

    def should_execute_agent_in_phase(self, agent_name: str, current_phase: Literal["macro", "mid", "micro"]) -> bool:
        """Determine if an agent should execute in the given hierarchical phase."""
        # Mapping of agents to appropriate phases
        agent_phase_mapping = {
            # Macro phase: High-level architectural tasks
            "world_builder": ["macro", "mid"],
            "pacing_advisor": ["macro", "mid"],
            "planner": ["macro", "mid"],

            # Mid phase: Organizational tasks
            "archivist": ["macro", "mid", "micro"],  # Continuity needed across all phases
            "consistency_checker": ["mid", "micro"],

            # Micro phase: Detailed execution tasks
            "writer": ["micro"],
            "editor": ["micro"],
            "dialogue_specialist": ["micro"],
            "humanizer": ["micro"],
        }

        # Get list of allowed phases for this agent
        allowed_phases = agent_phase_mapping.get(agent_name, ["macro", "mid", "micro"])

        # If current phase is in the allowed phases, return True
        return current_phase in allowed_phases

    def get_agents_for_phase(self, current_phase: Literal["macro", "mid", "micro"]) -> List[str]:
        """Get list of agents that should operate in the specified phase."""
        phase_agents = {
            "macro": ["planner", "world_builder", "pacing_advisor"],
            "mid": ["planner", "archivist", "consistency_checker"],
            "micro": ["writer", "editor", "dialogue_specialist", "archivist",
                     "consistency_checker", "humanizer"]
        }
        return phase_agents.get(current_phase, [])

    def evaluate_phase_completion(self, state: GraphState) -> Dict[str, Any]:
        """Evaluate whether the current phase is complete and what to do next."""
        current_phase = state.current_hierarchical_phase
        completion_status = {
            "phase_complete": False,
            "recommended_next_phase": current_phase,
            "reasoning": "",
            "progress": 0.0
        }

        if current_phase == "macro":
            # Macro phase complete when basic story architecture is established
            completion_status["progress"] = state.macro_progress
            is_complete = (
                bool(state.outline.get("story_arc")) and
                len(state.outline.get("chapters", [])) >= 3 and  # At least a few chapter plans
                bool(state.world_details) and
                len(state.characters) >= 2  # At least main characters
            )

            completion_status["phase_complete"] = is_complete
            completion_status["recommended_next_phase"] = "mid" if is_complete else "macro"
            completion_status["reasoning"] = (
                "Story framework established, proceeding to mid-level chapter planning"
                if is_complete else "Need more macro-level structure"
            )

        elif current_phase == "mid":
            # Mid phase complete when chapter plans are adequate
            completion_status["progress"] = state.mid_progress
            is_complete = (
                len(state.chapters) >= state.target_mid_completion or
                len(state.outline.get("chapters", [])) == len(state.chapters)
            )

            completion_status["phase_complete"] = is_complete
            # Use HierarchicalPhaseManager's method to determine transition instead of GraphState's method
            completion_status["recommended_next_phase"] = "micro" if is_complete else (
                "macro" if self.should_transition_to_phase(state, "macro") else "mid"
            )
            completion_status["reasoning"] = (
                "Chapter plans ready for detailed creation"
                if is_complete else "Creating more chapter plans"
            )

        else:  # micro
            # Micro phase complete when chapter is sufficiently developed
            completion_status["progress"] = state.micro_progress
            is_complete = (
                state.micro_progress >= 1.0 or
                len(state.chapters) >= state.target_mid_completion
            )

            completion_status["phase_complete"] = is_complete
            completion_status["recommended_next_phase"] = (
                "mid" if is_complete and len(state.chapters) < state.target_mid_completion else
                "macro" if self.should_transition_to_phase(state, "macro") else
                "micro"
            )
            completion_status["reasoning"] = (
                "Current chapter complete, moving to next phase"
                if is_complete else "Adding more content to current chapter"
            )

        return completion_status