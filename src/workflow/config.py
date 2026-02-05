"""
Configurable settings for the LangGraph workflow
"""
import os
from typing import Optional

from .constants import *


class WorkflowConfig:
    """Configuration class for workflow-specific settings."""

    def __init__(self):
        # Loop prevention settings
        self.loop_detection_threshold: int = int(os.getenv("LOOP_DETECTION_THRESHOLD", str(LOOP_DETECTION_THRESHOLD)))
        self.max_related_nodes_sequence: int = int(os.getenv("MAX_RELATED_NODES_SEQUENCE", str(MAX_RELATED_NODES_SEQUENCE)))
        self.infinite_loop_safety_factor: int = int(os.getenv("INFINITE_LOOP_SAFETY_FACTOR", str(INFINITE_LOOP_SAFETY_FACTOR)))

        # Chapter content settings
        self.chapter_normalization_factor: int = int(os.getenv("CHAPTER_NORMALIZATION_FACTOR", str(CHAPTER_LENGTH_NORMALIZATION_FACTOR)))
        self.chapter_size_threshold: int = int(os.getenv("CHAPTER_SIZE_THRESHOLD", str(DEFAULT_CHAPTER_SIZE_THRESHOLD)))
        self.chapter_content_snippet_limit: int = int(os.getenv("CHAPTER_CONTENT_SNIPPET_LIMIT", str(DEFAULT_CONTENT_SNIPPET_LIMIT)))

        # Progress thresholds
        self.macro_completion_chapters_count: int = int(os.getenv("MACRO_COMPLETION_CHAPTERS_COUNT", str(MACRO_COMPLETION_CHAPTERS_COUNT)))
        self.macro_min_character_count: int = int(os.getenv("MACRO_MIN_CHARACTER_COUNT", str(MACRO_MIN_CHARACTER_COUNT)))
        self.macro_min_world_details_count: int = int(os.getenv("MACRO_MIN_WORLD_DETAILS_COUNT", str(MACRO_MIN_WORLD_DETAILS_COUNT)))
        self.chapter_completion_threshold: float = float(os.getenv("CHAPTER_COMPLETION_THRESHOLD", str(DEFAULT_CHAPTER_COMPLETION_THRESHOLD)))
        self.macro_phase_completion_threshold: float = float(os.getenv("MACRO_PHASE_COMPLETION_THRESHOLD", str(MACRO_PHASE_COMPLETION_THRESHOLD)))
        self.mid_phase_completion_threshold: float = float(os.getenv("MID_PHASE_COMPLETION_THRESHOLD", str(MID_PHASE_COMPLETION_THRESHOLD)))
        self.micro_phase_completion_threshold: float = float(os.getenv("MICRO_PHASE_COMPLETION_THRESHOLD", str(MICRO_PHASE_COMPLETION_THRESHOLD)))

        # Agent-specific configuration
        self.agent_response_snippet_limit: int = int(os.getenv("AGENT_RESPONSE_SNIPPET_LIMIT", str(AGENT_RESPONSE_SNIPPET_LIMIT)))
        self.pacing_advisor_excerpt_limit: int = int(os.getenv("PACING_ADVISOR_EXCERPT_LIMIT", str(PACING_ADVISOR_EXCERPT_LIMIT)))

        # Phase management configuration
        self.min_story_outline_chapters: int = int(os.getenv("MIN_STORY_OUTLINE_CHAPTERS", str(MIN_STORY_OUTLINE_CHAPTERS)))
        self.max_chapters_target: int = int(os.getenv("MAX_CHAPTERS_TARGET", str(MAX_CHAPTERS_TARGET_DEFAULT)))
        self.target_mid_completion: int = int(os.getenv("TARGET_MID_COMPLETION", str(TARGET_MID_COMPLETION_DEFAULT)))
        self.progress_threshold_for_transition: float = float(os.getenv("PROGRESS_THRESHOLD_FOR_TRANSITION", str(PROGRESS_THRESHOLD_FOR_TRANSITION)))

        # Default phase values
        self.default_max_iterations: int = int(os.getenv("WORKFLOW_MAX_ITERATIONS", str(DEFAULT_MAX_ITERATIONS)))
        self.default_content_snippet_limit: int = int(os.getenv("DEFAULT_CONTENT_SNIPPET_LIMIT", str(DEFAULT_CONTENT_SNIPPET_LIMIT)))
        self.default_min_content_threshold: int = int(os.getenv("DEFAULT_MIN_CONTENT_THRESHOLD", str(DEFAULT_MIN_CONTENT_THRESHOLD)))

        # Progress calculation multipliers
        self.macro_outline_progress_multiplier: float = float(os.getenv("MACRO_OUTLINE_PROGRESS_MULTIPLIER", str(MACRO_OUTLINE_PROGRESS_MULTIPLIER)))
        self.macro_world_progress_multiplier: float = float(os.getenv("MACRO_WORLD_PROGRESS_MULTIPLIER", str(MACRO_WORLD_PROGRESS_MULTIPLIER)))
        self.macro_characters_progress_multiplier: float = float(os.getenv("MACRO_CHARACTERS_PROGRESS_MULTIPLIER", str(MACRO_CHARACTERS_PROGRESS_MULTIPLIER)))
        self.macro_arc_progress_multiplier: float = float(os.getenv("MACRO_ARC_PROGRESS_MULTIPLIER", str(MACRO_ARC_PROGRESS_MULTIPLIER)))

        # Phase transition settings
        self.micro_completion_factor: float = float(os.getenv("MICRO_COMPLETION_FACTOR", str(DEFAULT_MICRO_COMPLETION_FACTOR)))
        self.progress_increment_macro: float = float(os.getenv("PROGRESS_INCREMENT_MACRO", str(DEFAULT_PROGRESS_INCREMENT_MACRO)))
        self.progress_increment_world: float = float(os.getenv("PROGRESS_INCREMENT_WORLD", str(DEFAULT_PROGRESS_INCREMENT_WORLD)))
        self.progress_increment_characters: float = float(os.getenv("PROGRESS_INCREMENT_CHARACTERS", str(DEFAULT_PROGRESS_INCREMENT_CHARACTERS)))
        self.progress_increment_arc: float = float(os.getenv("PROGRESS_INCREMENT_ARC", str(DEFAULT_PROGRESS_INCREMENT_ARC)))

        # Cycle protection parameters
        self.max_iterations_per_node: int = int(os.getenv("MAX_ITERATIONS_PER_NODE", str(MAX_ITERATIONS_PER_NODE)))
        self.node_execution_sequence_limit: int = int(os.getenv("NODE_EXECUTION_SEQUENCE_LIMIT", str(NODE_EXECUTION_SEQUENCE_LIMIT)))

        # Agent phase mapping thresholds
        self.world_builder_threshold: int = int(os.getenv("WORLD_BUILDER_PHASE_THRESHOLD", str(WORLD_BUILDER_PHASE_THRESHOLD)))
        self.character_development_threshold: int = int(os.getenv("CHARACTER_DEVELOPMENT_THRESHOLD", str(CHARACTER_DEVELOPMENT_THRESHOLD)))
        self.story_outline_chapters_threshold: int = int(os.getenv("STORY_OUTLINE_CHAPTERS_THRESHOLD", str(STORY_OUTLINE_CHAPTERS_THRESHOLD)))

        # Chapter planning thresholds
        self.min_chapter_words_for_completion: int = int(os.getenv("MIN_CHAPTER_WORDS_FOR_COMPLETION", str(MIN_CHAPTER_WORDS_FOR_COMPLETION)))