import gradio as gr
import json
from typing import Dict, Any, List
from src.core.story_state import StoryState, Character, Location, Chapter, ChapterState
try:
    from src.core.knowledge_base import KnowledgeBase  # Original full knowledge base
except ImportError:
    from src.core.knowledge_base_minimal import KnowledgeBase  # Fallback minimal version
from src.core.workflow import NovelWritingWorkflow, create_default_workflow
from src.core.agent_factory import AgentFactory


class NovelWritingApp:
    """
    Gradio UI application for the AI collaborative novel writing system
    """

    def __init__(self):
        self.knowledge_base = KnowledgeBase()
        self.workflow = create_default_workflow(self.knowledge_base)
        self.current_story_state = StoryState()
        self.workflow_running = False
        self.workflow_thread = None

    def create_story_tab(self) -> gr.Tab:
        """Create the story creation tab"""
        with gr.Tab("Story Creation") as tab:
            with gr.Row():
                with gr.Column():
                    title = gr.Textbox(label="Story Title", placeholder="Enter your story title...")
                    genre = gr.Dropdown(
                        choices=["Fantasy", "Science Fiction", "Mystery", "Romance", "Thriller", "Historical", "Contemporary"],
                        label="Genre",
                        value="Fantasy"
                    )
                    summary = gr.Textbox(
                        label="Summary",
                        placeholder="One-sentence summary of the story...",
                        lines=2
                    )
                    target_chapters = gr.Number(label="Target Chapter Count", value=10)

                with gr.Column():
                    save_btn = gr.Button("Create Story")
                    save_status = gr.Textbox(label="Status", interactive=False)

            save_btn.click(
                self.create_new_story,
                inputs=[title, genre, summary, target_chapters],
                outputs=[save_status]
            )

        return tab

    def create_characters_tab(self) -> gr.Tab:
        """Create the characters management tab"""
        with gr.Tab("Characters") as tab:
            with gr.Row():
                with gr.Column():
                    char_name = gr.Textbox(label="Character Name", placeholder="Character's name...")
                    char_role = gr.Textbox(label="Role", placeholder="Character's role (protagonist, antagonist, etc.)")
                    char_description = gr.TextArea(label="Description", placeholder="Physical and personality description...")

                    create_char_btn = gr.Button("Add Character")
                    char_status = gr.Textbox(label="Status", interactive=False)

                    # Display existing characters
                    existing_chars = gr.Dataframe(
                        headers=["ID", "Name", "Role", "Description"],
                        datatype=["str", "str", "str", "str"],
                        interactive=False,
                        label="Existing Characters"
                    )

                with gr.Column():
                    refresh_chars_btn = gr.Button("Refresh Characters")
                    # Detailed character view
                    char_detail = gr.JSON(label="Character Details")

            create_char_btn.click(
                self.add_character,
                inputs=[char_name, char_role, char_description],
                outputs=[char_status, existing_chars]
            )

            refresh_chars_btn.click(
                self.refresh_characters,
                inputs=[],
                outputs=[existing_chars]
            )

        return tab

    def create_locations_tab(self) -> gr.Tab:
        """Create the locations management tab"""
        with gr.Tab("Locations") as tab:
            with gr.Row():
                with gr.Column():
                    loc_name = gr.Textbox(label="Location Name", placeholder="Name of the location...")
                    loc_type = gr.Textbox(label="Type", placeholder="e.g., City, Castle, Forest")
                    loc_description = gr.TextArea(label="Description")
                    loc_features = gr.TextArea(label="Key Features", placeholder="Notable features and landmarks...")

                    create_loc_btn = gr.Button("Add Location")
                    loc_status = gr.Textbox(label="Status", interactive=False)

                with gr.Column():
                    existing_locs = gr.Dataframe(
                        headers=["ID", "Name", "Type", "Description"],
                        datatype=["str", "str", "str", "str"],
                        interactive=False,
                        label="Existing Locations"
                    )

            create_loc_btn.click(
                self.add_location,
                inputs=[loc_name, loc_type, loc_description, loc_features],
                outputs=[loc_status, existing_locs]
            )

        return tab

    def create_chapters_tab(self) -> gr.Tab:
        """Create the chapters management tab"""
        with gr.Tab("Chapters") as tab:
            with gr.Row():
                with gr.Column():
                    chapter_selector = gr.Dropdown(
                        choices=self.get_chapter_list(),
                        label="Select Chapter",
                        interactive=True
                    )

                    generate_chapter_btn = gr.Button("Generate Current Chapter")
                    refresh_chapters_btn = gr.Button("Refresh Chapters")

                with gr.Column():
                    chapter_content = gr.TextArea(
                        label="Chapter Content",
                        placeholder="Chapter content will appear here...",
                        lines=15
                    )

            # Bind events
            refresh_chapters_btn.click(
                self.refresh_chapters,
                inputs=[],
                outputs=[chapter_selector, chapter_content]
            )

            chapter_selector.change(
                self.load_chapter_content,
                inputs=[chapter_selector],
                outputs=[chapter_content]
            )

            generate_chapter_btn.click(
                self.generate_chapter,
                inputs=[chapter_selector],
                outputs=[chapter_content]
            )

        return tab

    def create_workflow_tab(self) -> gr.Tab:
        """Create the workflow management tab"""
        with gr.Tab("Workflow") as tab:
            with gr.Row():
                with gr.Column():
                    action_choice = gr.Radio(
                        choices=[
                            "Run Full Chapter Workflow",
                            "Run Planning Only",
                            "Run Writing Only",
                            "Run Review Only"
                        ],
                        label="Workflow Action",
                        value="Run Full Chapter Workflow"
                    )

                    execute_workflow_btn = gr.Button("Execute Workflow")

                    workflow_status = gr.Textbox(label="Workflow Status", interactive=False)

                with gr.Column():
                    workflow_logs = gr.TextArea(
                        label="Real-time logs",
                        lines=15,
                        max_lines=20
                    )

            execute_workflow_btn.click(
                self.execute_workflow_action,
                inputs=[action_choice],
                outputs=[workflow_status, workflow_logs]
            )

        return tab

    def create_knowledge_base_tab(self) -> gr.Tab:
        """Create the knowledge base management tab"""
        with gr.Tab("Knowledge Base") as tab:
            with gr.Row():
                with gr.Column():
                    query = gr.Textbox(
                        label="Query Knowledge Base",
                        placeholder="Enter your query about story elements..."
                    )

                    search_btn = gr.Button("Search")

                with gr.Column():
                    search_results = gr.Dataframe(
                        headers=["ID", "Type", "Content Preview"],
                        datatype=["str", "str", "str"],
                        interactive=False,
                        label="Search Results"
                    )

            search_btn.click(
                self.query_knowledge_base,
                inputs=[query],
                outputs=[search_results]
            )

        return tab

    def create_new_story(self, title: str, genre: str, summary: str, target_chapters: int) -> str:
        """Create a new story with the provided details"""
        try:
            self.current_story_state = StoryState(
                title=title,
                genre=genre,
                summary=summary,
                target_chapter_count=target_chapters
            )

            # Add some basic metadata to KB for the story
            story_info = f"Story: {title}, Genre: {genre}, Summary: {summary}"
            self.knowledge_base.add_document(story_info, f"story_{title.replace(' ', '_')}")

            return f"Created new story: {title}"
        except Exception as e:
            return f"Error: {str(e)}"

    def add_character(self, name: str, role: str, description: str) -> tuple:
        """Add character to the story state and knowledge base"""
        try:
            # Create character with unique ID
            char_id = f"char_{len(self.current_story_state.characters) + 1}"
            character = Character(
                id=char_id,
                name=name,
                role=role,
                description=description,
                personality_traits=[],
                relationships={},
                metadata={}
            )

            # Add to the current story state
            self.current_story_state.add_character(character)

            # Add to knowledge base
            from src.core.knowledge_base import KnowledgeEntity
            self.knowledge_base.add_entity(
                KnowledgeEntity(
                    id=char_id,
                    name=character.name,
                    type="character",
                    description=character.description,
                    metadata=character.metadata,
                    relationships=list(character.relationships.keys())
                )
            )

            # Get updated characters list
            characters_list = []
            for id, char in self.current_story_state.characters.items():
                characters_list.append([id, char.name, char.role, char.description])

            return f"Added character: {name}", characters_list
        except Exception as e:
            return f"Error adding character: {str(e)}", []

    def add_location(self, name: str, type: str, description: str, features: str) -> tuple:
        """Add location to the story state and knowledge base"""
        try:
            loc_id = f"loc_{len(self.current_story_state.locations) + 1}"
            location = Location(
                id=loc_id,
                name=name,
                type=type,
                description=description,
                features=features.split('\n') if features else [],
                significance="",
                metadata={}
            )

            self.current_story_state.add_location(location)

            return f"Added location: {name}", self.get_locations_list()
        except Exception as e:
            return f"Error adding location: {str(e)}", []

    def get_chapter_list(self) -> List[str]:
        """Get list of existing chapters in dropdown format"""
        chapter_list = []
        for ch_id, chapter in sorted(
            self.current_story_state.chapters.items(),
            key=lambda x: x[1].number
        ):
            status_map = {
                ChapterState.DRAFT: "Draft",
                ChapterState.REVIEW: "Review",
                ChapterState.APPROVED: "Approved",
                ChapterState.REJECTED: "Rejected",
                ChapterState.REVISION: "Revision",
                ChapterState.COMPLETED: "Completed"
            }
            status = status_map.get(chapter.status, "Draft")
            chapter_list.append(f"Chapter {chapter.number} - {chapter.title} ({status})")

        return chapter_list if chapter_list else ["No chapters yet"]

    def get_locations_list(self) -> List[List[str]]:
        """Get list of existing locations in dataframe format"""
        locations_list = []
        for id, loc in self.current_story_state.locations.items():
            locations_list.append([id, loc.name, loc.type, loc.description])

        return locations_list

    def generate_chapter(self, chapter_choice: str) -> str:
        """Generate a chapter using the workflow"""
        try:
            # Parse selected chapter number from the formatted choice
            chapter_num_str = chapter_choice.split(' ')[1]  # Extract "Chapter X" -> "X"
            chapter_num = int(chapter_num_str)

            # Run the workflow to generate this chapter
            # This is a simplified implementation - in reality, would run the workflow until this point
            self.current_story_state.current_chapter_number = chapter_num

            # Return placeholder content
            placeholder_content = f"# Chapter {chapter_num}\n\nThis is the content of Chapter {chapter_num} generated by the AI agents."

            # Update the current state with this chapter
            from src.core.story_state import Chapter as StoryChapter
            chapter = StoryChapter(
                id=f"ch_{chapter_num}",
                number=chapter_num,
                title=f"Chapter {chapter_num}",
                content=placeholder_content,
                status=ChapterState.DRAFT
            )
            self.current_story_state.add_chapter(chapter)

            return placeholder_content
        except Exception as e:
            return f"Error generating chapter: {str(e)}"

    def refresh_chapters(self) -> tuple:
        """Refresh the list of chapters"""
        new_chapter_list = self.get_chapter_list()
        # Return the first chapter's content if available
        content = "No chapters available"
        if self.current_story_state.chapters:
            first_chapter = next(iter(self.current_story_state.chapters.values()))
            content = first_chapter.content
        return new_chapter_list, content

    def load_chapter_content(self, chapter_choice: str) -> str:
        """Load chapter content when chapter is selected"""
        try:
            # Parse selected chapter number from the formatted choice
            chapter_num_str = chapter_choice.split(' ')[1]  # Extract "Chapter X" -> "X"
            chapter_num = int(chapter_num_str)

            # Find the chapter with this number
            for ch_id, chapter in self.current_story_state.chapters.items():
                if chapter.number == chapter_num:
                    return chapter.content

            return f"Chapter {chapter_num} content not found"
        except:
            return "Could not load chapter content"

    def refresh_characters(self) -> List[List[str]]:
        """Refresh the list of existing characters"""
        characters_list = []
        for id, char in self.current_story_state.characters.items():
            characters_list.append([id, char.name, char.role, char.description])

        return characters_list

    def execute_workflow_action(self, action: str) -> tuple:
        """Execute selected workflow action"""
        try:
            log_message = f"Starting workflow action: {action}"

            if "Full Chapter" in action:
                # Run the entire workflow for one chapter
                result = self.workflow.run(self.current_story_state)
                log_message += f"\nCompleted: {result}"
            elif "Planning" in action:
                # Run only the planning part
                # This would require running part of the workflow
                log_message += "\nPlanning execution would start here"
            elif "Writing" in action:
                # Run only the writing part
                log_message += "\nWriting execution would start here"
            elif "Review" in action:
                # Run only the review part
                log_message += "\nReview execution would start here"

            return f"Executed: {action}", log_message
        except Exception as e:
            return f"Error: {str(e)}", f"Error during execution: {str(e)}"

    def query_knowledge_base(self, query: str) -> List[List[str]]:
        """Query the knowledge base"""
        try:
            results = self.knowledge_base.query(query, similarity_top_k=5)
            formatted_results = []

            for doc in results:
                # Simple formatting - in reality might want more sophisticated display
                preview = doc.text[:100] if len(doc.text) > 100 else doc.text
                formatted_results.append([getattr(doc, 'doc_id', 'unknown'), "document", preview])

            return formatted_results
        except Exception as e:
            return [["error", "error", f"Error querying knowledge base: {str(e)}"]]

    def launch(self, share: bool = False):
        """Launch the Gradio interface"""
        with gr.Blocks(title="AI Collaborative Novel Writing System") as app:
            gr.Markdown("# AI Collaborative Novel Writing System")

            # Create all tabs
            with gr.Tab("Dashboard"):
                gr.Markdown("## Current Story Status")
                with gr.Row():
                    with gr.Column():
                        story_title = gr.Textbox(label="Current Story", value=lambda: getattr(self.current_story_state, 'title', 'No story created yet'), interactive=False)
                        story_status = gr.Textbox(label="Status", value="Ready", interactive=False)
                        chapter_count = gr.Number(label="Chapters", value=lambda: len(self.current_story_state.chapters), interactive=False)
                    with gr.Column():
                        overall_progress = gr.Slider(label="Completion", minimum=0, maximum=100, value=0, interactive=False)
                        gr.Markdown("### Quick Actions")
                        with gr.Row():
                            save_state_btn = gr.Button("Save Current State")
                            load_state_btn = gr.Button("Load Saved State")

            self.create_story_tab()
            self.create_characters_tab()
            self.create_locations_tab()
            self.create_chapters_tab()
            self.create_workflow_tab()
            self.create_knowledge_base_tab()

            # Add general actions
            with gr.Row():
                clear_btn = gr.Button("Clear All")
                export_btn = gr.Button("Export Story")

        app.launch(share=share, server_port=7860)


if __name__ == "__main__":
    # Create and launch the application
    app = NovelWritingApp()
    app.launch(share=False)