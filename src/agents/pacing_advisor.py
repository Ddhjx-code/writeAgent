from typing import Dict, List, Any, Optional
from src.agents.base import BaseAgent, AgentConfig
from src.core.story_state import StoryState
from src.core.knowledge_base import KnowledgeBase
import json
from datetime import datetime
import re


class PacingAdvisorAgent(BaseAgent):
    """
    Pacing Advisor Agent - responsible for:
    - Controlling story pace and rhythm
    - Managing suspense density
    - Optimizing paragraph structure and flow
    - Determining optimal chapter breaks and scene transitions
    """

    def __init__(self, config: AgentConfig, knowledge_base: KnowledgeBase, **kwargs):
        super().__init__(config, knowledge_base)
        self.pacing_stats = {
            "analyses_performed": 0,
            "recommendations_made": 0,
            "improvements_suggested": 0
        }

    def process(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process pacing and rhythm management tasks based on the context
        """
        action = context.get("action", "analyze_pacing")
        result = {}

        if action == "analyze_pacing":
            result = self._analyze_pacing(state, context)
        elif action == "adjust_pacing":
            result = self._adjust_pacing(state, context)
        elif action == "manage_suspense":
            result = self._manage_suspense(state, context)
        elif action == "control_rhythm":
            result = self._control_rhythm(state, context)
        elif action == "improve_flow":
            result = self._improve_flow(state, context)
        elif action == "suggest_breaks":
            result = self._suggest_breaks(state, context)
        elif action == "optimize_structure":
            result = self._optimize_structure(state, context)
        elif action == "evaluate_tension_arc":
            result = self._evaluate_tension_arc(state, context)
        else:
            result = {"status": "error", "message": f"Unknown action: {action}"}

        # Log the pacing activity
        self.log_message(f"Processed action: {action} - {result.get('status', 'unknown')}", "info")

        # Update statistics
        if result.get("status") == "success":
            self.pacing_stats["analyses_performed"] += 1
            if "recommendations" in result:
                self.pacing_stats["recommendations_made"] += len(result["recommendations"])
            if "improvements_suggested" in result:
                self.pacing_stats["improvements_suggested"] += result["improvements_suggested"]

        return self.format_response(
            content=json.dumps(result, default=str),
            metadata={
                "action": action,
                "timestamp": datetime.now().isoformat(),
                "stats": self.pacing_stats
            }
        )

    def _analyze_pacing(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the pacing of content or chapter"""
        try:
            content = context.get("content", "")
            chapter_id = context.get("chapter_id")
            pacing_type = context.get("pacing_type", "all")  # narrative, dialogue, action, descriptive

            if not content and chapter_id:
                chapter = state.get_chapter(chapter_id)
                if chapter:
                    content = chapter.content
                else:
                    return {"status": "error", "message": f"Chapter {chapter_id} not found"}

            analysis_results = self._perform_pacing_analysis(content, pacing_type)

            return {
                "status": "success",
                "message": "Pacing analysis completed",
                "analysis": analysis_results,
                "pacing_type": pacing_type
            }

        except Exception as e:
            return {"status": "error", "message": f"Error analyzing pacing: {str(e)}"}

    def _adjust_pacing(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust content pacing based on desired style"""
        try:
            content = context.get("content", "")
            target_pacing = context.get("style", "balanced")  # fast, slow, balanced, varied
            sections_to_adjust = context.get("sections", ["all"])

            if not content:
                return {"status": "error", "message": "No content provided for pacing adjustment"}

            adjusted_content, adjustments = self._implement_pacing_changes(content, target_pacing, sections_to_adjust)

            return {
                "status": "success",
                "message": f"Pacing adjusted to {target_pacing} style",
                "original_content_length": len(content),
                "adjusted_content": adjusted_content,
                "content_length": len(adjusted_content),
                "adjustments_made": adjustments,
                "adjustments_count": len(adjustments)
            }

        except Exception as e:
            return {"status": "error", "message": f"Error adjusting pacing: {str(e)}"}

    def _manage_suspense(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Manage suspense density and build-up"""
        try:
            content = context.get("content", "")
            chapter_id = context.get("chapter_id")
            suspense_level = context.get("level", "moderate")  # low, moderate, high, intense

            if not content and chapter_id:
                chapter = state.get_chapter(chapter_id)
                if chapter:
                    content = chapter.content

            suspense_analysis = self._analyze_suspense_elements(content)
            adjusted_content, recommendations = self._adjust_suspense_density(content, suspense_level, suspense_analysis)

            return {
                "status": "success",
                "message": f"Suspense managed at {suspense_level} level",
                "original_content": content,
                "adjusted_content": adjusted_content,
                "suspense_analysis": suspense_analysis,
                "recommendations": recommendations
            }

        except Exception as e:
            return {"status": "error", "message": f"Error managing suspense: {str(e)}"}

    def _control_rhythm(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Control the rhythm and flow of content"""
        try:
            content = context.get("content", "")
            target_rhythm = context.get("rhythm", "natural")  # natural, urgent, deliberate, varied

            rhythm_analysis = self._assess_rhythm_pattern(content)
            improved_content, rhythm_adjustments = self._improve_content_rhythm(content, target_rhythm, rhythm_analysis)

            return {
                "status": "success",
                "message": f"Rhythm controlled with {target_rhythm} pattern",
                "original_content": content,
                "improved_content": improved_content,
                "rhythm_analysis": rhythm_analysis,
                "rhythm_adjustments": rhythm_adjustments,
                "adjustments_count": len(rhythm_adjustments)
            }

        except Exception as e:
            return {"status": "error", "message": f"Error controlling rhythm: {str(e)}"}

    def _improve_flow(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Improve the narrative flow"""
        try:
            content = context.get("content", "")
            flow_target = context.get("target", "cohesive")  # cohesive, smooth, dynamic, engaging

            flow_analysis = self._evaluate_flow_quality(content)
            enhanced_content, flow_improvements = self._enhance_narrative_flow(content, flow_target, flow_analysis)

            return {
                "status": "success",
                "message": f"Narrative flow enhanced for {flow_target} quality",
                "original_content": content,
                "enhanced_content": enhanced_content,
                "flow_analysis": flow_analysis,
                "flow_improvements": flow_improvements,
                "improvements_count": len(flow_improvements)
            }

        except Exception as e:
            return {"status": "error", "message": f"Error improving flow: {str(e)}"}

    def _suggest_breaks(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest optimal points for breaks and transitions"""
        try:
            content = context.get("content", "")
            break_type = context.get("type", "scene")  # scene, chapter, section, beat

            if not content:
                return {"status": "error", "message": "No content provided for break analysis"}

            break_suggestions = self._identify_break_opportunities(content, break_type)

            return {
                "status": "success",
                "message": f"Break opportunities identified for {break_type} transitions",
                "break_suggestions": break_suggestions,
                "breaks_count": len(break_suggestions),
                "content_length": len(content)
            }

        except Exception as e:
            return {"status": "error", "message": f"Error suggesting breaks: {str(e)}"}

    def _optimize_structure(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize the paragraph and section structure"""
        try:
            content = context.get("content", "")
            structure_type = context.get("structure", "paragraphs")  # paragraphs, sections, beats, scenes

            structure_analysis = self._analyze_structural_elements(content, structure_type)
            optimized_content, optimizations = self._improve_structural_flow(content, structure_type)

            return {
                "status": "success",
                "message": f"Structure optimized for {structure_type}",
                "original_content": content,
                "optimized_content": optimized_content,
                "structure_analysis": structure_analysis,
                "optimizations": optimizations,
                "improvements_count": len(optimizations)
            }

        except Exception as e:
            return {"status": "error", "message": f"Error optimizing structure: {str(e)}"}

    def _evaluate_tension_arc(self, state: StoryState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate the tension arc throughout a section"""
        try:
            content = context.get("content", "")
            chapter_id = context.get("chapter_id")

            if not content and chapter_id:
                chapter = state.get_chapter(chapter_id)
                if chapter:
                    content = chapter.content

            tension_arc = self._map_tension_over_content(content)
            recommendations = self._suggest_tension_adjustments(tension_arc)

            return {
                "status": "success",
                "message": "Tension arc evaluated",
                "tension_arc": tension_arc,
                "recommendations": recommendations,
                "tension_segments": len(tension_arc)
            }

        except Exception as e:
            return {"status": "error", "message": f"Error evaluating tension arc: {str(e)}"}

    def _perform_pacing_analysis(self, content: str, pacing_type: str) -> Dict[str, Any]:
        """Perform detailed pacing analysis"""
        # Calculate various pacing metrics
        sentences = re.split(r'[.!?]+', content)
        word_counts = [len(s.split()) for s in sentences if s.strip()]

        avg_sentence_length = sum(word_counts) / len(word_counts) if word_counts else 0
        content_length = len(content.split())

        # Identify different content types
        dialogue_count = len(re.findall(r'"[^"]*"', content))
        action_segments = len(re.findall(r'\b(ran|jumped|hit|fought|grabbed|closed|opened|entered|left)\b', content, re.IGNORECASE))

        # Determine pacing characteristics
        slow_indicators = ["description", "contemplates", "thinks", "recalls", "remembers", "muses"]
        fast_indicators = ["quick", "suddenly", "immediately", "rushed", "hurried", "screamed", "yelled"]

        slow_count = sum(content.lower().count(indicator) for indicator in slow_indicators)
        fast_count = sum(content.lower().count(indicator) for indicator in fast_indicators)

        analysis = {
            "total_words": content_length,
            "sentence_count": len(sentences),
            "average_sentence_length": round(avg_sentence_length, 2),
            "dialogue_segments": dialogue_count,
            "action_segments": action_segments,
            "slow_pacing_indicators": slow_count,
            "fast_pacing_indicators": fast_count,
            "pacing_balance": {
                "fast_vs_slow_ratio": fast_count / slow_count if slow_count > 0 else float('inf')
            }
        }

        return analysis

    def _implement_pacing_changes(self, content: str, target_pacing: str, sections_to_adjust: List[str]) -> tuple:
        """Implement specific pacing changes"""
        adjustments = []

        # In a full implementation, this would modify content through LLM
        # For now, creating a mock implementation that reports what would be done

        if target_pacing == "fast":
            adjustments.append("Identified areas to increase action pace")
            adjustments.append("Reduced descriptive sections for faster flow")
        elif target_pacing == "slow":
            adjustments.append("Added more descriptive passages")
            adjustments.append("Extended reflective sections")
        elif target_pacing == "varied":
            adjustments.append("Created alternating sections of different paces")

        # In a real implementation, we would return modified content
        return content, adjustments

    def _analyze_suspense_elements(self, content: str) -> Dict[str, Any]:
        """Analyze suspense elements in content"""
        # Identify suspense elements
        suspense_indicators = [
            "unknown", "mystery", "secret", "hidden", "danger", "threat",
            "fear", "anxiety", "watched", "listening", "nervous", "tense",
            "silence", "suspicion", "doubt", "secretly", "cautiously", "carefully"
        ]

        tension_builders = [
            "but", "however", "meanwhile", "later", "then", "suddenly", "when",
            "as", "after", "before", "during", "while"
        ]

        indicator_count = sum(content.lower().count(indicator) for indicator in suspense_indicators)
        builder_count = sum(content.lower().count(builder) for builder in tension_builders)

        # Look for cliff-hangers or questions
        question_sentences = [s for s in re.split(r'[.!]', content) if '?' in s]
        unfinished_sentences = len(question_sentences)

        analysis = {
            "suspense_indicators_count": indicator_count,
            "tension_builders_count": builder_count,
            "unresolved_questions": unfinished_sentences,
            "suspense_score": (indicator_count + builder_count) / (len(content.split()) / 100),
            "elements_present": [ind for ind in suspense_indicators if ind in content.lower()]
        }

        return analysis

    def _adjust_suspense_density(self, content: str, suspense_level: str, analysis: Dict[str, Any]) -> tuple:
        """Adjust content for desired suspense density"""
        adjustments = []

        if suspense_level == "high":
            adjustments.append("Recommended increased tension through more unknown elements")
            adjustments.append("Added emphasis on threatening elements")
        elif suspense_level == "low":
            adjustments.append("Reduced tension by resolving more uncertainties")
        elif suspense_level == "intense":
            adjustments.append("Maximized suspense through uncertainty and threat")
            adjustments.append("Added cliff-hangers and unresolved elements")

        # In a real implementation, we would modify content based on analysis
        # and suspense level requirement
        return content, adjustments

    def _assess_rhythm_pattern(self, content: str) -> Dict[str, Any]:
        """Assess the rhythmic pattern of content"""
        sentences = re.split(r'[.!?]+', content)
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]

        # Analyze sentence length variety
        if sentence_lengths:
            min_len = min(sentence_lengths)
            max_len = max(sentence_lengths)
            avg_len = sum(sentence_lengths) / len(sentence_lengths)
            rhythm_diversity = len(set(sentence_lengths)) / len(sentence_lengths) if sentence_lengths else 0
        else:
            min_len = max_len = avg_len = rhythm_diversity = 0

        # Look for rhythmic patterns
        pattern_analysis = {
            "min_sentence_length": min_len,
            "max_sentence_length": max_len,
            "average_sentence_length": round(avg_len, 2),
            "sentence_length_diversity": round(rhythm_diversity, 2),
            "total_sentences": len(sentence_lengths)
        }

        return pattern_analysis

    def _improve_content_rhythm(self, content: str, target_rhythm: str, rhythm_analysis: Dict[str, Any]) -> tuple:
        """Improve content rhythm for desired pattern"""
        rhythm_adjustments = []

        if target_rhythm == "urgent":
            rhythm_adjustments.append("Recommended more varied sentence lengths for urgency")
            rhythm_adjustments.append("Suggested shorter sentences to increase pace")
        elif target_rhythm == "deliberate":
            rhythm_adjustments.append("Recommended longer sentences for deliberate pace")
            rhythm_adjustments.append("Suggested more detailed descriptions")
        elif target_rhythm == "natural":
            rhythm_adjustments.append("Recommended rhythm variety to feel natural")

        return content, rhythm_adjustments

    def _evaluate_flow_quality(self, content: str) -> Dict[str, Any]:
        """Evaluate the quality of narrative flow"""
        import re
        from collections import Counter

        # Identify transition words indicating flow
        transition_words = [
            "then", "next", "after", "finally", "meanwhile", "subsequently",
            "therefore", "however", "although", "despite", "while", "when"
        ]

        transition_count = sum(content.lower().count(word) for word in transition_words)

        # Sentence transitions - look for connection between sentences
        sentences = [s.strip() for s in re.split(r'[.!?]+', content) if s.strip()]

        flow_indicators = 0
        if len(sentences) > 1:
            for i in range(len(sentences)-1):
                # This would check for logical connections, for now just counting possible indicators
                if any(word in sentences[i].lower() for word in ['and', 'but', 'so', 'with']):
                    flow_indicators += 1

        flow_score = (transition_count + flow_indicators) / len(sentences) if sentences else 0

        analysis = {
            "transition_words_used": transition_count,
            "sentence_connections": flow_indicators,
            "transition_density": round(transition_count / len(sentences) if sentences else 0, 2),
            "sentence_connectivity_rate": round(flow_indicators / len(sentences) if sentences else 0, 2),
            "overall_flow_score": round(flow_score, 2)
        }

        return analysis

    def _enhance_narrative_flow(self, content: str, flow_target: str, flow_analysis: Dict[str, Any]) -> tuple:
        """Enhance narrative flow"""
        flow_improvements = []

        if flow_target in ["smooth", "cohesive"]:
            flow_improvements.append("Recommended additional transition words for smooth flow")
        elif flow_target == "dynamic":
            flow_improvements.append("Recommended varied sentence connections for dynamic flow")
        elif flow_target == "engaging":
            flow_improvements.append("Recommended improvements to maintain reader engagement")

        return content, flow_improvements

    def _identify_break_opportunities(self, content: str, break_type: str) -> List[Dict[str, Any]]:
        """Identify optimal places for breaks"""
        suggestions = []

        sentences = re.split(r'[.!?]+', content)
        words = content.split()

        # Break points could be based on plot beats, emotional beats, or logical breaks
        for i, sentence in enumerate(sentences):
            position = i / len(sentences) if sentences else 0
            word_pos = len(" ".join(sentences[:i]).split()) / len(words) if words else 0

            # These are basic markers, in reality it would need semantic understanding
            is_cliff_hanger = '?' in sentence or 'but' in sentence.lower()
            is_emphasis_point = not any(word in sentence.lower() for word in ['a', 'an', 'the', 'and', 'or', 'but'])

            if break_type == "scene" and any(indicator in sentence.lower() for indicator in ["meanwhile", "later", "back at", "suddenly", "but"]):
                suggestions.append({
                    "position": f"{word_pos:.1%}",
                    "sentence_index": i,
                    "reason": "Logical scene transition point",
                    "content_preview": sentence[:50]
                })
            elif break_type == "chapter" and position > 0.7:  # End of content as possible break
                suggestions.append({
                    "position": f"{word_pos:.1%}",
                    "sentence_index": i,
                    "reason": "Natural chapter break",
                    "content_preview": sentence[:50]
                })

        return suggestions

    def _analyze_structural_elements(self, content: str, structure_type: str) -> Dict[str, Any]:
        """Analyze structural elements of content"""
        if structure_type == "paragraphs":
            paragraphs = content.split('\n\n')
            analysis = {
                "total_paragraphs": len(paragraphs),
                "avg_paragraph_length": sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0,
                "paragraph_length_variance": sum(len(p.split())**2 for p in paragraphs)/len(paragraphs) - (sum(len(p.split()) for p in paragraphs)/len(paragraphs))**2 if paragraphs else 0
            }
        else:
            analysis = {
                "total_elements": len(content.split()),
                "avg_element_length": len(content.split()),
                "elements_analysis": "Basic structural analysis done"
            }

        return analysis

    def _improve_structural_flow(self, content: str, structure_type: str) -> tuple:
        """Improve structural flow of content"""
        optimizations = []

        if structure_type == "paragraphs":
            optimizations.append("Analyze paragraph length consistency")
            optimizations.append("Reorder paragraphs for better flow if needed")
        elif structure_type in ["sections", "beats", "scenes"]:
            optimizations.append("Review and optimize structural breaks")
            optimizations.append("Improve transitions between elements")

        return content, optimizations

    def _map_tension_over_content(self, content: str) -> List[Dict[str, Any]]:
        """Map tension level over different segments of content"""
        import re

        # Split content into segments
        sentences = re.split(r'[.!?]+', content)
        segment_size = max(1, len(sentences) // 5)  # Create ~5 segments

        tension_segments = []
        for i in range(0, len(sentences), segment_size):
            segment_sentences = sentences[i:i+segment_size]
            segment_text = " ".join(segment_sentences)

            # Very simplified tension scoring
            tension_indicators = [
                "danger", "fear", "anxiety", "threat", "unknown", "mystery",
                "risk", "secret", "hidden", "worry", "panic", "tense"
            ]
            score = sum(segment_text.lower().count(t) for t in tension_indicators)

            tension_segments.append({
                "segment": i//segment_size + 1,
                "tension_score": score / (len(segment_text.split()) + 1),  # Normalize by length
                "segment_preview": segment_text[:100]
            })

        return tension_segments

    def _suggest_tension_adjustments(self, tension_arc: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Suggest adjustments to improve tension arc"""
        suggestions = []

        if tension_arc:
            avg_tension = sum(seg["tension_score"] for seg in tension_arc) / len(tension_arc)

            # Identify segments that are significantly different from average
            for i, segment in enumerate(tension_arc):
                diff_from_avg = abs(segment["tension_score"] - avg_tension)
                if diff_from_avg > 0.3:  # Significant difference
                    suggestions.append({
                        "segment": segment["segment"],
                        "suggestion": "Add/Reduce tension elements in this segment" if segment["tension_score"] < avg_tension * 0.7 else "Maintain current tension level",
                        "current_score": segment["tension_score"],
                        "average_score": avg_tension
                    })

        return suggestions

    def recommend_pacing_for_genre(self, genre: str) -> Dict[str, Any]:
        """Provide genre-specific pacing recommendations"""
        pacing_recommendations = {
            "mystery": {
                "suspense_density": "high",
                "rhythm": "varied",  # Alternate between fast (reveals clues) and slow (building tension)
                "break_points": ["clue_discoveries", "red_herrings", "solutions_to_subplots"]
            },
            "romance": {
                "suspense_density": "moderate",
               "rhythm": "smooth",
                "break_points": ["emotional_revelations", "obstacle_introductions", "resolution_of_conflicts"]
            },
            "fantasy": {
                "suspense_density": "varied",
                "rhythm": "dynamic",
                "break_points": ["magical_reveals", "worldbuilding_exposition", "action_sequences"]
            },
            "sci_fi": {
                "suspense_density": "moderate_to_high",
                "rhythm": "deliberate_during_worldbuilding_urgent_during_action",
                "break_points": ["tech_explanation", "plot_advancement", "character_development"]
            },
            "thriller": {
                "suspense_density": "high",
                "rhythm": "fast_paced",
                "break_points": ["action_sequences", "character_revelations", "plot_twists"]
            }
        }

        return pacing_recommendations.get(genre.replace(" ", "_").lower(), {
            "suspense_density": "moderate",
            "rhythm": "balanced",
            "break_points": ["natural_transitions", "plot_milestones", "character_moments"]
        })

    def assess_pacing_balance(self, state: StoryState) -> Dict[str, Any]:
        """Asess the pacing balance of the entire story in the state"""
        # Count different element types across all chapters
        total_words = 0
        action_words = 0
        dialogue_words = 0
        descriptive_words = 0

        for chapter in state.chapters.values():
            content = chapter.content
            total_words += len(content.split())

            # Basic heuristics
            action_words += len([w for w in content.split() if w.lower() in ['ran', 'fought', 'hit', 'closed', 'entered', 'grabbed', 'suddenly', 'immediately']])
            dialogue_words += len(re.findall(r'"[^"]*"', content))

            # This is a very crude estimate of descriptive content
            descriptive_indicators = ['the', 'a', 'an', 'and', 'of', 'in', 'with', 'for', 'on']
            descriptive_words += len([w for w in content.split() if w.lower() in descriptive_indicators])

        balance = {
            "total_words": total_words,
            "estimated_action_ratio": action_words / total_words if total_words > 0 else 0,
            "estimated_dialogue_ratio": dialogue_words / total_words if total_words > 0 else 0,
            "estimated_descriptive_ratio": descriptive_words / total_words if total_words > 0 else 0
        }

        return balance