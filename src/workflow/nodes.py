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
import asyncio


class NodeManager:
    """Manages all nodes in the LangGraph workflow."""

    def __init__(self, config: Config, knowledge_store: KnowledgeStore):
        self.config = config
        self.knowledge_store = knowledge_store

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
        print(f"Executing Planner node at iteration {state.iteration_count}")
        try:
            # Convert GraphState to dict for agent processing
            state_dict = state.get_agent_context()

            # Process with planner agent
            response: AgentResponse = await self.planner_agent.process(state_dict)

            # Update state with planner output
            import json
            new_outline = json.loads(response.content)

            new_state = state.copy()
            new_state.outline.update(new_outline)
            new_state.current_phase = "writing"
            new_state.next_agent = "writer"
            new_state.add_agent_response(response)

            # Store planner results in knowledge base
            await self.knowledge_store.store_memory(
                f"planning_session_{state.iteration_count}",
                new_outline,
                {"agent": "planner", "iteration": state.iteration_count}
            )

            return new_state

        except Exception as e:
            print(f"Error in planner_node: {str(e)}")
            new_state = state.copy()
            new_state.error_count += 1
            new_state.last_error = f"Planner node error: {str(e)}"
            return new_state

    async def writer_node(self, state: GraphState) -> Dict[str, Any]:
        """Node that writes the chapter content based on the plan."""
        print(f"Executing Writer node at iteration {state.iteration_count}")
        try:
            # Convert GraphState to dict for agent processing
            state_dict = state.get_agent_context()

            # Process with writer agent
            response: AgentResponse = await self.writer_agent.process(state_dict)

            # Update state with writer output
            new_state = state.copy()
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
            print(f"Error in writer_node: {str(e)}")
            new_state = state.copy()
            new_state.error_count += 1
            new_state.last_error = f"Writer node error: {str(e)}"
            return new_state

    async def archivist_node(self, state: GraphState) -> Dict[str, Any]:
        """Node that maintains story continuity, character tracking, and archive."""
        print(f"Executing Archivist node at iteration {state.iteration_count}")
        try:
            # Convert GraphState to dict for agent processing
            state_dict = state.get_agent_context()

            # Process with archivist agent
            response: AgentResponse = await self.archivist_agent.process(state_dict)

            # Update state with archivist output
            new_state = state.copy()
            # Assuming response contains JSON with archivist data
            import json
            archived_data = json.loads(response.content)
            new_state.retrieved_knowledge.append(archived_data)
            new_state.add_agent_response(response)

            # Store archivist data in knowledge base
            await self.knowledge_store.store_memory(
                f"archivist_session_{state.iteration_count}",
                archived_data,
                {"agent": "archivist", "iteration": state.iteration_count}
            )

            # Determine next agent
            new_state.next_agent = "consistency_checker"

            return new_state

        except Exception as e:
            print(f"Error in archivist_node: {str(e)}")
            new_state = state.copy()
            new_state.error_count += 1
            new_state.last_error = f"Archivist node error: {str(e)}"
            return new_state

    async def editor_node(self, state: GraphState) -> Dict[str, Any]:
        """Node that reviews and improves content quality."""
        print(f"Executing Editor node at iteration {state.iteration_count}")
        try:
            # Convert GraphState to dict for agent processing
            state_dict = state.get_agent_context()

            # Process with editor agent
            response: AgentResponse = await self.editor_agent.process(state_dict)

            # Update state with editor output
            new_state = state.copy()
            new_state.current_chapter = f"[Editor Review]{response.content}\n\n{state.current_chapter}"
            new_state.current_phase = "consistency_check"
            new_state.next_agent = "consistency_checker"
            new_state.add_agent_response(response)

            # Store editor review in knowledge base
            await self.knowledge_store.store_memory(
                f"editor_review_{state.iteration_count}",
                response,
                {"agent": "editor", "iteration": state.iteration_count}
            )

            return new_state

        except Exception as e:
            print(f"Error in editor_node: {str(e)}")
            new_state = state.copy()
            new_state.error_count += 1
            new_state.last_error = f"Editor node error: {str(e)}"
            return new_state

    async def consistency_checker_node(self, state: GraphState) -> Dict[str, Any]:
        """Node that verifies consistency across the entire story."""
        print(f"Executing Consistency Checker node at iteration {state.iteration_count}")
        try:
            # Convert GraphState to dict for agent processing
            state_dict = state.get_agent_context()

            # Process with consistency checker agent
            response: AgentResponse = await self.consistency_checker_agent.process(state_dict)

            # Update state with consistency check output
            new_state = state.copy()
            # Update story notes with consistency issues
            new_state.story_notes.extend(response.suggestions or [])
            new_state.next_agent = "dialogue_specialist"
            new_state.add_agent_response(response)

            # Store consistency report in knowledge base
            await self.knowledge_store.store_memory(
                f"consistency_report_{state.iteration_count}",
                response,
                {"agent": "consistency_checker", "iteration": state.iteration_count}
            )

            return new_state

        except Exception as e:
            print(f"Error in consistency_checker_node: {str(e)}")
            new_state = state.copy()
            new_state.error_count += 1
            new_state.last_error = f"Consistency checker node error: {str(e)}"
            return new_state

    async def dialogue_specialist_node(self, state: GraphState) -> Dict[str, Any]:
        """Node that analyzes and improves character dialogue."""
        print(f"Executing Dialogue Specialist node at iteration {state.iteration_count}")
        try:
            # Convert GraphState to dict for agent processing
            state_dict = state.get_agent_context()

            # Process with dialogue specialist agent
            response: AgentResponse = await self.dialogue_specialist_agent.process(state_dict)

            # Update state with dialogue specialist output
            new_state = state.copy()
            # Apply dialogue recommendations to current chapter (in a real system)
            new_state.next_agent = "world_builder"
            new_state.add_agent_response(response)

            # Store dialogue analysis in knowledge base
            await self.knowledge_store.store_memory(
                f"dialogue_analysis_{state.iteration_count}",
                response,
                {"agent": "dialogue_specialist", "iteration": state.iteration_count}
            )

            return new_state

        except Exception as e:
            print(f"Error in dialogue_specialist_node: {str(e)}")
            new_state = state.copy()
            new_state.error_count += 1
            new_state.last_error = f"Dialogue specialist node error: {str(e)}"
            return new_state

    async def world_builder_node(self, state: GraphState) -> Dict[str, Any]:
        """Node that develops and maintains the fictional world."""
        print(f"Executing World Builder node at iteration {state.iteration_count}")
        try:
            # Convert GraphState to dict for agent processing
            state_dict = state.get_agent_context()

            # Process with world builder agent
            response: AgentResponse = await self.world_builder_agent.process(state_dict)

            # Update state with world builder output
            import json
            world_data = json.loads(response.content)
            new_state = state.copy()
            new_state.world_details.update(world_data)

            # Check if this is a writing cycle and we should finalize the chapter
            if len(new_state.chapters) + 1 <= len(new_state.completed_chapters) + 1:
                # Add the newly completed chapter to the list
                chapter_num = len(new_state.chapters) + 1
                chapter_title = state.outline.get('current_chapter_outline', {}).get('title', f'Chapter {chapter_num}')
                new_state.add_chapter(new_state.current_chapter, chapter_num, chapter_title)

            new_state.current_chapter = ""  # Clear for next chapter
            new_state.next_agent = "pacing_advisor"
            new_state.add_agent_response(response)

            # Store world building in knowledge base
            await self.knowledge_store.store_memory(
                f"world_building_{state.iteration_count}",
                world_data,
                {"agent": "world_builder", "iteration": state.iteration_count}
            )

            return new_state

        except Exception as e:
            print(f"Error in world_builder_node: {str(e)}")
            new_state = state.copy()
            new_state.error_count += 1
            new_state.last_error = f"World builder node error: {str(e)}"
            return new_state

    async def pacing_advisor_node(self, state: GraphState) -> Dict[str, Any]:
        """Node that analyzes story rhythm and pace."""
        print(f"Executing Pacing Advisor node at iteration {state.iteration_count}")
        try:
            # Convert GraphState to dict for agent processing
            state_dict = state.get_agent_context()

            # Process with pacing advisor agent
            response: AgentResponse = await self.pacing_advisor_agent.process(state_dict)

            # Update state with pacing analysis
            new_state = state.copy()
            new_state.story_notes.extend(response.suggestions or [])
            new_state.next_agent = "humanizer"
            new_state.add_agent_response(response)

            # Determine if we should go to human review phase
            if new_state.current_chapter_index > 0:  # We have completed a chapter
                new_state.needs_human_review = True
                new_state.human_review_status = "pending" if not new_state.needs_human_review else new_state.human_review_status

            # Store pacing analysis in knowledge base
            await self.knowledge_store.store_memory(
                f"pacing_analysis_{state.iteration_count}",
                response,
                {"agent": "pacing_advisor", "iteration": state.iteration_count}
            )

            return new_state

        except Exception as e:
            print(f"Error in pacing_advisor_node: {str(e)}")
            new_state = state.copy()
            new_state.error_count += 1
            new_state.last_error = f"Pacing advisor node error: {str(e)}"
            return new_state

    async def humanizer_node(self, state: GraphState) -> Dict[str, Any]:
        """Node that removes AI writing traces to make content more human-like."""
        print(f"Executing Humanizer node at iteration {state.iteration_count}")
        try:
            # Convert GraphState to dict for agent processing
            state_dict = state.get_agent_context()

            # Process with humanizer agent
            response: AgentResponse = await self.humanizer_agent.process(state_dict)

            # Update state with humanizer output
            new_state = state.copy()
            # Apply humanizer results to the current chapter if there is one
            if new_state.current_chapter and state.current_chapter:
                new_state.current_chapter = response.content or state.current_chapter
            new_state.next_agent = "review_or_continue"
            new_state.add_agent_response(response)

            # Store humanization results in knowledge base
            await self.knowledge_store.store_memory(
                f"humanization_{state.iteration_count}",
                response,
                {"agent": "humanizer", "iteration": state.iteration_count}
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
            print(f"Error in humanizer_node: {str(e)}")
            new_state = state.copy()
            new_state.error_count += 1
            new_state.last_error = f"Humanizer node error: {str(e)}"
            return new_state

    async def human_review_node(self, state: GraphState) -> Dict[str, Any]:
        """Node that handles human feedback integration."""
        print(f"Executing Human Review node at iteration {state.iteration_count}")
        try:
            new_state = state.copy()
            new_state.needs_human_review = False
            new_state.human_review_status = "completed"

            # In a real system, this would interface with the UI system
            # For now, we'll assume approval to continue the cycle
            new_state.next_agent = "planner"

            return new_state

        except Exception as e:
            print(f"Error in human_review_node: {str(e)}")
            new_state = state.copy()
            new_state.error_count += 1
            new_state.last_error = f"Human review node error: {str(e)}"
            return new_state