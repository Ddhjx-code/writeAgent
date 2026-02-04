import asyncio
import argparse
import sys
import logging
from typing import Dict, Any, Optional
import json
import os

from .config import Config
from .core.engine import WritingEngine
from .workflow.state import GraphState


class CLIController:
    """Command-line interface controller for the AI collaborative novel writing system."""

    def __init__(self):
        self.config = Config()
        self.engine = WritingEngine(self.config)
        self.initialized = False

    async def initialize(self):
        """Initialize the CLI controller and its dependencies."""
        if not self.initialized:
            await self.engine.initialize()
            self.initialized = True

    async def create_story_interactive(self) -> GraphState:
        """Interactive creation of a new story through CLI."""
        print("\n=== Story Creation ===")

        title = input("Enter story title: ").strip()
        if not title:
            print("Story title is required!")
            return None

        print("\nQuick setup options:")
        print("1. Fantasy Adventure")
        print("2. Sci-Fi Space Opera")
        print("3. Mystery Thriller")
        print("4. Custom")

        choice = input("Choose a template (1-4): ").strip() or "4"

        story_data = {"title": title}

        if choice == "1":
            # Fantasy template
            story_data.update({
                "outline": {
                    "initial_outline": "An epic fantasy adventure with magic and mythical creatures",
                    "genre": "Fantasy",
                    "target_chapters": 8,
                    "themes": ["heroism", "magic", "good vs evil"]
                },
                "characters": {
                    "Erian": {
                        "name": "Erian",
                        "description": "Young mage with mysterious powers",
                        "role": "Protagonist",
                        "personality_traits": ["curious", "determined", "kind-hearted"]
                    }
                },
                "world_details": {
                    "setting": "A world divided between magic and technology",
                    "magic_system": "Arcane energies drawn from nature",
                    "locations": ["Elven Cities", "Wizard Towers", "Ancient Ruins"]
                },
                "notes": ["Start with discovery of hidden magical ability"]
            })
        elif choice == "2":
            # Sci-Fi template
            story_data.update({
                "outline": {
                    "initial_outline": "Space exploration with AI companions and alien civilizations",
                    "genre": "Science Fiction",
                    "target_chapters": 10,
                    "themes": ["discovery", "technology", "what makes us human"]
                },
                "characters": {
                    "Captain Zara": {
                        "name": "Captain Zara",
                        "description": "Experienced space explorer and AI specialist",
                        "role": "Protagonist",
                        "personality_traits": ["analytical", "brave", "empathetic"]
                    }
                },
                "world_details": {
                    "setting": "Deep space, distant civilizations",
                    "technology": "Advanced AI, faster-than-light travel",
                    "locations": ["Space Stations", "Unexplored Planets", "AI Worlds"]
                },
                "notes": ["Focus on relationship between humans and AI"]
            })
        elif choice == "3":
            # Mystery template
            story_data.update({
                "outline": {
                    "initial_outline": "Detective story with supernatural elements",
                    "genre": "Mystery",
                    "target_chapters": 7,
                    "themes": ["truth", "deception", "justice"]
                },
                "characters": {
                    "Detective Liu": {
                        "name": "Detective Liu",
                        "description": "Skilled detective with intuitive abilities",
                        "role": "Protagonist",
                        "personality_traits": ["perceptive", "determined", "skeptical"]
                    }
                },
                "world_details": {
                    "setting": "Modern city with hidden supernatural world",
                    "tone": "Noir style with supernatural elements",
                    "locations": ["Police Station", "Urban Mysteries", "Supernatural Realms"]
                },
                "notes": ["Blend crime procedural with supernatural mystery"]
            })
        else:
            # Custom story
            print("\nEnter custom story details:")
            genre = input("Genre: ").strip() or "General Fiction"
            outline = input("Brief outline: ").strip()
            target_chapters = input("Target number of chapters: ").strip()
            if target_chapters and target_chapters.isdigit():
                target_chapters = int(target_chapters)
            else:
                target_chapters = 5

            characters = {}
            char_input = input("Add main character? (Y/N, default=N): ").lower().strip()
            if char_input.startswith('y'):
                char_name = input("Character name: ").strip()
                char_desc = input("Character description: ").strip()
                if char_name and char_desc:
                    characters[char_name] = {
                        "name": char_name,
                        "description": char_desc,
                        "role": "Protagonist",
                        "personality_traits": []
                    }

            story_data.update({
                "outline": {
                    "initial_outline": outline or "A story with interesting characters and plot",
                    "genre": genre,
                    "target_chapters": target_chapters,
                    "themes": []
                },
                "characters": characters,
                "world_details": {},
                "notes": []
            })

        # Create the new story
        graph_state = await self.engine.create_new_story(story_data)

        print(f"\nStory '{graph_state.title}' has been created!")
        await self.show_story_metrics(graph_state)

        return graph_state

    async def run_story_generation_cli(self, state: GraphState, max_iterations: int = 15, target_chapters: int = 5):
        """Run story generation directly from CLI."""
        print(f"\n=== Starting Story Generation ===")
        print(f"Title: {state.title}")
        print(f"Target: {target_chapters} chapters in {max_iterations} iterations")

        final_state = await self.engine.run_story_generation(
            state,
            max_iterations=max_iterations,
            target_chapters=target_chapters
        )

        print(f"\nStory generation completed!")
        await self.show_story_metrics(final_state)

        # Export the final story
        print("\nGenerated Story Preview:")
        story_txt = await self.engine.export_story(final_state, "txt")
        print(story_txt[:1000] + "..." if len(story_txt) > 1000 else story_txt)

        return final_state

    async def show_story_metrics(self, state: GraphState):
        """Display metrics for a given story state."""
        metrics = await self.engine.get_story_metrics(state)
        print(f"Total words: {metrics.get('total_words', 0)}")
        print(f"Chapters completed: {metrics.get('total_chapters', 0)}")
        print(f"Progress: {metrics.get('story_progress', 0):.1f}%")
        print(f"Characters: {metrics.get('character_count', 0)}")
        print(f"Estimated completion: {metrics.get('estimated_completion_days', 0)} days")

    async def handle_save_load(self, state: GraphState, action: str, path: str = None):
        """Handle save/load operations."""
        if action == "save":
            if not path:
                print("Please specify a file path to save to.")
                return

            success = await self.engine.save_story_state(state, path)
            if success:
                print(f"Story state saved to {path}")
            else:
                print(f"Failed to save story state to {path}")

        elif action == "load":
            if not path:
                print("Please specify a file path to load from.")
                return

            loaded_state = await self.engine.load_story_state(path)
            if loaded_state:
                print(f"Story loaded successfully. Title: {loaded_state.title}")
                await self.show_story_metrics(loaded_state)
                return loaded_state
            else:
                print(f"Failed to load story from {path}")

        return state

    async def run_interactive(self):
        """Run the system in interactive mode."""
        await self.initialize()

        print("AI Collaborative Novel Writing System - Interactive Mode")
        print("="*55)

        current_state = None

        while True:
            print("\nOptions:")
            print("1. Create new story")
            print("2. Load story")
            print("3. Run story generation")
            print("4. View current story")
            print("5. View system status")
            print("6. Export story")
            print("7. Save current story")
            print("8. Add human feedback")
            print("0. Exit")

            choice = input("\nEnter your choice (0-8): ").strip()

            if choice == "0":
                print("Goodbye!")
                break
            elif choice == "1":
                current_state = await self.create_story_interactive()
            elif choice == "2":
                path = input("Enter path to story file: ").strip()
                loaded = await self.handle_save_load(current_state, "load", path)
                if loaded:
                    current_state = loaded
            elif choice == "3":
                if not current_state:
                    print("No story to run. Create a story first.")
                    continue

                max_iters = input("Max iterations (default 15): ").strip()
                max_iters = int(max_iters) if max_iters.isdigit() else 15

                target_chap = input("Target chapters (default 5): ").strip()
                target_chap = int(target_chap) if target_chap.isdigit() else 5

                current_state = await self.run_story_generation_cli(current_state, max_iters, target_chap)
            elif choice == "4":
                if current_state:
                    await self.show_story_metrics(current_state)
                    if current_state.chapters:
                        last_chapter = current_state.chapters[-1] if current_state.chapters else None
                        if last_chapter:
                            content = last_chapter.get('content', '')
                            preview = content[:200] + "..." if len(content) > 200 else content
                            print(f"Last Chapter Preview: {preview}")
                else:
                    print("No active story.")
            elif choice == "5":
                status = self.engine.get_system_status()
                print(f"System Status: {status}")
            elif choice == "6":
                if not current_state:
                    print("No story to export.")
                    continue

                format_type = input("Export format (json/txt/md, default txt): ").strip().lower() or "txt"
                if format_type not in ["json", "txt", "md", "markdown"]:
                    format_type = "txt"

                exported = await self.engine.export_story(current_state, format_type)
                output_file = f"exported_story.{format_type}"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(exported)
                print(f"Story exported to {output_file}")
            elif choice == "7":
                if not current_state:
                    print("No story to save.")
                    continue

                path = input("Enter save path (default: auto-named): ").strip()
                await self.handle_save_load(current_state, "save", path if path else None)
            elif choice == "8":
                if not current_state:
                    print("No active story for feedback.")
                    continue

                feedback = input("Enter your feedback for the current story: ").strip()
                if feedback:
                    await self.engine.add_human_feedback(feedback)
                    print("Feedback recorded.")
            else:
                print("Invalid choice. Please try again.")


async def main():
    """Entry point for CLI."""
    controller = CLIController()

    parser = argparse.ArgumentParser(description="CLI for AI Collaborative Novel Writing System")
    parser.add_argument("command", nargs="?", default="interactive",
                       choices=["interactive", "create", "run", "status"],
                       help="Command to execute")
    parser.add_argument("--title", type=str, help="Story title")
    parser.add_argument("--genre", type=str, help="Story genre")
    parser.add_argument("--outline", type=str, help="Story outline")
    parser.add_argument("--iterations", type=int, default=15, help="Max iterations for generation")
    parser.add_argument("--target-chapters", type=int, default=5, help="Target chapters")
    parser.add_argument("--output", type=str, help="Output file path")

    args = parser.parse_args()

    await controller.initialize()

    # For now, just enter interactive mode unless a specific command is given
    # This can be extended to add non-interactive options later
    await controller.run_interactive()


if __name__ == "__main__":
    asyncio.run(main())