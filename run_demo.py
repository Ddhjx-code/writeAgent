#!/usr/bin/env python3
"""
Demo script for the AI Collaborative Novel Writing System
"""

import sys
import os

def main():
    print("🎭 AI Collaborative Novel Writing System - Demo")
    print("="*50)
    print()

    print("📚 Loading system components...")

    # Add src to the Python path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

    # Import core system components
    try:
        from core.story_state import StoryState, Character, Location, Chapter, ChapterState
        print("✅ Story State management loaded")
    except Exception as e:
        print(f"❌ Error loading story state: {e}")
        return

    try:
        from core.agent_factory import AgentFactory
        print("✅ Agent Factory loaded")
    except Exception as e:
        print(f"❌ Error loading agent factory: {e}")
        return

    try:
        from core.knowledge_base_minimal import KnowledgeBase, KnowledgeEntity
        print("✅ Knowledge Base loaded")
    except Exception as e:
        print(f"❌ Error loading knowledge base: {e}")
        return

    print()
    print("🌟 Setting up a sample story...")

    # Create a sample story
    story = StoryState(
        title="The Crystal Labyrinth",
        genre="Fantasy",
        summary="An adventurers seeks an ancient crystal in a dangerous labyrinth",
        target_chapter_count=10
    )
    print(f"📖 Created story: '{story.title}' ({story.genre})")

    print()
    print("👤 Adding main characters...")
    # Add main character
    main_char = Character(
        id="main_001",
        name="Elena Spellbreaker",
        role="Protagonist",
        description="A young mage specializing in breaking ancient curses",
        personality_traits=["brave", "curious", "stubborn"],
        background="Apprentice to the court wizard"
    )
    story.add_character(main_char)
    print(f"  👤 Character: {main_char.name} - {main_char.description}")

    # Add antagonist
    antagonist = Character(
        id="ant_001",
        name="Vorthak the Eternal",
        role="Antagonist",
        description="Ancient lich who guards the crystal",
        personality_traits=["cunning", "malevolent", "power-hungry"],
        background="Once a great hero, now corrupted by power"
    )
    story.add_character(antagonist)
    print(f"  👤 Character: {antagonist.name} - {antagonist.description}")

    print()
    print("🏛️ Adding story locations...")
    labyrinth = Location(
        id="loc_labyrinth_001",
        name="The Crystal Labyrinth",
        description="A maze of crystalline passages filled with ancient magic and traps",
        type="dungeon",
        features=["crystal formations", "illusions", "shifting walls", "elemental guardians"],
        significance="Central location, the goal of the quest"
    )
    story.add_location(labyrinth)
    print(f"  🏛️ Location: {labyrinth.name}")
    print(f"     Features: {', '.join(labyrinth.features[:3])}")

    print()
    print("📜 Creating sample chapter outline...")
    # Create initial chapter
    first_chapter = Chapter(
        id="ch_001",
        number=1,
        title="The Journey Begins",
        content="Elena Spellbreaker stands before the entrance to the Crystal Labyrinth, her magical staff glowing softly in the twilight. Today she begins her quest to retrieve the ancient crystal...",
        status=ChapterState.DRAFT,
        word_count=2100,
        characters_in_chapter=[main_char.id],
        locations_in_chapter=[labyrinth.id]
    )
    story.add_chapter(first_chapter)
    print(f"  Chapter {first_chapter.number}: '{first_chapter.title}'")
    print(f"  Status: {first_chapter.status}, {first_chapter.word_count} words")

    print()
    print("🧠 Initializing AI agent collaboration...")

    # Create knowledge base
    kb = KnowledgeBase()

    # Create main character in knowledge base
    main_char_entity = KnowledgeEntity(
        id="main_001",
        name="Elena Spellbreaker",
        description="A young mage specializing in breaking ancient curses",
        type="character"
    )
    kb.add_entity(main_char_entity)

    # Create location in knowledge base
    labyrinth_entity = KnowledgeEntity(
        id="loc_labyrinth_001",
        name="The Crystal Labyrinth",
        description="A maze of crystalline passages filled with ancient magic and traps",
        type="location"
    )
    kb.add_entity(labyrinth_entity)

    # Initialize agent factory
    agent_factory = AgentFactory(knowledge_base=kb)

    # Create all specialized agents
    agents = agent_factory.create_all_agents()

    # Verify agents were created (even with fallbacks due to missing dependencies)
    agent_names = list(agents.keys())
    print(f"  🤖 Created {len(agent_names)} specialized agents: {', '.join(agent_names[:3])}...")

    print()
    print("🔍 System Summary:")
    print(f"  - Story: {story.title}")
    print(f"  - Genre: {story.genre}")
    print(f"  - Summary: {story.summary}")
    print(f"  - Characters: {len(story.characters)}")
    print(f"  - Locations: {len(story.locations)}")
    print(f"  - Chapters: {len(story.chapters)}")
    print(f"  - Target: {story.target_chapter_count} total chapters")

    print()
    print("🚀 Demo completed successfully!")
    print()
    print("💡 Next steps:")
    print("   1. Install dependencies: pip install -r requirements.txt")
    print("   2. Start the UI: python src/ui/gradio_app.py")
    print("   3. Begin creating your AI-assisted novel!")

if __name__ == "__main__":
    main()