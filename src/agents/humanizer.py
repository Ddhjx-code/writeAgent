from typing import Dict, Any, List
import json
from ..novel_types import AgentResponse
from ..config import Config
from .base import BaseAgent


class HumanizerAgent(BaseAgent):
    """Humanizer agent that removes AI writing traces to make text sound more natural and human."""

    def __init__(self, config: Config):
        super().__init__("humanizer", config)

    async def process(self, state: Dict[str, Any]) -> AgentResponse:
        """Remove AI writing traces to make content sound more natural and human."""
        try:
            # Build context for the humanizer
            context = self._build_context(state)

            # Get the content to humanize
            content_to_humanize = state.get('current_chapter', '') or state.get('content', '')

            if not content_to_humanize:
                return AgentResponse(
                    agent_name=self.name,
                    content="",
                    reasoning="No content provided to humanize",
                    status="success"
                )

            # Get the prompt template
            prompt = self.get_prompt()

            # Format the prompt with the content
            formatted_prompt = prompt.format(
                original_content=content_to_humanize
            )

            # Call the actual LLM with the formatted prompt
            response_content = await self.llm.acall(formatted_prompt, self.config.default_writer_model)

            # The response should be the humanized content
            # We can apply basic checks to see if AI traces were removed
            original_length = len(content_to_humanize)
            humanized_length = len(response_content)
            changes_summary = []

            if original_length > humanized_length:
                changes_summary.append("Reduced excessive content")

            return AgentResponse(
                agent_name=self.name,
                content=response_content,
                reasoning="Applied humanization techniques to remove AI writing patterns and make text sound more natural using LLM analysis",
                suggestions=changes_summary + ["AI text humanization applied via LLM processing"],
                status="success"
            )
        except Exception as e:
            return AgentResponse(
                agent_name=self.name,
                content="",
                reasoning=f"Error in HumanizerAgent processing: {str(e)}",
                status="failed"
            )

    def _humanize_text(self, original_text: str) -> str:
        """Apply humanization techniques to remove AI writing traces."""
        if not original_text or not isinstance(original_text, str):
            return original_text

        # Import here to avoid circular dependencies in the final system
        import re

        # This is a simplified implementation - in a real system, we would implement all the techniques from Humanizer-zh.md
        processed_text = original_text

        # Remove common AI fillers and patterns
        patterns_to_remove = [
            # Remove "As a professional writer..." introductions
            r"(As an? [^,]+,? )|(This is a professional )",
            # Remove AI sign-off phrases
            r"(Hope this helps!?)|(Please let me know if you need any modifications)",
            # Remove generic phrases
            r"(In today's world)|(In the current landscape)",
        ]

        for pattern in patterns_to_remove:
            processed_text = re.sub(pattern, "", processed_text, flags=re.IGNORECASE)
            processed_text.replace(r"\s+", " ").strip()  # Clean up spaces after removals

        # In a real implementation, we would apply all techniques from Humanizer-zh.md here
        return processed_text.strip()

    def _analyze_changes(self, original: str, humanized: str) -> List[str]:
        """Analyze what changes were made during humanization."""
        changes = []

        # Simple comparison for this implementation
        original_length = len(original)
        humanized_length = len(humanized)

        if original_length > humanized_length:
            changes.append("Reduced excessive content")

        # Check for specific AI patterns removal
        import re
        ai_intro_patterns = [
            r"(As an? [^,]+,? )",
            r"(In today's world)",
            r"(It is important to note)"
        ]

        for pattern in ai_intro_patterns:
            if re.search(pattern, original, re.IGNORECASE) and not re.search(pattern, humanized, re.IGNORECASE):
                changes.append("Removed AI introduction patterns")

        return changes

    def get_prompt(self) -> str:
        """Return the prompt for the Humanizer agent based on Humanizer-zh.md."""
        return """
        您是一位文字编辑，专门识别和去除 AI 生成文本的痕迹，使文字听起来更自然、更有人味。本指南基于维基百科的"AI 写作特征"页面，由 WikiProject AI Cleanup 维护。

        ## 任务
        当收到需要人性化处理的文本时：

        1. **识别 AI 模式** - 扫描下面列出的模式
        2. **重写问题片段** - 用自然的替代方案替换 AI 痕迹
        3. **保留含义** - 保持核心信息完整
        4. **维持语调** - 匹配预期的语气（正式、随意、技术等）
        5. **注入灵魂** - 不仅要去除不良模式，还要注入真实的个性

        ---

        以下是需要处理的原始内容：

        {original_content}

        ---

        ## 处理方法

        1. **过早强调意义** - 如 "标志着关键时刻"、"充当"、"体现其重要性" 等
        2. **过度强调知名度** - 用具体的引用替代模糊的 "广泛报道"、"知名专家" 等
        3. **-ing 结尾的肤浅分析** - 避免无意义的 "-ing" 短语堆砌
        4. **宣传式语言** - 如 "令人叹为观止"、"必游之地"、"富有活力" 等
        5. **模糊归因** - 如 "专家认为"、"观察者指出" 等，替换为具体信息
        6. **公式化结构** - 避免 "挑战与展望" 等固定模式
        7. **高频 AI 词汇** - 如 "此外、至关重要、深入探讨、强调" 等
        8. **系动词回避** - 避免用复杂结构替代简单的 "是/有"
        9. **重复性排比** - 避免 "不仅...而且..." 等过度使用
        10. **三段式法则** - 避免强行分成三个方面
        11. **同义词循环** - 避免同义替换
        12. **虚假范围** - 避免 "从X到Y" 的夸张结构
        13. **破折号过度使用** - 减少无意义的破折号
        14. **过度强调** - 减少标题化和过度修饰
        15. **协作痕迹** - 消除聊天机器人风格的语言

        应用人性化处理后，文字应具备:
        - 有观点和个性的表达
        - 变化的句子节奏
        - 承认复杂性和不确定性
        - 适当的主观性
        - 允许一些混乱，体现人的真实思考过程
        - 具体而非笼统的情感描述
        """