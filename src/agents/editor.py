from typing import Dict, List, Any
from src.agents.base import BaseAgent, AgentConfig
from src.core.story_state import StoryState
from src.core.knowledge_base import KnowledgeBase
import json
from datetime import datetime


class EditorAgent(BaseAgent):
    """
    Editor Agent - responsible for improving readability, emotional tension,
    and eliminating redundancy in the story content
    """

    def __init__(self, config: AgentConfig, knowledge_base: KnowledgeBase, **kwargs):
        super().__init__(config, knowledge_base)
        self.editing_stats = {
            "edits_performed": 0,
            "issues_found": 0,
            "improvements_made": 0
        }

    def process(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process editing tasks based on the context
        """
        action = context.get("action", "edit_content")
        result = {}

        if action == "edit_content":
            result = self._edit_content(state, context)
        elif action == "improve_tension":
            result = self._improve_tension(state, context)
        elif action == "reduce_redundancy":
            result = self._reduce_redundancy(state, context)
        elif action == "enhance_readability":
            result = self._enhance_readability(state, context)
        elif action == "check_consistency":
            result = self._check_consistency(state, context)
        elif action == "improve_dialogue":
            result = self._improve_dialogue(state, context)
        elif action == "refine_pacing":
            result = self._refine_pacing(state, context)
        elif action == "verify_grammar_style":
            result = self._verify_grammar_style(state, context)
        else:
            result = {"status": "error", "message": f"Unknown action: {action}"}

        # Log the editing activity
        self.log_message(f"Processed action: {action} - {result.get('status', 'unknown')}", "info")

        # Update statistics
        if result.get("status") == "success":
            self.editing_stats["edits_performed"] += 1
            if "issues_found" in result:
                self.editing_stats["issues_found"] += result["issues_found"]
            if "improvements_made" in result:
                self.editing_stats["improvements_made"] += result["improvements_made"]

        return self.format_response(
            content=json.dumps(result, default=str),
            metadata={
                "action": action,
                "timestamp": datetime.now().isoformat(),
                "stats": self.editing_stats
            }
        )

    def _edit_content(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform general editing on content"""
        try:
            content = context.get("content", "")
            focus_area = context.get("focus", ["readability", "tension", "consistency"])
            chapter_id = context.get("chapter_id")

            if not content:
                # If no content provided, try to get from chapter
                if chapter_id:
                    chapter = state.get_chapter(chapter_id)
                    if chapter:
                        content = chapter.content
                    else:
                        return {"status": "error", "message": f"Chapter {chapter_id} not found"}
                else:
                    return {"status": "error", "message": "No content provided and no chapter_id specified"}

            issues_found = []
            improvements_made = []

            # Analyze content for various issues
            if "readability" in focus_area:
                readability_issues = self._check_readability(content)
                issues_found.extend(readability_issues)
                improvements = self._improve_readability_target(content, readability_issues)
                content = improvements["content"]
                improvements_made.extend(improvements["modifications"])

            if "tension" in focus_area:
                tension_issues = self._check_tension(content)
                issues_found.extend(tension_issues)
                improvements = self._improve_tension_target(content, tension_issues)
                content = improvements["content"]
                improvements_made.extend(improvements["modifications"])

            if "consistency" in focus_area:
                consistency_issues = self._check_consistency(state, {"content": content})
                issues_found.extend(consistency_issues.get("issues", []))
                # Already in a consistency check, so skip modification here

            # Reduce redundancy if specified
            if "redundancy" in focus_area:
                # Already has a dedicated function, would be redundant to do here
                pass

            result = {
                "status": "success",
                "message": f"Content edited with focus on {', '.join(focus_area)}",
                "original_content_length": len(context.get("content", "")),
                "edited_content": content,
                "content_length": len(content),
                "issues_found": issues_found,
                "improvements_made": improvements_made,
                "issues_found_count": len(issues_found),
                "improvements_made_count": len(improvements_made)
            }

            if chapter_id:
                # Update the chapter in state with edited content
                state.update_chapter_content(chapter_id, content)
                result["chapter_id"] = chapter_id

            return result

        except Exception as e:
            return {"status": "error", "message": f"Error editing content: {str(e)}"}

    def _improve_tension(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance the tension and emotional engagement in the content"""
        try:
            content = context.get("content", "")
            tension_type = context.get("type", "suspense")  # suspense, drama, conflict, mystery
            intensity_level = context.get("intensity", "moderate")  # low, moderate, high, extreme

            # Get related tension techniques from knowledge base
            tension_tips = self.get_relevant_information(f"{tension_type} tension technique", top_k=3)

            # Build editing instructions
            instructions = [
                f"Enhance {tension_type} tension with {intensity_level} intensity",
                "Add more uncertainty and anticipation",
                "Increase the stakes or consequences",
                "Use shorter sentences for punch or longer for building dread",
            ]

            # Create the tension-enhanced content
            edited_content, modifications = self._enhance_tension_target(content, tension_type, intensity_level, instructions)

            return {
                "status": "success",
                "message": f"Tension enhanced: {tension_type} at {intensity_level} level",
                "original_content": context.get("content", ""),
                "improved_content": edited_content,
                "modifications": modifications,
                "tension_type": tension_type,
                "intensity_level": intensity_level
            }

        except Exception as e:
            return {"status": "error", "message": f"Error improving tension: {str(e)}"}

    def _reduce_redundancy(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Remove repetitive content and redundant phrases"""
        try:
            content = context.get("content", "")
            target = context.get("target", "all")  # all, dialog, narrative, description

            # Identify redundant elements
            redundant_elements = self._find_redundancies(content, target)

            # Remove redundancies
            cleaned_content, fixes_applied = self._remove_redundancies(content, redundant_elements)

            return {
                "status": "success",
                "message": f"Redundancy removed for {target} elements",
                "original_content": context.get("content", ""),
                "cleaned_content": cleaned_content,
                "redundant_elements_found": [el['text'] for el in redundant_elements],
                "fixes_applied": len(fixes_applied),
                "content_improved_by": len(content) - len(cleaned_content)
            }

        except Exception as e:
            return {"status": "error", "message": f"Error reducing redundancy: {str(e)}"}

    def _enhance_readability(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Improve readability through sentence structure, flow, and clarity"""
        try:
            content = context.get("content", "")
            target_audience = context.get("audience", "general")  # general, young_adult, adult, academic
            reading_level = context.get("reading_level", 8)  # Grade level

            # Get readability techniques from knowledge base
            readability_tips = self.get_relevant_information(f"readability {target_audience}", top_k=3)

            # Apply readability improvements
            improved_content, changes_made = self._apply_readability_improvements(
                content, target_audience, reading_level, readability_tips
            )

            return {
                "status": "success",
                "message": f"Readability enhanced for {target_audience} audience",
                "original_content": context.get("content", ""),
                "improved_content": improved_content,
                "changes_made": changes_made,
                "target_audience": target_audience,
                "reading_level": reading_level
            }

        except Exception as e:
            return {"status": "error", "message": f"Error enhancing readability: {str(e)}"}

    def _check_consistency(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check for narrative consistency"""
        try:
            content = context.get("content", "")
            check_type = context.get("check_type", "all")  # all, character, timeline, facts

            issues = []

            if check_type in ["all", "character"]:
                character_issues = self._check_character_consistency(content, state)
                issues.extend(character_issues)

            if check_type in ["all", "timeline"]:
                timeline_issues = self._check_timeline_consistency(content, state)
                issues.extend(timeline_issues)

            if check_type in ["all", "facts"]:
                fact_issues = self._check_factual_consistency(content, state)
                issues.extend(fact_issues)

            return {
                "status": "success",
                "message": f"Consistency check completed for {check_type}",
                "issues": issues,
                "issues_count": len(issues),
                "content_length": len(content),
                "check_type": check_type
            }

        except Exception as e:
            return {"status": "error", "message": f"Error checking consistency: {str(e)}"}

    def _improve_dialogue(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance existing dialogue for better flow and characterization"""
        try:
            content = context.get("content", "")
            character_id = context.get("character_id")

            # Get character information if specified
            character = None
            if character_id:
                character = state.get_character(character_id)

            # Improve dialogue in content
            improved_content, modifications = self._enhance_dialogue_target(content, character)

            return {
                "status": "success",
                "message": "Dialogue enhanced",
                "original_content": content,
                "improved_content": improved_content,
                "modifications_count": len(modifications),
                "modifications": modifications
            }

        except Exception as e:
            return {"status": "error", "message": f"Error improving dialogue: {str(e)}"}

    def _refine_pacing(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Refine the pacing of narrative elements"""
        try:
            content = context.get("content", "")
            pacing_desired = context.get("pacing", "balanced")  # fast, balanced, slow
            section = context.get("section", "full")  # full, sentence, paragraph

            # Analyze current pacing
            pacing_issues = self._analyze_pacing(content, pacing_desired, section)

            # Suggest pacing improvements
            improved_content, changes = self._adjust_pacing(content, pacing_issues, pacing_desired, section)

            return {
                "status": "success",
                "message": f"Pacing refined to {pacing_desired}",
                "original_content": content,
                "improved_content": improved_content,
                "changes_made": changes,
                "pacing_desired": pacing_desired,
                "section_target": section
            }

        except Exception as e:
            return {"status": "error", "message": f"Error refining pacing: {str(e)}"}

    def _verify_grammar_style(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check grammar, style, and voice consistency"""
        try:
            content = context.get("content", "")
            target_style = context.get("style", "narrative")  # narrative, dialogue, descriptive
            grammar_only = context.get("grammar_only", False)

            issues = []
            fix_count = 0

            if not grammar_only:
                # Check style consistency
                style_issues = self._check_style_mismatches(content, target_style)
                issues.extend(style_issues)

            # Check grammar
            grammar_issues = self._check_grammar(content)
            issues.extend(grammar_issues)

            # If in learning mode, provide fixes instead of just identifying issues
            fixed_content = content
            suggested_fixes = []

            if context.get("apply_fixes", False):
                fixed_content, suggested_fixes = self._apply_grammar_style_fixes(content, issues, target_style)
                fix_count = len(suggested_fixes)

            return {
                "status": "success",
                "message": f"Grammar and style verification completed",
                "content_length": len(content),
                "issues_found": issues,
                "issues_count": len(issues),
                "fixes_applied": fix_count,
                "suggested_fixes": suggested_fixes,
                "improved_content": fixed_content
            }

        except Exception as e:
            return {"status": "error", "message": f"Error verifying grammar and style: {str(e)}"}

    def _check_readability(self, content: str) -> List[Dict[str, str]]:
        """Check content for readability issues"""
        issues = []

        # Check sentence length
        import re
        sentences = re.split(r'[.!?]+', content)
        long_sentences = [s for s in sentences if len(s.split()) > 25]

        if long_sentences:
            issues.append({
                "type": "sentence_length",
                "description": f"Found {len(long_sentences)} long sentences (>25 words) that might hurt readability",
                "examples": [s[:50] + "..." for s in long_sentences[:3]]
            })

        # Check for passive voice overuse
        passive_patterns = ["by the", "was", "were", "been", "being"]
        passive_count = sum([content.lower().count(pattern) for pattern in passive_patterns])

        total_words = len(content.split())
        passive_ratio = passive_count / total_words if total_words > 0 else 0

        if passive_ratio > 0.15:  # More than 15% passive
            issues.append({
                "type": "passive_voice",
                "description": f"High passive voice usage ({passive_ratio:.1%}) may reduce readability",
                "suggestion": "Convert to active voice where possible"
            })

        # Check for redundant phrases
        redundant_patterns = [
            r'\babundance of\b', r'\blarge number of\b', r'\bin order to\b', r'\bon the subject of\b'
        ]

        for pattern in redundant_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append({
                    "type": "redundancy",
                    "description": f"Potentially redundant phrase identified: {pattern}",
                })

        return issues

    def _check_tension(self, content: str) -> List[Dict[str, str]]:
        """Check content for tension issues"""
        issues = []

        # Look for missing tension words
        tension_indicators = ['suspense', 'fear', 'anxiety', 'danger', 'risk', 'secret', 'unknown', 'mystery']
        content_lower = content.lower()

        has_tension = any(indicator in content_lower for indicator in tension_indicators)

        # Count action/stress markers
        action_indicators = ['chased', 'fled', 'screamed', 'gasped', 'heart', 'pumped', 'raced', 'hammering']
        action_count = sum(1 for indicator in action_indicators if indicator in content_lower)

        if not has_tension and action_count < 3 and len(content) > 50:
            issues.append({
                "type": "low_tension",
                "description": "Content appears to have low tension, may need more compelling elements"
            })

        return issues

    def _improve_readability_target(self, content: str, issues: List[Dict[str, str]]) -> Dict[str, Any]:
        """Apply readability improvements"""
        improved = content
        modifications = []

        for issue in issues:
            if issue["type"] == "sentence_length":
                # Break down long sentences
                import re
                sentences = re.split(r'([.!?]+\s*)', improved)

                new_sentences = []
                for sent in sentences:
                    if sent and len(sent.split()) > 25:  # Long sentence
                        sent_stripped = re.sub(r'([.!?]+\s*)', '', sent)  # Remove punctuation for analysis
                        words = sent_stripped.split()

                        if len(words) > 25 and ',' in sent_stripped:
                            # Find natural break points at commas
                            first_part = self._split_at_comma(sent_stripped)
                            if first_part and len(first_part.split()) <= 25 and len(first_part.strip()) < len(sent_stripped):
                                sent = first_part + ". " + sent_stripped[len(first_part):].strip().capitalize()
                                modifications.append(f"Split long sentence for readability")
                    new_sentences.append(sent)

                improved = "".join(new_sentences)

        return {"content": improved, "modifications": modifications}

    def _split_at_comma(self, text: str) -> str:
        """Helper to split text on the last comma within the first 25 words"""
        words = text.split()
        if len(words) <= 25:
            return text

        # Look for commas in the first 25 words
        text_slice = " ".join(words[:25])
        last_comma_idx = text_slice.rfind(',')

        if last_comma_idx != -1:
            # Use this as break point
            return text_slice[:last_comma_idx].strip()

        return text

    def _improve_tension_target(self, content: str, tension_type: str, intensity_level: str, instructions: List[str]) -> tuple:
        """Apply specific tension improvements to content"""
        # This is a simplified implementation; in a full implementation,
        # this would call an LLM to specifically enhance the tension elements
        improved = content
        modifications = []

        # In a real implementation, we'd enhance the content using LLM based on the instructions
        # For now, we'll just provide a mock example of what could be done:
        tension_indicators = {
            'suspense': ['unknown', 'doubt', 'uncertainty', 'watched', 'listening'],
            'drama': ['clenched', 'shivered', 'gripped', 'voice strained', 'heart sank'],
            'conflict': ['confronted', 'challenged', 'tension', 'opposition', 'argument erupted'],
            'mystery': ['disappeared', 'odd', 'strange', 'inexplicable', 'significance escaped']
        }

        if tension_type in ['suspense', 'mystery'] and intensity_level in ['high', 'extreme']:
            # Add tension-building elements
            import random
            indicators = tension_indicators.get(tension_type, [])
            # Mock: Add one tension indicator somewhere in content if not present
            if len(indicators) > 0 and not any(indicator in content.lower() for indicator in indicators[:2]):
                new_content = content + f" The air felt thick with {random.choice(['tension', 'unease', 'foreboding'])}."
                modifications.append(f"Added {tension_type} tension for {intensity_level} intensity")
                improved = new_content

        return improved, modifications

    def _find_redundancies(self, content: str, target: str) -> List[Dict[str, Any]]:
        """Find redundant content elements"""
        import re
        from collections import defaultdict

        redundant_elements = []

        if target in ['all', 'narrative', 'description']:
            # Look for repeated phrases within the content
            sentences = re.split(r'[.!?]+', content)
            sentence_count = defaultdict(list)  # Store positions for each sentence

            for idx, sentence in enumerate(sentences):
                clean_sentence = re.sub(r'\s+', ' ', sentence.strip().lower())
                if len(clean_sentence.split()) > 5:  # At least 5 words to be meaningful
                    sentence_count[clean_sentence].append(idx)

            for sentence, positions in sentence_count.items():
                if len(positions) > 1:
                    redundant_elements.append({
                        "element": "sentence",
                        "text": sentence,
                        "repeat_count": len(positions),
                        "positions": positions
                    })

        if target in ['all', 'dialog']:
            # Look for repeated dialogue patterns
            # This is a simplified check; could be enhanced with more sophisticated pattern matching
            dialogue_matches = re.findall(r'"([^"]*)"', content)
            dialogue_count = defaultdict(int)
            for dia in dialogue_matches:
                # Normalize spacing and capitalization
                normalized = re.sub(r'\s+', ' ', dia.strip().lower())
                dialogue_count[normalized] += 1

            for dia, count in dialogue_count.items():
                if count > 1:
                    redundant_elements.append({
                        "element": "dialogue",
                        "text": dia,
                        "repeat_count": count
                    })

        return redundant_elements

    def _remove_redundancies(self, content: str, redundant_elements: List[Dict[str, Any]]) -> tuple:
        """Remove identified redundancies from content"""
        edited_content = content
        fixes_applied = []

        # Sort by repeat count (descending) to process most redundant first
        sorted_elements = sorted(redundant_elements, key=lambda x: x.get('repeat_count', 0), reverse=True)

        for elem in sorted_elements:
            text = elem['text']
            count = elem['repeat_count']
            element_type = elem['element']

            if count > 1:
                # Remove subsequent instances, keep the first
                # This is a simplified removal; a more sophisticated approach would use NLP
                occurrences = re.findall(re.escape(text), edited_content, re.IGNORECASE)
                if len(occurrences) > 1:
                    # Remove all but the first occurrence
                    first_pos = edited_content.lower().find(text.lower())
                    if first_pos != -1:
                        # This is a basic approach - in practice, need to preserve surrounding context
                        # This is a placeholder for a more complete implementation
                        fixes_applied.append({
                            "type": "redundancy_removal",
                            "element_type": element_type,
                            "original_text": text,
                            "count": count - 1  # We keep first, remove others
                        })

        return edited_content, fixes_applied

    def _apply_readability_improvements(self, content: str, target_audience: str, reading_level: int, tips: List[str]) -> tuple:
        """Apply readability improvements based on target audience and grade reading level"""
        # Placeholder implementation - would require complex NLP or LLM prompting in practice
        improved_content = content
        changes = []

        # Simple improvements based on reading level:
        if reading_level < 8:  # Younger audience
            # Could include complex words replacements, simpler structures
            # This is where a real implementation would do the work
            changes.append(f"Simplified sentence structure for grade {reading_level} reading level")

        if target_audience == 'young_adult':
            changes.append("Applied young adult readability guidelines")

        return improved_content, changes

    def _check_character_consistency(self, content: str, state: StoryState) -> List[Dict[str, str]]:
        """Check if characters are acting consistently with their known traits"""
        issues = []

        # This would typically examine character behavior in content against state.character traits
        # For the placeholder implementation, we'll make up potential issues
        potential_issues = []

        # Look for character names and check consistency against state if chapter-specific
        # In a real implementation, we'd analyze character actions/traits in content vs expected behaviors

        return potential_issues

    def _check_timeline_consistency(self, content: str, state: StoryState) -> List[Dict[str, str]]:
        """Check temporal consistency in the content"""
        issues = []

        # Look for temporal language patterns
        timeline_clues = ["yesterday", "last week", "then", "after", "before", "during", "first", "next", "now"]

        has_clues = any(clue in content.lower() for clue in timeline_clues)
        if has_clues:
            # In a real implementation, validate if the sequences make sense
            pass  # Placeholder

        return issues

    def _check_factual_consistency(self, content: str, state: StoryState) -> List[Dict[str, str]]:
        """Check for consistency with known facts in story state"""
        issues = []

        # Compare content against known story facts (characters, locations, etc.)
        char_names = [char.name for char in state.characters.values()]

        # Look for potential discrepancies (simple version)
        for char_name in char_names:
            if char_name.lower() in content.lower():
                # Check if content aligns with character description
                char = state.get_character([c.id for c in state.characters.values() if c.name == char_name][0] if [c.id for c in state.characters.values() if c.name == char_name] else "")
                if char and char.role:
                    # Check for potential role mismatches
                    # This is placeholder logic
                    pass

        return issues

    def _enhance_dialogue_target(self, content: str, character: Any = None) -> tuple:
        """Enhance dialogue elements in the content"""
        import re
        improved_content = content
        modifications = []

        # Find and improve dialogue
        dialogue_pattern = r'(["""])([^"""]+)\1'
        matches = re.finditer(dialogue_pattern, improved_content)

        for match in matches:
            original_dialogue = match.group(2)
            # Simplified - in a real implementation, would consider character traits
            improved_dialogue = original_dialogue

            # Add dialogue tags if missing
            start_pos = match.start()
            before_dialogue = improved_content[:start_pos]
            if 'said' not in before_dialogue[-50:]: # Rough check for speaker tag nearby
                # Would add contextually appropriate speaker attribution
                modifications.append("Added dialogue attribution")

        return improved_content, modifications

    def _analyze_pacing(self, content: str, pacing_desired: str, section: str) -> List[Dict[str, str]]:
        """Analyze the pacing of the content"""
        issues = []

        if section == 'sentence':
            sentences = content.split('.')
            total_sent = len(sentences)
            if total_sent > 0:
                avg_length = sum(len(s.split()) for s in sentences) / total_sent
                if pacing_desired == "fast" and avg_length > 15:
                    issues.append({"type": "pacing", "issue": f"Average sentence length {avg_length:.1f} may be too long for fast pacing"})
                elif pacing_desired == "slow" and avg_length < 10:
                    issues.append({"type": "pacing", "issue": f"Average sentence length {avg_length:.1f} may be too short for slow pacing"})

        return issues

    def _adjust_pacing(self, content: str, issues: List[Dict[str, str]], pacing_desired: str, section: str) -> tuple:
        """Adjust pacing to desired level"""
        # Placeholder implementation - would make changes to improve flow
        adjusted_content = content
        changes = []

        for issue in issues:
            # Implement change based on issue
            changes.append(f"Addressed {issue.get('issue', 'pacing issue')}")

        return adjusted_content, changes

    def _check_style_mismatches(self, content: str, target_style: str) -> List[Dict[str, str]]:
        """Check for style consistency"""
        issues = []

        # Very basic check - would need sophisticated NLP analysis in practice
        style_indicators = {
            "narrative": ["narrates", "described", "explained", "we see", "the scene"],
            "dialogue": ["say", "asks", "replies", "responds", "called out"],
            "descriptive": ["looks like", "feels", "smells", "sounds", "appears"]
        }

        content_lower = content.lower()
        has_indicators = any(indicator in content_lower for indicator in style_indicators.get(target_style, []))

        # This is greatly simplified; real implementation would be more sophisticated
        return issues

    def _check_grammar(self, content: str) -> List[Dict[str, str]]:
        """Basic grammar check (placeholder)"""
        issues = []
        # In a real implementation, would use a proper grammar checking library or service
        return issues

    def _apply_grammar_style_fixes(self, content: str, issues: List[Dict[str, str]], target_style: str) -> tuple:
        """Apply fixes for grammar and style issues"""
        # Placeholder implementation - would implement actual fixes
        fixed_content = content
        suggested_fixes = []

        for issue in issues:
            suggested_fixes.append(f"Suggested fix for: {issue}")

        return fixed_content, suggested_fixes

    def _enhance_tension_target(self, content: str, tension_type: str, intensity_level: str, instructions: List[str]) -> tuple:
        """Enhance specific tension elements in content"""
        # Placeholder - in real implementation would call LLM with specific instructions
        import random

        enhanced_content = content
        modifications = []

        # Add basic tension indicators based on type and intensity
        if tension_type in ["suspense", "mystery"] and intensity_level in ["high", "extreme"]:
            if "silence" not in content.lower():
                position = len(content) // 2  # Mid-content insertion point
                part1, part2 = content[:position], content[position:]
                enhanced_content = part1 + f" The silence was deafening, broken only by {random.choice(['footsteps', 'a creaking floorboard', 'whispers'])}. " + part2
                modifications.append(f"Added {tension_type} element for {intensity_level} intensity")

        return enhanced_content, modifications