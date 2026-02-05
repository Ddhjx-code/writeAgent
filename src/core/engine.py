from typing import Dict, Any, Optional, List
import asyncio
import json
import os
import logging
from datetime import datetime

from ..config import Config
from ..workflow.graph import NovelWritingGraph
from ..workflow.state import GraphState
from ..knowledge.store import KnowledgeStore
from ..communication.protocol import CommunicationManager, CommunicationProtocol
from ..novel_types import StoryState
from ..agents.writer import WriterAgent
from ..agents.planner import PlannerAgent
from ..agents.archivist import ArchivistAgent
from ..agents.editor import EditorAgent
from ..agents.consistency_checker import ConsistencyCheckerAgent
from ..agents.dialogue_specialist import DialogueSpecialistAgent
from ..agents.world_builder import WorldBuilderAgent
from ..agents.pacing_advisor import PacingAdvisorAgent
from ..agents.humanizer import HumanizerAgent
# 已移除旧的Gradio界面依赖
# 新架构：API接口由src/api/server.py处理
from typing import Optional, Dict, Any


class WritingEngine:
    """Main engine that orchestrates the entire AI collaborative novel writing system."""

    def __init__(self, config: Config):
        self.config = config
        self.knowledge_store = KnowledgeStore(config)
        self.workflow = NovelWritingGraph(config)
        self.communication_manager = CommunicationManager(CommunicationProtocol.HYBRID, config)
        # 旧的Gradio界面已被移除 - 使用API接口
        # 保留接口对象以维持代码兼容性
        self.interface = None

        # Agents will be initialized after system starts
        self.planner_agent = None
        self.writer_agent = None
        self.archivist_agent = None
        self.editor_agent = None
        self.consistency_checker_agent = None
        self.dialogue_specialist_agent = None
        self.world_builder_agent = None
        self.pacing_advisor_agent = None
        self.humanizer_agent = None

        # System state
        self.system_state = "initialized"
        self.current_story = None
        self.is_running = False

    async def initialize(self):
        """Initialize all system components."""
        logging.info("Initializing writing engine components...")

        # Initialize knowledge base
        await self.knowledge_store.initialize()

        # Initialize agents
        self.planner_agent = PlannerAgent(self.config)
        self.writer_agent = WriterAgent(self.config)
        self.archivist_agent = ArchivistAgent(self.config)
        self.editor_agent = EditorAgent(self.config)
        self.consistency_checker_agent = ConsistencyCheckerAgent(self.config)
        self.dialogue_specialist_agent = DialogueSpecialistAgent(self.config)
        self.world_builder_agent = WorldBuilderAgent(self.config)
        self.pacing_advisor_agent = PacingAdvisorAgent(self.config)
        self.humanizer_agent = HumanizerAgent(self.config)

        # Register agents with communication manager
        for name, agent in [
            ("planner", self.planner_agent),
            ("writer", self.writer_agent),
            ("archivist", self.archivist_agent),
            ("editor", self.editor_agent),
            ("consistency", self.consistency_checker_agent),
            ("dialogue", self.dialogue_specialist_agent),
            ("world", self.world_builder_agent),
            ("pacing", self.pacing_advisor_agent),
            ("humanizer", self.humanizer_agent),
        ]:
            self.communication_manager.register_agent(name, agent)

        # Initialize workflow
        await self.workflow.initialize()

        # Interface initialization now handled by API layer
        # await self.interface.initialize()
        pass

        self.system_state = "ready"
        logging.info("Writing engine initialized successfully.")

    async def create_new_story(self, story_data: Dict[str, Any]) -> GraphState:
        """Create a new story from initial data."""
        if self.system_state != "ready":
            raise RuntimeError("Engine not ready. Call initialize() first.")

        # Validate story data
        required_fields = ["title"]
        for field in required_fields:
            if field not in story_data:
                raise ValueError(f"Missing required field: {field}")

        # Create initial state
        initial_state = GraphState(
            title=story_data["title"],
            outline=story_data.get("outline", {}),
            characters=story_data.get("characters", {}),
            world_details=story_data.get("world_details", {}),
            story_status="in_progress",
            story_notes=story_data.get("notes", [])
        )

        # Store initial story information in knowledge base
        await self.knowledge_store.store_memory(
            f"story_{story_data['title'].replace(' ', '_')}",
            story_data,
            {"type": "story_init", "timestamp": datetime.now().isoformat()}
        )

        self.current_story = initial_state
        return initial_state

    async def run_story_generation(self,
                                 initial_state: GraphState,
                                 max_iterations: int = None,
                                 target_chapters: int = 5) -> GraphState:
        """Run the story generation workflow with specified constraints."""
        if self.system_state != "ready":
            raise RuntimeError("Engine not ready. Call initialize() first.")

        # Use configuration value if max_iterations is None
        if max_iterations is None:
            max_iterations = self.config.workflow_config.default_max_iterations

        if not initial_state.should_continue() or max_iterations <= 0:
            return initial_state

        self.is_running = True
        current_state = initial_state

        logging.info(f"Starting story generation for '{current_state.title}'...")
        logging.info(f"Target: {target_chapters} chapters in {max_iterations} iterations")

        try:
            for iteration in range(max_iterations):
                # 更新迭代计数前检查结束条件
                current_state = current_state.copy(update={"iteration_count": iteration})

                if not current_state.should_continue() or len(current_state.completed_chapters) >= target_chapters:
                    logging.info(f"Story generation completed after {iteration+1} iterations")
                    break

                # Enhanced cycle detection: Check the state's execution sequence for potential infinite loops
                cycle_detected = current_state.detect_cycle(self.config.workflow_config.loop_detection_threshold)
                if cycle_detected:
                    logging.warning(f"Possibly infinite loop detected: {cycle_detected}")
                    # Force an end to the generation to break cycle
                    current_state.story_status = "complete"
                    break

                logging.info(f"Iteration {iteration+1}: Current phase - {current_state.current_phase}")

                # Use the new run_with_phase_management when running the workflow
                # This gives us more control over the execution and phase transitions
                current_state = await self.workflow.run_with_phase_management(current_state, debug=False)

                # Check if the story is complete
                if len(current_state.completed_chapters) >= target_chapters:
                    current_state.story_status = "complete"
                    break

            logging.info(f"Story generation finished after {current_state.iteration_count} iterations")
            return current_state

        except Exception as e:
            logging.error(f"Error during story generation: {str(e)}")
            current_state.error_count += 1
            current_state.last_error = str(e)
            return current_state
        finally:
            self.is_running = False

    async def add_human_feedback(self, feedback: str, target_chapter: int=None) -> GraphState:
        """Add human feedback to the story generation process."""
        if not self.current_story:
            raise RuntimeError("No active story. Create a story first.")

        # Store feedback in current story state
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "feedback": feedback,
            "target_chapter": target_chapter or len(self.current_story.chapters),
            "type": "human_input"
        }

        self.current_story.human_feedback.append(feedback_entry)
        self.current_story.needs_human_review = False  # Mark as addressed once processed

        # Store in knowledge base
        await self.knowledge_store.store_memory(
            f"feedback_{datetime.now().timestamp()}",
            feedback_entry,
            {"type": "feedback", "target_chapter": target_chapter}
        )

        return self.current_story

    async def get_story_metrics(self, story_state: GraphState) -> Dict[str, Any]:
        """Calculate and return metrics for the current story."""
        if not story_state:
            return {}

        from ..interface.utils import calculate_story_metrics
        return calculate_story_metrics(story_state)

    async def export_story(self, story_state: GraphState, format_type: str = "json") -> str:
        """Export the current story in the specified format."""
        from ..interface.utils import export_story_to_format
        return export_story_to_format(story_state, format_type)

    async def save_story_state(self, story_state: GraphState, save_path: str = None) -> bool:
        """Save the current story state to a file or persist it."""
        try:
            if save_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = f"story_save_{timestamp}.json"

            # Serialize the state
            state_dict = {
                "title": story_state.title,
                "current_chapter": story_state.current_chapter,
                "chapters": story_state.chapters,
                "outline": story_state.outline,
                "characters": story_state.characters,
                "world_details": story_state.world_details,
                "story_status": story_state.story_status,
                "story_notes": story_state.story_notes,
                "agent_responses": [resp.dict() for resp in story_state.agent_responses],
                "iteration_count": story_state.iteration_count,
                "current_phase": story_state.current_phase,
                "completed_chapters": story_state.completed_chapters,
                "timestamp": datetime.now().isoformat()
            }

            # Write to file
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(state_dict, f, ensure_ascii=False, indent=2)

            logging.info(f"Story state saved to {save_path}")
            return True

        except Exception as e:
            logging.error(f"Error saving story state: {str(e)}")
            return False

    async def load_story_state(self, load_path: str) -> Optional[GraphState]:
        """Load a story state from file."""
        try:
            with open(load_path, 'r', encoding='utf-8') as f:
                state_dict = json.load(f)

            # Create GraphState with loaded data
            # Note: AgentResponse needs to be reconstructed from dict
            from ..novel_types import AgentResponse
            agent_responses = [
                AgentResponse(**resp) for resp in state_dict.get("agent_responses", [])
            ]

            loaded_state = GraphState(
                title=state_dict.get("title", ""),
                current_chapter=state_dict.get("current_chapter", ""),
                chapters=state_dict.get("chapters", []),
                outline=state_dict.get("outline", {}),
                characters=state_dict.get("characters", {}),
                world_details=state_dict.get("world_details", {}),
                story_status=state_dict.get("story_status", "draft"),
                story_notes=state_dict.get("story_notes", []),
                agent_responses=agent_responses,
                iteration_count=state_dict.get("iteration_count", 0),
                current_phase=state_dict.get("current_phase", "planning"),
                completed_chapters=state_dict.get("completed_chapters", []),
                error_count=state_dict.get("error_count", 0),
                last_error=state_dict.get("last_error", None),
                human_feedback=state_dict.get("human_feedback", []),
                needs_human_review=state_dict.get("needs_human_review", False),
                human_review_status=state_dict.get("human_review_status", "not_needed")
            )

            logging.info(f"Story state loaded from {load_path}")
            return loaded_state

        except Exception as e:
            logging.error(f"Error loading story state: {str(e)}")
            return None

    async def start_interface_server(self, share: bool = False):
        """Start the interface server (now handled by API layer)."""
        if self.system_state != "ready":
            raise RuntimeError("Engine not ready. Call initialize() first.")

        logging.info("Interface server now handled by API layer. See: src/api/server.py")
        # await self.interface.run_app(share=share)  # This is handled by the API layer
        pass

    async def get_system_status(self) -> Dict[str, Any]:
        """Get the current status of the system."""
        knowledge_status = None
        if self.knowledge_store:
            knowledge_status = await self.knowledge_store.get_backend_status()

        return {
            "engine_state": self.system_state,
            "is_running": self.is_running,
            "current_story": self.current_story.title if self.current_story else None,
            "knowledge_store_status": knowledge_status,
            "timestamp": datetime.now().isoformat()
        }

    async def get_agent_status(self) -> List[Dict[str, Any]]:
        """Get the status of all AI agents."""
        agent_statuses = []

        # In the current architecture, agents are stored in the NodeManager of the workflow
        # Check the actual status from the workflow
        agents_info = [
            ("planner", "Planner Agent", "设计故事主线、章节梗概、转折点"),
            ("writer", "Writer Agent", "主笔生成章节正文内容"),
            ("archivist", "Archivist Agent", "管理人物卡、世界观设定、版本控制"),
            ("editor", "Editor Agent", "优化可读性、情感张力、避免冗余"),
            ("consistency_checker", "Consistency Checker Agent", "校验时间线、人物行为、因果链"),
            ("dialogue_specialist", "Dialogue Specialist Agent", "优化角色对话风格、口吻、潜台词"),
            ("world_builder", "World Builder Agent", "丰富场景细节、感官描写"),
            ("pacing_advisor", "Pacing Advisor Agent", "控制快慢节奏、悬念密度、段落分布"),
            ("humanizer", "Humanizer Agent", "去除AI生成文本痕迹，使文字更自然"),
            ("human_review", "Human Review Node", "处理人类反馈和评审")
        ]

        # Check if these agents are initialized in the workflow
        for agent_id, display_name, role in agents_info:
            # Try to check if the agents are available in workflow
            if self.workflow and hasattr(self.workflow.node_manager, f"{agent_id}_agent"):
                agent_is_initialized = True
            elif agent_id == "planner" and self.planner_agent:
                agent_is_initialized = True
            elif agent_id == "writer" and self.writer_agent:
                agent_is_initialized = True
            elif agent_id == "archivist" and self.archivist_agent:
                agent_is_initialized = True
            elif agent_id == "editor" and self.editor_agent:
                agent_is_initialized = True
            elif agent_id == "consistency_checker" and self.consistency_checker_agent:
                agent_is_initialized = True
            elif agent_id == "dialogue_specialist" and self.dialogue_specialist_agent:
                agent_is_initialized = True
            elif agent_id == "world_builder" and self.world_builder_agent:
                agent_is_initialized = True
            elif agent_id == "pacing_advisor" and self.pacing_advisor_agent:
                agent_is_initialized = True
            elif agent_id == "humanizer" and self.humanizer_agent:
                agent_is_initialized = True
            else:
                agent_is_initialized = False

            # Check if the agent is currently active in a workflow run
            is_active = self.is_running and agent_is_initialized  # Only active if the engine is running

            agent_statuses.append({
                "id": agent_id,
                "name": display_name,
                "role": role,
                "status": "initialized" if agent_is_initialized else "uninitialized",
                "active": is_active,  # Only active if the engine is running
                "tasks": []  # Incomplete implementation would track current tasks
            })

        return agent_statuses