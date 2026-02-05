import asyncio
import json
import re
from typing import Dict, Any, List
from ..novel_types import AgentResponse
from ..agents.writer import WriterAgent
from ..agents.planner import PlannerAgent
from ..agents.archivist import ArchivistAgent
from ..agents.editor import EditorAgent
from ..agents.consistency_checker import ConsistencyCheckerAgent
from ..agents.dialogue_specialist import DialogueSpecialistAgent
from ..agents.world_builder import WorldBuilderAgent
from ..agents.pacing_advisor import PacingAdvisorAgent
from ..agents.humanizer import HumanizerAgent
from ..knowledge.store import KnowledgeStore
from ..config import Config
from .state import GraphState
from .phase_manager import HierarchicalPhaseManager
from .config import WorkflowConfig
import logging

logger = logging.getLogger(__name__)


class NodeManager:
    """Manages all nodes in the LangGraph workflow with hierarchical phase support."""

    def __init__(self, config: Config, knowledge_store: KnowledgeStore):
        self.config = config
        self.knowledge_store = knowledge_store
        self.phase_manager = HierarchicalPhaseManager()
        self.workflow_config = WorkflowConfig()  # Add workflow configuration

        # Initialize agents
        self.writer_agent = WriterAgent(config)
        self.planner_agent = PlannerAgent(config)
        self.archivist_agent = ArchivistAgent(config)
        self.editor_agent = EditorAgent(config)
        self.consistency_checker_agent = ConsistencyCheckerAgent(config)
        self.dialogue_specialist_agent = DialogueSpecialistAgent(config)
        self.world_builder_agent = WorldBuilderAgent(config)
        self.pacing_advisor_agent = PacingAdvisorAgent(config)
        self.humanizer_agent = HumanizerAgent(config)

    async def planner_node(self, state: GraphState) -> Dict[str, Any]:
        """Node that plans the story structure and chapter outlines."""
        # Update phase progress
        updated_state = self.phase_manager.update_phase_progress(state)
        logger.info(f"Executing Planner node in {updated_state.current_hierarchical_phase} phase at iteration {updated_state.iteration_count}")

        try:
            # Check if this agent should run in the current hierarchical phase
            if not self.phase_manager.should_execute_agent_in_phase("planner", updated_state.current_hierarchical_phase):
                logger.info(f"Skipping planner node: not appropriate for {updated_state.current_hierarchical_phase} phase")
                return updated_state

            # Convert GraphState to dict for agent processing
            state_dict = updated_state.get_agent_context()

            # Process with planner agent
            response: AgentResponse = await self.planner_agent.process(state_dict)

            # Update state with planner output
            new_outline = {}
            try:
                new_outline = json.loads(response.content)
            except json.JSONDecodeError:
                logger.warning(f"Could not decode planner response as JSON: {response.content[:self.workflow_config.agent_response_snippet_limit]}...")
                # Try to extract JSON from markdown if present
                json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', response.content, re.DOTALL)
                if json_match:
                    try:
                        new_outline = json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        logger.warning("Could not decode markdown JSON either.")
                        # If no JSON found, create a simple dict from content
                        new_outline = {"basic_outline": response.content[:self.workflow_config.agent_response_snippet_limit]}
                else:
                    # If no JSON found, create a simple dict from content
                    new_outline = {"basic_outline": response.content[:self.workflow_config.agent_response_snippet_limit]}

            new_state = updated_state.copy()
            new_state.outline.update(new_outline)
            new_state.current_phase = "writing"
            new_state.next_agent = "writer"
            new_state.add_agent_response(response)

            # Update phase-specific data
            if new_state.current_hierarchical_phase == "macro":
                new_state.macro_phase_data.update(new_outline)
            elif new_state.current_hierarchical_phase == "mid":
                new_state.mid_phase_data.update(new_outline)

            # Store planner results in knowledge base
            await self.knowledge_store.store_memory(
                f"planning_session_{updated_state.iteration_count}",
                new_outline,
                {"agent": "planner", "iteration": updated_state.iteration_count, "phase": updated_state.current_hierarchical_phase}
            )

            return new_state

        except Exception as e:
            logger.error(f"Error in planner_node: {str(e)}")
            new_state = updated_state.copy()
            new_state.error_count += 1
            new_state.last_error = f"Planner node error: {str(e)}"
            return new_state

    async def writer_node(self, state: GraphState) -> Dict[str, Any]:
        """Node that writes the chapter content based on the plan."""
        # Update phase progress
        updated_state = self.phase_manager.update_phase_progress(state)
        logger.info(f"Executing Writer node in {updated_state.current_hierarchical_phase} phase at iteration {updated_state.iteration_count}")

        try:
            # Check if this agent should run in the current hierarchical phase
            if not self.phase_manager.should_execute_agent_in_phase("writer", updated_state.current_hierarchical_phase):
                logger.info(f"Skipping writer node: not appropriate for {updated_state.current_hierarchical_phase} phase")
                return updated_state

            # Convert GraphState to dict for agent processing
            state_dict = updated_state.get_agent_context()

            # Process with writer agent
            response: AgentResponse = await self.writer_agent.process(state_dict)

            # Update state with writer output
            new_state = updated_state.copy()
            new_state.current_chapter = response.content
            new_state.current_phase = "editing"
            new_state.next_agent = "editor"
            new_state.add_agent_response(response)

            # Store chapter content in knowledge base
            await self.knowledge_store.store_chapter_content(
                {
                    "chapter_number": len(new_state.chapters) + 1,
                    "title": f"Chapter {len(new_state.chapters) + 1}",
                    "content": response.content,
                    "characters_mentioned": list(new_state.characters.keys()) if new_state.characters else [],
                    "locations_mentioned": list(new_state.world_details.get('locations', [])) if new_state.world_details else [],
                    "key_plot_points": new_state.outline.get('current_chapter_outline', {}).get('content_goals', [])
                }
            )

            return new_state

        except Exception as e:
            logger.error(f"Error in writer_node: {str(e)}")
            new_state = updated_state.copy()
            new_state.error_count += 1
            new_state.last_error = f"Writer node error: {str(e)}"
            return new_state

    async def archivist_node(self, state: GraphState) -> Dict[str, Any]:
        """Node that maintains story continuity, character tracking, and archive."""
        # Update phase progress
        updated_state = self.phase_manager.update_phase_progress(state)
        logger.info(f"Executing Archivist node in {updated_state.current_hierarchical_phase} phase at iteration {updated_state.iteration_count}")

        try:
            # Check if this agent should run in the current hierarchical phase
            if not self.phase_manager.should_execute_agent_in_phase("archivist", updated_state.current_hierarchical_phase):
                logger.info(f"Skipping archivist node: not appropriate for {updated_state.current_hierarchical_phase} phase")
                return updated_state

            # Convert GraphState to dict for agent processing
            state_dict = updated_state.get_agent_context()

            # Process with archivist agent
            response: AgentResponse = await self.archivist_agent.process(state_dict)

            # Update state with archivist output
            new_state = updated_state.copy()
            # Assuming response contains JSON with archivist data
            archived_data = {}
            try:
                archived_data = json.loads(response.content)
            except json.JSONDecodeError:
                logger.warning(f"Could not decode archivist response as JSON: {response.content[:200]}...")
                # Try to extract JSON from markdown if present
                json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', response.content, re.DOTALL)
                if json_match:
                    try:
                        archived_data = json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        logger.warning("Could not decode markdown JSON either.")
                        # If no JSON found, create a simple dict from content
                        archived_data = {"basic_archive": response.content[:500]}
                else:
                    # If no JSON found, create a simple dict from content
                    archived_data = {"basic_archive": response.content[:500]}

            new_state.retrieved_knowledge.append(archived_data)
            new_state.add_agent_response(response)

            # Update phase-specific data
            if new_state.current_hierarchical_phase in ["macro", "mid"]:
                new_state.macro_phase_data["continuity"] = archived_data
            else:  # micro
                new_state.micro_phase_data["continuity"] = archived_data

            # Store archivist data in knowledge base
            await self.knowledge_store.store_memory(
                f"archivist_session_{updated_state.iteration_count}",
                archived_data,
                {"agent": "archivist", "iteration": updated_state.iteration_count, "phase": updated_state.current_hierarchical_phase}
            )

            # Determine next agent
            new_state.next_agent = "consistency_checker"

            return new_state

        except Exception as e:
            logger.error(f"Error in archivist_node: {str(e)}")
            new_state = updated_state.copy()
            new_state.error_count += 1
            new_state.last_error = f"Archivist node error: {str(e)}"
            return new_state

    async def editor_node(self, state: GraphState) -> Dict[str, Any]:
        """Node that reviews and improves content quality."""
        # Update phase progress
        updated_state = self.phase_manager.update_phase_progress(state)
        logging.info(f"Executing Editor node in {updated_state.current_hierarchical_phase} phase at iteration {updated_state.iteration_count}")

        try:
            # Check if this agent should run in the current hierarchical phase
            if not self.phase_manager.should_execute_agent_in_phase("editor", updated_state.current_hierarchical_phase):
                logging.debug(f"Skipping editor node: not appropriate for {updated_state.current_hierarchical_phase} phase")
                return updated_state

            # Convert GraphState to dict for agent processing
            state_dict = updated_state.get_agent_context()

            # Process with editor agent
            response: AgentResponse = await self.editor_agent.process(state_dict)

            # Update state with editor output
            new_state = updated_state.copy()
            content_to_merge = response.content if response.content else state_dict['current_chapter']
            new_state.current_chapter = f"[Editor Review]\n{content_to_merge}\n\n[Original Content]\n{state.current_chapter}"
            new_state.current_phase = "consistency_check"
            new_state.next_agent = "consistency_checker"
            new_state.add_agent_response(response)

            # Store editor review in knowledge base
            await self.knowledge_store.store_memory(
                f"editor_review_{updated_state.iteration_count}",
                response,
                {"agent": "editor", "iteration": updated_state.iteration_count, "phase": updated_state.current_hierarchical_phase}
            )

            return new_state

        except Exception as e:
            logging.error(f"Error in editor_node: {str(e)}")
            new_state = updated_state.copy()
            new_state.error_count += 1
            new_state.last_error = f"Editor node error: {str(e)}"
            return new_state

    async def consistency_checker_node(self, state: GraphState) -> Dict[str, Any]:
        """Node that verifies consistency across the entire story."""
        # Update phase progress
        updated_state = self.phase_manager.update_phase_progress(state)
        logging.info(f"Executing Consistency Checker node in {updated_state.current_hierarchical_phase} phase at iteration {updated_state.iteration_count}")

        try:
            # Check if this agent should run in the current hierarchical phase
            if not self.phase_manager.should_execute_agent_in_phase("consistency_checker", updated_state.current_hierarchical_phase):
                logging.debug(f"Skipping consistency_checker node: not appropriate for {updated_state.current_hierarchical_phase} phase")
                return updated_state

            # Convert GraphState to dict for agent processing
            state_dict = updated_state.get_agent_context()

            # Process with consistency checker agent
            response: AgentResponse = await self.consistency_checker_agent.process(state_dict)

            # Update state with consistency check output
            new_state = updated_state.copy()
            # Update story notes with consistency issues
            new_state.story_notes.extend(response.suggestions or [])
            new_state.next_agent = "dialogue_specialist"
            new_state.add_agent_response(response)

            # Store consistency report in knowledge base
            await self.knowledge_store.store_memory(
                f"consistency_report_{updated_state.iteration_count}",
                response,
                {"agent": "consistency_checker", "iteration": updated_state.iteration_count, "phase": updated_state.current_hierarchical_phase}
            )

            return new_state

        except Exception as e:
            logging.error(f"Error in consistency_checker_node: {str(e)}")
            new_state = updated_state.copy()
            new_state.error_count += 1
            new_state.last_error = f"Consistency checker node error: {str(e)}"
            return new_state

    async def dialogue_specialist_node(self, state: GraphState) -> Dict[str, Any]:
        """Node that analyzes and improves character dialogue."""
        # Update phase progress
        updated_state = self.phase_manager.update_phase_progress(state)
        logging.info(f"Executing Dialogue Specialist node in {updated_state.current_hierarchical_phase} phase at iteration {updated_state.iteration_count}")

        try:
            # Check if this agent should run in the current hierarchical phase
            if not self.phase_manager.should_execute_agent_in_phase("dialogue_specialist", updated_state.current_hierarchical_phase):
                logging.debug(f"Skipping dialogue_specialist node: not appropriate for {updated_state.current_hierarchical_phase} phase")
                return updated_state

            # Convert GraphState to dict for agent processing
            state_dict = updated_state.get_agent_context()

            # Process with dialogue specialist agent
            response: AgentResponse = await self.dialogue_specialist_agent.process(state_dict)

            # Update state with dialogue specialist output
            new_state = updated_state.copy()
            # Apply dialogue recommendations to current chapter (in a real system)
            new_state.next_agent = "world_builder"
            new_state.add_agent_response(response)

            # Store dialogue analysis in knowledge base
            await self.knowledge_store.store_memory(
                f"dialogue_analysis_{updated_state.iteration_count}",
                response,
                {"agent": "dialogue_specialist", "iteration": updated_state.iteration_count, "phase": updated_state.current_hierarchical_phase}
            )

            return new_state

        except Exception as e:
            logging.error(f"Error in dialogue_specialist_node: {str(e)}")
            new_state = updated_state.copy()
            new_state.error_count += 1
            new_state.last_error = f"Dialogue specialist node error: {str(e)}"
            return new_state

    async def world_builder_node(self, state: GraphState) -> Dict[str, Any]:
        """Node that develops and maintains the fictional world."""
        # Update phase progress
        updated_state = self.phase_manager.update_phase_progress(state)
        logger.info(f"Executing World Builder node in {updated_state.current_hierarchical_phase} phase at iteration {updated_state.iteration_count}")

        try:
            # Check if this agent should run in the current hierarchical phase
            if not self.phase_manager.should_execute_agent_in_phase("world_builder", updated_state.current_hierarchical_phase):
                logger.info(f"Skipping world_builder node: not appropriate for {updated_state.current_hierarchical_phase} phase")
                return updated_state

            # Convert GraphState to dict for agent processing
            state_dict = updated_state.get_agent_context()

            # Process with world builder agent
            response: AgentResponse = await self.world_builder_agent.process(state_dict)

            # Update state with world builder output
            world_data = {}
            try:
                world_data = json.loads(response.content)
            except json.JSONDecodeError:
                logger.warning(f"Could not decode world_builder response as JSON: {response.content[:200]}...")
                # Try to extract JSON from markdown if present
                json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', response.content, re.DOTALL)
                if json_match:
                    try:
                        world_data = json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        logger.warning("Could not decode markdown JSON either.")
                        # If no JSON found, create a simple dict from content
                        world_data = {"world_details": response.content[:500]}
                else:
                    # If no JSON found, create a simple dict from content
                    world_data = {"world_details": response.content[:500]}

            new_state = updated_state.copy()
            new_state.world_details.update(world_data)

            # Update phase data
            if new_state.current_hierarchical_phase == "macro":
                new_state.macro_phase_data["world"] = world_data
            elif new_state.current_hierarchical_phase == "mid":
                new_state.mid_phase_data["world"] = world_data

            # Check if this is a writing cycle and we should finalize the chapter
            if len(new_state.chapters) + 1 <= len(new_state.completed_chapters) + 1:
                # Add the newly completed chapter to the list
                chapter_num = len(new_state.chapters) + 1
                chapter_title = updated_state.outline.get('current_chapter_outline', {}).get('title', f'Chapter {chapter_num}')
                new_state.add_chapter(new_state.current_chapter, chapter_num, chapter_title)

            new_state.current_chapter = ""  # Clear for next chapter
            new_state.next_agent = "pacing_advisor"
            new_state.add_agent_response(response)

            # Store world building in knowledge base
            await self.knowledge_store.store_memory(
                f"world_building_{updated_state.iteration_count}",
                world_data,
                {"agent": "world_builder", "iteration": updated_state.iteration_count, "phase": updated_state.current_hierarchical_phase}
            )

            return new_state

        except Exception as e:
            logger.error(f"Error in world_builder_node: {str(e)}")
            new_state = updated_state.copy()
            new_state.error_count += 1
            new_state.last_error = f"World builder node error: {str(e)}"
            return new_state

    async def pacing_advisor_node(self, state: GraphState) -> Dict[str, Any]:
        """Node that analyzes story rhythm and pace."""
        # Update phase progress
        updated_state = self.phase_manager.update_phase_progress(state)
        logging.info(f"Executing Pacing Advisor node in {updated_state.current_hierarchical_phase} phase at iteration {updated_state.iteration_count}")

        try:
            # Check if this agent should run in the current hierarchical phase
            if not self.phase_manager.should_execute_agent_in_phase("pacing_advisor", updated_state.current_hierarchical_phase):
                logging.debug(f"Skipping pacing_advisor node: not appropriate for {updated_state.current_hierarchical_phase} phase")
                return updated_state

            # Convert GraphState to dict for agent processing
            state_dict = updated_state.get_agent_context()

            # Process with pacing advisor agent
            response: AgentResponse = await self.pacing_advisor_agent.process(state_dict)

            # Update state with pacing analysis
            new_state = updated_state.copy()
            new_state.story_notes.extend(response.suggestions or [])
            new_state.next_agent = "humanizer"
            new_state.add_agent_response(response)

            # Update phase data
            if new_state.current_hierarchical_phase == "macro":
                new_state.macro_phase_data["pacing"] = response.content[:500]  # Only store excerpt
            elif new_state.current_hierarchical_phase == "mid":
                new_state.mid_phase_data["pacing"] = response.content[:500]

            # Determine if we should go to human review phase
            if new_state.current_chapter_index > 0:  # We have completed a chapter
                new_state.needs_human_review = True
                new_state.human_review_status = "pending" if not new_state.needs_human_review else new_state.human_review_status

            # Store pacing analysis in knowledge base
            await self.knowledge_store.store_memory(
                f"pacing_analysis_{updated_state.iteration_count}",
                response,
                {"agent": "pacing_advisor", "iteration": updated_state.iteration_count, "phase": updated_state.current_hierarchical_phase}
            )

            return new_state

        except Exception as e:
            logging.error(f"Error in pacing_advisor_node: {str(e)}")
            new_state = updated_state.copy()
            new_state.error_count += 1
            new_state.last_error = f"Pacing advisor node error: {str(e)}"
            return new_state

    async def humanizer_node(self, state: GraphState) -> Dict[str, Any]:
        """Node that removes AI writing traces to make content more human-like."""
        # Update phase progress
        updated_state = self.phase_manager.update_phase_progress(state)
        logger.info(f"Executing Humanizer node in {updated_state.current_hierarchical_phase} phase at iteration {updated_state.iteration_count}")

        try:
            # Check if this agent should run in the current hierarchical phase
            if not self.phase_manager.should_execute_agent_in_phase("humanizer", updated_state.current_hierarchical_phase):
                logger.info(f"Skipping humanizer node: not appropriate for {updated_state.current_hierarchical_phase} phase")
                return updated_state

            # Convert GraphState to dict for agent processing
            state_dict = updated_state.get_agent_context()

            # Process with humanizer agent
            response: AgentResponse = await self.humanizer_agent.process(state_dict)

            # Update state with humanizer output
            new_state = updated_state.copy()
            # Apply humanizer results to the current chapter if there is one
            if new_state.current_chapter and state_dict['current_chapter']:
                new_state.current_chapter = response.content or state_dict['current_chapter']
            new_state.next_agent = "review_or_continue"
            new_state.add_agent_response(response)

            # Store humanization results in knowledge base
            await self.knowledge_store.store_memory(
                f"humanization_{updated_state.iteration_count}",
                response,
                {"agent": "humanizer", "iteration": updated_state.iteration_count, "phase": updated_state.current_hierarchical_phase}
            )

            # If we have completed a chapter, consider whether to start human review
            chapter_complete = len(new_state.chapters) > len(state.chapters)
            if chapter_complete:
                new_state.next_agent = "archivist"  # Run archivist for the complete chapter
                # For now, set up for potential human review after archivist runs
            else:
                new_state.next_agent = "planner"  # Plan the next chapter

            return new_state

        except Exception as e:
            logger.error(f"Error in humanizer_node: {str(e)}")
            new_state = updated_state.copy()
            new_state.error_count += 1
            new_state.last_error = f"Humanizer node error: {str(e)}"
            return new_state

    async def human_review_node(self, state: GraphState) -> Dict[str, Any]:
        """Node that handles human feedback integration."""
        logger.info(f"Executing Human Review node at iteration {state.iteration_count}")
        try:
            updated_state = self.phase_manager.update_phase_progress(state)
            new_state = updated_state.copy()
            new_state.needs_human_review = False
            new_state.human_review_status = "completed"

            # In a real system, this would interface with the UI system
            # For now, we'll assume approval to continue the cycle
            # Update based on hierarchical phase
            if new_state.current_hierarchical_phase == "micro":
                new_state.next_agent = "planner"  # Back to planning for the next part
            elif new_state.current_hierarchical_phase == "mid":
                new_state.next_agent = "writer"  # Ready to write
            else:  # macro
                new_state.next_agent = "planner"  # Continue with overall planning

            return new_state
        except Exception as e:
            logger.error(f"Error in human_review_node: {str(e)}")
            new_state = state.copy()
            new_state.error_count += 1
            new_state.last_error = f"Human review node error: {str(e)}"
            return new_state