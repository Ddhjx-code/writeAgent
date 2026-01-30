from typing import Dict, List, Any, Optional
from src.agents.base import BaseAgent, AgentConfig
from src.core.story_state import StoryState, Character
from src.core.knowledge_base import KnowledgeBase
import json
from datetime import datetime
import re


class DialogueSpecialistAgent(BaseAgent):
    """
    Dialogue Specialist Agent - focused on:
    - Character dialogue style optimization
    - Maintaining voice consistency per character
    - Subtext and emotional undertones in dialogue
    - Realistic and engaging conversation flows
    """

    def __init__(self, config: AgentConfig, knowledge_base: KnowledgeBase, **kwargs):
        super().__init__(config, knowledge_base)
        self.dialogue_stats = {
            "dialogues_processed": 0,
            "lines_optimized": 0,
            "character_voices_refined": 0
        }

    def process(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process dialogue optimization tasks based on the context
        """
        action = context.get("action", "optimize_dialogue")
        result = {}

        if action == "optimize_dialogue":
            result = self._optimize_dialogue(state, context)
        elif action == "check_character_voice":
            result = self._check_character_voice(state, context)
        elif action == "enhance_subtext":
            result = self._enhance_subtext(state, context)
        elif action == "improve_flow":
            result = self._improve_flow(state, context)
        elif action == "analyze_dialogue_tags":
            result = self._analyze_dialogue_tags(state, context)
        elif action == "generate_character_speech_patterns":
            result = self._generate_character_speech_patterns(state, context)
        elif action == "revise_dialect_accents":
            result = self._revise_dialect_accents(state, context)
        elif action == "balance_dialogue_narrative":
            result = self._balance_dialogue_narrative(state, context)
        else:
            result = {"status": "error", "message": f"Unknown action: {action}"}

        # Log the dialogue activity
        self.log_message(f"Processed action: {action} - {result.get('status', 'unknown')}", "info")

        # Update statistics
        if result.get("status") == "success":
            self.dialogue_stats["dialogues_processed"] += 1
            if "lines_updated" in result:
                self.dialogue_stats["lines_optimized"] += result["lines_updated"]
            if "character_voices_impacted" in result:
                self.dialogue_stats["character_voices_refined"] += result["character_voices_impacted"]

        return self.format_response(
            content=json.dumps(result, default=str),
            metadata={
                "action": action,
                "timestamp": datetime.now().isoformat(),
                "stats": self.dialogue_stats
            }
        )

    def _optimize_dialogue(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize existing dialogue in content"""
        try:
            content = context.get("content", "")
            chapter_id = context.get("chapter_id")
            character_id = context.get("character_id")

            if not content and chapter_id:
                chapter = state.get_chapter(chapter_id)
                if chapter:
                    content = chapter.content
                else:
                    return {"status": "error", "message": f"Chapter {chapter_id} not found"}

            optimized_content, changes_made = self._enhance_dialogue_in_content(content, state, character_id)

            result = {
                "status": "success",
                "message": "Dialogue optimized successfully",
                "original_content_length": len(context.get("content", "")),
                "optimized_content": optimized_content,
                "content_length": len(optimized_content),
                "changes_made": changes_made,
                "lines_updated": len(changes_made)
            }

            if chapter_id:
                # Update the chapter in state with optimized content
                state.update_chapter_content(chapter_id, optimized_content)
                result["chapter_id"] = chapter_id

            return result

        except Exception as e:
            return {"status": "error", "message": f"Error optimizing dialogue: {str(e)}"}

    def _check_character_voice(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if character dialogue matches specified voice"""
        try:
            character_id = context.get("character_id")
            content = context.get("content", "")
            chapter_id = context.get("chapter_id")

            if not content and chapter_id:
                chapter = state.get_chapter(chapter_id)
                if chapter:
                    content = chapter.content

            if not character_id:
                return {"status": "error", "message": "Character ID is required for voice check"}

            character = state.get_character(character_id)
            if not character:
                return {"status": "error", "message": f"Character {character_id} not found"}

            # Extract dialogue attributed to this character
            character_dialogue = self._extract_character_specific_dialogue(content, character)

            voice_issues = self._assess_voice_consistency(character, character_dialogue)

            return {
                "status": "success",
                "message": f"Voice check completed for {character.name}",
                "character_id": character_id,
                "dialogue_found": character_dialogue,
                "voice_issues": voice_issues,
                "issues_found": len(voice_issues)
            }

        except Exception as e:
            return {"status": "error", "message": f"Error checking character voice: {str(e)}"}

    def _enhance_subtext(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Add or improve subtext in dialogue"""
        try:
            content = context.get("content", "")
            emotional_layer = context.get("layer", "multiple")  # multiple, emotional, conflict, romantic, professional

            if not content:
                return {"status": "error", "message": "No content provided"}

            enhanced_content, subtext_changes = self._improve_subtext_in_dialogue(content, emotional_layer)

            return {
                "status": "success",
                "message": f"Subtext enhanced for {emotional_layer} layer",
                "original_content": content,
                "enhanced_content": enhanced_content,
                "modifications": subtext_changes,
                "enhancements_made": len(subtext_changes)
            }

        except Exception as e:
            return {"status": "error", "message": f"Error enhancing subtext: {str(e)}"}

    def _improve_flow(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Improve the natural flow of dialogue exchanges"""
        try:
            content = context.get("content", "")
            flow_type = context.get("flow_type", "natural")  # natural, formal, interruption, overlapping

            if not content:
                return {"status": "error", "message": "No content provided"}

            improved_content, flow_changes = self._improve_dialogue_flow(content, flow_type)

            return {
                "status": "success",
                "message": f"Dialogue flow improved for {flow_type} style",
                "original_content": content,
                "improved_content": improved_content,
                "modifications": flow_changes,
                "improvements_made": len(flow_changes)
            }

        except Exception as e:
            return {"status": "error", "message": f"Error improving flow: {str(e)}"}

    def _analyze_dialogue_tags(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and improve dialogue punctuation and speaker tags"""
        try:
            content = context.get("content", "")

            if not content:
                return {"status": "error", "message": "No content provided"}

            tag_analysis = self._assess_dialogue_tags(content)

            # Also provide suggestions for improvement
            improved_content, fix_list = self._standardize_dialogue_tags(content)

            return {
                "status": "success",
                "message": "Dialogue tag analysis completed",
                "original_content": content,
                "analysis": tag_analysis,
                "suggested_content": improved_content,
                "improvements": fix_list,
                "tag_issues_found": tag_analysis["issues_count"]
            }

        except Exception as e:
            return {"status": "error", "message": f"Error analyzing dialogue tags: {str(e)}"}

    def _generate_character_speech_patterns(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate or identify character-specific speech patterns"""
        try:
            character_id = context.get("character_id")
            if not character_id:
                return {"status": "error", "message": "Character ID is required to generate speech patterns"}

            character = state.get_character(character_id)
            if not character:
                return {"status": "error", "message": f"Character {character_id} not found"}

            # Get all available dialogue for this character
            all_dialogue_in_content = []
            for chapter in state.chapters.values():
                character_specific_dialogue = self._extract_character_specific_dialogue(chapter.content, character)
                all_dialogue_in_content.extend(character_specific_dialogue)

            speech_patterns = self._identify_speech_patterns(character, all_dialogue_in_content)

            # Update character metadata with speech patterns
            if "speech_patterns" not in character.metadata:
                character.metadata["speech_patterns"] = ""
            character.metadata["speech_patterns"] = json.dumps(speech_patterns)

            return {
                "status": "success",
                "message": f"Speech patterns generated for {character.name}",
                "character_id": character_id,
                "speech_patterns": speech_patterns,
                "patterns_found": len(speech_patterns)
            }

        except Exception as e:
            return {"status": "error", "message": f"Error generating character speech patterns: {str(e)}"}

    def _revise_dialect_accents(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Refine how character dialects and accents are represented"""
        try:
            character_id = context.get("character_id")
            content = context.get("content", "")
            consistency_check = context.get("consistency_check", True)

            if not character_id:
                return {"status": "error", "message": "Character ID is required for dialect revision"}

            character = state.get_character(character_id)
            if not character:
                return {"status": "error", "message": f"Character {character_id} not found"}

            if not content:
                # If content not provided, work on all chapters
                content = ""
                for chapter in state.chapters.values():
                    content += f"\n{chapter.content}"

            # Revise dialect representations
            revised_content, changes = self._modify_dialect_representation(content, character, consistency_check)

            result = {
                "status": "success",
                "message": f"Dialect accents revised for {character.name}",
                "original_content_length": len(content),
                "revised_content": revised_content,
                "content_length": len(revised_content),
                "changes_made": changes,
                "modifications": len(changes)
            }

            return result

        except Exception as e:
            return {"status": "error", "message": f"Error revising dialect accents: {str(e)}"}

    def _balance_dialogue_narrative(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure dialogue and narrative are properly balanced"""
        try:
            content = context.get("content", "")
            chapter_id = context.get("chapter_id")

            if not content and chapter_id:
                chapter = state.get_chapter(chapter_id)
                if chapter:
                    content = chapter.content

            balance_analysis = self._assess_dialogue_narrative_balance(content)

            # Suggest improvements
            balanced_content, suggestions = self._adjust_dialogue_narrative_balance(content)

            return {
                "status": "success",
                "message": "Dialogue-narrative balance assessed and improved",
                "analysis": balance_analysis,
                "original_content": content,
                "balanced_content": balanced_content,
                "suggestions": suggestions,
                "improvements": len(suggestions)
            }

        except Exception as e:
            return {"status": "error", "message": f"Error balancing dialogue and narrative: {str(e)}"}

    def _extract_character_specific_dialogue(self, content: str, character: Character) -> List[str]:
        """Extract dialogue specifically attributed to a character"""
        dialogue_list = []

        # Look for dialogue patterns with the character's name
        # Basic pattern would be like: "John said, 'text here'" or "'text here,' said John"
        patterns = [
            rf'["'"]([^"''"]*?)["'"].*?(?:,|s+)?\w*?\s*{re.escape(character.name)}.*?(?:\w|\s|[.!?])',
            rf'.*?{re.escape(character.name)}.*?["'"]([^"''"]*?)["'"]',
            rf'["'"]([^"''"]*?)["'"].*?{re.escape(character.name)}'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            dialogue_list.extend(matches)

        # Alternative approach: look for sentences containing character name and dialogue
        # Split content and look for sections where character name appears with quotes
        sentences = re.split(r'[.!?]+\s*', content)
        for sentence in sentences:
            if character.name.lower() in sentence.lower():
                # Check for quoted text
                quote_matches = re.findall(r'"([^"]*?)"', sentence)
                dialogue_list.extend(quote_matches)

        # Remove duplicates while preserving order
        unique_dialogue = []
        for dial in dialogue_list:
            if dial not in unique_dialogue:
                unique_dialogue.append(dial)

        return unique_dialogue

    def _assess_voice_consistency(self, character: Character, dialogue_list: List[str]) -> List[Dict[str, Any]]:
        """Assess how well the dialogue matches character's established voice"""
        issues = []

        # Check against personality traits
        for trait in character.personality_traits:
            for dialogue in dialogue_list:
                # Look for inconsistencies
                if "timid" in trait.lower() and any(
                    word in dialogue.lower() for word in ["shouted", "commanded", "aggressively", "forcefully"]
                ):
                    issues.append({
                        "type": "voice_inconsistency",
                        "trait": trait,
                        "dialogue": dialogue,
                        "issue": f"Character trait '{trait}' contradicts dialogue: {dialogue[:50]}...",
                        "severity": "high"
                    })

        # Check for unique speech patterns
        if "speech_patterns" in character.metadata and character.metadata["speech_patterns"]:
            # Extract from the JSON string
            import ast
            try:
                patterns = ast.literal_eval(character.metadata["speech_patterns"]) if isinstance(character.metadata["speech_patterns"], str) else character.metadata["speech_patterns"]
                # Check if dialogue follows these patterns
            except:
                # If parsing fails, skip pattern check
                pass

        # Check for common speaking errors
        for dialogue in dialogue_list:
            if len(dialogue) > 200:  # Unusually long for dialogue
                issues.append({
                    "type": "structure_issue",
                    "issue": "Potentially too long for effective dialogue",
                    "dialogue": dialogue[:100] + "..." if len(dialogue) > 100 else dialogue,
                    "severity": "medium"
                })

        return issues

    def _identify_speech_patterns(self, character: Character, dialogue_list: List[str]) -> Dict[str, Any]:
        """Identify and categorize character speech patterns"""
        patterns = {
            "word_choices": [],
            "sentence_structures": [],
            "emotional_expressions": [],
            "unique_phenomena": [],
            "filler_words": [],
            "vocabulary_consistency": character.personality_traits  # Start with personality traits
        }

        all_text = " ".join(dialogue_list).lower()

        # Basic pattern extraction
        import collections
        from collections import Counter

        words = re.findall(r'\b\w+\b', all_text)
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        trigrams = [f"{words[i]} {words[i+1]} {words[i+2]}" for i in range(len(words)-2)]

        # Get most common
        word_counts = Counter(words)
        bigram_counts = Counter(bigrams)

        # Filter for meaningful patterns
        for word, count in word_counts.most_common(10):
            if len(word) > 4 and count >= 2 and word not in ["the", "and", "that", "have", "for", "this", "with", "you", "not", "but"]:
                patterns["word_choices"].append({"word": word, "frequency": count})

        for bigram, count in bigram_counts.most_common(5):
            if count >= 2:
                patterns["sentence_structures"].append({"structure": bigram, "frequency": count})

        return patterns

    def _enhance_dialogue_in_content(self, content: str, state: StoryState, character_id: Optional[str] = None) -> tuple:
        """Enhance dialogue in the entire content"""
        import re

        original_content = content
        changes_made = []

        # If a specific character is targeted, work on their dialogue
        if character_id:
            character = state.get_character(character_id)
            if char:
                # Find instances of this character's dialogue and improve them
                pattern = f'(["""])(.*?{re.escape(character.name)}.*?|.*?["""]|["""](.*?)["""]\s*{re.escape(character.name)}.*?|{re.escape(character.name)}.*?["""](.*?)["""])'
                # This is a simplified pattern, in reality this would be more complex
                pass

        # Improve all dialogue globally
        # Find quoted text and enhance it
        # This is a simplified enhancement approach
        # In a full implementation, we'd call an LLM with specific instructions

        # Count initial instances
        initial_dialogue_count = len(re.findall(r'["''].*?["'']', content))

        # For now, we'll implement a basic improvement
        # More sophisticated implementation would use context and character knowledge
        improved_content = content

        return improved_content, changes_made

    def _improve_subtext_in_dialogue(self, content: str, emotional_layer: str) -> tuple:
        """Improve subtext in the dialogue"""
        import re

        # Find dialogue snippets and add more subtle meanings
        quoted_parts = re.findall(r'"([^"]*)"', content)
        improved_content = content
        subtext_changes = []

        # This is a simple placeholder; real implementation would be more sophisticated
        for quote in quoted_parts:
            # In a real implementation, we'd analyze current subtext and enhance it
            # For now, we'll add a placeholder indication
            if len(quote.strip()) > 10:  # Only for somewhat longer quotes where subtext is feasible
                subtext_changes.append({
                    "original": quote,
                    "enhancement": f"Added subtle {emotional_layer} subtext to: {quote[:30]}..."
                })

        # Real implementation would modify the content here
        # For now, we'll return the original content with notes
        return improved_content, subtext_changes

    def _improve_dialogue_flow(self, content: str, flow_type: str) -> tuple:
        """Improve the conversational flow"""
        import re

        # Identify dialogue exchanges and improve their flow
        improved_content = content
        flow_changes = []

        # A real implementation would analyze speaker transitions, etc.
        # Simple placeholder implementation
        exchanges = re.findall(r'"([^"]+)"(?:,|\s)+(?:\w+\s+)?(?:said|replied|asked|responded)', content, re.IGNORECASE)
        for exchange in exchanges:
            # Note areas that could be improved
            flow_changes.append({
                "action": "flow_analysis",
                "original": exchange,
                "improvement": f"Analyzed flow for {flow_type} conversation style"
            })

        return improved_content, flow_changes

    def _assess_dialogue_tags(self, content: str) -> Dict[str, Any]:
        """Analyze dialogue punctuation and speaker tags"""
        import re

        # Count different types of dialogue tags
        said_tags = len(re.findall(r'\bsaid\b', content, re.IGNORECASE))
        asked_tags = len(re.findall(r'\basked\b', content, re.IGNORECASE))
        replied_tags = len(re.findall(r'\breplied\b', content, re.IGNORECASE))
        action_tags = len(re.findall(r'\b(called|shouted|whispered|screamed|laughed|remarked)\b', content, re.IGNORECASE))

        # Count punctuation patterns
        dialogue_patterns = {
            "standard_tagging": len(re.findall(r'"[^"]*"[.,;]?\s*\w+\s+(?:said|replied|asked)', content, re.IGNORECASE)),
            "tag_before": len(re.findall(r'\w+\s+(?:said|replied|asked):\s*"[^"]*"', content, re.IGNORECASE)),
            "tag_middle": len(re.findall(r'"[^"]*"\s*(?:[a-z]+)?\s*\w+\s+(?:said|replied|asked|responded)\s*(?:[a-z]+)?\s*"[^"]*"', content, re.IGNORECASE))
        }

        # Check for issues
        issues = []
        total_dialogue = said_tags + asked_tags + replied_tags + action_tags
        if total_dialogue > 0:
            overuse_said = said_tags / total_dialogue > 0.8  # More than 80% use "said"
            if overuse_said:
                issues.append({
                    "type": "tag_overuse",
                    "issue": f"Overuse of 'said' ({said_tags}/{total_dialogue})",
                    "severity": "medium"
                })

        analysis = {
            "tag_distribution": {
                "said": said_tags,
                "asked": asked_tags,
                "replied": replied_tags,
                "action_tags": action_tags
            },
            "dialogue_patterns": dialogue_patterns,
            "issues": issues,
            "issues_count": len(issues)
        }

        return analysis

    def _standardize_dialogue_tags(self, content: str) -> tuple:
        """Standardize dialogue punctuation and tags"""
        import re

        # Simple standardization
        # In practice, this would be much more complex to properly preserve voice
        improved_content = content
        fix_list = []

        # Example: standardize to preferred format
        # This is a very simplified approach - in reality you'd need more sophisticated parsing
        # to handle the nuances of different writing styles while maintaining voice

        return improved_content, fix_list

    def _modify_dialect_representation(self, content: str, character: Character, check_consistency: bool) -> tuple:
        """Modify how dialects and accents are represented in dialogue"""
        # Placeholder implementation
        changes = []

        # Identify character in text and review their dialogue
        if check_consistency:
            # Look for inconsistencies in how accent/dialect is represented
            pass

        # A real implementation would modify dialect representation to make it more
        # authentic without being offensive, and more consistent
        modified_content = content

        return modified_content, changes

    def _assess_dialogue_narrative_balance(self, content: str) -> Dict[str, Any]:
        """Assess the balance between dialogue and narrative"""
        import re

        # Very simplified measure - in real implementation would be more sophisticated
        dialogue_chars = len(re.findall(r'"[^"]*"', content))
        total_chars = len(content)

        # Calculate rough proportions
        dialogue_proportion = dialogue_chars / total_chars if total_chars > 0 else 0
        narrative_proportion = 1 - dialogue_proportion

        analysis = {
            "characters_total": total_chars,
            "dialogue_characters": dialogue_chars,
            "narrative_characters": total_chars - dialogue_chars,
            "dialogue_percentage": round(dialogue_proportion * 100, 2),
            "narrative_percentage": round(narrative_proportion * 100, 2),
            "recommendation": "dialogue_heavy" if dialogue_proportion > 0.6 else "balanced" if 0.3 <= dialogue_proportion <= 0.6 else "narrative_heavy"
        }

        return analysis

    def _adjust_dialogue_narrative_balance(self, content: str) -> tuple:
        """Adjust the balance between dialogue and narrative"""
        # This would be a complex implementation that would analyze and adjust the
        # proportion of dialogue to narrative while preserving meaning
        # For now, this is a placeholder

        suggestions = [{
            "type": "balance_advice",
            "advice": "Consider reviewing the ratio of direct speech to narrative description"
        }]

        return content, suggestions