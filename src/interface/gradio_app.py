import gradio as gr
from typing import Dict, Any, List
import asyncio
import json
from ..workflow.graph import NovelWritingGraph
from ..workflow.state import GraphState
from ..config import Config
from ..knowledge.store import KnowledgeStore
from .components import (
    create_story_input_section, create_outline_section, create_character_input_section,
    create_story_output_section, create_agent_control_section,
    create_human_feedback_section, create_visualization_section
)


class GradioInterface:
    """Main Gradio interface for the AI collaborative novel writing system."""

    def __init__(self):
        self.config = Config()
        self.knowledge_store = KnowledgeStore(self.config)
        self.workflow = NovelWritingGraph(self.config)
        self.story_state = None
        self.current_task = None
        self.character_list = []

    async def initialize(self):
        """Initialize the application components."""
        await self.knowledge_store.initialize()
        await self.workflow.initialize()

    def build_interface(self):
        """Build and return the Gradio interface."""
        with gr.Blocks(title="AI Collaborative Novel Writing System") as interface:
            # Header section
            gr.Markdown("# 📚 AI Collaborative Novel Writing System")
            gr.Markdown("A collaborative tool for creating novels with AI assistance")

            # Create component sections
            title, genre, description, target_length = create_story_input_section()
            outline_input, chapters_count, pov_character = create_outline_section()
            char_name, char_role, char_desc, add_char_btn = create_character_input_section()
            curr_chapter, progress_bar, chapters_display, download_btn = create_story_output_section()
            agent_status, agent_speed, start_btn, pause_btn, stop_btn, agent_msgs = create_agent_control_section()
            feedback_area, approve_btn, revision_btn, suggest_btn, revision_preview = create_human_feedback_section()
            char_tree, world_map, plot_chart = create_visualization_section()

            # Create global variables to store state
            story_data = gr.State({
                "title": "",
                "genre": "",
                "description": "",
                "outline": "",
                "chapters_count": 10,
                "characters": [],
                "current_chapter": "",
                "all_chapters": []
            })

            # Define event handlers for components
            def add_character(name, role, description, current_chars):
                if name and description:
                    new_char = {
                        "name": name,
                        "role": role,
                        "description": description
                    }
                    current_chars.append(new_char)
                    return current_chars, "", "", ""
                return current_chars, name, role, description

            def start_writing(title_val, genre_val, desc_val, outline_val, chapters_val, chars_val, progress_state):
                """Start the novel writing process."""
                # Create initial graph state
                initial_state = GraphState(
                    title=title_val,
                    story_status="in_progress",
                    outline={"initial_outline": outline_val, "total_chapters": chapters_val},
                    characters={char["name"]: char for char in chars_val} if chars_val else {}
                )

                # In a real system, we would run the workflow
                story_data = {
                    "title": title_val,
                    "genre": genre_val,
                    "description": desc_val,
                    "outline": outline_val,
                    "chapters_count": chapters_val,
                    "characters": chars_val,
                    "current_chapter": "",
                    "all_chapters": []
                }

                return story_data, "Writing started...", 0.1  # Simulated progress

            def approve_chapter(progress_state):
                """Approve current chapter and move to next."""
                # In a real system, this would set human review status to approved
                progress_state = min(1.0, progress_state + 0.1)
                return "Chapter approved. Moving to next phase...", progress_state

            def provide_feedback(feedback, progress_state):
                """Process human feedback."""
                # In a real system, this would store feedback for agent processing
                processed = f"Feedback received: {feedback[:50]}..."
                progress_state = min(1.0, progress_state + 0.05)
                return processed, "Revision based on feedback...", progress_state

            # Set up interactions
            add_char_btn.click(
                add_character,
                inputs=[char_name, char_role, char_desc, gr.State(self.character_list)],
                outputs=[gr.State(self.character_list), char_name, char_role, char_desc]
            )

            start_btn.click(
                start_writing,
                inputs=[title, genre, description, outline_input, chapters_count, gr.State(self.character_list), progress_bar],
                outputs=[story_data, agent_msgs, progress_bar]
            )

            approve_btn.click(
                approve_chapter,
                inputs=[progress_bar],
                outputs=[agent_msgs, progress_bar]
            )

            revision_btn.click(
                provide_feedback,
                inputs=[feedback_area, progress_bar],
                outputs=[agent_msgs, revision_preview, progress_bar]
            )

            # Set up tabbed layout
            with gr.Row():
                with gr.Column(scale=3):
                    gr.Markdown("### Story Setup")
                    # All the input sections would go here

                with gr.Column(scale=5):
                    gr.Markdown("### Story Output & Controls")
                    # All the output sections would go here

        return interface

    async def run_app(self, share: bool = False, server_name: str = "127.0.0.1", server_port: int = 7860):
        """Run the Gradio application."""
        await self.initialize()
        interface = self.build_interface()

        # Launch the interface
        interface.launch(share=share, server_name=server_name, server_port=server_port)

    def start_server(self, share: bool = False):
        """Start the Gradio server."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def start():
            await self.run_app(share=share)

        loop.run_until_complete(start())


def create_interface():
    """Create and return the Gradio interface."""
    app = GradioInterface()
    return app.build_interface()


# For direct execution
if __name__ == "__main__":
    app = GradioInterface()
    app.start_server(share=False)