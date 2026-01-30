from typing import Dict, List, Any
from src.agents.base import BaseAgent, AgentConfig
from src.core.story_state import StoryState, Character, Chapter
from src.core.knowledge_base import KnowledgeBase
import json
from datetime import datetime


class WriterAgent(BaseAgent):
    """
    Writer Agent - responsible for generating novel content including:
    - Chapter content based on outlines
    - Character dialogue
    - Descriptive prose
    - Maintaining style and tone consistency
    """

    def __init__(self, config: AgentConfig, knowledge_base: KnowledgeBase, **kwargs):
        super().__init__(config, knowledge_base)
        self.writing_stats = {
            "chapters_written": 0,
            "words_written": 0,
            "sessions": 0
        }

    def process(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process writing tasks based on the context
        """
        action = context.get("action", "write_chapter")
        result = {}

        if action == "write_chapter":
            result = self._write_chapter(state, context)
        elif action == "write_section":
            result = self._write_section(state, context)
        elif action == "write_dialogue":
            result = self._write_dialogue(state, context)
        elif action == "revise_content":
            result = self._revise_content(state, context)
        elif action == "generate_opening":
            result = self._generate_opening(state, context)
        elif action == "generate_closing":
            result = self._generate_closing(state, context)
        elif action == "add_descriptive_text":
            result = self._add_descriptive_text(state, context)
        elif action == "develop_character_voice":
            result = self._develop_character_voice(state, context)
        else:
            result = {"status": "error", "message": f"Unknown action: {action}"}

        # Log the writing activity
        self.log_message(f"Processed action: {action} - {result.get('status', 'unknown')}", "info")

        # Update statistics
        if result.get("status") == "success":
            self.writing_stats["sessions"] += 1
            if "new_content_length" in result:
                self.writing_stats["words_written"] += result["new_content_length"]

        return self.format_response(
            content=json.dumps(result, default=str),
            metadata={
                "action": action,
                "timestamp": datetime.now().isoformat(),
                "stats": self.writing_stats
            }
        )

    def _write_chapter(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Write a complete chapter based on provided outline"""
        try:
            chapter_number = context.get("chapter_number", state.get_next_chapter_number())
            title = context.get("title", f"Chapter {chapter_number}")
            outline = context.get("outline", "")
            target_words = context.get("target_words", 2000)
            characters_in_scene = context.get("characters", [])
            locations_in_scene = context.get("locations", [])

            # Get context from knowledge base
            character_info = []
            for char_id in characters_in_scene:
                char = state.get_character(char_id)
                if char:
                    character_info.append({
                        "name": char.name,
                        "description": char.description,
                        "personality_traits": char.personality_traits,
                        "current_arc": char.metadata.get("arc", ""),
                        "relationships": char.relationships
                    })

            location_info = []
            for loc_id in locations_in_scene:
                loc = state.get_location(loc_id)
                if loc:
                    location_info.append({
                        "name": loc.name,
                        "description": loc.description,
                        "features": loc.features,
                        "atmosphere": loc.metadata.get("atmosphere", ""),
                        "details": loc.metadata.get("details", "")
                    })

            # Build prompt for content generation
            prompt_parts = []
            prompt_parts.append(f"Write Chapter {chapter_number} titled '{title}'")
            prompt_parts.append(f"Genre: {state.genre}")
            prompt_parts.append(f"Target word count: approximately {target_words}")
            prompt_parts.append(f"Overall story summary: {state.summary}")

            if outline:
                prompt_parts.append(f"Chapter outline: {outline}")

            if character_info:
                prompt_parts.append("Characters in this chapter:")
                for char in character_info:
                    prompt_parts.append(
                        f"- {char['name']}: {char['description']}. "
                        f"Personality: {', '.join(char['personality_traits'])}. "
                        f"Arc: {char['current_arc']}"
                    )

            if location_info:
                prompt_parts.append("Setting information:")
                for loc in location_info:
                    prompt_parts.append(
                        f"- {loc['name']}: {loc['description']}. "
                        f"Features: {', '.join(loc['features'])}. "
                        f"Atmosphere: {loc['atmosphere']}"
                    )

            # Get relevant information from knowledge base
            related_info = self.get_relevant_information(f"{outline} {title} {state.genre}", top_k=5)

            for info in related_info:
                prompt_parts.append(f"Relevant previous information: {info}")

            full_prompt = "\n\n".join(prompt_parts)

            # This is where we would call an LLM to generate content
            # For this implementation, we'll create placeholder content
            generated_content = self._generate_placeholder_content(full_prompt, target_words)

            # Create Chapter object
            from src.core.story_state import ChapterState
            chapter = Chapter(
                id=f"chapter_{chapter_number}_{int(datetime.now().timestamp())}",
                number=chapter_number,
                title=title,
                content=generated_content,
                status=ChapterState.DRAFT,
                word_count=len(generated_content.split()),
                characters_in_chapter=characters_in_scene,
                locations_in_chapter=locations_in_scene
            )

            # Add to state
            state.add_chapter(chapter)

            self.writing_stats["chapters_written"] += 1
            self.writing_stats["words_written"] += chapter.word_count

            return {
                "status": "success",
                "message": f"Chapter {chapter_number} '{title}' written successfully",
                "chapter_id": chapter.id,
                "word_count": chapter.word_count,
                "content_preview": generated_content[:200] + "..." if len(generated_content) > 200 else generated_content
            }

        except Exception as e:
            return {"status": "error", "message": f"Error writing chapter: {str(e)}"}

    def _write_section(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Write a specific section of content"""
        try:
            target_section = context.get("section_type", "action")  # action, dialogue, description, transition
            scene_setup = context.get("scene", "")
            character_focus = context.get("character_focus", "")
            target_words = context.get("target_words", 500)

            # Build prompt for section
            prompt = f"Write {target_section} section: {scene_setup}"
            if character_focus:
                prompt += f" with focus on character {character_focus}"

            # Include relevant information from knowledge base
            related_info = self.get_relevant_information(scene_setup, top_k=3)
            for info in related_info:
                prompt += f"\n\nRelated information: {info}"

            # Generate content
            generated_content = self._generate_placeholder_content(prompt, target_words)

            return {
                "status": "success",
                "message": f"Section of type {target_section} written",
                "content": generated_content,
                "word_count": len(generated_content.split())
            }

        except Exception as e:
            return {"status": "error", "message": f"Error writing section: {str(e)}"}

    def _write_dialogue(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate character dialogue"""
        try:
            # Get the character speaking
            character_id = context.get("character_id")
            character = state.get_character(character_id) if character_id else None

            # Get scene context
            scene_context = context.get("scene", "")
            emotional_state = context.get("emotional_state", "")
            conversational_partner = context.get("partner", "")

            if not character:
                return {"status": "error", "message": "Character not found"}

            # Get related dialogue patterns from knowledge base
            character_dialogue_style = character.metadata.get("speech_patterns", "")
            character_personality = character.personality_traits

            # Build prompt
            prompt_parts = [
                f"Write dialogue for character {character.name} ({character.description})",
                f"Personality traits: {', '.join(character_personality)}",
                f"Speech patterns: {character_dialogue_style}",
                f"Scene context: {scene_context}",
            ]

            if emotional_state:
                prompt_parts.append(f"Character's emotional state: {emotional_state}")
            if conversational_partner:
                prompt_parts.append(f"Talking to: {conversational_partner}")

            dialogue_context = "\n".join(prompt_parts)

            # Get relevant dialogue examples from knowledge base
            related_dialogue = self.get_relevant_information(f"dialogue {character.name}", top_k=3)
            if related_dialogue:
                prompt_parts.append("Previous dialogue examples for this character:")
                for example in related_dialogue:
                    if character.name in example:
                        prompt_parts.append(f"> {example}")

            final_prompt = "\n\n".join(prompt_parts)

            # Generate dialogue content
            generated_dialogue = self._generate_placeholder_content(final_prompt, 200)

            return {
                "status": "success",
                "message": f"Dialogue for {character.name} written",
                "character_id": character_id,
                "content": generated_dialogue,
                "word_count": len(generated_dialogue.split())
            }

        except Exception as e:
            return {"status": "error", "message": f"Error writing dialogue: {str(e)}"}

    def _revise_content(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Revise existing content based on feedback"""
        try:
            chapter_id = context.get("chapter_id")
            section = context.get("section", "full")  # full, beginning, middle, end, specific_section
            revision_notes = context.get("notes", "")
            focus = context.get("focus", "style")  # style, clarity, pacing, consistency

            # Get the current content
            chapter = state.get_chapter(chapter_id) if chapter_id else None
            if not chapter:
                return {"status": "error", "message": f"Chapter {chapter_id} not found"}

            current_content = chapter.content
            content_to_revise = current_content

            if section != "full":
                # Extract specific section to revise
                words = content_to_revise.split()
                if section == "beginning":
                    content_to_revise = " ".join(words[:len(words)//3])
                elif section == "middle":
                    mid_start = len(words)//3
                    mid_end = 2 * len(words)//3
                    content_to_revise = " ".join(words[mid_start:mid_end])
                elif section == "end":
                    content_to_revise = " ".join(words[2*len(words)//3:])

            # Build revision prompt
            prompt = f"Revise the following content with focus on {focus}:\n\n{content_to_revise}"
            if revision_notes:
                prompt += f"\n\nRevision notes: {revision_notes}"

            # Get related information that might help with revision
            theme_info = self.get_relevant_information(f"{state.genre} {focus} writing", top_k=2)
            for info in theme_info:
                prompt += f"\n\nReference: {info}"

            # Generate revised content
            revised_content = self._generate_placeholder_content(prompt, len(content_to_revise.split()))

            # If revising a section, reconstruct the full content
            if section != "full":
                words = current_content.split()
                if section == "beginning":
                    revised_content = revised_content + " " + " ".join(words[len(content_to_revise.split()):])
                elif section == "middle":
                    mid_idx = len(words)//3
                    mid_end_idx = 2 * len(words)//3
                    beginning = " ".join(words[:mid_idx])
                    end = " ".join(words[mid_end_idx:])
                    revised_content = beginning + " " + revised_content + " " + end
                elif section == "end":
                    beginning = " ".join(words[:2*len(words)//3])
                    revised_content = beginning + " " + revised_content

            # Update the state with revised content
            state.update_chapter_content(chapter_id, revised_content)

            return {
                "status": "success",
                "message": f"Content revised for chapter {chapter_id}",
                "chapter_id": chapter_id,
                "focus": focus,
                "content_preview": revised_content[:200] + "..." if len(revised_content) > 200 else revised_content
            }

        except Exception as e:
            return {"status": "error", "message": f"Error revising content: {str(e)}"}

    def _generate_opening(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate opening content for the story"""
        try:
            opening_type = context.get("type", "hook")  # hook, setting, character_introduction
            story_context = context.get("story_context", "first chapter of a novel")
            word_count = context.get("target_words", 300)

            # Get story information
            prompt_parts = [
                f"Write an opening {opening_type} for {story_context}. Genre: {state.genre}",
                f"Story summary: {state.summary}",
                f"Target word count: {word_count}"
            ]

            # Get related information from knowledge base
            related_tropes = self.get_relevant_information(f"{state.genre} opening {opening_type}", top_k=3)
            for trope in related_tropes:
                prompt_parts.append(f"Common {state.genre} opening techniques: {trope}")

            # Include important story elements to potentially feature in the opening
            if state.characters:
                sample_char = list(state.characters.values())[0]
                prompt_parts.append(f"Main character: {sample_char.name} - {sample_char.description}")

            if state.locations:
                sample_loc = list(state.locations.values())[0]
                prompt_parts.append(f"Setting: {sample_loc.name} - {sample_loc.description}")

            prompt = "\n\n".join(prompt_parts)

            # Generate opening content
            opening_content = self._generate_placeholder_content(prompt, word_count)

            return {
                "status": "success",
                "message": f"{opening_type} opening generated",
                "content": opening_content,
                "word_count": len(opening_content.split())
            }

        except Exception as e:
            return {"status": "error", "message": f"Error generating opening: {str(e)}"}

    def _generate_closing(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate closing content for a chapter or story"""
        try:
            target_type = context.get("target_type", "chapter")  # chapter, story, section
            tone = context.get("tone", "satisfying")  # satisfying, cliffhanger, reflective
            content_summary = context.get("current_content", "")

            # Get story information
            prompt_parts = [
                f"Write a {tone} {target_type} closing",
                f"Genre: {state.genre}",
                f"Story summary: {state.summary}"
            ]

            if content_summary:
                prompt_parts.append(f"Previous content to lead into closing: {content_summary}")

            # Get related information from knowledge base
            related_endings = self.get_relevant_information(f"{state.genre} {target_type} ending {tone}", top_k=3)
            for ending in related_endings:
                prompt_parts.append(f"Example {tone} {target_type} ending technique: {ending}")

            # Include story elements to tie up
            important_plot_points = list(state.plot_points.values())[:3]  # Top 3 plot points
            if important_plot_points:
                prompt_parts.append("Important plot points to potentially acknowledge:")
                for pp in important_plot_points:
                    prompt_parts.append(f"- {pp.title}: {pp.description}")

            prompt = "\n\n".join(prompt_parts)

            # Generate closing content
            closing_content = self._generate_placeholder_content(prompt, 150)

            return {
                "status": "success",
                "message": f"{target_type} closing generated",
                "content": closing_content,
                "tone": tone,
                "word_count": len(closing_content.split())
            }

        except Exception as e:
            return {"status": "error", "message": f"Error generating closing: {str(e)}"}

    def _add_descriptive_text(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Add sensory and descriptive details to existing content"""
        try:
            target_text = context.get("text", "")
            focus = context.get("focus", "visual")  # visual, auditory, olfactory, tactile, flavor
            intensity = context.get("intensity", "moderate")  # subtle, moderate, vivid

            if not target_text:
                return {"status": "error", "message": "No text provided"}

            # Build prompt for adding description
            prompt_parts = [
                f"Add {intensity} {focus} sensory details to the following content:",
                target_text
            ]

            # Get environmental information from knowledge base
            environment_context = self.get_relevant_information(f"sensory {focus} details", top_k=2)
            for details in environment_context:
                prompt_parts.append(f"Possible {intensity} {focus} details: {details}")

            # Include any location information if applicable
            if "location" in context or state.locations:
                # Use the first location or a specific one
                loc_id = context.get("location")
                loc = state.get_location(loc_id) if loc_id else list(state.locations.values())[0] if state.locations else None
                if loc:
                    prompt_parts.append(f"Environment setting: {loc.description}")
                    if "atmosphere" in loc.metadata:
                        prompt_parts.append(f"Environment atmosphere: {loc.metadata['atmosphere']}")

            prompt = "\n\n".join(prompt_parts)

            # Generate descriptive content
            descriptive_content = self._generate_placeholder_content(prompt, 300)

            return {
                "status": "success",
                "message": f"Added {intensity} {focus} descriptions",
                "original_text": target_text,
                "enhanced_text": descriptive_content,
                "word_count": len(descriptive_content.split())
            }

        except Exception as e:
            return {"status": "error", "message": f"Error adding descriptions: {str(e)}"}

    def _develop_character_voice(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Develop or maintain consistent character voice"""
        try:
            character_id = context.get("character_id")
            content = context.get("content", "")
            focus = context.get("focus", "dialogue")  # dialogue, narration, internal_thought, action

            if not character_id:
                return {"status": "error", "message": "No character_id provided"}

            character = state.get_character(character_id)
            if not character:
                return {"status": "error", "message": f"Character {character_id} not found"}

            # Build prompt for voice development
            prompt_parts = [
                f"Write or enhance content with {character.name}'s voice:",
                f"Character: {character.name} - {character.description}",
                f"Personality traits: {', '.join(character.personality_traits)}",
                f"Speech patterns: {character.metadata.get('speech_patterns', 'N/A')}",
                f"Background: {character.background}",
                f"Content to be in character: {content}",
                f"Focus: {focus}"
            ]

            # Get character's previous writing patterns from knowledge base
            char_voice_samples = self.get_relevant_information(f"dialogue {character.name} voice", top_k=5)
            if char_voice_samples:
                prompt_parts.append(f"Previous {character.name} voice examples:")
                for sample in char_voice_samples:
                    if character.name in sample:
                        prompt_parts.append(f"> {sample}")

            prompt = " ".join(prompt_parts)

            # Generate content in character's voice
            voiced_content = self._generate_placeholder_content(prompt, len(content.split()))

            return {
                "status": "success",
                "message": f"Applied {character.name}'s voice to content",
                "character_id": character_id,
                "content": voiced_content,
                "focus": focus,
                "word_count": len(voiced_content.split())
            }

        except Exception as e:
            return {"status": "error", "message": f"Error developing character voice: {str(e)}"}

    def _generate_placeholder_content(self, prompt: str, target_word_count: int) -> str:
        """
        Placeholder method to generate text content
        In a real implementation, this would call a language model API
        """
        # This is a placeholder - in real implementation would call LLM
        import random

        placeholder_sentences = [
            f"This is generated content based on: {prompt[:50]}...",
            f"Continuing with scene development in the genre of {prompt.split()[0] if prompt.split() else 'fiction'}",
            "The characters interact in the setting as planned in the outline.",
            "Action, dialogue, and narrative flow seamlessly together.",
            "The plot progresses with attention to character development.",
            "Scenes are described with appropriate sensory details.",
            "Dialogue reflects character personalities and advances the plot.",
            "Descriptive passages enhance the atmosphere of the scene.",
            "Pacing varies to maintain reader interest and advance the narrative.",
            "Character motivations are clear and understandable to the reader.",
        ]

        # Generate content with approximately correct word count
        current_words = 0
        result_content = []

        while current_words < target_word_count:
            sentence = random.choice(placeholder_sentences)
            result_content.append(sentence)
            current_words += len(sentence.split())

        return " ".join(result_content[:min(len(result_content), max(1, target_word_count//20))])

    def adjust_writing_style(self, state: StoryState, target_style: str) -> None:
        """
        Adjust the agent's approach to match a specific writing style
        In a full implementation would adjust prompting strategy, model parameters etc.
        """
        self.log_message(f"Adjusting writing style to: {target_style}")
        self.config.system_message += f"\nStyle requirement: {target_style}"