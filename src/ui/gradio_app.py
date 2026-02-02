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

            # Add story info to KB with story_id for filtering
            story_info = {
                'title': title,
                'genre': genre,
                'summary': summary
            }

            from src.core.knowledge_base import KnowledgeEntity
             # Add to KB as an entity with story_id
            story_entity = KnowledgeEntity(
                id=f"story_{title.replace(' ', '_').replace(':', '_')}",
                name=title,
                type="story_info",
                description=summary,
                metadata={
                    'genre': genre,
                    'summary': summary,
                    'target_chapters': target_chapters,
                    'story_id': self.current_story_state.id  # Add story_id for filtering
                },
                relationships=[]
            )
            self.knowledge_base.add_entity(story_entity)

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

                # Add chapter placeholder to knowledge base with story_id
                chapter_entity = KnowledgeEntity(
                    id=f"ch_{self.current_story_state.id}_{i}",
                    name=f"Chapter {i}",
                    type="chapter",
                    description=f"Chapter {i} of {title}",
                    metadata={
                        'story_id': self.current_story_state.id,
                        'chapter_number': i,
                        'status': 'planned'
                    },
                    relationships=[]
                )
                self.knowledge_base.add_entity(chapter_entity)

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

            # Add story_id to metadata to enable filtering
            simple_metadata['story_id'] = self.current_story_state.id

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

            # Also add to knowledge base with story_id
            from src.core.knowledge_base import KnowledgeEntity
            loc_entity = KnowledgeEntity(
                id=loc_id,
                name=location.name,
                type="location",
                description=location.description,
                metadata={
                    'type': location.type,
                    'features': location.features,
                    'significance': location.significance,
                    'story_id': self.current_story_state.id  # Add story_id for filtering
                },
                relationships=[]
            )
            self.knowledge_base.add_entity(loc_entity)

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
            # Handle both enum and string representations of status
            if isinstance(chapter.status, ChapterState):
                status_value = chapter.status.value if hasattr(chapter.status, 'value') else str(chapter.status)
            else:
                status_value = str(chapter.status)

            # Map status to user-friendly string
            status_display = status_value.title() if status_value else "Draft"
            chapter_list.append(f"Chapter {chapter.number} - {chapter.title} ({status_display})")

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
            content = "没有章节可显示"
            if self.current_story_state.chapters:
                first_chapter = next(iter(self.current_story_state.chapters.values()))
                content = first_chapter.content or f"第{first_chapter.number}章内容为空"
            return new_chapter_list, content
        except Exception as e:
            print(f"Error refreshing chapters: {str(e)}")
            import traceback
            traceback.print_exc()
            return ["No chapters yet"], "刷新章节时出错"

    def load_chapter_content(self, chapter_choice: str) -> str:
        """Load chapter content when chapter is selected"""
        try:
            if chapter_choice == "No chapters yet":
                return "没有章节可显示"

            # Check if chapter exists by directly looking for match
            for ch_id, chapter in self.current_story_state.chapters.items():
                expected_format1 = f"Chapter {chapter.number} - {chapter.title} ({chapter.status.value if hasattr(chapter.status, 'value') else chapter.status})"
                expected_format2 = f"Chapter {chapter.number} - {chapter.title} ({chapter.status})"

                if chapter_choice == expected_format1 or chapter_choice == expected_format2 or chapter_choice.startswith(f"Chapter {chapter.number} - "):
                    return chapter.content or f"第{chapter.number}章内容为空"

            # Fallback: Parse selected chapter number from the formatted choice
            import re
            numbers = re.findall(r'\d+', chapter_choice)
            if numbers:
                chapter_num = int(numbers[0])

                # Find the chapter with this number
                for ch_id, chapter in self.current_story_state.chapters.items():
                    if chapter.number == chapter_num:
                        return chapter.content or f"第{chapter.number}章内容为空"

            return f"章节内容未找到: {chapter_choice}\n可用章节: {list(self.current_story_state.chapters.keys())}"
        except Exception as e:
            print(f"Error loading chapter content: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"无法加载章节内容: {str(e)}"

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
            import concurrent.futures

            # 确保当前故事状态和知识库同步
            if not self.current_story_state.title:
                return "错误: 请先创建故事", "❌ 错误: 工作流需要一个有效的故事作为上下文，请先创建新故事\n\n当前没有故事，请转到'故事创作'标签页创建新故事。"

            # 开始日志消息
            log_message = f"🚀 开始工作流执行"
            log_message += f"\n------------------------"
            log_message += f"\n📖 故事: {self.current_story_state.title}"
            log_message += f"\n🎭 角色: {len(self.current_story_state.characters)} 个"
            log_message += f"\n🌍 地点: {len(self.current_story_state.locations)} 个"
            log_message += f"\n📚 目标章节数: {self.current_story_state.target_chapter_count} 章"
            log_message += f"\n ⏳ 状态: 待开始"

            # 在执行工作流前同步当前故事信息到知识库
            self._sync_story_state_to_knowledge_base()
            log_message += f"\n🔄 知识库同步: 完成"

            if "完整章节" in action:
                # 用流式执行方法更新UI
                def run_workflow_streamed():
                    import inspect
                    progress_log = log_message
                    if hasattr(self.workflow, 'stream_execution'):
                        # 使用流式执行方法，可以显示实时进度
                        results_received = 0
                        try:
                            for step_key, step_value in self.workflow.stream_execution(self.current_story_state):
                                results_received += 1
                                progress_log = f"🚀 执行中... {step_value.get('progress', '')}"
                                progress_log += f"\n------------------------"
                                progress_log += f"\n📖 故事: {self.current_story_state.title}"
                                progress_log += f"\n🎭 角色: {len(self.current_story_state.characters)} 个"
                                progress_log += f"\n🌍 地点: {len(self.current_story_state.locations)} 个"
                                progress_log += f"\n📚 目标章节数: {self.current_story_state.target_chapter_count} 章"

                                # 添加详细的步骤信息
                                if 'step' in step_value:
                                    progress_log += f"\n📋 当前步骤: {step_value['step']}"
                                elif 'chapter_number' in step_value:
                                    progress_log += f"\n📝 处理章节: 第{step_value['chapter_number']}章"

                                if 'status' in step_value:
                                    status_emoji = "✅" if step_value['status'] == 'completed' else "🔄" if step_value['status'] == 'in_progress' else "⏸️"
                                    progress_log += f"\n🔹 状态: {status_emoji} {step_value['status']}"

                                progress_log += f"\n⏱️ 进度: {step_value.get('progress', '未知')}"

                                # 增加当前统计信息
                                progress_log += f"\n📊 当前状态:"
                                progress_log += f"\n   - 已完成章节: {len(self.current_story_state.chapters)}"
                                progress_log += f"\n   - 当前角色: {len(self.current_story_state.characters)}"
                                progress_log += f"\n   - 当前地点: {len(self.current_story_state.locations)}"

                                if 'result' in step_value:
                                    # 添加简化的结果信息，避免日志过大
                                    result_str = str(step_value['result'])
                                    if len(result_str) > 100:
                                        result_str = result_str[:100] + "..."
                                    progress_log += f"\n🔍 结果预览: {result_str}"

                                progress_log += f"\n------------------------"

                                # 打印进度更新（这对用户不可见，仅用于系统日志）
                                print(f"Progress update: {step_value.get('progress', 'unknown')} - {step_key}")

                                # 为了演示目的，实际实现中这里可能需要yield
                                # 但由于在Gradio上下文中这个函数是被单次调用，我们会显示最终日志
                                pass

                        except Exception as step_error:
                            progress_log += f"\n❌ 执行步骤时出错: {str(step_error)}"
                            import traceback
                            progress_log += f"\n🔧 技术详情: {traceback.format_exc()[:500]}..."
                    else:
                        # 如果没有stream_execution方法，则执行传统工作流
                        import asyncio
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            if inspect.iscoroutinefunction(self.workflow.run):
                                result = loop.run_until_complete(self.workflow.run(self.current_story_state))
                            else:
                                result = self.workflow.run(self.current_story_state)
                            progress_log += f"\n⚠️ 警告: 使用传统执行方法（无详细进度信息）"
                        finally:
                            loop.close()

                    # 添加最终完成统计
                    progress_log += f"\n\n🎉 工作流执行完成! 🎉"
                    progress_log += f"\n------------------------"
                    progress_log += f"\n📊 最终统计:"
                    progress_log += f"\n   - 总体进度: 100%"
                    progress_log += f"\n   - 已完成章节: {len(self.current_story_state.chapters)}"
                    progress_log += f"\n   - 保存角色: {len(self.current_story_state.characters)}"
                    progress_log += f"\n   - 保存地点: {len(self.current_story_state.locations)}"
                    progress_log += f"\n   - 故事状态: 准备就绪"
                    progress_log += f"\n------------------------"
                    progress_log += f"\n✨ 感谢使用AI协作小说创作系统！"

                    return progress_log

                # 使用线程池执行工作流
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_workflow_streamed)
                    try:
                        # 获取最终执行日志 (3小时超时 - 10800秒)
                        log_message = future.result(timeout=10800)
                    except concurrent.futures.TimeoutError:
                        timeout_msg = f"\n\n⏰ ⚠️ 警告: 工作流执行超时 (已运行超过3小时)\n"
                        timeout_msg += f"------------------------\n"
                        timeout_msg += f"📋 超时时的系统状态:\n"
                        timeout_msg += f"   - 已完成章节: {len(self.current_story_state.chapters)}\n"
                        timeout_msg += f"   - 当前角色: {len(self.current_story_state.characters)}\n"
                        timeout_msg += f"   - 当前地点: {len(self.current_story_state.locations)}\n"
                        timeout_msg += f"💡 建议:\n"
                        timeout_msg += f"   - 检查API密钥配置并确保网络连接正常\n"
                        timeout_msg += f"   - 或者尝试减少目标章节数再次执行\n"
                        timeout_msg += f"   - 如果问题持续，请重启应用程序\n"
                        timeout_msg += f"------------------------\n"
                        log_message += timeout_msg

            elif "仅运行规划" in action:
                log_message += "\n\nℹ️ [说明] 部分高级工作流选项仍处于开发阶段"
                log_message += f"\n🎯 当前操作: {action}"
                log_message += "\n💡 温馨提示: 推荐选择'运行完整章节工作流'以获得最完整的故事创作体验"
                log_message += "\n------------------------"
            elif "仅运行写作" in action:
                log_message += "\n\nℹ️ [说明] 部分高级工作流选项仍处于开发阶段"
                log_message += f"\n🎯 当前操作: {action}"
                log_message += "\n💡 温馨提示: 推荐选择'运行完整章节工作流'以获得最完整的故事创作体验"
                log_message += "\n------------------------"
            elif "仅运行审阅" in action:
                log_message += "\n\nℹ️ [说明] 部分高级工作流选项仍处于开发阶段"
                log_message += f"\n🎯 当前操作: {action}"
                log_message += "\n💡 温馨提示: 推荐选择'运行完整章节工作流'以获得最完整的故事创作体验"
                log_message += "\n------------------------"
            else:
                log_message += f"\n\n⚠️ 未知操作: {action}"
                log_message += "\n💡 可用操作: '运行完整章节工作流', '仅运行规划', '仅运行写作', '仅运行审阅'"
                log_message += "\n------------------------"

            return f"✅ 工作流执行完成", log_message
        except Exception as e:
            # 详细错误报告显示
            import traceback
            error_details = traceback.format_exc()

            # 创建用户友好的错误报告
            user_friendly_error = f"❌ 执行失败: {type(e).__name__}"
            user_friendly_error += f"\n------------------------"
            user_friendly_error += f"\n📖 错误描述: {str(e)}"
            user_friendly_error += f"\n🔧 执行上下文:"
            user_friendly_error += f"\n   • 当前故事: {self.current_story_state.title or '（无标题）'}"
            user_friendly_error += f"\n   • 章节数: {len(self.current_story_state.chapters)}"
            user_friendly_error += f"\n   • 角色数: {len(self.current_story_state.characters)}"
            user_friendly_error += f"\n   • 地点数: {len(self.current_story_state.locations)}"
            user_friendly_error += f"\n\n⚙️ 系统配置检查:"
            import os
            openai_configured = bool(os.getenv('OPENAI_API_KEY'))
            anthropic_configured = bool(os.getenv('ANTHROPIC_API_KEY'))
            user_friendly_error += f"\n   • OpenAI API: {'✅ 已配置' if openai_configured else '❌ 未配置'}"
            user_friendly_error += f"\n   • Anthropic API: {'✅ 已配置' if anthropic_configured else '❌ 未配置'}"
            user_friendly_error += f"\n\n📋 常见问题与解决方案:"
            user_friendly_error += f"\n   1️⃣  缺少API密钥 - 请检查config/.env文件中的配置"
            user_friendly_error += f"\n   2️⃣  API密钥无效 - 请确认密钥正确且有效"
            user_friendly_error += f"\n   3️⃣  网络连接问题 - 请检查网络连接"
            user_friendly_error += f"\n   4️⃣  API服务不可用 - 请稍后重试"
            user_friendly_error += f"\n\n💡 如果问题持续存在，请联系系统管理员"
            user_friendly_error += f"\n------------------------"

            # 仅对开发者显示技术细节
            user_friendly_error += f"\n🔧 技术详情 (仅开发者使用):"
            user_friendly_error += f"\n{error_details[:1500]}..." if len(error_details) > 1500 else f"\n{error_details}"
            user_friendly_error += f"\n------------------------"

            # 记录错误到系统日志
            print(f"Workflow execution error: {str(e)}")
            print(f"Traceback: {error_details}")

            return f"❌ 执行失败: {type(e).__name__}", user_friendly_error

    def _sync_story_state_to_knowledge_base(self):
        """同步当前故事状态到知识库"""
        try:
            # 同步角色
            for char_id, character in self.current_story_state.characters.items():
                from src.core.knowledge_base import KnowledgeEntity
                updated_char_entity = KnowledgeEntity(
                    id=char_id,
                    name=character.name,
                    type="character",
                    description=character.description,
                    metadata={
                        'role': character.role,
                        'personality_traits': character.personality_traits,
                        'background': character.background,
                        'story_id': self.current_story_state.id
                    },
                    relationships=list(character.relationships.keys()) if character.relationships else [],
                    story_id=self.current_story_state.id
                )
                self.knowledge_base.add_entity(updated_char_entity)

            # 同步地点
            for loc_id, location in self.current_story_state.locations.items():
                from src.core.knowledge_base import KnowledgeEntity
                updated_loc_entity = KnowledgeEntity(
                    id=loc_id,
                    name=location.name,
                    type="location",
                    description=location.description,
                    metadata={
                        'type': location.type,
                        'features': location.features,
                        'significance': location.significance,
                        'story_id': self.current_story_state.id
                    },
                    relationships=[],
                    story_id=self.current_story_state.id
                )
                self.knowledge_base.add_entity(updated_loc_entity)

        except Exception as e:
            print(f"同步故事状态到知识库时出错: {str(e)}")

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

    def clear_current_story(self) -> str:
        """清空当前故事状态，但保留用户配置"""
        try:
            # 保留API配置信息，只清空故事数据
            current_api_key = os.getenv("OPENAI_API_KEY")
            current_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            current_ollama_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "qwen3-embedding:0.6b")

            # 1. 重新初始化知识库 (清理故事相关数据，但保留配置)
            self.knowledge_base = KnowledgeBase(
                openai_api_key=current_api_key,
                openai_base_url=current_base_url,
                ollama_model=current_ollama_model
            )

            # 2. 重新初始化工作流 (保持知识库引用)
            self.workflow = create_default_workflow(self.knowledge_base)

            # 3. 重置故事状态
            self.current_story_state = StoryState()

            # 4. 重置UI标志
            self.workflow_running = False

            return "当前故事已清空，系统已重置"
        except Exception as e:
            return f"清除故事时发生错误: {str(e)}"

    def reset_system(self) -> str:
        """重置整个系统到初始状态"""
        try:
            # 保留API配置信息，只清空所有数据
            current_api_key = os.getenv("OPENAI_API_KEY")
            current_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            current_ollama_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "qwen3-embedding:0.6b")

            # 重新初始化所有组件
            self.knowledge_base = KnowledgeBase(
                openai_api_key=current_api_key,
                openai_base_url=current_base_url,
                ollama_model=current_ollama_model
            )

            self.workflow = create_default_workflow(self.knowledge_base)
            self.current_story_state = StoryState()
            self.workflow_running = False

            # 尝试删除本地存储的文件
            import shutil
            try:
                if os.path.exists("./storage"):
                    shutil.rmtree("./storage")
                    os.makedirs("./storage", exist_ok=True)
            except Exception as storage_error:
                print(f"清除存储目录时出错（可忽略）: {storage_error}")

            return "系统已完全重置"
        except Exception as e:
            return f"重置系统时发生错误: {str(e)}"

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
                clear_btn = gr.Button("清空当前故事")
                reset_btn = gr.Button("重置系统")
                export_btn = gr.Button("导出故事")

            with gr.Row():
                clear_status = gr.Textbox(label="操作状态", interactive=False)

            # 绑定清除事件
            clear_btn.click(
                self.clear_current_story,
                inputs=[],
                outputs=[clear_status]
            )

            reset_btn.click(
                self.reset_system,
                inputs=[],
                outputs=[clear_status]
            )

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