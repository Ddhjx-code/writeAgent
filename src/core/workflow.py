from typing import Dict, List, Any, Optional
try:
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolExecutor, ToolInvocation
    from langchain_core.tools import tool
except ImportError:
    # Mock imports if LangGraph is not available
    StateGraph = None
    END = None
    ToolExecutor = None
    ToolInvocation = None
    tool = lambda f: f

from src.core.story_state import StoryState
try:
    from src.core.knowledge_base import KnowledgeBase  # Original full knowledge base
except ImportError:
    from src.core.knowledge_base_minimal import KnowledgeBase  # Fallback minimal version
from src.core.agent_factory import AgentFactory
from src.agents.base import BaseAgent
from pydantic import BaseModel
from enum import Enum
import asyncio


class NodeType(str, Enum):
    """Enum representing different node types in the workflow"""
    START = "start"
    PLANNING = "planning"
    WRITING = "writing"
    REVIEW = "review"
    EDITING = "editing"
    ARCHIVE = "archive"
    CONSISTENCY_CHECK = "consistency_check"
    DIALOGUE_ENHANCE = "dialogue_enhance"
    WORLD_BUILDING = "world_building"
    PACING_ADJUST = "pacing_adjust"
    HUMAN_REVIEW = "human_review"
    END = "end"


class WorkflowState(BaseModel):
    """State model for the LangGraph workflow"""
    model_config = {"arbitrary_types_allowed": True}

    story_state: StoryState
    current_chapter: str = ""
    current_agent: str = ""
    review_needed: bool = False
    human_feedback: str = ""
    task_completed: str = ""  # e.g. "draft", "revised", "final"
    agents: Dict[str, BaseAgent] = {}
    knowledge_base: KnowledgeBase


class NovelWritingWorkflow:
    """
    LangGraph workflow for novel writing with multiple AI agents working together
    """

    def __init__(self, knowledge_base: KnowledgeBase):
        self.knowledge_base = knowledge_base
        self.agent_factory = AgentFactory(knowledge_base)
        self.agents = self.agent_factory.create_all_agents()
        self.knowledge_base = knowledge_base

        # Check if LangGraph is available
        if StateGraph is None:
            print("LangGraph not available, workflow not constructed")
            self.workflow = None
            self.app = None
        else:
            # Create the workflow graph
            self.workflow = StateGraph(WorkflowState)

            # Add nodes with the updated architecture (global planning then per-chapter processing)
            self._add_improved_nodes()

            # Add edges with the updated flow
            self._add_improved_edges()

            # Compile the graph
            self.app = self.workflow.compile()

    def _add_improved_nodes(self):
        """Add all nodes to the workflow graph with improved architecture"""
        self.workflow.add_node(NodeType.START, self.start_node)
        # Phase 1: Global planning (done once)
        self.workflow.add_node(NodeType.GLOBAL_PLANNING, self.global_planning_node)
        self.workflow.add_node(NodeType.GLOBAL_PACING_SETUP, self.global_pacing_setup_node)
        # Phase 2: Per-chapter processing (done for each chapter)
        self.workflow.add_node(NodeType.PROCESS_CHAPTER, self.process_single_chapter)
        self.workflow.add_node(NodeType.DIALOGUE_ENHANCE, self.dialogue_enhance_node)
        self.workflow.add_node(NodeType.WORLD_BUILDING, self.world_building_node)
        self.workflow.add_node(NodeType.CONSISTENCY_CHECK, self.consistency_check_node)
        self.workflow.add_node(NodeType.EDITING, self.editing_node)
        self.workflow.add_node(NodeType.ARCHIVE, self.archive_node)
        # Phase 3: Final integration (done once)
        self.workflow.add_node(NodeType.INTEGRATE_FULL_STORY, self.integrate_full_story_node)
        self.workflow.add_node(NodeType.END, self.end_node)

    def _add_improved_edges(self):
        """Define the execution flow between nodes with improved architecture"""
        # Phase 1: Initial global setup
        self.workflow.add_edge(NodeType.START, NodeType.GLOBAL_PLANNING)
        self.workflow.add_edge(NodeType.GLOBAL_PLANNING, NodeType.GLOBAL_PACING_SETUP)

        # Phase 2: Per-chapter processing with loop
        self.workflow.add_edge(NodeType.GLOBAL_PACING_SETUP, NodeType.PROCESS_CHAPTER)

        # Chapter processing flow: Writer -> Dialogue -> World -> Consistency -> Edit -> Archive
        self.workflow.add_edge(NodeType.PROCESS_CHAPTER, NodeType.DIALOGUE_ENHANCE)
        self.workflow.add_edge(NodeType.DIALOGUE_ENHANCE, NodeType.WORLD_BUILDING)
        self.workflow.add_edge(NodeType.WORLD_BUILDING, NodeType.CONSISTENCY_CHECK)
        self.workflow.add_edge(NodeType.CONSISTENCY_CHECK, NodeType.EDITING)
        self.workflow.add_edge(NodeType.EDITING, NodeType.ARCHIVE)

        # Loop back to process next chapter if more chapters are needed
        self.workflow.add_conditional_edges(
            NodeType.ARCHIVE,
            self._should_continue_writing,  # Check if we need to write more chapters
            {
                "continue": NodeType.PROCESS_CHAPTER,
                "complete": NodeType.INTEGRATE_FULL_STORY
            }
        )

        # Phase 3: Final integration
        self.workflow.add_edge(NodeType.INTEGRATE_FULL_STORY, NodeType.END)

        # Start and end configuration
        self.workflow.set_entry_point(NodeType.START)
        self.workflow.set_finish_point(NodeType.END)

    def global_planning_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Global planning phase - creates story arc, outlines all chapters, characters and locations"""
        print("Running Planner Agent for global story planning")

        # Get the planner agent
        planner_agent = state.agents.get("Planner")
        if not planner_agent:
            planner_agent = self.agents.get("Planner")

        if planner_agent:
            # Create story arc for the entire novel
            context = {
                "action": "design_story_arc",
                "target_chapters": state.story_state.target_chapter_count,
                "story_type": "three_act",
                "theme": "general"
            }

            result = planner_agent.process(state.story_state, context)
            print(f"Global planning result: {result}")

            # Also create general outlines for all chapters now
            if state.story_state.target_chapter_count > 0:
                # Create basic outlines for each chapter (will be refined individually later)
                for chap_num in range(1, state.story_state.target_chapter_count + 1):
                    context = {
                        "action": "outline_chapter",
                        "chapter_number": chap_num,
                        "title": f"Chapter {chap_num}",
                        "plot_advancement": f"Advance story plot for chapter {chap_num}",
                        "characters": list(state.story_state.characters.keys()),
                        "locations": list(state.story_state.locations.keys())
                    }
                    result = planner_agent.process(state.story_state, context)

        return {
            "current_agent": "Planner",
            "task_completed": "global_planning_complete",
            "story_state": state.story_state
        }

    def global_pacing_setup_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Global pacing setup phase - defines the pacing and tension across all chapters"""
        print("Running Pacing Advisor for global pacing setup")

        pacing_agent = state.agents.get("PacingAdvisor") if state.agents.get("PacingAdvisor") else self.agents.get("PacingAdvisor")

        if pacing_agent:
            # Plan pacing for the entire story first
            context = {
                "action": "evaluate_tension_arc",
                "content": state.story_state.summary,
                "total_chapters": state.story_state.target_chapter_count
            }

            result = pacing_agent.process(state.story_state, context)
            print(f"Global pacing setup result: {result}")

            # Apply pacing to metadata
            state.story_state.metadata["global_pacing_plan"] = result.get("tension_arc", [])

        return {
            "current_agent": "PacingAdvisor",
            "task_completed": "global_pacing_setup_complete",
            "story_state": state.story_state
        }

    def process_single_chapter(self, state: WorkflowState) -> Dict[str, Any]:
        """Process a single chapter according to the global plan"""
        print(f"Running Writer Agent for chapter {state.story_state.get_next_chapter_number()}")

        # Get the writer agent
        writer_agent = state.agents.get("Writer")
        if not writer_agent:
            writer_agent = self.agents.get("Writer")

        if writer_agent:
            # Determine chapter to write based on global planning
            next_chapter_num = state.story_state.get_next_chapter_number()

            # Get the chapter outline that was prepared in global planning
            # For now, we use a placeholder - in a full implementation, outlines would be stored by the planner
            outline = f"Chapter {next_chapter_num} outline based on global story arc"

            context = {
                "action": "write_chapter",
                "chapter_number": next_chapter_num,
                "outline": outline,
                "target_words": 2000,  # Could adjust based on pacing requirements
                "characters": list(state.story_state.characters.keys()),
                "locations": list(state.story_state.locations.keys())
            }

            result = writer_agent.process(state.story_state, context)
            print(f"Chapter writing result: {result}")

            # Extract the generated chapter ID to set as current
            if result.get("status") == "success":
                chapter_id = result.get("chapter_id")
                if chapter_id:
                    return {
                        "current_chapter": chapter_id,
                        "current_agent": "Writer",
                        "task_completed": "draft_written",
                        "story_state": state.story_state
                    }

        return {
            "current_agent": "Writer",
            "task_completed": "draft_written",
            "story_state": state.story_state
        }

    def integrate_full_story_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Final integration step to review entire story for consistency"""
        print("Performing final full story integration and consistency check")

        # Run consistency checker on the entire story
        consistency_agent = state.agents.get("ConsistencyChecker") if state.agents.get("ConsistencyChecker") else self.agents.get("ConsistencyChecker")

        if consistency_agent:
            context = {
                "action": "check_all_consistencies",
                "chapter_id": None  # Check all chapters
            }

            result = consistency_agent.process(state.story_state, context)
            print(f"Full story integration check result: {result}")

            # Perform a full story edit pass
            editor_agent = state.agents.get("Editor") if state.agents.get("Editor") else self.agents.get("Editor")
            if editor_agent:
                context = {
                    "action": "edit_content",
                    "focus": ["readability", "continuity", "cohesion"]
                }
                full_content = "\n".join([ch.content for ch in state.story_state.chapters.values()])
                editor_result = editor_agent.process(state.story_state, context)
                print(f"Full story editing result: {editor_result}")

        return {
            "current_agent": "Final Integration",
            "task_completed": "full_story_integrated",
            "story_state": state.story_state
        }

    def start_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Start node - initializes the workflow"""
        print("Starting the novel writing workflow")

        # Update task status
        updated_state = state.model_dump()
        return {
            "task_completed": "initiated",
            "current_agent": "system",
            "story_state": state.story_state
        }

    def planning_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Planning node - creates story outline and chapter plan"""
        print("Running Planner Agent for story planning")

        # Get the planner agent
        planner_agent = state.agents.get("Planner")
        if not planner_agent:
            planner_agent = self.agents.get("Planner")

        if planner_agent:
            # Determine chapter to plan based on current story state
            chapter_num = state.story_state.get_next_chapter_number()

            context = {
                "action": "outline_chapter",
                "chapter_number": chapter_num,
                "title": f"Chapter {chapter_num}",
                "plot_advancement": f"Advance story plot for chapter {chapter_num}",
                "characters": list(state.story_state.characters.keys()),
                "locations": list(state.story_state.locations.keys())
            }

            result = planner_agent.process(state.story_state, context)
            print(f"Planning result: {result}")

        return {
            "current_agent": "Planner",
            "task_completed": "outline_created",
            "story_state": state.story_state
        }

    def writing_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Writing node - generates chapter content"""
        print("Running Writer Agent for content creation")

        # Get the writer agent
        writer_agent = state.agents.get("Writer")
        if not writer_agent:
            writer_agent = self.agents.get("Writer")

        if writer_agent:
            # Identify chapter to write based on planning
            next_chapter_num = state.story_state.get_next_chapter_number()
            outline = f"Chapter {next_chapter_num} outline would typically come from planning stage"

            context = {
                "action": "write_chapter",
                "chapter_number": next_chapter_num,
                "outline": outline,
                "target_words": 2000,
                "characters": list(state.story_state.characters.keys()),
                "locations": list(state.story_state.locations.keys())
            }

            result = writer_agent.process(state.story_state, context)
            print(f"Writing result: {result}")

            # Extract the generated chapter ID to set as current
            if result.get("status") == "success":
                chapter_id = result.get("chapter_id")
                if chapter_id:
                    return {
                        "current_chapter": chapter_id,
                        "current_agent": "Writer",
                        "task_completed": "draft_written",
                        "story_state": state.story_state
                    }

        return {
            "current_agent": "Writer",
            "task_completed": "draft_written",
            "story_state": state.story_state
        }

    def consistency_check_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Consistency checking node"""
        print("Running Consistency Checker Agent")

        consistency_agent = state.agents.get("ConsistencyChecker")
        if not consistency_agent:
            consistency_agent = self.agents.get("ConsistencyChecker")

        if consistency_agent:
            context = {
                "action": "check_all_consistencies",
                "chapter_id": state.current_chapter
            }

            result = consistency_agent.process(state.story_state, context)
            print(f"Consistency check result: {result}")

        return {
            "current_agent": "ConsistencyChecker",
            "story_state": state.story_state
        }

    def dialogue_enhance_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Dialogue enhancement node"""
        print("Running Dialogue Specialist Agent")

        dialogue_agent = state.agents.get("DialogueSpecialist")
        if not dialogue_agent:
            dialogue_agent = self.agents.get("DialogueSpecialist")

        if dialogue_agent:
            context = {
                "action": "optimize_dialogue",
                "chapter_id": state.current_chapter
            }

            result = dialogue_agent.process(state.story_state, context)
            print(f"Dialogue enhancement result: {result}")

        return {
            "current_agent": "DialogueSpecialist",
            "story_state": state.story_state
        }

    def world_building_node(self, state: WorkflowState) -> Dict[str, Any]:
        """World building node"""
        print("Running World Builder Agent")

        world_agent = None
        if "WorldBuilder" in state.agents:
            world_agent = state.agents["WorldBuilder"]
        elif "WorldBuilder" in self.agents:
            world_agent = self.agents["WorldBuilder"]

        if world_agent:
            context = {
                "action": "enhance_scene",
                "chapter_id": state.current_chapter
            }

            result = world_agent.process(state.story_state, context)
            print(f"World building result: {result}")

        return {
            "current_agent": "WorldBuilder",
            "story_state": state.story_state
        }

    def pacing_adjust_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Pacing adjustment node"""
        print("Running Pacing Advisor Agent")

        pacing_agent = None
        if "PacingAdvisor" in state.agents:
            pacing_agent = state.agents["PacingAdvisor"]
        elif "PacingAdvisor" in self.agents:
            pacing_agent = self.agents["PacingAdvisor"]

        if pacing_agent:
            context = {
                "action": "adjust_pacing",
                "style": "balanced",
                "content": state.story_state.get_chapter(state.current_chapter).content if state.current_chapter else ""
            }

            result = pacing_agent.process(state.story_state, context)
            print(f"Pacing adjustment result: {result}")

        return {
            "current_agent": "PacingAdvisor",
            "story_state": state.story_state
        }

    def editing_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Editing node - improves readability and flow"""
        print("Running Editor Agent")

        editor_agent = None
        if "Editor" in state.agents:
            editor_agent = state.agents["Editor"]
        elif "Editor" in self.agents:
            editor_agent = self.agents["Editor"]

        if editor_agent:
            context = {
                "action": "edit_content",
                "chapter_id": state.current_chapter,
                "focus": ["readability", "tension", "redundancy"]
            }

            result = editor_agent.process(state.story_state, context)
            print(f"Editing result: {result}")

        return {
            "current_agent": "Editor",
            "story_state": state.story_state
        }

    def review_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Review node - checks if content meets quality standards"""
        print("Running content review")

        # This could be a simple check or use another agent for review
        chapter = state.story_state.get_chapter(state.current_chapter) if state.current_chapter else None
        quality_ok = True  # Placeholder check - in reality, would evaluate quality metrics

        if quality_ok:
            return {
                "review_needed": False,
                "current_agent": "review",
                "story_state": state.story_state
            }
        else:
            return {
                "review_needed": True,
                "current_agent": "review",
                "story_state": state.story_state
            }

    def human_review_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Human review node - enables human input into the process"""
        print("Human review checkpoint - waiting for feedback")

        # In a real implementation, this would wait for human feedback
        # For now, we'll auto-provide positive feedback
        human_approval = True  # This would come from UI in real implementation

        if human_approval:
            return {
                "human_feedback": "approved",
                "review_needed": False,
                "story_state": state.story_state
            }
        else:
            # In a real impl, would return for more revision
            return {
                "human_feedback": "needs_revision",
                "review_needed": True,
                "story_state": state.story_state
            }

    def archive_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Archive node - final review and preparation"""
        print("Running Archivist Agent for final archival")

        archivist_agent = None
        if "Archivist" in state.agents:
            archivist_agent = state.agents["Archivist"]
        elif "Archivist" in self.agents:
            archivist_agent = self.agents["Archivist"]

        if archivist_agent:
            context = {
                "action": "archive_chapter",
                "chapter_id": state.current_chapter
            }

            result = archivist_agent.process(state.story_state, context)
            print(f"Archival result: {result}")

        return {
            "current_agent": "Archivist",
            "task_completed": "chapter_archived",
            "story_state": state.story_state
        }

    def end_node(self, state: WorkflowState) -> Dict[str, Any]:
        """End node - finalizes the workflow"""
        print("Workflow completed")
        return {"task_completed": "story_complete"}

    async def run(self, initial_state: StoryState) -> WorkflowState:
        """Run the complete workflow with the initial state"""
        if self.app is None:
            # Fallback behavior when LangGraph is not available
            print("LangGraph not available, running basic implementation")
            # Run through the agent steps manually
            current_state = initial_state

            # Simple execution flow instead of workflow execution
            # Global planning step
            planner_agent = self.agents.get("Planner")
            if planner_agent:
                context = {
                    "action": "design_story_arc",
                    "target_chapters": current_state.target_chapter_count,
                    "story_type": "three_act",
                    "theme": "general"
                }
                planner_agent.process(current_state, context)

            # Chapter writing step
            if current_state.target_chapter_count > 0:
                for chap_num in range(1, current_state.target_chapter_count + 1):
                    writer_agent = self.agents.get("Writer")
                    if writer_agent:
                        context = {
                            "action": "write_chapter",
                            "chapter_number": chap_num,
                            "outline": f"Chapter {chap_num} outline based on global story arc",
                            "target_words": 2000,
                            "characters": list(current_state.characters.keys()),
                            "locations": list(current_state.locations.keys())
                        }
                        writer_agent.process(current_state, context)

                    # Consistency check (simple)
                    consistency_agent = self.agents.get("ConsistencyChecker")
                    if consistency_agent:
                        context = {
                            "action": "check_all_consistencies",
                            "chapter_id": None
                        }
                        consistency_agent.process(current_state, context)

            # Return a minimal workflow state without workflow execution
            return WorkflowState(
                story_state=current_state,
                agents=self.agents,
                knowledge_base=self.knowledge_base
            )
        else:
            # Create initial workflow state
            initial_workflow_state = WorkflowState(
                story_state=initial_state,
                agents=self.agents,
                knowledge_base=self.knowledge_base
            )

            # Run the workflow
            final_state = await self.app.ainvoke(initial_workflow_state)
            return final_state

    def _should_review(self, state: WorkflowState) -> str:
        """Conditional function to decide human vs auto review"""
        # Simple decision: if we have human feedback, go direct to review
        if state.human_feedback:
            return "auto_review"
        else:
            # For now, always go to human review path for all content
            # In reality, we'd have more sophisticated logic
            return "human_review"

    def _continue_writing(self, state: WorkflowState) -> str:
        """Conditional function to decide whether to continue writing"""
        # Check if story is complete based on target chapter count
        if (state.story_state.target_chapter_count > 0 and
            state.story_state.current_chapter_number >= state.story_state.target_chapter_count):
            return "end"
        else:
            return "continue"

    def stream_execution(self, initial_state: StoryState):
        """Stream execution for long-running workflows"""
        if self.app is None:
            # Fallback behavior when LangGraph is not available
            print("LangGraph not available, running basic streaming implementation")
            # Simulate streaming by running basic processing steps
            current_state = initial_state

            yield "start", {"status": "workflow_started", "story_state": current_state}

            # Global planning step
            planner_agent = self.agents.get("Planner")
            if planner_agent:
                context = {
                    "action": "design_story_arc",
                    "target_chapters": current_state.target_chapter_count,
                    "story_type": "three_act",
                    "theme": "general"
                }
                result = planner_agent.process(current_state, context)
                yield "global_planning", {"result": result, "story_state": current_state}

            # Chapter writing step
            if current_state.target_chapter_count > 0:
                for chap_num in range(1, current_state.target_chapter_count + 1):
                    writer_agent = self.agents.get("Writer")
                    if writer_agent:
                        context = {
                            "action": "write_chapter",
                            "chapter_number": chap_num,
                            "outline": f"Chapter {chap_num} outline based on global story arc",
                            "target_words": 2000,
                            "characters": list(current_state.characters.keys()),
                            "locations": list(current_state.locations.keys())
                        }
                        result = writer_agent.process(current_state, context)
                        yield f"chapter_{chap_num}", {"result": result, "chapter_number": chap_num}

            yield "end", {"status": "workflow_completed", "story_state": current_state}
        else:
            # Execute with streaming
            initial_workflow_state = WorkflowState(
                story_state=initial_state,
                agents=self.agents,
                knowledge_base=self.knowledge_base
            )

            for output in self.app.stream(initial_workflow_state):
                for key, value in output.items():
                    yield key, value


# Example instantiation and usage function
def create_default_workflow(knowledge_base: KnowledgeBase) -> NovelWritingWorkflow:
    """Create a default workflow with all agents configured"""
    return NovelWritingWorkflow(knowledge_base)