from typing import Dict, Any, Literal
from langgraph.graph import END
from .state import GraphState


def route_after_planner(state: GraphState) -> str:
    """Route to the next node after the planner has run."""
    # After planning, move to the writer
    return "writer"


def route_after_writer(state: GraphState) -> str:
    """Route to the next node after the writer has run."""
    # After writing, move to the humanizer to remove AI traces
    return "humanizer"


def route_after_archivist(state: GraphState) -> str:
    """Route to the next node after the archivist has run."""
    # After archivist organizes content, check consistency
    return "consistency_checker"


def route_after_editor(state: GraphState) -> str:
    """Route to the next node after the editor has run."""
    # After editing, move to consistency checker
    return "consistency_checker"


def route_after_consistency_checker(state: GraphState) -> str:
    """Route to the next node after the consistency checker has run."""
    # After consistency checking, improve dialogue
    return "dialogue_specialist"


def route_after_dialogue_specialist(state: GraphState) -> str:
    """Route to the next node after the dialogue specialist has run."""
    # After dialogue improvement, develop the world elements
    return "world_builder"


def route_after_world_builder(state: GraphState) -> str:
    """Route to the next node after the world builder has run."""
    # After world building, analyze the pacing
    return "pacing_advisor"


def route_after_pacing_advisor(state: GraphState) -> str:
    """Route to the next node after the pacing advisor has run."""
    # After pacing analysis, decide if human review is needed
    if state.needs_human_review:
        return "human_review"
    else:
        # If chapter is completed, go back to planner for next chapter; else continue refining
        chapter_completed = len(state.completed_chapters) > 0
        if chapter_completed:
            return "planner"
        else:
            return "editor"


def route_after_humanizer(state: GraphState) -> str:
    """Route to the next node after the humanizer has run."""
    # After humanizing, the content might be ready to save and then continue workflow
    if state.current_chapter_index >= 0:  # If we just completed a chapter
        return "archivist"  # Run archivist to organize the complete chapter
    else:
        # If still developing this chapter, return to an improvement cycle
        return "editor"


def route_after_human_review(state: GraphState) -> str:
    """Route to the next node after human review."""
    if state.human_review_status == "approved":
        # If approved, continue with the workflow
        return "planner"
    elif state.human_review_status == "rejected":
        # If rejected, potentially go back to editor to incorporate feedback
        return "editor"
    else:
        # Default action if status is unknown
        return "planner"


def route_workflow_logic(state: GraphState) -> str:
    """Main routing function that determines the next node based on current state."""
    # Check if we have completed a chapter (by seeing if it was added to the chapters list)
    chapter_in_progress = bool(state.current_chapter and len(state.current_chapter) > 50)  # Simple metric
    chapter_completed = len(state.completed_chapters) > len([c for c in state.chapters if c.get('completed_at_iteration', 0) < state.iteration_count])

    if state.next_agent:
        # Follow predetermined next agent if set
        if state.next_agent == "planner":
            return "planner"
        elif state.next_agent == "writer":
            return "writer"
        elif state.next_agent == "archivist":
            return "archivist"
        elif state.next_agent == "editor":
            return "editor"
        elif state.next_agent == "consistency_checker":
            return "consistency_checker"
        elif state.next_agent == "dialogue_specialist":
            return "dialogue_specialist"
        elif state.next_agent == "world_builder":
            return "world_builder"
        elif state.next_agent == "pacing_advisor":
            return "pacing_advisor"
        elif state.next_agent == "humanizer":
            return "humanizer"
        elif state.next_agent == "human_review":
            return "human_review"

    # Default routing based on story progress
    if state.current_phase == "planning":
        return "planner"
    elif state.current_phase == "writing":
        if chapter_in_progress:
            return "humanizer"  # Process current content first
        else:
            return "planner"  # Plan before writing
    elif state.current_phase == "editing":
        return "editor"
    elif state.current_phase == "review":
        if state.needs_human_review:
            return "human_review"
        else:
            return "planner"
    else:
        # Default fallback to planner
        return "planner"


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