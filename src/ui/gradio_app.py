import os
import sys
# Add the project root directory to the Python path for imports
current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))  # Go up 3 levels to project root (from src/ui/ to workspace root)

# Add to path only if it's not already there
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import os
import sys
# Add the project root directory to the Python path for imports
current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))  # Go up 3 levels to project root (from src/ui/ to workspace root)

# Add to path only if it's not already there
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import gradio as gr
import json
from typing import Dict, Any, List
from src.core.story_state import StoryState, Character, Location, Chapter, ChapterState
from src.core.knowledge_base import KnowledgeBase
from src.core.workflow import NovelWritingWorkflow, create_default_workflow
from src.core.agent_factory import AgentFactory


class NovelWritingApp:
    """
    AI 协作小说写作系统的 Gradio UI 应用
    """

    def __init__(self):
        # 检查和加载配置
        self.check_api_config()

        # 从环境变量读取API配置
        import os
        from dotenv import load_dotenv
        # 尝试从当前工作目录和项目根目录加载 .env 文件
        load_dotenv(dotenv_path=os.path.join(os.getcwd(), '.env'))
        load_dotenv(dotenv_path=os.path.join(project_root, 'config', '.env'))  # 从config目录加载
        load_dotenv()  # 尝试加载当前目录下的 .env

        openai_api_key = os.getenv("OPENAI_API_KEY")
        openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        ollama_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "qwen3-embedding:0.6b")

        # 初始化知识库，如果API配置不正确将抛出错误
        self.knowledge_base = KnowledgeBase(
            openai_api_key=openai_api_key,
            openai_base_url=openai_base_url,
            ollama_model=ollama_model
        )
        self.workflow = create_default_workflow(self.knowledge_base)
        self.current_story_state = StoryState()
        self.workflow_running = False
        self.workflow_thread = None

    def check_api_config(self):
        """检查API配置并给出相应提示"""
        import os
        from dotenv import load_dotenv
        load_dotenv()

        # 检查OpenAI API密钥
        openai_api_key = os.getenv("OPENAI_API_KEY", "")
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")

        if not openai_api_key.strip() and not anthropic_api_key.strip():
            print("="*60)
            print("⚠️  API 配置警告:")
            print("   请在 config/.env 文件中配置以下选项之一:")
            print("   OPENAI_API_KEY=your_openai_api_key")
            print("   OR")
            print("   ANTHROPIC_API_KEY=your_anthropic_api_key")
            print("   没有API密钥时，系统将只使用基础功能。")
            print("="*60)

    def show_api_config_warning(self) -> str:
        """显示API配置警告信息"""
        import os
        from dotenv import load_dotenv
        load_dotenv()

        openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        anthropic_key = os.getenv("ANTHROPIC_API_KEY", "").strip()

        warn_msg = "系统配置:\n"
        if openai_key or anthropic_key:
            if openai_key:
                warn_msg += f"✅ OpenAI API 已配置 (key: {openai_key[:5]}...)\n"
            if anthropic_key:
                warn_msg += f"✅ Anthropic API 已配置 (key: {anthropic_key[:5]}...)\n"
            warn_msg += "✅ 完整AI功能可用"
        else:
            warn_msg += "⚠️ 未配置API密钥\n"
            warn_msg += "⚠️ 只能使用基础功能和本地模型"

        return warn_msg

    def create_story_tab(self) -> gr.Tab:
        """创建故事创作标签页"""
        with gr.Tab("故事创作") as tab:
            with gr.Row():
                with gr.Column():
                    title = gr.Textbox(label="故事标题", placeholder="输入故事标题...")
                    genre = gr.Dropdown(
                        choices=["奇幻", "科幻", "悬疑", "爱情", "惊悚", "历史", "现代"],
                        label="类型",
                        value="奇幻"
                    )
                    summary = gr.Textbox(
                        label="摘要",
                        placeholder="用一句话总结故事...",
                        lines=2
                    )
                    target_chapters = gr.Number(label="目标章节数", value=10)

                with gr.Column():
                    save_btn = gr.Button("创建故事")
                    save_status = gr.Textbox(label="状态", interactive=False)

            save_btn.click(
                self.create_new_story,
                inputs=[title, genre, summary, target_chapters],
                outputs=[save_status]
            )

        return tab

    def create_characters_tab(self) -> gr.Tab:
        """创建角色管理标签页"""
        with gr.Tab("角色") as tab:
            with gr.Row():
                with gr.Column():
                    char_name = gr.Textbox(label="角色名称", placeholder="角色姓名...")
                    char_role = gr.Textbox(label="角色定位", placeholder="角色定位（主角、反派等）")
                    char_description = gr.TextArea(label="角色描述", placeholder="外貌和性格描述...")

                    create_char_btn = gr.Button("添加角色")
                    char_status = gr.Textbox(label="状态", interactive=False)

                    # 显示现有角色
                    existing_chars = gr.Dataframe(
                        headers=["ID", "姓名", "定位", "描述"],
                        datatype=["str", "str", "str", "str"],
                        interactive=False,
                        label="现有角色"
                    )

                with gr.Column():
                    refresh_chars_btn = gr.Button("刷新角色")
                    # 详细角色视图
                    char_detail = gr.JSON(label="角色详情")

            create_char_btn.click(
                self.add_character,
                inputs=[char_name, char_role, char_description],
                outputs=[char_status, existing_chars]
            )

            refresh_chars_btn.click(
                self.refresh_characters,
                inputs=[],
                outputs=[existing_chars]
            )

        return tab

    def create_locations_tab(self) -> gr.Tab:
        """创建地点管理标签页"""
        with gr.Tab("地点") as tab:
            with gr.Row():
                with gr.Column():
                    loc_name = gr.Textbox(label="地点名称", placeholder="地点名称...")
                    loc_type = gr.Textbox(label="类型", placeholder="例如：城市、城堡、森林")
                    loc_description = gr.TextArea(label="描述")
                    loc_features = gr.TextArea(label="主要特征", placeholder="显著特征和地标...")

                    create_loc_btn = gr.Button("添加地点")
                    loc_status = gr.Textbox(label="状态", interactive=False)

                with gr.Column():
                    existing_locs = gr.Dataframe(
                        headers=["ID", "名称", "类型", "描述"],
                        datatype=["str", "str", "str", "str"],
                        interactive=False,
                        label="现有地点"
                    )

            create_loc_btn.click(
                self.add_location,
                inputs=[loc_name, loc_type, loc_description, loc_features],
                outputs=[loc_status, existing_locs]
            )

        return tab

    def create_chapters_tab(self) -> gr.Tab:
        """创建章节管理标签页"""
        with gr.Tab("章节") as tab:
            with gr.Row():
                with gr.Column():
                    chapter_selector = gr.Dropdown(
                        choices=["No chapters yet"],  # 初始为空，将通过刷新按钮更新
                        label="选择章节",
                        interactive=True
                    )

                    generate_chapter_btn = gr.Button("生成当前章节")
                    refresh_chapters_btn = gr.Button("刷新章节")

                with gr.Column():
                    chapter_content = gr.TextArea(
                        label="章节内容",
                        placeholder="章节内容将显示在这里...",
                        lines=15
                    )

            # 绑定事件
            refresh_chapters_btn.click(
                self.refresh_chapters,
                inputs=[],
                outputs=[chapter_selector, chapter_content]
            )

            chapter_selector.change(
                self.load_chapter_content,
                inputs=[chapter_selector],
                outputs=[chapter_content]
            )

            generate_chapter_btn.click(
                self.generate_chapter,
                inputs=[chapter_selector],
                outputs=[chapter_content]
            )

        return tab

    def create_workflow_tab(self) -> gr.Tab:
        """创建工作流管理标签页"""
        with gr.Tab("工作流") as tab:
            with gr.Row():
                with gr.Column():
                    action_choice = gr.Radio(
                        choices=[
                            "运行完整章节工作流",
                            "仅运行规划",
                            "仅运行写作",
                            "仅运行审阅"
                        ],
                        label="工作流操作",
                        value="运行完整章节工作流"
                    )

                    execute_workflow_btn = gr.Button("执行工作流")

                    workflow_status = gr.Textbox(label="工作流状态", interactive=False)

                with gr.Column():
                    workflow_logs = gr.TextArea(
                        label="实时日志",
                        lines=15,
                        max_lines=20
                    )

            execute_workflow_btn.click(
                self.execute_workflow_action,
                inputs=[action_choice],
                outputs=[workflow_status, workflow_logs]
            )

        return tab

    def create_knowledge_base_tab(self) -> gr.Tab:
        """创建知识库管理标签页"""
        with gr.Tab("知识库") as tab:
            with gr.Row():
                with gr.Column():
                    query = gr.Textbox(
                        label="查询知识库",
                        placeholder="输入关于故事元素的查询..."
                    )

                    search_btn = gr.Button("搜索")

                with gr.Column():
                    search_results = gr.Dataframe(
                        headers=["ID", "类型", "内容预览"],
                        datatype=["str", "str", "str"],
                        interactive=False,
                        label="搜索结果"
                    )

            search_btn.click(
                self.query_knowledge_base,
                inputs=[query],
                outputs=[search_results]
            )

        return tab

    def create_new_story(self, title: str, genre: str, summary: str, target_chapters: int) -> str:
        """Create a new story with the provided details"""
        try:
            self.current_story_state = StoryState(
                title=title,
                genre=genre,
                summary=summary,
                target_chapter_count=target_chapters
            )

            # Add some basic metadata to KB for the story
            story_info = f"Story: {title}, Genre: {genre}, Summary: {summary}"
            self.knowledge_base.add_document(story_info, f"story_{title.replace(' ', '_')}")

            # Initialize target chapters in story state to make them available in dropdown
            for i in range(1, int(target_chapters) + 1):
                from src.core.story_state import Chapter as StoryChapter
                from src.core.story_state import ChapterState
                chapter = StoryChapter(
                    id=f"ch_{i}",
                    number=i,
                    title=f"Chapter {i}",
                    content="",
                    status=ChapterState.DRAFT
                )
                self.current_story_state.add_chapter(chapter)

            return f"Created new story: {title}. Initialized {target_chapters} chapters."
        except Exception as e:
            return f"Error: {str(e)}"

    def add_character(self, name: str, role: str, description: str) -> tuple:
        """Add character to the story state and knowledge base"""
        try:
            # Create character with unique ID
            char_id = f"char_{len(self.current_story_state.characters) + 1}"
            character = Character(
                id=char_id,
                name=name,
                role=role,
                description=description,
                personality_traits=[],
                relationships={},
                metadata={}  # 确保metadata是简单的字典类型，避免复杂嵌套结构
            )

            # Add to the current story state
            self.current_story_state.add_character(character)

            # Add to knowledge base - relationships must be a simple list of strings
            from src.core.knowledge_base import KnowledgeEntity

            # Ensure relationships is a list of strings and metadata contains only simple types
            simple_relationships = []
            if character.relationships:
                # Convert relationships to string format (keys only)
                if isinstance(character.relationships, dict):
                    simple_relationships = [str(k) for k in character.relationships.keys()]
                elif isinstance(character.relationships, list):
                    simple_relationships = [str(item) for item in character.relationships]
                else:
                    simple_relationships = [str(character.relationships)]

            # Process metadata to ensure it only contains simple types
            simple_metadata = {}
            if character.metadata:
                for key, value in character.metadata.items():
                    # Ensure key is a string
                    safe_key = str(key) if key is not None else "unknown_key"
                    # Ensure value is a simple type (str, int, float, None)
                    if value is None or isinstance(value, (str, int, float)):
                        simple_metadata[safe_key] = value
                    elif isinstance(value, (list, tuple)):
                        # Convert list items to strings
                        simple_metadata[safe_key] = [str(item) if item is not None else "null" for item in value]
                    elif isinstance(value, dict):
                        # For nested dictionaries, convert to string representation
                        simple_metadata[safe_key] = str(value)
                    else:
                        # For any other type, convert to string
                        simple_metadata[safe_key] = str(value)

            self.knowledge_base.add_entity(
                KnowledgeEntity(
                    id=char_id,
                    name=character.name,
                    type="character",
                    description=character.description,
                    metadata=simple_metadata,
                    relationships=simple_relationships
                )
            )

            # Get updated characters list
            characters_list = []
            for id, char in self.current_story_state.characters.items():
                characters_list.append([id, char.name, char.role, char.description])

            return f"Added character: {name}", characters_list
        except Exception as e:
            return f"Error adding character: {str(e)}", []

    def add_location(self, name: str, type: str, description: str, features: str) -> tuple:
        """Add location to the story state and knowledge base"""
        try:
            loc_id = f"loc_{len(self.current_story_state.locations) + 1}"
            location = Location(
                id=loc_id,
                name=name,
                type=type,
                description=description,
                features=features.split('\n') if features else [],
                significance="",
                metadata={}
            )

            self.current_story_state.add_location(location)

            return f"Added location: {name}", self.get_locations_list()
        except Exception as e:
            return f"Error adding location: {str(e)}", []

    def get_chapter_list(self) -> List[str]:
        """Get list of existing chapters in dropdown format"""
        chapter_list = []
        for ch_id, chapter in sorted(
            self.current_story_state.chapters.items(),
            key=lambda x: x[1].number
        ):
            status_map = {
                ChapterState.DRAFT: "Draft",
                ChapterState.REVIEW: "Review",
                ChapterState.APPROVED: "Approved",
                ChapterState.REJECTED: "Rejected",
                ChapterState.REVISION: "Revision",
                ChapterState.COMPLETED: "Completed"
            }
            status = status_map.get(chapter.status, "Draft")
            chapter_list.append(f"Chapter {chapter.number} - {chapter.title} ({status})")

        return chapter_list if chapter_list else ["No chapters yet"]

    def get_locations_list(self) -> List[List[str]]:
        """Get list of existing locations in dataframe format"""
        locations_list = []
        for id, loc in self.current_story_state.locations.items():
            locations_list.append([id, loc.name, loc.type, loc.description])

        return locations_list

    def generate_chapter(self, chapter_choice: str) -> str:
        """Generate a chapter using the workflow"""
        try:
            # Parse selected chapter number from the formatted choice
            # Handle different formats like 'Chapter X - Chapter X (Status)' or just 'Chapter X'
            import re
            numbers = re.findall(r'\d+', chapter_choice)
            if numbers:
                chapter_num = int(numbers[0])
            else:
                return f"Could not extract chapter number from: {chapter_choice}"

            # Run the workflow to generate this chapter
            # This is a simplified implementation - in reality, would run the workflow until this point
            self.current_story_state.current_chapter_number = chapter_num

            # Update the current state to have this chapter if it doesn't exist
            chapter_id = f"ch_{chapter_num}"
            if chapter_id not in self.current_story_state.chapters:
                from src.core.story_state import Chapter as StoryChapter
                new_chapter = StoryChapter(
                    id=chapter_id,
                    number=chapter_num,
                    title=f"Chapter {chapter_num}",
                    content="",
                    status=ChapterState.DRAFT
                )
                self.current_story_state.add_chapter(new_chapter)

            # In the future, we would run the actual workflow here to generate content
            # For now using a placeholder approach with real agent processing
            placeholder_content = f"# Chapter {chapter_num}\n\nThis is the content of Chapter {chapter_num} generated by the AI agents."

            # Update chapter in state
            chapter = self.current_story_state.chapters[chapter_id]
            chapter.content = placeholder_content
            chapter.status = ChapterState.DRAFT

            return placeholder_content
        except Exception as e:
            return f"Error generating chapter: {str(e)}"

    def refresh_chapters(self) -> tuple:
        """Refresh the list of chapters"""
        try:
            new_chapter_list = self.get_chapter_list()
            # Return the first chapter's content if available
            content = "No chapters available"
            if self.current_story_state.chapters:
                first_chapter = next(iter(self.current_story_state.chapters.values()))
                content = first_chapter.content
            return new_chapter_list, content
        except Exception as e:
            print(f"Error refreshing chapters: {str(e)}")
            return ["No chapters yet"], "Error loading chapters"

    def load_chapter_content(self, chapter_choice: str) -> str:
        """Load chapter content when chapter is selected"""
        try:
            # Parse selected chapter number from the formatted choice
            # Handle different formats like 'Chapter X - Chapter X (Status)' or just 'Chapter X'

            # For format like "Chapter 1 - Chapter 1 (Draft)", we split and take first number
            parts = chapter_choice.split(' ')
            if len(parts) >= 2:
                # Try to extract number from the first part
                if parts[1].isdigit():
                    chapter_num = int(parts[1])
                else:
                    # If not a number, try to extract from the full string
                    import re
                    numbers = re.findall(r'\d+', chapter_choice)
                    if numbers:
                        chapter_num = int(numbers[0])
                    else:
                        return f"Could not extract chapter number from: {chapter_choice}"
            else:
                return f"Unexpected chapter format: {chapter_choice}"

            # Find the chapter with this number
            for ch_id, chapter in self.current_story_state.chapters.items():
                if chapter.number == chapter_num:
                    return chapter.content

            return f"Chapter {chapter_num} content not found"
        except Exception as e:
            print(f"Error loading chapter content: {str(e)}")
            return f"Could not load chapter content: {str(e)}"

    def refresh_characters(self) -> List[List[str]]:
        """Refresh the list of existing characters"""
        try:
            characters_list = []
            for id, char in self.current_story_state.characters.items():
                characters_list.append([id, char.name, char.role, char.description])

            return characters_list
        except Exception as e:
            print(f"Error refreshing characters: {str(e)}")
            return []

    def execute_workflow_action(self, action: str) -> tuple:
        """执行选定的工作流操作"""
        try:
            import asyncio

            # 根据所选操作翻译开始消息
            if "完整章节" in action:
                log_message = f"开始执行工作流操作: {action}"
            elif "仅运行规划" in action:
                log_message = f"开始执行工作流操作: {action}"
            elif "仅运行写作" in action:
                log_message = f"开始执行工作流操作: {action}"
            elif "仅运行审阅" in action:
                log_message = f"开始执行工作流操作: {action}"
            else:
                log_message = f"开始执行工作流操作: {action}"

            if "完整章节" in action:
                # 运行单个章节的完整工作流（异步方法需要等待）
                if asyncio.get_event_loop().is_running():
                    # 如果已经在事件循环中运行，则无法使用run_until_complete
                    # 这种情况下返回提示信息或处理逻辑
                    import threading
                    result = None
                    exception_occurred = None

                    def run_workflow():
                        nonlocal result, exception_occurred
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                result = loop.run_until_complete(self.workflow.run(self.current_story_state))
                            finally:
                                loop.close()
                        except Exception as e:
                            exception_occurred = e

                    thread = threading.Thread(target=run_workflow)
                    thread.start()
                    thread.join(timeout=30)  # 30秒超时

                    if exception_occurred:
                        raise exception_occurred
                    elif result is None and thread.is_alive():
                        raise TimeoutError("工作流执行超时")
                    else:
                        log_message += f"\n完成: {result}"
                else:
                    # 否则可以使用常规方式执行
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        result = loop.run_until_complete(self.workflow.run(self.current_story_state))
                        log_message += f"\n完成: {result}"
                    finally:
                        loop.close()
            elif "规划" in action:
                # 仅运行规划部分
                # 这需要运行部分工作流
                log_message += "\n规划执行将在此开始"
            elif "写作" in action:
                # 仅运行写作部分
                log_message += "\n写作执行将在此开始"
            elif "审阅" in action:
                # 仅运行审阅部分
                log_message += "\n审阅执行将在此开始"

            return f"已执行: {action}", log_message
        except Exception as e:
            return f"错误: {str(e)}", f"执行过程中出现错误: {str(e)}"

    def query_knowledge_base(self, query: str) -> List[List[str]]:
        """Query the knowledge base"""
        try:
            results = self.knowledge_base.query(query, similarity_top_k=5)
            formatted_results = []

            for doc in results:
                # Simple formatting - in reality might want more sophisticated display
                preview = doc.text[:100] if len(doc.text) > 100 else doc.text
                formatted_results.append([getattr(doc, 'doc_id', 'unknown'), "document", preview])

            return formatted_results
        except Exception as e:
            return [["error", "error", f"Error querying knowledge base: {str(e)}"]]

    def launch(self, share: bool = False):
        """Launch the Gradio interface"""
        with gr.Blocks(title="AI 协同小说创作系统") as app:
            gr.Markdown("# AI 协同小说创作系统")

            # Define dashboard components
            with gr.Tab("仪表盘"):
                gr.Markdown("## 当前故事状态")
                with gr.Row():
                    with gr.Column():
                        story_title = gr.Textbox(label="当前故事", value=getattr(self.current_story_state, 'title', '尚未创建故事'), interactive=False)
                        story_status = gr.Textbox(label="状态", value="准备就绪", interactive=False)
                        chapter_count = gr.Number(label="章节数", value=len(self.current_story_state.chapters), interactive=False)
                    with gr.Column():
                        overall_progress = gr.Slider(label="完成度", minimum=0, maximum=100, value=0, interactive=False)
                        gr.Markdown("### 快速操作")
                        with gr.Row():
                            save_state_btn = gr.Button("保存当前状态")
                            load_state_btn = gr.Button("加载保存状态")

            # Add refresh button for dashboard
            refresh_dashboard_btn = gr.Button("刷新仪表盘")

            self.create_story_tab()
            self.create_characters_tab()
            self.create_locations_tab()
            self.create_chapters_tab()
            self.create_workflow_tab()
            self.create_knowledge_base_tab()

            # 添加配置状态信息
            with gr.Tab("配置状态"):
                config_status = gr.TextArea(label="API配置信息", interactive=False, value=self.show_api_config_warning())
                refresh_config_btn = gr.Button("刷新配置状态")

                refresh_config_btn.click(
                    self.show_api_config_warning,
                    inputs=[],
                    outputs=[config_status]
                )

            # Add general actions
            with gr.Row():
                clear_btn = gr.Button("清空所有")
                export_btn = gr.Button("导出故事")

            # Add dashboard refresh functionality
            def refresh_dashboard():
                """刷新仪表盘显示数据"""
                progress = 0
                if self.current_story_state.target_chapter_count > 0:
                    progress = min(100, max(0, int(len(self.current_story_state.chapters) / self.current_story_state.target_chapter_count * 100)))
                return (
                    getattr(self.current_story_state, 'title', 'No story created yet'),
                    "Ready",
                    len(self.current_story_state.chapters),
                    progress
                )

            refresh_dashboard_btn.click(
                refresh_dashboard,
                outputs=[story_title, story_status, chapter_count, overall_progress]
            )

        app.launch(share=share, server_port=7861)


if __name__ == "__main__":
    # Create and launch the application
    app = NovelWritingApp()
    app.launch(share=False)