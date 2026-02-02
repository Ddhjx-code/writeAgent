from typing import Dict, List, Any, Optional
from src.agents.base import BaseAgent, AgentConfig
from src.core.story_state import StoryState, PlotPoint, Character, Location
from src.core.knowledge_base import KnowledgeBase
import json
from datetime import datetime


class PlannerAgent(BaseAgent):
    """
    Planner Agent - responsible for story planning including:
    - Story main thread design
    - Chapter outlines and structure
    - Plot points and turning points
    - Character story arcs
    - Pacing and tension structure
    """

    def __init__(self, config: AgentConfig, knowledge_base: KnowledgeBase, **kwargs):
        super().__init__(config, knowledge_base)
        self.planning_stats = {
            "stories_planned": 0,
            "chapters_outlined": 0,
            "plot_points_created": 0
        }

    def process(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process planning tasks based on the context
        """
        action = context.get("action", "outline_chapter")
        result = {}

        if action == "outline_chapter":
            result = self._outline_chapter(state, context)
        elif action == "design_story_arc":
            result = self._design_story_arc(state, context)
        elif action == "create_plot_points":
            result = self._create_plot_points(state, context)
        elif action == "plan_character_arc":
            result = self._plan_character_arc(state, context)
        elif action == "outline_multiple_chapters":
            result = self._outline_multiple_chapters(state, context)
        elif action == "create_synopsis":
            result = self._create_synopsis(state, context)
        elif action == "plan_pacing":
            result = self._plan_pacing(state, context)
        elif action == "design_conflict_structure":
            result = self._design_conflict_structure(state, context)
        else:
            result = {"status": "error", "message": f"Unknown action: {action}"}

        # Log the planning activity
        self.log_message(f"Processed action: {action} - {result.get('status', 'unknown')}", "info")

        # Update statistics
        if result.get("status") == "success":
            if action == "outline_chapter":
                self.planning_stats["chapters_outlined"] += 1
            elif action == "create_plot_points":
                self.planning_stats["plot_points_created"] += len(result.get("plot_points", []))
            elif action in ["design_story_arc", "create_synopsis"]:
                self.planning_stats["stories_planned"] += 1

        return self.format_response(
            content=json.dumps(result, default=str),
            metadata={
                "action": action,
                "timestamp": datetime.now().isoformat(),
                "stats": self.planning_stats
            }
        )

    def _outline_chapter(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create an outline for a specific chapter"""
        try:
            chapter_number = context.get("chapter_number", state.get_next_chapter_number())
            chapter_title = context.get("title", f"Chapter {chapter_number}")
            scene_list = context.get("scenes", [])
            pov_character = context.get("pov_character", "")
            plot_advancement = context.get("plot_advancement", "")
            character_development = context.get("character_development", "")

            # Get related planning information from knowledge base
            planning_tips = self.get_relevant_information(f"chapter outline {state.genre}", top_k=3)

            # Build chapter outline
            outline_parts = [
                f"Chapter {chapter_number}: {chapter_title}",
                f"Point of View: {pov_character}",
                f"Genre: {state.genre}",
                f"Setting: {context.get('setting', 'various')}",
            ]

            if plot_advancement:
                outline_parts.append(f"Plot advancement: {plot_advancement}")
            if character_development:
                outline_parts.append(f"Character development: {character_development}")

            if scene_list:
                outline_parts.append("Scenes:")
                for i, scene in enumerate(scene_list, 1):
                    outline_parts.append(f"  {i}. {scene}")
            else:
                # Generate default scenes if not specified
                outline_parts.append("Scenes:")
                outline_parts.append(f"  1. Opening hook")
                outline_parts.append(f"  2. Character interaction/development")
                outline_parts.append(f"  3. Plot advancement/plot point")
                outline_parts.append(f"  4. Conflict/increase tension")
                outline_parts.append(f"  5. Closing/setup for next chapter")

            # Add relevant planning tips
            for tip in planning_tips:
                if "chapter" in tip.lower():
                    outline_parts.append(f"Planning consideration: {tip}")

            chapter_outline = "\n".join(outline_parts)

            # Generate additional details
            goals = context.get("goals", [])
            conflicts = context.get("conflicts", [])
            reveals = context.get("reveals", [])

            details = {
                "chapter_number": chapter_number,
                "title": chapter_title,
                "outline": chapter_outline,
                "scenes": scene_list or ["Opening hook", "Character development", "Plot advancement", "Conflict", "Closing"],
                "goals": goals,
                "conflicts": conflicts,
                "reveals": reveals,
                "pov_character": pov_character,
            }

            return {
                "status": "success",
                "message": f"Chapter {chapter_number} outline created",
                "chapter_number": chapter_number,
                "outline": chapter_outline,
                "details": details
            }

        except Exception as e:
            return {"status": "error", "message": f"Error outlining chapter: {str(e)}"}

    def _design_story_arc(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Design the overall story arc"""
        try:
            target_chapters = context.get("target_chapters", 10)
            story_type = context.get("story_type", "three_act")
            theme = context.get("theme", "general")

            # Get character IDs for the story
            character_ids = list(state.characters.keys())[:3]  # Primary characters
            # Get location IDs for the story
            location_ids = list(state.locations.keys())[:3]  # Key locations

            # Get related story arc information from knowledge base
            arc_info = self.get_relevant_information(f"story arc {story_type} {state.genre}", top_k=5)

            # Define the basic structure
            acts = self._generate_story_structure(story_type, target_chapters)

            # Build full story arc
            story_arc_parts = [
                f"TITLE: {state.title or 'Untitled'}",
                f"GENRE: {state.genre}",
                f"STORY TYPE: {story_type}",
                f"THEME: {theme}",
                f"TARGET CHAPTERS: {target_chapters}\n"
            ]

            # Add act-by-act breakdown
            for i, act in enumerate(acts, 1):
                story_arc_parts.append(f"ACT {i}: {act['name']}")
                story_arc_parts.append(f"Chapters: {act['chapter_range']}")
                story_arc_parts.append(f"Focus: {act['focus']}")
                story_arc_parts.append(f"Key Elements: {act['key_elements']}")
                story_arc_parts.append("")

            # Add character arcs
            if character_ids:
                story_arc_parts.append("CHARACTER ARCS:")
                for char_id in character_ids:
                    char = state.get_character(char_id)
                    if char:
                        story_arc_parts.append(f"- {char.name}: {char.arc if hasattr(char, 'arc') else 'Change and development'}")
                story_arc_parts.append("")

            # Add location significance
            if location_ids:
                story_arc_parts.append("KEY LOCATIONS:")
                for loc_id in location_ids:
                    loc = state.get_location(loc_id)
                    if loc:
                        story_arc_parts.append(f"- {loc.name}: {loc.significance}")
                story_arc_parts.append("")

            # Add any tips from the knowledge base
            for info in arc_info:
                if any(keyword in info.lower() for keyword in ["structure", "act", "arc", "plot"]):
                    story_arc_parts.append(f"PLANNING TIP: {info}")
                    story_arc_parts.append("")

            story_arc = "\n".join(story_arc_parts)

            # Extract plot points from the structure
            all_plot_points = []
            chapter_idx = 1
            for i, act in enumerate(acts, 1):
                # Create plot points based on act structure
                if act['key_elements']:
                    for j, key_element in enumerate(act['key_elements'].split(", ")):
                        plot_point = PlotPoint(
                            id=f"plot_{chapter_idx}_{i}_{j}",
                            title=f"{act['name']} - {key_element}",
                            description=key_element,
                            type="key_turning_point",
                            chapter=chapter_idx,
                            order=j,
                            consequences=[f"Advances {act['focus']}"]
                        )
                        all_plot_points.append(plot_point)
                chapter_idx = min(chapter_idx + target_chapters // len(acts), target_chapters)

            # Update story state with plot points
            for plot_point in all_plot_points:
                state.add_plot_point(plot_point)

            return {
                "status": "success",
                "message": f"Story arc designed with {len(acts)} acts",
                "story_arc": story_arc,
                "acts": acts,
                "plot_points": [pp.model_dump() for pp in all_plot_points]
            }

        except Exception as e:
            return {"status": "error", "message": f"Error designing story arc: {str(e)}"}

    def _create_plot_points(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create major plot points for the story"""
        try:
            # Extract context information
            start_chapter = context.get("start_chapter", 1)
            end_chapter = context.get("end_chapter", 10)
            point_types = context.get("types", ["inciting_incident", "rising_action", "climax", "resolution"])
            theme_elements = context.get("themes", ["theme1", "theme2"])

            # Get related plot information from knowledge base
            plot_info = self.get_relevant_information(f"plot development {state.genre}", top_k=5)

            # Generate plot points
            plot_points = []
            current_chapter = start_chapter

            for idx, plot_type in enumerate(point_types * max(1, len(range(start_chapter, end_chapter)) // len(point_types))):
                if current_chapter > end_chapter:
                    break

                plot_point = PlotPoint(
                    id=f"plot_{current_chapter}_{idx}",
                    title=getattr(self, f'_generate_plot_title_{plot_type}', lambda: f"{plot_type.replace('_', ' ').title()}")(),
                    description=self._generate_plot_description(plot_type, state.genre, theme_elements),
                    type=plot_type,
                    chapter=current_chapter,
                    order=idx,
                    consequences=self._generate_consequences(plot_type),
                    metadata={"importance": self._get_plot_type_importance(plot_type)}
                )

                plot_points.append(plot_point)
                current_chapter += max(1, (end_chapter - start_chapter) // len(point_types))

            # Add plot points to state
            for plot_point in plot_points:
                state.add_plot_point(plot_point)

            # Format response
            formatted_points = []
            for pp in plot_points:
                formatted_points.append({
                    "id": pp.id,
                    "title": pp.title,
                    "description": pp.description,
                    "type": pp.type,
                    "chapter": pp.chapter,
                    "consequences": pp.consequences,
                    "order": pp.order
                })

            return {
                "status": "success",
                "message": f"Created {len(plot_points)} plot points",
                "plot_points": formatted_points
            }

        except Exception as e:
            return {"status": "error", "message": f"Error creating plot points: {str(e)}"}

    def _plan_character_arc(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Plan a character arc for a specific character"""
        try:
            character_id = context.get("character_id")
            if not character_id or character_id not in state.characters:
                return {"status": "error", "message": f"Character {character_id} not found"}

            char = state.get_character(character_id)

            # Determine the story length for arc
            total_chapters = context.get("total_chapters", 10)
            story_type = context.get("story_type", "transformation")

            # Get character info
            char_name = char.name
            initial_state = f"{char.description} with traits: {', '.join(char.personality_traits)}"
            character_goal = char.metadata.get("goal", "Unknown")
            internal_conflict = char.metadata.get("internal_conflict", "None")

            # Define stages of character arc
            stages = self._define_character_arc_stages(story_type, total_chapters)

            # Build character arc description
            arc_parts = [
                f"CHARACTER ARC FOR: {char_name}",
                f"Initial State: {initial_state}",
                f"Main Goal: {character_goal}",
                f"Internal Conflict: {internal_conflict}",
                "\nARC STAGES:"
            ]

            for stage_name, chapters in stages.items():
                stage_desc = self._generate_stage_description(character_id, stage_name, story_type)
                arc_parts.append(f"{stage_name.upper()} (Chapters {chapters[0]}-{chapters[-1] if len(chapters) > 1 else chapters[0]}):")
                arc_parts.append(f"  {stage_desc}")
                arc_parts.append("")

            character_arc = "\n".join(arc_parts)

            # Update character metadata with arc information
            if "arc" not in char.metadata:
                char.metadata["arc"] = {}
            char.metadata["arc"]["story_type"] = story_type
            char.metadata["arc"]["stages"] = stages
            char.metadata["arc"]["description"] = character_arc

            # Add to knowledge base
            self.knowledge_base.update_entity(self._create_char_entity(char))

            return {
                "status": "success",
                "message": f"Character arc planned for {char_name}",
                "character_id": character_id,
                "arc_description": character_arc,
                "stages": stages
            }

        except Exception as e:
            return {"status": "error", "message": f"Error planning character arc: {str(e)}"}

    def _outline_multiple_chapters(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create outlines for multiple consecutive chapters"""
        try:
            start_chapter = context.get("start_chapter", state.get_next_chapter_number())
            end_chapter = context.get("end_chapter", start_chapter + 5)

            # Get related information
            outline_tips = self.get_relevant_information(f"chapter {state.genre} structure", top_k=3)

            chapter_outlines = []

            # Generate outlines with story arc progression
            story_progress = 0
            for chap_num in range(start_chapter, end_chapter + 1):
                progress_percentage = story_progress / (end_chapter - start_chapter + 1)

                # Generate context for this specific chapter
                chapter_context = {
                    "chapter_number": chap_num,
                    "title": f"Chapter {chap_num}",
                    "pacing": self._determine_pacing(progress_percentage),
                    "story_beat": self._determine_story_beat(progress_percentage),
                    "character_focus": self._determine_character_focus(state, progress_percentage)
                }

                # Generate the outline
                result = self._outline_chapter(state, chapter_context)
                if result["status"] == "success":
                    result["details"]["chapter_number"] = chap_num
                    chapter_outlines.append(result["details"])

                story_progress += 1

            return {
                "status": "success",
                "message": f"Outlined {len(chapter_outlines)} chapters ({start_chapter} to {end_chapter})",
                "outlines": chapter_outlines,
                "chapters_count": len(chapter_outlines)
            }

        except Exception as e:
            return {"status": "error", "message": f"Error outlining multiple chapters: {str(e)}"}

    def _create_synopsis(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a detailed synopsis of the story"""
        try:
            tone = context.get("tone", "comprehensive")  # comprehensive, brief, detailed
            focus = context.get("focus", "plot")  # plot, characters, world

            # Get story elements
            characters = list(state.characters.values())
            locations = list(state.locations.values())

            # Build synopsis
            synopsis_parts = [
                f"SYNOPSIS FOR: {state.title or 'Untitled Story'}",
                f"Genre: {state.genre}",
                f"Status: {state.status}",
                ""
            ]

            # Add plot summary
            all_plot_points = list(state.plot_points.values())
            if all_plot_points:
                synopsis_parts.append("PLOT OVERVIEW:")
                plot_sorted = sorted(all_plot_points, key=lambda x: (x.chapter, x.order))

                for point in plot_sorted:
                    synopsis_parts.append(f"  Chapter {point.chapter}: {point.title}")
                    synopsis_parts.append(f"    {point.description}")
                synopsis_parts.append("")

            # Add character info if requested
            if focus in ["characters", "plot"]:
                if characters:
                    synopsis_parts.append("MAIN CHARACTERS:")
                    for char in characters:
                        synopsis_parts.append(f"- {char.name}: {char.description} ({char.role})")
                    synopsis_parts.append("")

            # Add location info if requested
            if focus in ["world", "plot"]:
                if locations:
                    synopsis_parts.append("KEY LOCATIONS:")
                    for loc in locations:
                        synopsis_parts.append(f"- {loc.name}: {loc.description}")
                    synopsis_parts.append("")

            # Get related story synopsis examples
            if tone == "comprehensive":
                examples = self.get_relevant_information(f"synopsis {state.genre} example", top_k=2)
                for example in examples:
                    synopsis_parts.append(f"EXAMPLE STRUCTURE: {example}")
                    synopsis_parts.append("")

            synopsis_text = "\n".join(synopsis_parts)

            return {
                "status": "success",
                "message": "Synopsis created",
                "synopsis": synopsis_text,
                "tone": tone,
                "focus": focus
            }

        except Exception as e:
            return {"status": "error", "message": f"Error creating synopsis: {str(e)}"}

    def _plan_pacing(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Plan the pacing structure for the story"""
        try:
            total_chapters = context.get("total_chapters", 10)
            pacing_style = context.get("style", "balanced")  # fast_paced, slow_burn, balanced

            pacing_plan = {
                "pacing_style": pacing_style,
                "total_chapters": total_chapters,
                "chapters": []
            }

            for chapter_num in range(1, total_chapters + 1):
                # Calculate where we are in the story (0 to 1)
                progress = (chapter_num - 1) / total_chapters if total_chapters > 0 else 0.0

                chapter_pacing = self._calculate_chapter_pacing(progress, pacing_style, total_chapters, chapter_num)

                pacing_plan["chapters"].append({
                    "chapter": chapter_num,
                    "pacing_intensity": chapter_pacing["intensity"],
                    "content_focus": chapter_pacing["focus"],
                    "action_dialogue_ratio": chapter_pacing["action_dialogue_ratio"],
                    "exposition_level": chapter_pacing["exposition_level"]
                })

            # Add to story metadata
            state.metadata["pacing_plan"] = pacing_plan

            return {
                "status": "success",
                "message": f"Pacing plan created for {total_chapters} chapters",
                "pacing_plan": pacing_plan
            }

        except Exception as e:
            return {"status": "error", "message": f"Error planning pacing: {str(e)}"}

    def _design_conflict_structure(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Design the overall conflict structure"""
        try:
            conflict_types = context.get("types", ["internal", "external", "interpersonal"])
            intensity_arc = context.get("intensity_arc", "escalating")  # escalating, oscillating, steady

            # Get characters for conflict
            characters = list(state.characters.values())

            conflict_structure = {
                "main_conflicts": [],
                "conflict_interconnections": [],
                "intensity_arc": intensity_arc
            }

            # Generate conflicts based on type
            for conflict_type in conflict_types:
                conflict_info = self._generate_conflict_info(conflict_type, characters, state.genre)
                conflict_structure["main_conflicts"].append(conflict_info)

                # Generate resolution points
                for i in range(1, state.target_chapter_count + 1 if state.target_chapter_count > 0 else 6):
                    intensity = self._calculate_conflict_intensity(intensity_arc, i, conflict_type, state.target_chapter_count)
                    if intensity > 0.3:  # Only add when intensity is significant
                        conflict_structure["conflict_interconnections"].append({
                            "chapter": i,
                            "conflict_type": conflict_type,
                            "intensity": intensity,
                            "resolution_step": f"Develop tension around {conflict_type} conflict"
                        })

            return {
                "status": "success",
                "message": f"Conflict structure designed with {len(conflict_structure['main_conflicts'])} main conflicts",
                "conflict_structure": conflict_structure
            }

        except Exception as e:
            return {"status": "error", "message": f"Error designing conflict structure: {str(e)}"}

    def _generate_plot_title_inciting_incident(self) -> str:
        return "Inciting Incident"

    def _generate_plot_title_rising_action(self) -> str:
        return "Rising Action"

    def _generate_plot_title_climax(self) -> str:
        return "Climax"

    def _generate_plot_title_resolution(self) -> str:
        return "Resolution"

    def _generate_plot_description(self, plot_type: str, genre: str, themes: List[str]) -> str:
        """Generate a description for a plot point based on type, genre, and themes"""
        descriptions = {
            "inciting_incident": f"The initial event that sets the story in motion within the {genre} setting, introducing the main conflict related to {', '.join(themes)}",
            "rising_action": f"Events that develop the conflict and tension related to {genre}, building on the themes of {', '.join(themes)}",
            "climax": f"The most intense moment of the story in {genre}, where the main conflicts tied to {', '.join(themes)} reach their peak",
            "resolution": f"The conclusion of the main conflicts in {genre}, resolving the central concerns about {', '.join(themes)}"
        }
        return descriptions.get(plot_type, f"A pivotal moment in the {genre} story concerning the themes of {', '.join(themes)}")

    def _generate_consequences(self, plot_type: str) -> List[str]:
        """Generate consequences for a plot point based on its type"""
        consequence_sets = {
            "inciting_incident": ["Sets main plot in motion", "Establishes stakes", "Introduces key conflicts"],
            "rising_action": ["Develops character arcs", "Increases tension", "Advances subplots"],
            "climax": ["Resolve main conflict", "Character transformation", "High stakes resolution"],
            "resolution": ["Tie up loose ends", "Character growth conclusion", "Set up possible sequel"]
        }
        return consequence_sets.get(plot_type, ["Advances the story", "Develops characters", "Sets up next events"])

    def _get_plot_type_importance(self, plot_type: str) -> str:
        """Get the importance level of a plot type"""
        importance_map = {
            "inciting_incident": "high",
            "climax": "high",
            "resolution": "high",
            "rising_action": "medium"
        }
        return importance_map.get(plot_type, "medium")

    def _create_char_entity(self, char: Character):
        """Helper to create a knowledge base entity from a character"""
        from src.core.knowledge_base import KnowledgeEntity
        # Process relationships to ensure they are simple strings
        simple_relationships = []
        if char.relationships:
            # Convert relationships to string format (keys only)
            if isinstance(char.relationships, dict):
                simple_relationships = [str(k) for k in char.relationships.keys()]
            elif isinstance(char.relationships, list):
                simple_relationships = [str(item) for item in char.relationships]
            else:
                simple_relationships = [str(char.relationships)]

        # Process metadata to ensure it only contains simple types
        simple_metadata = {}
        if char.metadata:
            for key, value in char.metadata.items():
                # Ensure key is a string
                safe_key = str(key) if key is not None else "unknown_key"
                # Ensure value is a simple type (str, int, float, None)
                if value is None or isinstance(value, (str, int, float)):
                    simple_metadata[safe_key] = value
                elif isinstance(value, (list, tuple)):
                    # Convert list items to strings
                    simple_metadata[safe_key] = [str(item) if item is not None else "null" for item in value]
                elif isinstance(value, dict):
                    # For nested dictionaries, convert to string representation
                    simple_metadata[safe_key] = str(value)
                else:
                    # For any other type, convert to string
                    simple_metadata[safe_key] = str(value)

        return KnowledgeEntity(
            id=char.id,
            name=char.name,
            type="character",
            description=char.description,
            metadata=simple_metadata,
            relationships=simple_relationships
        )

    def _define_character_arc_stages(self, story_type: str, total_chapters: int) -> Dict[str, List]:
        """Define stages of a character arc based on story type"""
        if story_type == "transformation":
            # Three stages: Setup, Conflict, Resolution
            third = max(1, total_chapters // 3)
            return {
                "establishment": [1, 2, 3][:min(3, total_chapters)],
                "conflict_and_growth": list(range(4, 4 + third * 2))[:total_chapters-3 if total_chapters > 3 else 0],
                "resolution": list(range(max(4, total_chapters - 2), total_chapters + 1))
            }
        else:
            # Default structure
            half = max(1, total_chapters // 2)
            return {
                "setup": list(range(1, half + 1)),
                "development": list(range(half + 1, total_chapters + 1))
            }

    def _generate_stage_description(self, character_id: str, stage_name: str, story_type: str) -> str:
        """Generate a description for a character arc stage"""
        descriptors = {
            "establishment": "Establish character's baseline personality and situation",
            "setup": "Introduce character traits and initial goals",
            "conflict_and_growth": "Challenge character beliefs and create growth",
            "development": "Challenge and develop character through obstacles",
            "resolution": "Resolve character's arc with transformation or growth"
        }
        return descriptors.get(stage_name, f"Key moment for character development in {story_type} arc")

    def _determine_pacing(self, progress: float) -> str:
        """Determine pacing type based on progress in story"""
        if progress < 0.2:
            return "establishing"
        elif progress < 0.5:
            return "developing"
        elif progress < 0.8:
            return "intensifying"
        else:
            return "concluding"

    def _determine_story_beat(self, progress: float) -> str:
        """Determine which story beat this chapter should focus on"""
        if progress < 0.1:
            return "hook/inciting incident"
        elif progress < 0.25:
            return "setup/exposition"
        elif progress < 0.4:
            return "rising action/character development"
        elif progress < 0.6:
            return "conflict escalation"
        elif progress < 0.75:
            return "climax preparation"
        elif progress < 0.9:
            return "climax action"
        else:
            return "resolution/conclusion"

    def _determine_character_focus(self, state: StoryState, progress: float) -> str:
        """Determine which character should be focal based on progress"""
        characters = list(state.characters.keys())
        if not characters:
            return ""

        index = int(progress * len(characters)) % len(characters) if len(characters) > 0 else 0
        return characters[index] if index < len(characters) else characters[0]

    def _calculate_chapter_pacing(self, progress: float, pacing_style: str, total_chapters: int, chapter_num: int) -> Dict[str, Any]:
        """Calculate pacing characteristics for a chapter"""
        base_intensity = {
            "slow_burn": 0.3,
            "balanced": 0.5,
            "fast_paced": 0.8
        }.get(pacing_style, 0.5)

        # Adjust for story position
        if progress < 0.3:
            intensity_multiplier = 0.7  # Lower for beginning
        elif progress < 0.7:
            intensity_multiplier = 1.0  # Standard in middle
        else:
            intensity_multiplier = 1.2  # Higher for ending

        # Calculate intensity
        intensity = min(1.0, base_intensity * intensity_multiplier)

        # Determine focus based on intensity and story position
        if intensity < 0.4:
            focus = "character_development/exposition"
        elif intensity < 0.7:
            focus = "character_development/planning/action"
        else:
            focus = "action/conflict/plot_advancement"

        # Determine action-dialogue-exposition ratios
        if "action" in focus:
            action_ratio = 0.6
            dialogue_ratio = 0.25
            exposition_ratio = 0.15
        elif "character" in focus:
            action_ratio = 0.3
            dialogue_ratio = 0.5
            exposition_ratio = 0.2
        else:
            action_ratio = 0.4
            dialogue_ratio = 0.3
            exposition_ratio = 0.3

        return {
            "intensity": round(intensity, 2),
            "focus": focus,
            "action_dialogue_ratio": f"{action_ratio:.0%} action, {dialogue_ratio:.0%} dialogue, {exposition_ratio:.0%} exposition",
            "exposition_level": "high" if exposition_ratio > 0.3 else "medium" if exposition_ratio > 0.15 else "low"
        }

    def _generate_conflict_info(self, conflict_type: str, characters: List[Character], genre: str) -> Dict[str, Any]:
        """Generate information for a given conflict type"""
        return {
            "type": conflict_type,
            "description": f"{conflict_type} conflict appropriate for {genre} genre",
            "connected_characters": [c.id for c in characters[:2]] if characters else [],
            "severity": "medium",
            "resolvability": True
        }

    def _calculate_conflict_intensity(self, arc_type: str, chapter_num: int, conflict_type: str, total_chapters: int) -> float:
        """Calculate the intensity of a conflict at a given chapter"""
        if arc_type == "escalating":
            if total_chapters > 0:
                return min(1.0, chapter_num / total_chapters)
            else:
                return 0.3  # Default to medium if no total is known
        elif arc_type == "oscillating":
            # Create an oscillating pattern
            cycle = 4  # Oscillate every 4 chapters
            pos = (chapter_num - 1) % cycle
            if pos in [0, 3]:
                return 0.3  # Lower intensity
            else:
                return 0.7  # Higher intensity
        else:  # steady
            return 0.5  # Constant medium intensity

    def _generate_story_structure(self, story_type: str, target_chapters: int) -> List[Dict[str, Any]]:
        """Generate the overall story structure in acts."""
        if story_type.lower() == "three_act":
            chapters_per_act = target_chapters // 3
            remaining = target_chapters % 3

            acts = [
                {
                    "name": "Setup",
                    "chapter_range": f"1-{chapters_per_act}",
                    "focus": "Character introduction, world building, initial conflict presentation",
                    "key_elements": "Character motivation, world rules, inciting incident, initial obstacles"
                },
                {
                    "name": "Confrontation",
                    "chapter_range": f"{chapters_per_act+1}-{chapters_per_act*2 + (1 if remaining > 0 else 0)}",
                    "focus": "Conflict escalation, character development, complications",
                    "key_elements": "Rising action, deepening conflict, character growth, plot complications"
                },
                {
                    "name": "Resolution",
                    "chapter_range": f"{chapters_per_act*2 + (1 if remaining > 0 else 0) + 1}-{target_chapters}",
                    "focus": "Climax, crisis, resolution, character transformation",
                    "key_elements": "Climactic confrontation, main conflict resolution, character change, new equilibrium"
                }
            ]
        else:
            # Default 2-part structure for non-three-act stories
            midpoint = target_chapters // 2
            acts = [
                {
                    "name": "Setup and Rising Action",
                    "chapter_range": f"1-{midpoint}",
                    "focus": "Establish story elements and build tension",
                    "key_elements": "Characters, setting, initial conflict, building stakes"
                },
                {
                    "name": "Climax and Resolution",
                    "chapter_range": f"{midpoint+1}-{target_chapters}",
                    "focus": "Confrontation and concluding the narrative",
                    "key_elements": "Major confrontation, final obstacles, story conclusion"
                }
            ]

        return acts