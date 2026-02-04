from typing import Dict, Any, Literal
from langgraph.graph import END
from .state import GraphState
from .phase_manager import HierarchicalPhaseManager

# Initialize the hierarchical phase manager
phase_manager = HierarchicalPhaseManager()


def route_after_planner(state: GraphState) -> str:
    """Route to the next node after the planner has run."""
    # Update phase progress
    updated_state = phase_manager.update_phase_progress(state)

    # Determine next node based on the current hierarchical phase
    if updated_state.current_hierarchical_phase == "macro":
        # In macro phase, planner typically sets up basic structure
        # Move to world builder to establish global settings
        return "world_builder"
    elif updated_state.current_hierarchical_phase == "mid":
        # In mid phase, planner works on chapter-specific details
        # Move to next mid-level organization step
        return "archivist"
    else:  # micro
        # In micro phase, after planning a particular section
        # Move to writer to create content
        return "writer"


def route_after_writer(state: GraphState) -> str:
    """Route to the next node after the writer has run."""
    # Update phase progress
    updated_state = phase_manager.update_phase_progress(state)

    # Writer primarily operates in micro phase only
    if updated_state.current_hierarchical_phase != "micro":
        # For non-micro phases, bypass writer
        return "planner"

    # After writing, move to the humanizer to remove AI traces
    return "humanizer"


def route_after_archivist(state: GraphState) -> str:
    """Route to the next node after the archivist has run."""
    # Update phase progress
    updated_state = phase_manager.update_phase_progress(state)

    # Archivist operates in all phases for continuity
    if updated_state.current_hierarchical_phase in ["macro", "mid"]:
        # In macro/mid phases, focus is on organization and consistency checking
        return "consistency_checker"
    else:  # micro
        # In micro phase, after organizing content, check consistency
        return "consistency_checker"


def route_after_editor(state: GraphState) -> str:
    """Route to the next node after the editor has run."""
    # Update phase progress
    updated_state = phase_manager.update_phase_progress(state)

    # Editor primarily operates in micro phase to refine detailed content
    if updated_state.current_hierarchical_phase in ["macro", "mid"]:
        # For macro/mid phases, editor may not be primary path
        # Check completion of phase
        completion = phase_manager.evaluate_phase_completion(updated_state)
        if completion["phase_complete"]:
            # Switch phase
            recommended = completion["recommended_next_phase"]
            if recommended == "macro":
                return "planner"  # Return to high-level planning
            elif recommended == "mid":
                return "planner"  # Plan chapter details
            else:  # micro
                return "writer"  # Create content
        else:
            return "consistency_checker"
    else:  # micro
        # After editing, move to consistency checker
        return "consistency_checker"


def route_after_consistency_checker(state: GraphState) -> str:
    """Route to the next node after the consistency checker has run."""
    # Update phase progress
    updated_state = phase_manager.update_phase_progress(state)

    # Determine routing based on hierarchical phase
    if updated_state.current_hierarchical_phase == "macro":
        # In macro phase, check if we need more planning
        completion = phase_manager.evaluate_phase_completion(updated_state)
        if completion["phase_complete"]:
            return "pacing_advisor"  # Move to pacing advisor
        else:
            return "planner"  # Continue planning
    elif updated_state.current_hierarchical_phase == "mid":
        # In mid phase, after checking consistency
        return "dialogue_specialist"  # Continue with dialogue specialist
    else:  # micro
        # After consistency checking, improve dialogue
        return "dialogue_specialist"


def route_after_dialogue_specialist(state: GraphState) -> str:
    """Route to the next node after the dialogue specialist has run."""
    # Update phase progress
    updated_state = phase_manager.update_phase_progress(state)

    # Dialogue specialist primarily operates in micro phase
    if updated_state.current_hierarchical_phase == "micro":
        # After dialogue improvement, consider next steps
        return "editor"  # Return to editor for further refinement
    elif updated_state.current_hierarchical_phase == "mid":
        # In mid phase, move to next organizing agent
        return "archivist"  # Continue organizing chapter-level details
    else:  # macro
        # In macro phase, might need more structural elements
        return "world_builder"  # Build more world details


def route_after_world_builder(state: GraphState) -> str:
    """Route to the next node after the world builder has run."""
    # Update phase progress
    updated_state = phase_manager.update_phase_progress(state)

    # World builder primarily operates in macro phase
    if updated_state.current_hierarchical_phase == "macro":
        # After world building at macro level, check completion
        completion = phase_manager.evaluate_phase_completion(updated_state)
        if completion["phase_complete"]:
            return "pacing_advisor"  # Move to pacing advisor
        else:
            return "planner"  # Continue planning foundational structure
    elif updated_state.current_hierarchical_phase == "mid":
        # In mid phase, world building is for chapter-specific details
        return "archivist"  # Organize new details
    else:  # micro
        # In micro phase, light world detail adjustments
        return "consistency_checker"  # Check consistency of new elements


def route_after_pacing_advisor(state: GraphState) -> str:
    """Route to the next node after the pacing advisor has run."""
    # Update phase progress
    updated_state = phase_manager.update_phase_progress(state)

    # Pacing advisor operates primarily in macro and mid phases
    if updated_state.current_hierarchical_phase == "macro":
        # After pacing advice at macro level, check phase completion
        completion = phase_manager.evaluate_phase_completion(updated_state)
        if completion["phase_complete"]:
            # Transition to mid to start chapter planning
            return "planner"  # Start mid-level planning
        else:
            return "planner"  # Continue planning
    elif updated_state.current_hierarchical_phase == "mid":
        # After pacing input in mid phase, check if ready for content creation
        if len(state.chapters) < state.target_mid_completion:
            return "planner"  # Plan more chapter details
        else:
            # Ready to move to micro phase
            return "writer"  # Start content creation
    else:  # micro
        # At micro level, after pacing considerations
        if state.needs_human_review:
            return "human_review"  # Check if human review needed
        else:
            # Determine if chapter is complete enough to move to next
            if updated_state.micro_progress >= 1.0:
                return "archivist"  # Organize completed chapter
            else:
                return "writer"  # Continue writing


def route_after_humanizer(state: GraphState) -> str:
    """Route to the next node after the humanizer has run."""
    # Update phase progress
    updated_state = phase_manager.update_phase_progress(state)

    # Humanizer operates primarily in micro phase
    if updated_state.current_hierarchical_phase == "micro":
        # After humanizing, check if chapter is complete
        if state.current_chapter_index >= 0:  # If we just completed a chapter
            return "archivist"  # Run archivist to organize the complete chapter
        else:
            # If still developing this chapter, check where to go next
            return "editor"  # Return to editor for improvements
    else:
        # In other phases, humanizer is less relevant, return to macro workflow
        return "consistency_checker"


def route_after_human_review(state: GraphState) -> str:
    """Route to the next node after human review."""
    if state.human_review_status == "approved":
        # If approved, determine next move based on phase
        if state.current_hierarchical_phase == "micro":
            # In micro phase, after approved review, check if chapter is complete
            if len(state.chapters) >= len(state.outline.get("chapters", [])):
                # Completed available chapter outlines, go back to planning
                return "planner"
            else:
                # Continue creating content
                return "writer"
        else:
            # In macro/mid phase, after review
            return "planner"
    elif state.human_review_status == "rejected":
        # If rejected, go back to editor to incorporate feedback
        return "editor"
    else:
        # Default action if status is unknown
        return "planner"


def route_workflow_logic(state: GraphState) -> str:
    """Main routing function that determines the next node based on current state and hierarchical phase."""
    # Update phase progress
    updated_state = phase_manager.update_phase_progress(state)

    # Check if we should transition to a different hierarchical phase
    if phase_manager.should_transition_to_phase(updated_state, "macro"):
        updated_state = phase_manager.prepare_phase_transition(updated_state, "macro")
        return "planner"
    elif phase_manager.should_transition_to_phase(updated_state, "mid") and updated_state.current_hierarchical_phase != "macro":
        updated_state = phase_manager.prepare_phase_transition(updated_state, "mid")
        return "planner"
    elif phase_manager.should_transition_to_phase(updated_state, "micro") and updated_state.current_hierarchical_phase in ["mid", "macro"]:
        updated_state = phase_manager.prepare_phase_transition(updated_state, "micro")
        return "writer"

    chapter_in_progress = bool(state.current_chapter and len(state.current_chapter) > 50)  # Simple metric
    chapter_completed = len(state.completed_chapters) > len([c for c in state.chapters if c.get('completed_at_iteration', 0) < state.iteration_count])

    if state.next_agent:
        # Follow predetermined next agent if set
        # Check if this agent is allowed in current phase
        if phase_manager.should_execute_agent_in_phase(state.next_agent, state.current_hierarchical_phase):
            if state.next_agent == "planner":
                return "planner"
            elif state.next_agent == "writer":
                if phase_manager.should_execute_agent_in_phase("writer", state.current_hierarchical_phase):
                    return "writer"
            elif state.next_agent == "archivist":
                return "archivist"
            elif state.next_agent == "editor":
                if phase_manager.should_execute_agent_in_phase("editor", state.current_hierarchical_phase):
                    return "editor"
            elif state.next_agent == "consistency_checker":
                return "consistency_checker"
            elif state.next_agent == "dialogue_specialist":
                if phase_manager.should_execute_agent_in_phase("dialogue_specialist", state.current_hierarchical_phase):
                    return "dialogue_specialist"
            elif state.next_agent == "world_builder":
                if phase_manager.should_execute_agent_in_phase("world_builder", state.current_hierarchical_phase):
                    return "world_builder"
            elif state.next_agent == "pacing_advisor":
                if phase_manager.should_execute_agent_in_phase("pacing_advisor", state.current_hierarchical_phase):
                    return "pacing_advisor"
            elif state.next_agent == "humanizer":
                if phase_manager.should_execute_agent_in_phase("humanizer", state.current_hierarchical_phase):
                    return "humanizer"
            elif state.next_agent == "human_review":
                return "human_review"

    # Default routing based on hierarchy and story progress
    if state.current_hierarchical_phase == "macro":
        # In macro phase, focus on high-level planning
        if not state.outline or len(state.outline) == 0:
            return "planner"
        elif not state.world_details or len(state.world_details) < 3:  # Arbitrary number
            return "world_builder"
        else:
            return "pacing_advisor"  # Check/adjust pacing strategy

    elif state.current_hierarchical_phase == "mid":
        # In mid phase, work on chapter organization
        if len(state.chapters) < state.target_mid_completion and state.outline.get("chapters"):
            return "planner"  # Plan additional chapters
        else:
            # Ready to work on content
            return "writer"
    else:  # state.current_hierarchical_phase == "micro"
        # In micro phase, focus on content creation and refinement
        if chapter_in_progress:
            if state.current_chapter_index < len(state.chapters):
                return "editor"  # Refine current content
            else:
                return "writer"  # Continue writing
        else:
            return "planner"  # Plan current chapter content


# Define conditional edges for the workflow
CONDITIONAL_EDGES = {
    "planner": route_after_planner,
    "writer": route_after_writer,
    "archivist": route_after_archivist,
    "editor": route_after_editor,
    "consistency_checker": route_after_consistency_checker,
    "dialogue_specialist": route_after_dialogue_specialist,
    "world_builder": route_after_world_builder,
    "pacing_advisor": route_after_pacing_advisor,
    "humanizer": route_after_humanizer,
    "human_review": route_after_human_review,
}


# Define the default route function
DEFAULT_ROUTE = route_workflow_logic