from typing import Dict, List, Any
from src.agents.base import BaseAgent, AgentConfig
from src.core.story_state import StoryState, Location
from src.core.knowledge_base import KnowledgeBase
import json
from datetime import datetime
import re


class WorldBuilderAgent(BaseAgent):
    """
    World Builder Agent - responsible for:
    - Creating rich scene details and descriptions
    - Enhancing environment and atmosphere
    - Managing consistent world-building elements
    - Providing sensory details for immersion
    """

    def __init__(self, config: AgentConfig, knowledge_base: KnowledgeBase, **kwargs):
        super().__init__(config, knowledge_base)
        self.world_building_stats = {
            "descriptions_added": 0,
            "locations_enhanced": 0,
            "atmosphere_elements_created": 0
        }

    def process(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process world-building tasks based on the context
        """
        action = context.get("action", "enhance_scene")
        result = {}

        if action == "enhance_scene":
            result = self._enhance_scene(state, context)
        elif action == "create_location":
            result = self._create_location(state, context)
        elif action == "enhance_atmosphere":
            result = self._enhance_atmosphere(state, context)
        elif action == "add_sensory_details":
            result = self._add_sensory_details(state, context)
        elif action == "maintain_continuity":
            result = self._maintain_continuity(state, context)
        elif action == "create_envir_description":
            result = self._create_envir_description(state, context)
        elif action == "check_world_coherence":
            result = self._check_world_coherence(state, context)
        elif action == "develop_cultural_elements":
            result = self._develop_cultural_elements(state, context)
        else:
            result = {"status": "error", "message": f"Unknown action: {action}"}

        # Log the world-building activity
        self.log_message(f"Processed action: {action} - {result.get('status', 'unknown')}", "info")

        # Update statistics
        if result.get("status") == "success":
            self.world_building_stats["descriptions_added"] += 1
            if "locations_updated" in result:
                self.world_building_stats["locations_enhanced"] += result["locations_updated"]
            if "atmospheric_elements" in result:
                self.world_building_stats["atmosphere_elements_created"] += result["atmospheric_elements"]

        return self.format_response(
            content=json.dumps(result, default=str),
            metadata={
                "action": action,
                "timestamp": datetime.now().isoformat(),
                "stats": self.world_building_stats
            }
        )

    def _enhance_scene(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance a scene with rich environmental details"""
        try:
            content = context.get("content", "")
            location_id = context.get("location_id")
            chapter_id = context.get("chapter_id")

            if not content and chapter_id:
                chapter = state.get_chapter(chapter_id)
                if chapter:
                    content = chapter.content
                else:
                    return {"status": "error", "message": f"Chapter {chapter_id} not found"}

            # If location is specified, get location details
            location_details = None
            if location_id:
                location = state.get_location(location_id)
                if location:
                    location_details = location

            # Enhance the content with environmental details
            enhanced_content, details_added = self._add_environmental_descriptions(
                content, state, location_details, context.get("sensory_elements", ["visual", "auditory"])
            )

            return {
                "status": "success",
                "message": "Scene enhanced with environmental details",
                "original_content_length": len(context.get("content", "")),
                "enhanced_content": enhanced_content,
                "content_length": len(enhanced_content),
                "details_added": details_added,
                "details_count": len(details_added)
            }

        except Exception as e:
            return {"status": "error", "message": f"Error enhancing scene: {str(e)}"}

    def _create_location(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new location with full descriptive details"""
        try:
            name = context.get("name", "")
            location_type = context.get("type", "general")
            description = context.get("description", "")
            features = context.get("features", [])
            atmosphere = context.get("atmosphere", "")
            cultural_elements = context.get("cultural_elements", [])

            if not name:
                return {"status": "error", "message": "Location name is required"}

            # Create Location object
            location = Location(
                id=f"loc_{len(state.locations) + 1}",
                name=name,
                description=description,
                type=location_type,
                features=features,
                significance=context.get("significance", "background"),
                metadata={
                    "atmosphere": atmosphere,
                    "cultural_elements": cultural_elements,
                    "sensory_elements": context.get("sensory_profile", {}),
                    "historical_significance": context.get("historical_background", ""),
                    "current_events": context.get("current_events", [])
                }
            )

            # Add to state
            location_id = state.add_location(location)

            # Also add to knowledge base
            from src.core.knowledge_base import KnowledgeEntity
            entity = KnowledgeEntity(
                id=location_id,
                name=location.name,
                type="location",
                description=location.description,
                metadata=location.metadata
            )
            self.knowledge_base.add_entity(entity)

            return {
                "status": "success",
                "message": f"Location '{name}' created successfully",
                "location_id": location_id,
                "location": location.model_dump()
            }

        except Exception as e:
            return {"status": "error", "message": f"Error creating location: {str(e)}"}

    def _enhance_atmosphere(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance the atmospheric elements of content or setting"""
        try:
            content = context.get("content", "")
            location_id = context.get("location_id")
            mood = context.get("mood", "neutral")  # ominous, cheerful, mysterious, tense, etc.
            weather = context.get("weather", None)  # Weather condition to incorporate

            if location_id:
                location = state.get_location(location_id)
                if not location:
                    return {"status": "error", "message": f"Location {location_id} not found"}

            # Apply atmospheric enhancement based on mood
            enhanced_content, atmosphere_changes = self._apply_atmospheric_mood(
                content, mood, weather, context.get("intensity", "moderate")
            )

            return {
                "status": "success",
                "message": f"Atmosphere enhanced with {mood} mood",
                "original_content": content,
                "enhanced_content": enhanced_content,
                "atmospheric_changes": atmosphere_changes,
                "mood_applied": mood
            }

        except Exception as e:
            return {"status": "error", "message": f"Error enhancing atmosphere: {str(e)}"}

    def _add_sensory_details(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Add rich sensory details to content"""
        try:
            content = context.get("content", "")
            location_id = context.get("location_id")
            sensory_focus = context.get("sensory_elements", ["visual", "auditory", "tactile"])

            # Get location context if available
            location_context = None
            if location_id:
                location = state.get_location(location_id)
                if location:
                    location_context = location

            # Add sensory details
            enhanced_content, sensory_additions = self._insert_sensory_details(
                content, sensory_focus, location_context
            )

            return {
                "status": "success",
                "message": f"Sensory details added for {', '.join(sensory_focus)}",
                "original_content": content,
                "enhanced_content": enhanced_content,
                "sensory_additions": sensory_additions,
                "additions_count": len(sensory_additions)
            }

        except Exception as e:
            return {"status": "error", "message": f"Error adding sensory details: {str(e)}"}

    def _maintain_continuity(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure world-building continuity across content"""
        try:
            content = context.get("content", "")
            element_type = context.get("element", "location")  # location, object, concept, entity
            element_id = context.get("element_id")

            continuity_issues = self._identify_continuity_issues(content, element_type, element_id, state)

            return {
                "status": "success",
                "message": f"Continuity check completed for {element_type}",
                "continuity_issues": continuity_issues,
                "issues_found": len(continuity_issues)
            }

        except Exception as e:
            return {"status": "error", "message": f"Error maintaining continuity: {str(e)}"}

    def _create_envir_description(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create full environmental description based on context"""
        try:
            location_id = context.get("location_id")
            time_period = context.get("time_period", "day")
            weather_conditions = context.get("weather", "clear")
            season = context.get("season", "spring")

            location = state.get_location(location_id) if location_id else None
            if not location:
                return {"status": "error", "message": f"Location {location_id} not found"}

            # Create rich environmental description
            detailed_description = self._generate_full_environmental_description(
                location, time_period, weather_conditions, season, context
            )

            # Update location with enhanced description
            if "detailed_environment" not in location.metadata:
                location.metadata["detailed_environment"] = {}
            location.metadata["detailed_environment"].update({
                "full_description": detailed_description,
                "time_period": time_period,
                "weather": weather_conditions,
                "season": season
            })

            return {
                "status": "success",
                "message": f"Detailed environmental description created for {location.name}",
                "location_id": location_id,
                "detailed_description": detailed_description,
                "time_period": time_period,
                "weather": weather_conditions
            }

        except Exception as e:
            return {"status": "error", "message": f"Error creating environmental description: {str(e)}"}

    def _check_world_coherence(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check overall coherence of world-building elements"""
        try:
            # Analyze all locations, cultural elements, and world-building aspects
            issues = []
            suggestions = []

            # Check location consistency
            for loc_id, location in state.locations.items():
                # Check for incomplete information
                if not location.description or len(location.description) < 20:
                    issues.append({
                        "type": "detail_missing",
                        "element_id": loc_id,
                        "element_type": "location",
                        "issue": f"Location {location.name} has minimal description",
                        "severity": "medium"
                    })

                # Check metadata consistency
                if "atmosphere" not in location.metadata:
                    suggestions.append({
                        "type": "atmosphere_missing",
                        "element_id": loc_id,
                        "suggestion": f"Consider adding atmospheric details for {location.name}"
                    })

            # Cross-reference character backgrounds with locations
            for char_id, character in state.characters.items():
                if hasattr(character, 'origin_location') and character.origin_location not in state.locations:
                    issues.append({
                        "type": "inconsistency",
                        "element_id": char_id,
                        "element_type": "character",
                        "issue": f"Character {character.name} references missing location: {character.origin_location}",
                        "severity": "high"
                    })

            return {
                "status": "success",
                "message": "World coherence check completed",
                "issues": issues,
                "suggestions": suggestions,
                "issues_count": len(issues),
                "suggestions_count": len(suggestions)
            }

        except Exception as e:
            return {"status": "error", "message": f"Error checking world coherence: {str(e)}"}

    def _develop_cultural_elements(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Develop cultural, social, or historical elements for the world"""
        try:
            element_name = context.get("element_name", "")
            element_type = context.get("type", "cultural")  # cultural, historical, social, political
            related_location = context.get("related_location")

            # Create a cultural element description
            element_description = self._create_world_element(
                element_name, element_type, state, related_location, context
            )

            if related_location:
                # Add to the location's metadata
                location = state.get_location(related_location)
                if location:
                    section = f"{element_type}_aspects"
                    if section not in location.metadata:
                        location.metadata[section] = []
                    location.metadata[section].append({
                        "name": element_name,
                        "description": element_description,
                        "timestamp": datetime.now().isoformat()
                    })

            return {
                "status": "success",
                "message": f"{element_type.title()} element '{element_name}' created",
                "element_name": element_name,
                "element_type": element_type,
                "description": element_description
            }

        except Exception as e:
            return {"status": "error", "message": f"Error developing cultural elements: {str(e)}"}

    def _add_environmental_descriptions(self, content: str, state: StoryState, location_details: Location, sensory_elements: List[str]) -> tuple:
        """Add environmental descriptions to content"""
        # Placeholder implementation - in practice would be implemented with LLM
        enhanced_content = content
        details_added = []

        # Add location-based environmental details if available
        if location_details:
            # Insert environmental context based on location
            intro_text = f"The scene unfolds in {location_details.name} - {location_details.description}. "
            if location_details.features:
                features_str = ", ".join(location_details.features[:3])  # Use first 3 features
                intro_text += f"Key features include: {features_str}. "

            # Only add the intro once at the beginning if not already there
            if content.count(location_details.name) > 0:  # If location is mentioned
                enhanced_content = intro_text + content
                details_added.append({
                    "type": "environmental_context",
                    "description": f"Added context for {location_details.name}",
                    "location": location_details.name
                })

        # Add sensory details based on requested types
        for sensory_type in sensory_elements:
            # Add placeholder for sensory enhancement
            if sensory_type == "visual":
                # Add visual details enhancement
                pass
            elif sensory_type == "auditory":
                # Add sound details enhancement
                pass
            # etc.

        return enhanced_content, details_added

    def _apply_atmospheric_mood(self, content: str, mood: str, weather: str, intensity: str) -> tuple:
        """Apply specific mood and atmosphere to content"""
        changes = []

        # Create mood-appropriate atmospheric modifications
        if mood == "ominous":
            if not weather:
                weather = "storm clouds gathering"
            changes.append("Added ominous atmospheric elements")
        elif mood == "cheerful":
            if not weather:
                weather = "golden sunshine"
            changes.append("Enhanced with cheerful elements")
        elif mood == "mysterious":
            if not weather:
                weather = "thick fog" or "twilight shadows"
            changes.append("Added mysterious atmosphere")
        elif mood == "tense":
            changes.append("Increased tension in atmosphere")

        # In practice, this would modify content with mood-appropriate details
        # The implementation would be more complex, calling an LLM with instructions

        modified_content = content  # Placeholder

        return modified_content, changes

    def _insert_sensory_details(self, content: str, sensory_focus: List[str], location_context: Location) -> tuple:
        """Insert sensory details based on focus and location"""
        sensory_additions = []

        # In practice, we would add specific sensory details to the content
        # For now, returning as is with metadata about what sensory elements we would focus on
        for sense in sensory_focus:
            sensory_additions.append(f"Identified need for more {sense} details")

        return content, sensory_additions

    def _identify_continuity_issues(self, content: str, element_type: str, element_id: str, state: StoryState) -> List[Dict[str, Any]]:
        """Identify continuity issues in world-building"""
        issues = []

        if element_type == "location":
            if element_id and element_id in state.locations:
                location = state.locations[element_id]
                # Check if content describes this location consistently with the saved details
                if not all(feature in content or feature.lower() in content.lower() for feature in location.features):
                    issues.append({
                        "type": "feature_omission",
                        "element_id": element_id,
                        "severity": "low",
                        "issue": f"Location features not fully reflected in current content: {', '.join(location.features)}"
                    })

        # Other continuity checks would go here

        return issues

    def _generate_full_environmental_description(self, location: Location, time_period: str, weather: str, season: str, context: Dict[str, Any]) -> str:
        """Generate a full environmental description for a location"""
        # Create a rich description based on all the parameters
        description_parts = [
            f"{location.name} - Environmental Profile:",
            f"Setting Type: {location.type}",
            f"Basic Description: {location.description}",
            f"Time of Day: {time_period.title()}",
            f"Season: {season.title()}",
            f"Current Weather: {weather}",
            f"Key Features: {', '.join(location.features)}",
        ]

        # Add time-specific details
        if time_period == "night":
            description_parts.append("Under a star-filled sky, shadows deepen and sounds carry differently across the landscape.")
        elif time_period == "dawn":
            description_parts.append("The world awakens with gentle hues and stirring signs of life.")
        else:
            description_parts.append("The scene unfolds in full daylight, with all its details visible and clear.")

        # Add weather-specific details
        if "rain" in weather.lower():
            description_parts.append("The environment is affected by moisture, with surfaces glistening and sounds dampened.")
        elif "sun" in weather.lower():
            description_parts.append("Bright illumination brings out the colors and textures of the surroundings.")

        # Add seasonal details
        vegetation_info = {
            "spring": "New growth emerges, bringing fresh colors and scents to the air.",
            "summer": "Full vegetation provides shade and abundant life sounds.",
            "autumn": "Changing colors indicate the season's transition with crisp air.",
            "winter": "Barren branches and stillness characterize the cooler environment."
        }
        description_parts.append(vegetation_info.get(season.lower(), "The environment shows seasonal characteristics."))

        # Add cultural/historical context from metadata if available
        if "significance" in location.metadata:
            description_parts.append(f"Cultural/Historical Significance: {location.metadata['significance']}")

        return "\n\n".join(description_parts)

    def _create_world_element(self, element_name: str, element_type: str, state: StoryState, related_location: str, context: Dict[str, Any]) -> str:
        """Create a description for a world-building element"""
        # In practice, would create rich description using LLM
        # For now, returning a structured placeholder
        element_parts = [
            f"{element_type.title()} Element: {element_name}",
        ]

        if related_location:
            location = state.get_location(related_location)
            if location:
                element_parts.append(f"Located in: {location.name}")

        # Add context details
        if context.get("purpose", ""):
            element_parts.append(f"Purpose: {context['purpose']}")
        if context.get("inhabitants", ""):
            element_parts.append(f"Inhabitants/Culture: {context['inhabitants']}")
        if context.get("history", ""):
            element_parts.append(f"History: {context['history']}")

        # Add type-specific details
        if element_type == "cultural":
            element_parts.extend([
                "Cultural Significance:",
                "Traditional Practices:",
                "Symbolic Meaning:"
            ])
        elif element_type == "historical":
            element_parts.extend([
                "Historical Time Period:",
                "Major Events:",
                "Legacy Impact:"
            ])
        elif element_type == "social":
            element_parts.extend([
                "Social Structure:",
                "Community Practices:",
                "Interpersonal Dynamics:"
            ])
        elif element_type == "political":
            element_parts.extend([
                "Governance Structure:",
                "Power Dynamics:",
                "Decision-Making Processes:"
            ])

        return "\n".join(element_parts)

    def enhance_existing_location(self, state: StoryState, location_id: str, enhancements: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance an existing location with additional details"""
        try:
            location = state.get_location(location_id)
            if not location:
                return {"status": "error", "message": f"Location {location_id} not found"}

            # Apply enhancements
            for key, value in enhancements.items():
                if key == "description":
                    location.description += f"\n\n{value}"
                elif key == "features":
                    if isinstance(value, list):
                        location.features.extend([f for f in value if f not in location.features])
                    else:
                        location.features.append(value)
                elif key == "metadata":
                    location.metadata.update(value)
                else:
                    # For unknown keys, update accordingly
                    setattr(location, key, value)

            return {
                "status": "success",
                "message": f"Location {location_id} enhanced",
                "location": location.model_dump()
            }

        except Exception as e:
            return {"status": "error", "message": f"Error enhancing location: {str(e)}"}

    def get_location_atmosphere(self, state: StoryState, location_id: str, time_period: str = "day") -> str:
        """Get appropriate atmospheric description for a location at a particular time"""
        location = state.get_location(location_id)
        if not location:
            return "Unknown location"

        # Combine location description with time-appropriate atmosphere
        atmosphere = f"The {time_period} atmosphere of {location.name} is defined by {location.description}."
        if location.features:
            atmosphere += f" Its distinctive features - {', '.join(location.features[:3])} - add to its character."

        return atmosphere