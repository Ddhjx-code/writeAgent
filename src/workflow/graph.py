from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from ..config import Config
from ..knowledge.store import KnowledgeStore
from .state import GraphState
from .nodes import NodeManager
from .edges import CONDITIONAL_EDGES, DEFAULT_ROUTE
from .phase_manager import HierarchicalPhaseManager


class NovelWritingGraph:
    """Main LangGraph workflow for the AI collaborative novel writing system with hierarchical phase support."""

    def __init__(self, config: Config):
        self.config = config
        self.knowledge_store = KnowledgeStore(config)
        self.node_manager = NodeManager(config, self.knowledge_store)
        self.phase_manager = HierarchicalPhaseManager()
        self.workflow = None

    async def initialize(self):
        """Initialize the workflow graph."""
        await self.knowledge_store.initialize()
        # Initialize nodes might do some setup, but mostly they're ready to go
        # Create the LangGraph state graph
        self.workflow = StateGraph(GraphState)

        # Add nodes to the graph
        self.workflow.add_node("planner", self.node_manager.planner_node)
        self.workflow.add_node("writer", self.node_manager.writer_node)
        self.workflow.add_node("archivist", self.node_manager.archivist_node)
        self.workflow.add_node("editor", self.node_manager.editor_node)
        self.workflow.add_node("consistency_checker", self.node_manager.consistency_checker_node)
        self.workflow.add_node("dialogue_specialist", self.node_manager.dialogue_specialist_node)
        self.workflow.add_node("world_builder", self.node_manager.world_builder_node)
        self.workflow.add_node("pacing_advisor", self.node_manager.pacing_advisor_node)
        self.workflow.add_node("humanizer", self.node_manager.humanizer_node)
        self.workflow.add_node("human_review", self.node_manager.human_review_node)

        # Set up the conditional edges - now with hierarchical phase-aware routing
        for node_name, condition_func in CONDITIONAL_EDGES.items():
            self.workflow.add_conditional_edges(node_name, condition_func)

        # Set up the entry point to start the workflow - defaults to planner which will handle phase initialization
        self.workflow.set_entry_point("planner")

        # Compile the graph
        self.compiled_graph = self.workflow.compile()

    def get_graph(self):
        """Return the compiled graph for running."""
        if not self.compiled_graph:
            raise RuntimeError("Graph not initialized. Call initialize() first.")
        return self.compiled_graph

    async def run_workflow(self, initial_state: GraphState, debug: bool = False) -> GraphState:
        """Run the complete workflow with the given initial state."""
        if not self.compiled_graph:
            await self.initialize()

        if debug:
            print(f"Starting novel writing workflow in {initial_state.current_hierarchical_phase} phase...")

        # Run the graph with the initial state
        final_state = await self.compiled_graph.ainvoke(initial_state)

        if debug:
            print(f"Workflow completed. Final state: {final_state.current_phase}, Hierarchical Phase: {final_state.current_hierarchical_phase}")

        return final_state

    async def run_single_step(self, current_state: GraphState, step_node: str) -> GraphState:
        """Run a single step of the workflow."""
        if not self.compiled_graph:
            await self.initialize()

        # Based on the step_node, run the appropriate node function
        if step_node == "planner":
            return await self.node_manager.planner_node(current_state)
        elif step_node == "writer":
            return await self.node_manager.writer_node(current_state)
        elif step_node == "archivist":
            return await self.node_manager.archivist_node(current_state)
        elif step_node == "editor":
            return await self.node_manager.editor_node(current_state)
        elif step_node == "consistency_checker":
            return await self.node_manager.consistency_checker_node(current_state)
        elif step_node == "dialogue_specialist":
            return await self.node_manager.dialogue_specialist_node(current_state)
        elif step_node == "world_builder":
            return await self.node_manager.world_builder_node(current_state)
        elif step_node == "pacing_advisor":
            return await self.node_manager.pacing_advisor_node(current_state)
        elif step_node == "humanizer":
            return await self.node_manager.humanizer_node(current_state)
        elif step_node == "human_review":
            return await self.node_manager.human_review_node(current_state)
        else:
            raise ValueError(f"Unknown step node: {step_node}")

    def visualize(self, output_path: str = "workflow.png") -> str:
        """Generate a visualization of the workflow."""
        if not self.compiled_graph:
            raise RuntimeError("Graph not initialized. Call initialize() first.")

        try:
            # This would generate the visualization
            img_bytes = self.compiled_graph.get_graph(xray=True).draw_mermaid_png()
            with open(output_path, 'wb') as f:
                f.write(img_bytes)
            return output_path
        except Exception as e:
            print(f"Could not generate visualization: {e}")
            # Return None to indicate failure
            return None

    async def reset_workflow(self):
        """Reset the workflow to its initial state."""
        self.compiled_graph = None
        await self.initialize()

    async def run_with_phase_management(self, initial_state: GraphState, debug: bool = False) -> GraphState:
        """Run workflow with explicit phase management for more control over hierarchical transitions."""
        if not self.compiled_graph:
            await self.initialize()

        current_state = initial_state
        max_iterations = initial_state.max_iterations

        iteration_count = 0
        while iteration_count < max_iterations and current_state.should_continue():
            # Update phase progress
            current_state = self.phase_manager.update_phase_progress(current_state)

            # Check if we should transition to a different phase
            should_transition = self.phase_manager.should_transition_to_phase(current_state, "macro")
            if not should_transition:
                should_transition = self.phase_manager.should_transition_to_phase(current_state, "mid") and current_state.current_hierarchical_phase != "macro"
            if not should_transition:
                should_transition = self.phase_manager.should_transition_to_phase(current_state, "micro") and current_state.current_hierarchical_phase in ["mid", "macro"]

            if should_transition:
                # Prepare for phase transition
                target_phase = "macro" if self.phase_manager.should_transition_to_phase(current_state, "macro") else \
                              "mid" if self.phase_manager.should_transition_to_phase(current_state, "mid") and current_state.current_hierarchical_phase != "macro" else \
                              "micro"
                current_state = self.phase_manager.prepare_phase_transition(current_state, target_phase)
                if debug:
                    print(f"Phase transition: {target_phase} at iteration {iteration_count}")

            # Run a step of the workflow
            current_state = await self.compiled_graph.ainvoke(current_state)

            iteration_count += 1

        return current_state