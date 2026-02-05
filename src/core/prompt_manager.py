"""System Prompt Manager for the novel writing system that loads prompts from MD files."""
import os
import re
from typing import Dict, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class PromptTemplate:
    """Container for a prompt template with system and user messages."""

    def __init__(self, system_prompt: str, user_prompt: str = ""):
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt

    def format(self, **kwargs) -> 'PromptTemplate':
        """Format the prompts with the given arguments."""
        formatted_system = self.system_prompt.format(**kwargs) if self.system_prompt else self.system_prompt
        formatted_user = self.user_prompt.format(**kwargs) if self.user_prompt else self.user_prompt
        return PromptTemplate(formatted_system, formatted_user)


class PromptManager:
    """Manages loading and formatting prompts from external MD files."""

    def __init__(self, prompts_dir: Optional[str] = None):
        """
        初始化 PromptManager
        :param prompts_dir: 存放提示词文件的目录，默认为 ./prompts
        """
        self.set_prompts_dir(prompts_dir or "./prompts")
        self._prompts_cache: Dict[str, PromptTemplate] = {}

        if not self.prompts_dir.exists():
            logger.warning(f"Prompts directory {self.prompts_dir} does not exist.")

    def set_prompts_dir(self, prompts_dir: str):
        """
        Set the prompts directory, ensuring it's stored as a Path object.
        :param prompts_dir: The path to the prompts directory
        """
        self.prompts_dir = Path(prompts_dir)

    def get_prompt_template(self, agent_name: str) -> PromptTemplate:
        """
        获取指定代理的完整提示词模板（包含系统和用户消息）

        :param agent_name: 代理名称 (如 'writer', 'editor', 'planner', etc.)
        :return: PromptTemplate对象
        """
        cache_key = agent_name.lower()
        if cache_key in self._prompts_cache:
            return self._prompts_cache[cache_key]

        # 查找可能的文件名
        possible_file_names = [
            f"{agent_name.capitalize()}.md",
            f"{agent_name.capitalize()}-zh.md",
            f"{agent_name.upper()}.md",
            f"{agent_name.capitalize()}.txt",
            f"{agent_name}.md",
        ]

        system_content = None
        user_content = None

        # 查找第一个存在的文件
        for file_name in possible_file_names:
            file_path = self.prompts_dir / file_name
            if file_path.exists():
                logger.info(f"Loading prompt from {file_path}")
                system_content, user_content = self._read_prompt_file(file_path)
                break
            else:
                logger.debug(f"Prompt file {file_path} not found")

        if system_content is None:
            # 如果没找到对应的文件，返回一个默认的系统提示词
            logger.warning(f"No prompt file found for agent '{agent_name}', falling back to a default prompt")
            system_content = self._get_default_system_prompt(agent_name)
            user_content = self._get_default_user_prompt(agent_name)

        prompt_template = PromptTemplate(system_content, user_content)
        self._prompts_cache[cache_key] = prompt_template

        return prompt_template

    def _read_prompt_file(self, file_path: Path) -> tuple[str, str]:
        """从MD文件中解析出系统和用户消息"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 尝试分离系统消息和用户消息
            # 常见的分隔方法：
            # 1. 搜索"## System Prompt" 或 "## User Prompt"
            # 2. 搜索"# 系统提示" 或 "# 用户提示"
            # 3. 使用文档结构来区分

            # 尝试按特定标记分割
            system_match = re.search(r'(?i)(?:##\s*System Prompt|##\s*系统提示|###? System|###? 系统):\s*\n(.*?)(?=\n##\s|\n###?\s|\Z)', content, re.DOTALL)
            user_match = re.search(r'(?i)(?:##\s*User Prompt|##\s*用户提示|###? User|###? 用户):\s*\n(.*?)(?=\n##\s|\n###?\s|\Z)', content, re.DOTALL)

            system_content = system_match.group(1).strip() if system_match else ""
            user_content = user_match.group(1).strip() if user_match else ""

            # 如果找不到标记，将所有内容作为系统内容
            if not system_content and not user_content:
                return content.strip(), ""

            return system_content.strip(), user_content.strip()

        except Exception as e:
            logger.error(f"Error reading prompt file {file_path}: {e}")
            return self._get_default_system_prompt(file_path.stem.lower().rstrip('-zh')), self._get_default_user_prompt(file_path.stem.lower().rstrip('-zh'))

    def _get_default_system_prompt(self, agent_name: str) -> str:
        """获取默认系统提示词"""
        defaults = {
            "writer": "你是一位专业的创意小说作家，负责生成高质量的叙事内容。请根据给定故事背景、大纲、角色等信息创作生动的小说片段",
            "editor": "你是一位专业的编辑，负责审查和改进文学作品，分析叙事结构、人物发展、情节连贯性等方面的问题",
            "planner": "你是一位专业的故事规划师，负责制定完整的故事大纲，包括角色发展弧线、情节线索、世界观构建等",
            "archivist": "你是一位档案管理员，负责维护故事连续性，跟踪角色、场景、事件和世界观设定的一致性",
            "consistency_checker": "你是一位一致性检查专家，专注于检查故事在逻辑、角色行为、世界观、时间线等方面的一致性问题",
            "dialogue_specialist": "你是一位对话专家，专门负责优化和提升角色对话的自然度和角色适配性",
            "world_builder": "你是一位世界构建师，专注于发展和完善故事情境的世界细节，包括地理、文化、规则等",
            "pacing_advisor": "你是一位节奏顾问，专注分析和调节故事节奏，确保张弛适度和读者参与感",
            "humanizer": "你是一位人性化编辑，专注移除AI写作痕迹，使内容更自然人性化，消除机械化表述"
        }

        return defaults.get(agent_name.lower(), f"你是负责{agent_name}任务的专业助理，请提供专业的内容生成或分析结果。")

    def _get_default_user_prompt(self, agent_name: str) -> str:
        """获取默认用户提示词"""
        return f"基于当前故事状态（情节、角色、世界观等）为{agent_name}任务执行操作。"

    def refresh_cache(self):
        """刷新提示词缓存"""
        self._prompts_cache.clear()

# 全局单例
prompt_manager = PromptManager()