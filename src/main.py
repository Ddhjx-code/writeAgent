import asyncio
import argparse
import sys
import logging
from typing import Dict, Any
from .config import Config
from .core.engine import WritingEngine
from .workflow.state import GraphState
import uvicorn


def create_sample_story_data() -> Dict[str, Any]:
    """Create sample story data to initialize the system."""
    return {
        "title": "My AI Collaborative Novel",
        "description": "A story created with AI collaboration",
        "outline": {
            "initial_outline": "A fantasy adventure story about a hero's journey",
            "genre": "Fantasy",
            "target_chapters": 5,
            "themes": ["heroism", "friendship", "discovery"]
        },
        "characters": {
            "Aelar": {
                "name": "Aelar",
                "description": "A young wizard with untapped magical abilities",
                "role": "Protagonist",
                "personality_traits": ["curious", "brave", "sometimes reckless"]
            },
            "Mira": {
                "name": "Mira",
                "description": "A seasoned warrior and guide",
                "role": "Supporting",
                "personality_traits": ["wise", "protective", "practical"]
            }
        },
        "world_details": {
            "setting": "A fantasy world with magic and mythical creatures",
            "magic_system": "Elemental magic based on natural forces",
            "locations": ["Crystal Caves", "Sky Cities", "Ancient Forests"]
        },
        "notes": ["Begin with character introduction and magic discovery"]
    }


async def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="AI Collaborative Novel Writing System")
    parser.add_argument("--ui", action="store_true", help="Launch the Gradio UI")
    parser.add_argument("--api", action="store_true", help="Launch the FastAPI server")
    parser.add_argument("--interface-share", action="store_true", help="Share the Gradio UI publicly")
    parser.add_argument("--create-story", action="store_true", help="Create a sample story")
    parser.add_argument("--run-story", action="store_true", help="Run the story generation process")
    parser.add_argument("--iterations", type=int, default=20, help="Maximum iterations for story generation")
    parser.add_argument("--target-chapters", type=int, default=5, help="Target number of chapters to generate")
    parser.add_argument("--load-state", type=str, help="Path to load existing story state")
    parser.add_argument("--save-path", type=str, help="Path to save story state")

    args = parser.parse_args()

    # Initialize configuration
    config = Config()

    # Initialize the writing engine
    engine = WritingEngine(config)
    await engine.initialize()

    logging.info("AI Collaborative Novel Writing System initialized!")
    logging.info(f"System Status: {await engine.get_system_status()}")

    initial_state = None

    # Load existing story if specified
    if args.load_state:
        logging.info(f"Loading story state from {args.load_state}")
        initial_state = await engine.load_story_state(args.load_state)
    elif args.create_story or args.run_story:
        # Create a new story
        logging.info("Creating a new story...")
        story_data = create_sample_story_data()
        initial_state = await engine.create_new_story(story_data)
        logging.info(f"Created story: '{initial_state.title}''")

    # Run story generation if requested
    if args.run_story and initial_state:
        logging.info("Starting story generation...")
        final_state = await engine.run_story_generation(
            initial_state,
            max_iterations=args.iterations,
            target_chapters=args.target_chapters
        )

        logging.info(f"Story generation completed!")
        logging.info(f"Generated {len(final_state.chapters)} chapters")
        logging.info(f"Final status: {final_state.story_status}")

        # Display metrics
        metrics = await engine.get_story_metrics(final_state)
        logging.info(f"Story metrics: {metrics}")

        # Save the result if path was specified
        if args.save_path:
            success = await engine.save_story_state(final_state, args.save_path)
            logging.info(f"Story state saved: {success}")

        # Export the story
        logging.info("\\nExporting story as text...")
        story_txt = await engine.export_story(final_state, "txt")
        logging.info(story_txt[:500] + "..." if len(story_txt) > 500 else story_txt)

    # Launch UI if requested
    if args.ui:
        if engine.is_running:
            logging.warning("The engine is currently running a story generation process.")
            logging.warning("You may want to complete that first before starting the UI, or run them separately.")

        logging.warning("注意: 当前的UI启动命令仍然引用旧的Gradio界面。")
        logging.warning("如需使用新的现代化React界面，请使用 --api 参数启动API服务器，")
        logging.warning("然后单独启动React前端 (cd src/frontend && npm run dev)")
        await engine.start_interface_server(share=args.interface_share)

    # Launch API server if requested
    elif args.api:
        if engine.is_running:
            logging.warning("The engine is currently running a story generation process.")
            logging.warning("Launching API server alongside running process.")

        from .api.server import app
        # Set the engine to the app so it can be accessed by API endpoints
        app.engine = engine

        # Run FastAPI with uvicorn from a sync context
        import nest_asyncio
        nest_asyncio.apply()

        logging.info("Starting FastAPI server for new interface...")
        uvicorn.run(app, host="0.0.0.0", port=8000)

    # If no specific mode is selected, show status and instructions
    if not any([args.ui, args.api, args.run_story, args.create_story, args.load_state]):
        print("\\nAvailable modes:")
        print("  --ui                    Launch the Gradio web interface (deprecated)")
        print("  --api                   Launch the FastAPI server for new React interface")
        print("  --create-story          Create a sample story to work with")
        print("  --run-story             Execute the story generation workflow")
        print("  --load-state <path>     Load an existing story state")
        print("  --help                  Show this help message")
        print("\\nExample usage:")
        print("  python -m src.main --create-story --run-story --iterations 15")
        print("  python -m src.main --ui --interface-share")
        print("  python -m src.main --api")
        print("  python -m src.main --load-state my_story.json --ui")


if __name__ == "__main__":
    asyncio.run(main())