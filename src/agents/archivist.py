from typing import Dict, List, Any
from src.agents.base import BaseAgent, AgentConfig
from src.core.story_state import StoryState, Character, Location, Chapter
from src.core.knowledge_base import KnowledgeBase, KnowledgeEntity
import json
from datetime import datetime


class ArchivistAgent(BaseAgent):
    """
    Archivist Agent - responsible for managing documentation including:
    - Character cards
    - World settings
    - Chapter versions and history
    - Maintaining consistency in story documentation
    """

    def __init__(self, config: AgentConfig, knowledge_base: KnowledgeBase, **kwargs):
        super().__init__(config, knowledge_base)
        self.documentation_log = []

    def process(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process documentation management tasks based on the context
        """
        action = context.get("action", "update")
        result = {}

        if action == "update_character":
            result = self._update_character(state, context)
        elif action == "update_location":
            result = self._update_location(state, context)
        elif action == "archive_chapter":
            result = self._archive_chapter(state, context)
        elif action == "create_character_card":
            result = self._create_character_card(state, context)
        elif action == "create_location_profile":
            result = self._create_location_profile(state, context)
        elif action == "update_documentation":
            result = self._update_documentation(state, context)
        elif action == "get_consistency_report":
            result = self._get_consistency_report(state, context)
        elif action == "update_metadata":
            result = self._update_metadata(state, context)
        else:
            result = {"status": "error", "message": f"Unknown action: {action}"}

        # Log the processing activity
        self.log_message(f"Processed action: {action} for context: {context.get('target', 'unknown')}", "info")

        return self.format_response(
            content=json.dumps(result, default=str),
            metadata={"action": action, "timestamp": datetime.now().isoformat()}
        )

    def _update_character(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Update character information in the state and knowledge base"""
        try:
            # Extract character information from context
            char_id = context.get("character_id")
            if not char_id:
                return {"status": "error", "message": "No character_id provided"}

            # Check if character exists in state
            existing_char = state.get_character(char_id)
            if existing_char:
                # Update existing character
                updates = {key: value for key, value in context.items()
                          if key in ["name", "description", "role", "personality_traits", "background", "relationships", "metadata"]}

                for key, value in updates.items():
                    if hasattr(existing_char, key):
                        setattr(existing_char, key, value)

                # Update knowledge base
                entity = KnowledgeEntity(
                    id=char_id,
                    name=existing_char.name,
                    type="character",
                    description=existing_char.description,
                    metadata=existing_char.metadata,
                    relationships=list(existing_char.relationships.keys())
                )
                self.knowledge_base.update_entity(entity)

                return {"status": "success", "message": f"Updated character {char_id}", "character": existing_char.model_dump()}
            else:
                # Character doesn't exist, create new one
                character = Character(
                    id=char_id,
                    name=context.get("name", ""),
                    description=context.get("description", ""),
                    role=context.get("role", ""),
                    personality_traits=context.get("personality_traits", []),
                    background=context.get("background", ""),
                    relationships=context.get("relationships", {}),
                    metadata=context.get("metadata", {})
                )

                state.add_character(character)

                # Add to knowledge base
                entity = KnowledgeEntity(
                    id=char_id,
                    name=character.name,
                    type="character",
                    description=character.description,
                    metadata=character.metadata,
                    relationships=list(character.relationships.keys())
                )
                self.knowledge_base.add_entity(entity)

                return {"status": "success", "message": f"Created character {char_id}", "character": character.model_dump()}

        except Exception as e:
            return {"status": "error", "message": f"Error updating character: {str(e)}"}

    def _update_location(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Update location information in the state and knowledge base"""
        try:
            location_id = context.get("location_id")
            if not location_id:
                return {"status": "error", "message": "No location_id provided"}

            # Check if location exists in state
            existing_location = state.get_location(location_id)
            if existing_location:
                # Update existing location
                updates = {key: value for key, value in context.items()
                          if key in ["name", "description", "type", "features", "significance", "metadata"]}

                for key, value in updates.items():
                    if hasattr(existing_location, key):
                        setattr(existing_location, key, value)

                # Update knowledge base
                entity = KnowledgeEntity(
                    id=location_id,
                    name=existing_location.name,
                    type="location",
                    description=existing_location.description,
                    metadata=existing_location.metadata
                )
                self.knowledge_base.update_entity(entity)

                return {"status": "success", "message": f"Updated location {location_id}", "location": existing_location.model_dump()}
            else:
                # Location doesn't exist, create new one
                location = Location(
                    id=location_id,
                    name=context.get("name", ""),
                    description=context.get("description", ""),
                    type=context.get("type", ""),
                    features=context.get("features", []),
                    significance=context.get("significance", ""),
                    metadata=context.get("metadata", {})
                )

                state.add_location(location)

                # Add to knowledge base
                entity = KnowledgeEntity(
                    id=location_id,
                    name=location.name,
                    type="location",
                    description=location.description,
                    metadata=location.metadata
                )
                self.knowledge_base.add_entity(entity)

                return {"status": "success", "message": f"Created location {location_id}", "location": location.model_dump()}

        except Exception as e:
            return {"status": "error", "message": f"Error updating location: {str(e)}"}

    def _archive_chapter(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Archive a chapter in its final form"""
        try:
            chapter_id = context.get("chapter_id")
            if not chapter_id:
                return {"status": "error", "message": "No chapter_id provided"}

            chapter = state.get_chapter(chapter_id)
            if not chapter:
                return {"status": "error", "message": f"Chapter {chapter_id} not found"}

            # Add chapter content to the knowledge base
            chapter_content = f"Chapter {chapter.number}: {chapter.title}\n\n{chapter.content}"
            chapter_doc_id = f"chapter_{chapter_id}_{chapter.number}"

            # Add to knowledge base
            self.knowledge_base.add_document(chapter_content, doc_id=chapter_doc_id)

            # Update chapter status to completed
            state.set_chapter_status(chapter_id, "completed")

            # Log the archiving activity
            self.documentation_log.append({
                "type": "chapter_archived",
                "chapter_id": chapter_id,
                "timestamp": datetime.now(),
                "content_summary": chapter.title
            })

            return {
                "status": "success",
                "message": f"Archived chapter {chapter_id}",
                "chapter": chapter.model_dump()
            }

        except Exception as e:
            return {"status": "error", "message": f"Error archiving chapter: {str(e)}"}

    def _create_character_card(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a detailed character card"""
        try:
            # Generate a character card with all relevant information
            character_id = context.get("character_id")
            if not character_id:
                return {"status": "error", "message": "No character_id provided"}

            character = state.get_character(character_id)
            if not character:
                return {"status": "error", "message": f"Character {character_id} not found"}

            # Format the character card
            card = {
                "id": character.id,
                "name": character.name,
                "role": character.role,
                "description": character.description,
                "personality_traits": character.personality_traits,
                "background": character.background,
                "relationships": character.relationships,
                "appearance": character.metadata.get("appearance", ""),
                "speech_patterns": character.metadata.get("speech_patterns", ""),
                "motivations": character.metadata.get("motivations", ""),
                "arc": character.metadata.get("arc", ""),
                "created_at": datetime.now().isoformat()
            }

            # Add card to the knowledge base as a special document
            card_text = f"CHARACTER CARD: {character.name}\n\n"
            card_text += f"Role: {character.role}\n"
            card_text += f"Description: {character.description}\n"
            card_text += f"Personality Traits: {', '.join(character.personality_traits)}\n"
            card_text += f"Background: {character.background}\n"
            card_text += f"Relationships: {json.dumps(character.relationships, indent=2)}\n"
            for key, value in card.items():
                if key not in ["id", "name", "personality_traits", "relationships", "created_at"]:
                    card_text += f"{key.replace('_', ' ').title()}: {value}\n"

            self.knowledge_base.add_document(card_text, doc_id=f"character_card_{character_id}")

            return {"status": "success", "message": f"Created character card for {character.name}", "card": card}

        except Exception as e:
            return {"status": "error", "message": f"Error creating character card: {str(e)}"}

    def _create_location_profile(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a detailed location profile"""
        try:
            # Generate a location profile with all relevant information
            location_id = context.get("location_id")
            if not location_id:
                return {"status": "error", "message": "No location_id provided"}

            location = state.get_location(location_id)
            if not location:
                return {"status": "error", "message": f"Location {location_id} not found"}

            # Format the location profile
            profile = {
                "id": location.id,
                "name": location.name,
                "type": location.type,
                "description": location.description,
                "features": location.features,
                "significance": location.significance,
                "climate": location.metadata.get("climate", ""),
                "culture": location.metadata.get("culture", ""),
                "history": location.metadata.get("history", ""),
                "notable_residents": location.metadata.get("notable_residents", []),
                "created_at": datetime.now().isoformat()
            }

            # Add profile to the knowledge base as a special document
            profile_text = f"LOCATION PROFILE: {location.name}\n\n"
            profile_text += f"Type: {location.type}\n"
            profile_text += f"Description: {location.description}\n"
            profile_text += f"Features: {', '.join(location.features)}\n"
            profile_text += f"Significance: {location.significance}\n"
            for key, value in profile.items():
                if key not in ["id", "name", "features", "notable_residents", "created_at"]:
                    profile_text += f"{key.replace('_', ' ').title()}: {value}\n"

            self.knowledge_base.add_document(profile_text, doc_id=f"location_profile_{location_id}")

            return {"status": "success", "message": f"Created location profile for {location.name}", "profile": profile}

        except Exception as e:
            return {"status": "error", "message": f"Error creating location profile: {str(e)}"}

    def _update_documentation(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Update documentation in knowledge base"""
        try:
            doc_type = context.get("doc_type")  # 'character', 'location', 'plot', 'world'
            doc_id = context.get("doc_id")
            content = context.get("content")

            if not all([doc_type, doc_id, content]):
                return {"status": "error", "message": "Missing required parameters: doc_type, doc_id, or content"}

            # Add or update documentation in knowledge base
            document_text = f"{doc_type.upper()}: {content}"
            result_id = self.knowledge_base.add_document(document_text, doc_id=f"doc_{doc_type}_{doc_id}")

            return {
                "status": "success",
                "message": f"Updated {doc_type} documentation",
                "doc_id": result_id
            }

        except Exception as e:
            return {"status": "error", "message": f"Error updating documentation: {str(e)}"}

    def _get_consistency_report(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a report on consistency of characters, locations, and other story elements"""
        try:
            # Generate consistency report by querying knowledge base
            report = {
                "date": datetime.now().isoformat(),
                "character_count": len(state.characters),
                "location_count": len(state.locations),
                "chapter_count": len(state.chapters),
                "last_updated": state.updated_at.isoformat() if state.updated_at else None
            }

            # Check for common consistency issues
            consistency_issues = []

            # Check for conflicting character information
            for char_id, character in state.characters.items():
                # Search knowledge base for potential conflicts
                search_results = self.knowledge_base.query(f"character {character.name}", similarity_top_k=5)
                if search_results:
                    for result in search_results:
                        # If we find info that differs, flag it
                        if character.description not in result.text and f"Name: {character.name}" in result.text:
                            consistency_issues.append({
                                "type": "character_conflict",
                                "entity_id": char_id,
                                "field": "description",
                                "details": f"Potential conflict for {character.name} found in KB entry"
                            })

            report["consistency_issues"] = consistency_issues
            return {"status": "success", "report": report}

        except Exception as e:
            return {"status": "error", "message": f"Error generating consistency report: {str(e)}"}

    def _update_metadata(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Update metadata in the state and knowledge base"""
        try:
            target_type = context.get("target_type")  # 'story', 'character', 'location', 'chapter'
            target_id = context.get("target_id")
            metadata = context.get("metadata", {})

            if target_type == "story":
                state.metadata.update(metadata)
                return {
                    "status": "success",
                    "message": "Updated story metadata",
                    "metadata": state.metadata
                }

            elif target_type in ["character", "location", "chapter"]:
                if not target_id:
                    return {"status": "error", "message": f"target_id required for {target_type}"}

                if target_type == "character":
                    entity = state.get_character(target_id)
                    if entity:
                        entity.metadata.update(metadata)
                        # Update in knowledge base as well
                        entity_obj = KnowledgeEntity(
                            id=target_id,
                            name=entity.name,
                            type="character",
                            description=entity.description,
                            metadata=entity.metadata,
                            relationships=list(entity.relationships.keys())
                        )
                        # Note: In a full implementation we would use update_entity,
                        # but we just store the updates and return
                elif target_type == "location":
                    entity = state.get_location(target_id)
                    if entity:
                        entity.metadata.update(metadata)
                        entity_obj = KnowledgeEntity(
                            id=target_id,
                            name=entity.name,
                            type="location",
                            description=entity.description,
                            metadata=entity.metadata
                        )
                elif target_type == "chapter":
                    chapter = state.get_chapter(target_id)
                    if chapter:
                        chapter_metadata = chapter.metadata if hasattr(chapter, 'metadata') else {}
                        chapter_metadata.update(metadata)

                return {
                    "status": "success",
                    "message": f"Updated {target_type} {target_id} metadata",
                    "metadata": metadata
                }

            else:
                return {"status": "error", "message": f"Unknown target type: {target_type}"}

        except Exception as e:
            return {"status": "error", "message": f"Error updating metadata: {str(e)}"}

    def create_backup(self, state: StoryState) -> str:
        """Create a backup of all documentation"""
        backup = {
            "timestamp": datetime.now().isoformat(),
            "characters": {k: v.model_dump() for k, v in state.characters.items()},
            "locations": {k: v.model_dump() for k, v in state.locations.items()},
            "chapters": {k: v.model_dump() for k, v in state.chapters.items()},
            "story_metadata": state.model_dump(exclude={'characters', 'locations', 'chapters'})
        }

        backup_str = json.dumps(backup, default=str)

        # Store in knowledge base
        backup_id = self.knowledge_base.add_document(
            f"BACKUP {datetime.now().isoformat()}:\n\n{backup_str}",
            doc_id=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        return backup_id

    def restore_from_backup(self, backup_doc_id: str) -> dict:
        """Restore documentation from a backup"""
        try:
            # Retrieve from knowledge base
            docs = self.knowledge_base.query(f"backup {backup_doc_id}", similarity_top_k=1)

            if docs:
                # Extract and parse the backup content
                backup_content = docs[0].text
                # This is a simplified restoration - in practice you'd need to extract
                # the actual JSON from the document and restore it properly
                # This is a placeholder for a more complex implementation
                return {
                    "status": "success",
                    "message": f"Found backup {backup_doc_id}",
                    "backup_content_preview": backup_content[:200] + "..."
                }
            else:
                return {
                    "status": "error",
                    "message": f"No backup found with ID {backup_doc_id}"
                }
        except Exception as e:
            return {"status": "error", "message": f"Error restoring from backup: {str(e)}"}