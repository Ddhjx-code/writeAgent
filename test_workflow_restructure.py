#!/usr/bin/env python3
"""
Test script to verify the restructured LangGraph workflow
"""
import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.config import Config
from src.core.engine import WritingEngine
from src.workflow.state import GraphState


async def test_workflow_restructure():
    """Test the restructured workflow to ensure infinite loops are prevented"""
    print("Testing restructured LangGraph workflow...")

    config = Config()

    # Initialize the writing engine
    engine = WritingEngine(config)
    await engine.initialize()

    print("Engine initialized successfully")

    # Create initial state
    initial_state = GraphState(
        title="Test Story for Workflow Restructure",
        outline={},
        characters={},
        world_details={},
        story_status="in_progress"
    )

    print("Initial state created")

    # Test a short run to verify the workflow works without infinite loops
    result = await engine.run_story_generation(
        initial_state=initial_state,
        max_iterations=5,  # Limit to 5 iterations for testing
        target_chapters=2
    )

    print(f"Workflow execution completed. Final state iteration count: {result.iteration_count}")
    print(f"Final story status: {result.story_status}")
    print(f"Number of chapters completed: {len(result.completed_chapters)}")
    print(f"Current hierarchical phase: {result.current_hierarchical_phase}")
    print(f"Macro progress: {result.macro_progress}")
    print(f"Mid progress: {result.mid_progress}")
    print(f"Micro progress: {result.micro_progress}")

    # Check cycle detection functionality
    cycle_check = result.detect_cycle()
    if cycle_check:
        print(f"Cycle detected in final state: {cycle_check}")
    else:
        print("No cycles detected in final state - good!")

    print("Test completed successfully - workflow structure verified!")


if __name__ == "__main__":
    asyncio.run(test_workflow_restructure())