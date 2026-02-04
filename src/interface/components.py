"""UI组件定义 - 原Gradio定义，现为React前端提供参考

该文件包含原Gradio组件定义，
现已重构为React组件结构和API规范的参考。
"""

from typing import Dict, Any, List, Optional
from ..novel_types import StoryState


def get_story_input_fields():
    """返回故事输入字段定义 (供前端参考)"""
    return {
        "title": {
            "type": "text",
            "label": "故事标题",
            "placeholder": "Enter the title of your story...",
            "required": True
        },
        "genre": {
            "type": "select",
            "label": "故事类型",
            "options": [
                "Fantasy", "Science Fiction", "Mystery", "Romance",
                "Thriller", "Literary Fiction", "Historical", "Horror", "Other"
            ],
            "default": "Fantasy"
        },
        "description": {
            "type": "textarea",
            "label": "故事描述",
            "placeholder": "Briefly describe your story concept...",
            "rows": 3
        },
        "target_length": {
            "type": "slider",
            "label": "目标字数",
            "min": 1000,
            "max": 100000,
            "step": 1000,
            "default": 10000
        }
    }


def get_outline_fields():
    """返回大纲字段定义 (供前端参考)"""
    return {
        "outline_input": {
            "type": "textarea",
            "label": "大纲",
            "placeholder": "Provide a brief outline of your story, or leave empty for AI to generate...",
            "rows": 5
        },
        "chapters_count": {
            "type": "slider",
            "label": "章节数量",
            "min": 1,
            "max": 30,
            "default": 10,
            "step": 1
        },
        "pov_character": {
            "type": "text",
            "label": "视角角色",
            "placeholder": "Which character will be the main POV?"
        }
    }


def get_character_fields():
    """返回角色字段定义 (供前端参考)"""
    return {
        "character_name": {
            "type": "text",
            "label": "角色姓名",
            "placeholder": "输入角色姓名"
        },
        "character_role": {
            "type": "select",
            "label": "角色职能",
            "options": ["Protagonist", "Antagonist", "Supporting", "Minor", "Other"],
            "default": "Protagonist"
        },
        "character_description": {
            "type": "textarea",
            "label": "角色描述",
            "placeholder": "描述角色特征...",
            "rows": 3
        }
    }


def get_agent_controls():
    """返回AI代理控制字段定义 (供前端参考)"""
    return {
        "agent_statuses": {
            "type": "select",
            "label": "代理状态配置",
            "options": ["All Active", "Writer Only", "Planner Only", "Editor Only", "All Agents", "Custom"],
            "default": "All Active"
        },
        "agent_speed": {
            "type": "slider",
            "label": "代理处理速度",
            "min": 1,
            "max": 10,
            "default": 5,
            "step": 1
        }
    }