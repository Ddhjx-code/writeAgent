from typing import Dict, List, Any, Optional
from src.agents.base import BaseAgent, AgentConfig
from src.core.story_state import StoryState, Character, Location, Chapter
from src.core.knowledge_base import KnowledgeBase
import json
from datetime import datetime


class ConsistencyCheckerAgent(BaseAgent):
    """
    Consistency Checker Agent - responsible for ensuring:
    - Timeline consistency
    - Character behavior continuity
    - Causal chain integrity
    - World-building coherence
    """

    def __init__(self, config: AgentConfig, knowledge_base: KnowledgeBase, **kwargs):
        super().__init__(config, knowledge_base)
        self.check_stats = {
            "checks_performed": 0,
            "inconsistencies_found": 0,
            "resolutions_applied": 0
        }

    def process(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process consistency checking tasks based on the context
        """
        action = context.get("action", "check_consistency")
        result = {}

        if action == "check_character_consistency":
            result = self._check_character_consistency(state, context)
        elif action == "check_timeline_consistency":
            result = self._check_timeline_consistency(state, context)
        elif action == "check_world_coherence":
            result = self._check_world_coherence(state, context)
        elif action == "check_causal_chains":
            result = self._check_causal_chains(state, context)
        elif action == "check_all_consistencies":
            result = self._check_all_consistencies(state, context)
        elif action == "resolve_inconsistencies":
            result = self._resolve_inconsistencies(state, context)
        elif action == "generate_consistency_report":
            result = self._generate_consistency_report(state, context)
        elif action == "validate_character_actions":
            result = self._validate_character_actions(state, context)
        else:
            result = {"status": "error", "message": f"Unknown action: {action}"}

        # Log the checking activity
        self.log_message(f"Processed action: {action} - {result.get('status', 'unknown')}", "info")

        # Update statistics
        if result.get("status") == "success":
            self.check_stats["checks_performed"] += 1
            if "inconsistencies_found" in result:
                self.check_stats["inconsistencies_found"] += result["inconsistencies_found"]
            if "resolutions_applied" in result:
                self.check_stats["resolutions_applied"] += result.get("resolutions_applied", 0)

        return self.format_response(
            content=json.dumps(result, default=str),
            metadata={
                "action": action,
                "timestamp": datetime.now().isoformat(),
                "stats": self.check_stats
            }
        )

    def _check_character_consistency(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check for character behavior consistency"""
        try:
            character_id = context.get("character_id")
            chapter_id = context.get("chapter_id")

            inconsistencies = []

            # Get the relevant content based on context
            target_content = ""
            chapter = None
            if chapter_id:
                chapter = state.get_chapter(chapter_id)
                if chapter:
                    target_content = chapter.content
            else:
                target_content = context.get("content", "")

            if character_id:
                # Check if this character appears in the content
                character = state.get_character(character_id)
                if not character:
                    return {"status": "error", "message": f"Character {character_id} not found"}

                # Check if character name appears in content
                # In a full implementation we'd analyze behavior, dialog, etc.
                if character.name.lower() in target_content.lower():
                    # Check character consistency for this specific character
                    char_inconsistencies = self._analyze_character_behavior(
                        character, target_content, chapter.location if chapter else None
                    )
                    inconsistencies.extend(char_inconsistencies)

            else:
                # Check all characters in the content
                for char_id, character in state.characters.items():
                    if character.name.lower() in target_content.lower():
                        char_inconsistencies = self._analyze_character_behavior(
                            character, target_content, chapter.location if chapter else None if chapter else None
                        )
                        inconsistencies.extend(char_inconsistencies)

            return {
                "status": "success",
                "message": f"Character consistency check completed",
                "inconsistencies": inconsistencies,
                "inconsistencies_found": len(inconsistencies)
            }

        except Exception as e:
            return {"status": "error", "message": f"Error checking character consistency: {str(e)}"}

    def _check_timeline_consistency(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check for timeline and chronological consistency"""
        try:
            chapter_id = context.get("chapter_id")
            content = context.get("content", "")

            if not content and chapter_id:
                chapter = state.get_chapter(chapter_id)
                if chapter:
                    content = chapter.content
                else:
                    return {"status": "error", "message": f"Chapter {chapter_id} not found"}

            inconsistencies = self._analyze_timeline(content, state)

            return {
                "status": "success",
                "message": "Timeline consistency check completed",
                "inconsistencies": inconsistencies,
                "inconsistencies_found": len(inconsistencies)
            }

        except Exception as e:
            return {"status": "error", "message": f"Error checking timeline consistency: {str(e)}"}

    def _check_world_coherence(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check for world-building consistency"""
        try:
            chapter_id = context.get("chapter_id")
            content = context.get("content", "")

            if not content and chapter_id:
                chapter = state.get_chapter(chapter_id)
                if chapter:
                    content = chapter.content
                else:
                    return {"status": "error", "message": f"Chapter {chapter_id} not found"}

            inconsistencies = self._analyze_world_coherence(content, state)

            return {
                "status": "success",
                "message": "World coherence check completed",
                "inconsistencies": inconsistencies,
                "inconsistencies_found": len(inconsistencies)
            }

        except Exception as e:
            return {"status": "error", "message": f"Error checking world coherence: {str(e)}"}

    def _check_causal_chains(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check logical causal relationships"""
        try:
            chapter_id = context.get("chapter_id")
            content = context.get("content", "")

            if not content and chapter_id:
                chapter = state.get_chapter(chapter_id)
                if chapter:
                    content = chapter.content
                else:
                    return {"status": "error", "message": f"Chapter {chapter_id} not found"}

            causal_issues = self._analyze_causal_chain(content, state)

            return {
                "status": "success",
                "message": "Causal chain check completed",
                "causal_issues": causal_issues,
                "issues_found": len(causal_issues)
            }

        except Exception as e:
            return {"status": "error", "message": f"Error checking causal chains: {str(e)}"}

    def _check_all_consistencies(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform all consistency checks"""
        try:
            results = {}

            # Check character consistency
            char_result = self._check_character_consistency(state, context)
            results["character_consistency"] = char_result

            # Check timeline
            timeline_result = self._check_timeline_consistency(state, context)
            results["timeline_consistency"] = timeline_result

            # Check world coherence
            world_result = self._check_world_coherence(state, context)
            results["world_coherence"] = world_result

            # Check causal chains
            causal_result = self._check_causal_chains(state, context)
            results["causal_chains"] = causal_result

            # Consolidate summary
            total_inconsistencies = (
                char_result.get("inconsistencies_found", 0) +
                timeline_result.get("inconsistencies_found", 0) +
                world_result.get("inconsistencies_found", 0) +
                len(causal_result.get("causal_issues", []))
            )

            return {
                "status": "success",
                "message": f"Comprehensive consistency check completed. Total issues: {total_inconsistencies}",
                "results": results,
                "total_inconsistencies_found": total_inconsistencies
            }

        except Exception as e:
            return {"status": "error", "message": f"Error performing all checks: {str(e)}"}

    def _resolve_inconsistencies(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to resolve identified inconsistencies"""
        try:
            inconsistencies = context.get("inconsistencies", [])
            chapter_id = context.get("chapter_id")

            resolved_count = 0
            resolutions = []

            for inc in inconsistencies:
                resolution = self._create_resolution_for_inconsistency(inc, state, chapter_id)
                if resolution:
                    resolutions.append(resolution)
                    resolved_count += 1

            if chapter_id:
                # If chapter context provided, update the chapter content where possible
                resolution_note = f"Resolved {resolved_count} inconsistencies"
                # In a full implementation, we'd modify the actual content
                # This is where we'd update the state or return fix suggestions

            return {
                "status": "success",
                "message": f"Attempted to resolve {resolved_count} inconsistencies",
                "resolutions": resolutions,
                "resolutions_applied": resolved_count
            }

        except Exception as e:
            return {"status": "error", "message": f"Error resolving inconsistencies: {str(e)}"}

    def _generate_consistency_report(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive consistency report"""
        try:
            # Perform checks across all chapters if not specified
            target_chapters = context.get("chapters", [])
            if not target_chapters:
                target_chapters = list(state.chapters.keys())

            report = {
                "generated_at": datetime.now().isoformat(),
                "total_chapters": len(target_chapters),
                "checked_elements": [],
                "summary": {}
            }

            all_issues = []
            for chapter_id in target_chapters:
                chapter_report = self._check_all_consistencies(state, {"chapter_id": chapter_id})
                report["checked_elements"].append({
                    "chapter_id": chapter_id,
                    "chapter_number": state.chapters[chapter_id].number if chapter_id in state.chapters else None,
                    "chapter_report": chapter_report
                })

                # Gather issues for summary
                if chapter_report.get("status") == "success":
                    all_issues.extend(self._extract_issues_from_report(chapter_report))

            # Create summary
            issue_types = {}
            for issue in all_issues:
                issue_type = issue.get("type", "unknown")
                if issue_type not in issue_types:
                    issue_types[issue_type] = 0
                issue_types[issue_type] += 1

            report["summary"] = {
                "total_issues": len(all_issues),
                "issue_types": issue_types,
                "recommendations": self._generate_recommendations(all_issues)
            }

            return {
                "status": "success",
                "message": "Consistency report generated",
                "report": report
            }

        except Exception as e:
            return {"status": "error", "message": f"Error generating report: {str(e)}"}

    def _validate_character_actions(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Specifically validate that character actions align with their personality and traits"""
        try:
            character_id = context.get("character_id")
            content = context.get("content", "")
            chapter_id = context.get("chapter_id")

            if not content and chapter_id:
                chapter = state.get_chapter(chapter_id)
                if chapter:
                    content = chapter.content

            if not character_id:
                return {"status": "error", "message": "character_id is required for action validation"}

            character = state.get_character(character_id)
            if not character:
                return {"status": "error", "message": f"Character {character_id} not found"}

            action_issues = self._analyze_character_action_alignment(character, content)

            return {
                "status": "success",
                "message": f"Character action validation completed for {character.name}",
                "character_id": character_id,
                "action_issues": action_issues,
                "issues_found": len(action_issues)
            }

        except Exception as e:
            return {"status": "error", "message": f"Error validating character actions: {str(e)}"}

    def _analyze_character_behavior(self, character: Character, content: str, location: Optional[str] = None) -> List[Dict[str, Any]]:
        """Analyze a character's behavior in content for consistency with known traits"""
        inconsistencies = []

        # Check if character's personality traits are reflected in the content
        content_lower = content.lower()
        name_variations = [character.name.lower(), character.name.split()[0].lower()]

        # Check for actions that might contradict personality traits
        if any("calm" in trait.lower() for trait in character.personality_traits):
            urgent_words = ["rushed", "panicked", "frantically", "hastily"]
            for word in urgent_words:
                if word in content_lower and any(name in content_lower for name in name_variations):
                    inconsistencies.append({
                        "type": "personality_inconsistency",
                        "severity": "medium",
                        "element": f"Character {character.name}",
                        "issue": f"Character described as calm but performing {word} action",
                        "location": location,
                        "suggestion": f"Consider whether {character.name} would really behave this way given their calm personality"
                    })

        # Check speech patterns alignment
        if "speech_patterns" in character.metadata:
            speech_patterns = character.metadata["speech_patterns"].lower()
            # In a real implementation, we'd analyze actual dialogue
            # This is a simplified version
            if "formal" in speech_patterns and "informal" in content_lower:
                # This is a simplified check
                pass

        # Check for character background consistency
        if character.background and any(word in content_lower for word in character.background.lower().split()[:5]):
            # Basic check for potential inconsistencies with background
            pass

        return inconsistencies

    def _analyze_timeline(self, content: str, state: StoryState) -> List[Dict[str, Any]]:
        """Analyze timeline consistency in the content"""
        inconsistencies = []

        # Look for temporal sequence indicators
        time_indicators = [
            "yesterday", "today", "tomorrow",
            "last week", "last month", "last year",
            "next week", "next month", "next year",
            "ago", "before", "after", "then", "previously"
        ]

        # Count time references
        time_refs = []
        for indicator in time_indicators:
            if indicator in content.lower():
                time_refs.append(indicator)

        # Check for potentially conflicting time statements
        contradictory_pairs = [
            ("yesterday", "tomorrow"),
            ("last week", "next week"),
            ("before", "after")
        ]

        for pair in contradictory_pairs:
            if pair[0] in content.lower() and pair[1] in content.lower():
                inconsistencies.append({
                    "type": "timeline_inconsistency",
                    "severity": "high",
                    "element": f"Time indicators ({pair[0]}, {pair[1]})",
                    "issue": f"Potentially conflicting time references: {pair[0]} and {pair[1]}",
                    "suggestion": "Verify temporal sequence of events"
                })

        return inconsistencies

    def _analyze_world_coherence(self, content: str, state: StoryState) -> List[Dict[str, Any]]:
        """Analyze world-building consistency"""
        inconsistencies = []

        # Check location references against known locations
        for location_id, location in state.locations.items():
            if location.name.lower() in content.lower():
                # Check for consistency in location description
                if location.features:
                    # In a real implementation we'd verify the setting details match
                    # what's described in content
                    pass

        # Check for consistency in setting details
        setting_elements = ["technology level", "social structure", "customs", "geography"]
        for element in setting_elements:
            if element in content.lower():
                # Compare against what's established in the world state
                # This would require a more complex knowledge-based check
                pass

        return inconsistencies

    def _analyze_causal_chain(self, content: str, state: StoryState) -> List[Dict[str, Any]]:
        """Analyze the logical causal chain in the content"""
        issues = []

        # Look for action-reaction patterns
        cause_indicators = ["because", "therefore", "as a result", "so", "consequently", "led to"]
        effect_indicators = ["resulted", "followed", "ensued", "occurred"]

        # Check for potential causality issues
        if "because" in content.lower() and "but" in content.lower():
            # Potential issue where an explanation conflicts with the outcome
            issues.append({
                "type": "causal_inconsistency",
                "severity": "medium",
                "element": "Causal relationship",
                "issue": "Detected 'because' and 'but' in proximity - possible contradiction in causal chain",
                "suggestion": "Verify that the causal explanation aligns with the outcome"
            })

        return issues

    def _create_resolution_for_inconsistency(self, inconsistency: Dict[str, Any], state: StoryState, chapter_id: Optional[str]) -> Optional[Dict[str, Any]]:
        """Create a resolution for a specific inconsistency"""
        if inconsistency.get("type") == "personality_inconsistency":
            char_name = inconsistency.get("element", "").split()[1] if "Character" in inconsistency.get("element", "") else ""
            return {
                "type": "character_alignment",
                "target": char_name,
                "action": f"Review and adjust {char_name}'s behavior to align with their established traits",
                "chapter_id": chapter_id
            }
        elif inconsistency.get("type") == "timeline_inconsistency":
            return {
                "type": "timeline_correction",
                "target": inconsistency.get("element", ""),
                "action": f"Verify and correct the timeline sequence: {inconsistency.get('issue', '')}",
                "chapter_id": chapter_id
            }

        return None

    def _extract_issues_from_report(self, report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract specific issues from a consistency report for further processing"""
        all_issues = []

        results = report.get("results", {})
        for check_type, result in results.items():
            # This would need to handle all different types of reports
            issues = self._extract_type_issues(result)
            all_issues.extend(issues)

        return all_issues

    def _extract_type_issues(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract issues of various types from results."""
        issues = []

        if result.get("status") == "success":
            if "inconsistencies" in result:
                issues.extend(result["inconsistencies"])
            if "causal_issues" in result:
                issues.extend(result["causal_issues"])

        return issues

    def _generate_recommendations(self, all_issues: List[Dict[str, Any]]) -> List[str]:
        """Generate high-level recommendations based on issues found"""
        recommendations = []

        if not all_issues:
            return ["No inconsistencies detected. Story maintains high consistency across elements."]

        issue_types = set(issue["type"] for issue in all_issues if "type" in issue)
        if "personality_inconsistency" in issue_types:
            recommendations.append("Character behavior is inconsistent with established personalities; review character sheets and align actions/dialogue with traits")

        if "timeline_inconsistency" in issue_types:
            recommendations.append("Timeline or chronology inconsistencies detected; establish clear sequence of events or create timeline reference")

        if "causal_inconsistency" in issue_types:
            recommendations.append("Causal relationships not clearly established; ensure all consequences have appropriate causes")

        return recommendations

    def _analyze_character_action_alignment(self, character: Character, content: str) -> List[Dict[str, Any]]:
        """Specifically analyze whether content shows character acting in alignment with traits"""
        action_issues = []

        content_lower = content.lower()

        for trait in character.personality_traits:
            trait_lower = trait.lower()

            # Define behavioral antonyms or contradicting actions
            contradictory_behaviors = {
                "shy": ["spoke loudly", "demanded attention", "boasted", "commanded"],
                "brave": ["fled", "hid", "cowered", "retreated in fear"],
                "honest": ["lied", "deceived", "withheld truth", "misled"],
                "patient": ["rushed", "impatient", "hurried", "reacted angrily"],
                "wise": ["acted foolishly", "made bad choice", "ignored advice", "rushed judgment"]
            }

            if trait_lower in contradictory_behaviors:
                for contradictory_action in contradictory_behaviors[trait_lower]:
                    if contradictory_action in content_lower:
                        action_issues.append({
                            "type": "action_trait_mismatch",
                            "trait": trait,
                            "action": contradictory_action,
                            "character": character.name,
                            "issue": f"{character.name} ({trait}) is described as {contradictory_action}",
                            "severity": "high",
                            "suggestion": f"Align the action '{contradictory_action}' with {character.name}'s {trait} personality trait"
                        })

        return action_issues

    def run_comprehensive_check(self, state: StoryState) -> Dict[str, Any]:
        """Run a full consistency check on the entire story in the state"""
        return self._check_all_consistencies(state, {})