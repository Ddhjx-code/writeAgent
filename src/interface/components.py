from typing import Dict, Any, List, Optional
import gradio as gr
from ..novel_types import StoryState


def create_story_input_section():
    """Create the story input section of the interface."""
    with gr.Accordion("Story Information", open=True):
        title = gr.Textbox(label="Story Title", placeholder="Enter the title of your story...")
        genre = gr.Dropdown(
            choices=["Fantasy", "Science Fiction", "Mystery", "Romance", "Thriller", "Literary Fiction", "Historical", "Horror", "Other"],
            label="Genre",
            value="Fantasy"
        )
        description = gr.Textbox(
            label="Story Description",
            placeholder="Briefly describe your story concept...",
            lines=3
        )
        target_length = gr.Slider(
            minimum=1000,
            maximum=100000,
            value=10000,
            step=1000,
            label="Target Word Count"
        )
    return title, genre, description, target_length


def create_outline_section():
    """Create the story outline section of the interface."""
    with gr.Accordion("Story Outline", open=True):
        outline_input = gr.Textbox(
            label="Outline",
            placeholder="Provide a brief outline of your story, or leave empty for AI to generate...",
            lines=5
        )
        chapters_count = gr.Slider(
            minimum=1,
            maximum=30,
            value=10,
            step=1,
            label="Number of Chapters"
        )
        pov_character = gr.Textbox(
            label="Point of View Character",
            placeholder="Which character will be the main POV?"
        )
    return outline_input, chapters_count, pov_character


def create_character_input_section():
    """Create the character input section."""
    with gr.Group():
        gr.Markdown("### Character Creation")
        with gr.Row():
            character_name = gr.Textbox(label="Character Name")
        with gr.Row():
            character_role = gr.Dropdown(
                choices=["Protagonist", "Antagonist", "Supporting", "Minor", "Other"],
                label="Character Role",
                value="Protagonist"
            )
        with gr.Row():
            character_description = gr.Textarea(label="Description")
        add_character_btn = gr.Button("Add Character")
    return character_name, character_role, character_description, add_character_btn


def create_story_output_section():
    """Create the story output and visualization section."""
    with gr.Accordion("Story Output", open=True):
        current_chapter_display = gr.Textbox(
            label="Current Chapter",
            lines=15,
            interactive=False
        )
        story_progress_bar = gr.Slider(
            label="Writing Progress",
            minimum=0,
            maximum=1,
            value=0,
            step=0.01
        )
        generated_chapters_display = gr.Dataframe(
            label="Chapter List",
            headers=["Chapter #", "Title", "Word Count", "Status"],
            datatype=["str", "str", "str", "str"],
            value=[]
        )
        download_btn = gr.Button("Download Story")
    return current_chapter_display, story_progress_bar, generated_chapters_display, download_btn


def create_agent_control_section():
    """Create the AI agent control section."""
    with gr.Accordion("AI Agent Controls", open=False):
        gr.Markdown("### Agent Management")
        agent_statuses = gr.Dropdown(
            choices=["All Active", "Writer Only", "Planner Only", "Editor Only", "All Agents", "Custom"],
            label="Agent Configuration",
            value="All Active"
        )
        agent_speed = gr.Slider(
            label="Agent Processing Speed",
            minimum=1,
            maximum=10,
            value=5,
            step=1
        )
        with gr.Row():
            start_btn = gr.Button("Start Writing", variant="primary")
            pause_btn = gr.Button("Pause", variant="secondary")
            stop_btn = gr.Button("Stop", variant="stop")
        agent_messages = gr.TextArea(
            label="Agent Messages",
            placeholder="Agent status and messages will appear here...",
            lines=8,
            interactive=False
        )
    return agent_statuses, agent_speed, start_btn, pause_btn, stop_btn, agent_messages


def create_human_feedback_section():
    """Create the human feedback section."""
    with gr.Accordion("Human Feedback", open=True):
        gr.Markdown("### Chapter Review")
        feedback_textarea = gr.Textarea(
            label="Your Feedback",
            placeholder="Provide feedback on the last chapter or suggest changes...",
            lines=5
        )
        with gr.Row():
            approve_btn = gr.Button("Approve Chapter", variant="primary")
            request_revision_btn = gr.Button("Request Revision", variant="secondary")
            suggest_changes_btn = gr.Button("Suggest Changes", variant="secondary")
        revision_preview = gr.Textbox(
            label="Revision Preview",
            lines=10,
            interactive=False
        )
    return feedback_textarea, approve_btn, request_revision_btn, suggest_changes_btn, revision_preview


def create_visualization_section():
    """Create data visualization section."""
    with gr.Accordion("Story Visualization", open=False):
        with gr.Tab("Characters"):
            character_tree = gr.Graph(
                label="Character Relationships",
                # In a real implementation, this would render a character relationship graph
                value=None
            )
        with gr.Tab("World Building"):
            world_map = gr.Textbox(
                label="World Details",
                placeholder="World building elements will be visualized here...",
                lines=10,
                interactive=False
            )
        with gr.Tab("Plot Progression"):
            plot_chart = gr.BarPlot(
                title="Plot Development",
                # In a real implementation, this would show a plot development chart
            )
    return character_tree, world_map, plot_chart