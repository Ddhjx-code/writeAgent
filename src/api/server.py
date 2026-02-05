import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
import json
import logging
from uuid import uuid4

from ..config import Config
from ..core.engine import WritingEngine
from .types import StoryConfig, StoryStateResponse, AgentStatus, SystemStatus, AgentMessage, StoryProgress
from ..workflow.state import GraphState  # 导入GraphState

app = FastAPI(
    title="AI 协同小说写作系统 API",
    description="用于现代化AI驱动小说创作系统的RESTful API接口",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI文档
    redoc_url="/redoc"     # ReDoc文档
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应限制来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 写作引擎将从主应用传递
engine = None

@app.on_event("startup")
async def startup_event():
    global engine
    # 在启动时提供一个方式来初始化引擎
    from ..config import Config
    from ..core.engine import WritingEngine

    try:
        config = Config()
        engine = WritingEngine(config)
        await engine.initialize()
        logger.info("API服务器已启动，写作引擎已初始化")
    except Exception as e:
        logger.error(f"引擎初始化错误: {e}")

@app.get("/")
async def read_root():
    """
    API根端点
    返回API信息和基本状态
    """
    return {
        "message": "AI 协同小说写作系统 API",
        "version": "1.0.0",
        "status": "running",
        "docs_url": "/docs"
    }

# 系统状态API
@app.get("/api/status")
async def get_system_status():
    """
    获取系统整体状态
    返回引擎、知识库等的整体运行状态
    """
    try:
        if engine is None:
            await startup_event()  # 尝试初始化引擎

        if engine is None:
            return {"success": False, "error": "Engine not initialized"}
        status = await engine.get_system_status()
        return {
            "success": True,
            "data": {"status": status}
        }
    except Exception as e:
        logger.error(f"获取系统状态失败: {str(e)}")
        return {"success": False, "error": str(e)}

@app.get("/api/agents/status")
async def get_agent_status():
    """
    获取AI代理状态
    返回当前所有AI代理的工作状态
    """
    try:
        if engine is None:
            return {"success": False, "error": "Engine not initialized"}
        status = await engine.get_agent_status()
        return {
            "success": True,
            "data": {"agents_status": status}
        }
    except Exception as e:
        logger.error(f"获取代理状态失败: {str(e)}")
        return {"success": False, "error": str(e)}

# 使用流程API：按照plan.md中的例子设计，与实际工作流对齐
@app.post("/api/stories")
async def create_story(config: StoryConfig):
    """
    1.人类输入故事梗概/大纲 (按plan.md使用例子)
    通过API将故事配置传递给AI协同创作系统
    """
    try:
        if engine is None:
            return {"success": False, "error": "Engine not initialized"}

        # 构建符合引擎接口的story_data
        story_data = {
            "title": config.title,
            "description": config.description,
            "outline": {
                "initial_outline": config.outline or "",
                "genre": config.genre,
                "target_chapters": config.chapters_count
            },
            "characters": config.characters if config.characters else {},
            "world_details": config.world_details if config.world_details else {},
            "themes": config.themes if config.themes else [],
            "notes": config.notes if config.notes else []
        }

        # 使用WritingEngine创建新故事
        initial_state = await engine.create_new_story(story_data)
        logger.info(f"故事创建成功: {initial_state.title}")

        return {
            "success": True,
            "message": "故事创建成功",
            "data": {
                "story_id": initial_state.title,  # 使用实际创建的GraphState的title作为ID
                "title": initial_state.title,
                "status": initial_state.story_status,
                "current_phase": initial_state.current_phase,
                "current_hierarchical_phase": initial_state.current_hierarchical_phase
            }
        }
    except Exception as e:
        logger.error(f"创建故事失败: {str(e)}")
        return {"success": False, "error": str(e)}

@app.post("/api/stories/{story_id}/run")
async def run_story_generation(story_id: str, run_config: Dict[str, Any] = None):
    """
    2.系统接受后，各agent开始协作创作 (按plan.md使用例子)
    启动完整的故事生成工作流
    """
    try:
        if engine is None:
            return {"success": False, "error": "Engine not initialized"}

        # 获取当前的故事状态
        # 注意：我们实际上无法直接通过ID获取状态，需要通过引擎状态管理
        # 现在使用一个模拟逻辑获取当前活跃故事
        if not engine.current_story or engine.current_story.title != story_id:
            logger.warning(f"Current story is not {story_id}, cannot start generation")
            return {"success": False, "error": f"Story {story_id} is not loaded in engine"}

        # 获取运行配置参数
        max_iterations = run_config.get("max_iterations", 20) if run_config else 20
        target_chapters = run_config.get("target_chapters", 5) if run_config else 5

        logger.info(f"开始故事生成: {story_id}, 迭代数: {max_iterations}, 目标章节: {target_chapters}")

        # 运行故事生成工作流
        final_state = await engine.run_story_generation(engine.current_story, max_iterations, target_chapters)

        return {
            "success": True,
            "message": "故事生成流程完成",
            "data": {
                "story_id": final_state.title,
                "final_state": {
                    "title": final_state.title,
                    "status": final_state.story_status,
                    "current_phase": final_state.current_phase,
                    "current_hierarchical_phase": final_state.current_hierarchical_phase,
                    "chapters_count": len(final_state.chapters),
                    "completed_chapters": final_state.completed_chapters,
                    "iteration_count": final_state.iteration_count
                }
            }
        }
    except Exception as e:
        logger.error(f"运行故事生成失败: {str(e)}")
        return {"success": False, "error": str(e)}

@app.get("/api/stories/{story_id}/state")
async def get_story_state(story_id: str):
    """
    获取实时故事状态，用于人机协同审核
    - 在产出大纲，人物，每n章后提供给人类评审修改 (按plan.md使用例子)
    """
    try:
        if engine is None:
            return {"success": False, "error": "Engine not initialized"}

        # 获取当前故事状态
        current_story = engine.current_story
        if not current_story or current_story.title != story_id:
            return {"success": False, "error": f"Story {story_id} not found in current session"}

        # 返回包含所有相关信息的完整状态
        return {
            "success": True,
            "data": {
                "story_id": current_story.title,
                "title": current_story.title,
                "description": current_story.story_notes[0] if current_story.story_notes else "",
                "outline": current_story.outline,
                "characters": current_story.characters,
                "chapters": current_story.chapters,
                "world_details": current_story.world_details,
                "current_phase": current_story.current_phase,
                "current_hierarchical_phase": current_story.current_hierarchical_phase,
                "needs_human_review": current_story.needs_human_review,
                "human_review_status": current_story.human_review_status,
                "completed_chapters": current_story.completed_chapters,
                "current_chapter_index": current_story.current_chapter_index,
                "story_progress": current_story.story_arc_progress,
                "agent_responses": [resp.dict() for resp in current_story.agent_responses],
                "story_status": current_story.story_status,
                "is_running": engine.is_running
            }
        }
    except Exception as e:
        logger.error(f"获取故事状态失败: {str(e)}")
        return {"success": False, "error": str(e)}

@app.post("/api/stories/{story_id}/human-review")
async def submit_human_review(story_id: str, review_data: Dict[str, Any]):
    """
    4.评审后以人类意见进行返工 (按plan.md使用例子)
    处理人类反馈并更新工作流状态
    """
    try:
        if engine is None:
            return {"success": False, "error": "Engine not initialized"}

        # 获取当前故事
        if not engine.current_story or engine.current_story.title != story_id:
            return {"success": False, "error": f"Story {story_id} not found in current session"}

        # 获取反馈内容
        feedback = review_data.get("feedback", "")
        if not feedback:
            return {"success": False, "error": "Feedback content is required"}

        # 使用引擎的人类反馈方法
        updated_state = await engine.add_human_feedback(feedback)

        return {
            "success": True,
            "message": "人类评审已提交并处理",
            "data": {
                "story_id": story_id,
                "feedback_processed": True,
                "human_feedback": feedback,
                "updated_state": {
                    "status": updated_state.story_status,
                    "needs_human_review": updated_state.needs_human_review,
                    "current_phase": updated_state.current_phase
                }
            }
        }
    except Exception as e:
        logger.error(f"处理人类评审失败: {str(e)}")
        return {"success": False, "error": str(e)}

# 其他辅助API端点
@app.get("/api/stories")
async def list_stories():
    """获取当前会话中的故事列表"""
    try:
        if engine is None:
            return {"success": False, "error": "Engine not initialized"}

        # 系统目前没有持久化存储，所以只返回当前活动的故事
        current_story = engine.current_story
        stories = []
        if current_story:
            stories.append({
                "id": current_story.title,
                "title": current_story.title,
                "status": current_story.story_status,
                "current_phase": current_story.current_phase,
                "chapters_count": len(current_story.chapters),
                "progress": current_story.story_arc_progress
            })

        return {
            "success": True,
            "data": {
                "stories": stories
            }
        }
    except Exception as e:
        logger.error(f"获取故事列表失败: {str(e)}")
        return {"success": False, "error": str(e)}

@app.get("/api/stories/{story_id}/chapters")
async def get_chapters(story_id: str):
    """获取特定故事的章节列表"""
    try:
        if engine is None:
            return {"success": False, "error": "Engine not initialized"}

        # 检查当前活动的故事
        current_story = engine.current_story
        if not current_story or current_story.title != story_id:
            return {"success": False, "error": f"Story {story_id} not found in current session"}

        return {
            "success": True,
            "data": {
                "story_id": story_id,
                "chapters": [
                    {
                        "number": chap.get("number", idx),
                        "title": chap.get("title", f"第{chap.get('number', idx)}章"),
                        "content_preview": chap.get("content", "")[:100],  # 预览前100个字符
                        "content_length": len(chap.get("content", "")),
                        "word_count": chap.get("word_count", 0)
                    }
                    for idx, chap in enumerate(current_story.chapters)
                ]
            }
        }
    except Exception as e:
        logger.error(f"获取章节失败: {str(e)}")
        return {"success": False, "error": str(e)}

@app.get("/api/stories/{story_id}/characters")
async def get_characters(story_id: str):
    """获取故事中的角色信息"""
    try:
        if engine is None:
            return {"success": False, "error": "Engine not initialized"}

        current_story = engine.current_story
        if not current_story or current_story.title != story_id:
            return {"success": False, "error": f"Story {story_id} not found in current session"}

        return {
            "success": True,
            "data": {
                "story_id": story_id,
                "characters": current_story.characters
            }
        }
    except Exception as e:
        logger.error(f"获取角色信息失败: {str(e)}")
        return {"success": False, "error": str(e)}

# 实时通信 - 用于调试和工作流状态更新
@app.websocket("/ws/updates")
async def websocket_updates(websocket: WebSocket):
    """
    WebSocket连接用于实时更新
    提供实时的工作流状态、故事进度等更新
    """
    await websocket.accept()
    logger.info("WebSocket连接已建立，提供实时工作流更新")
    try:
        while True:
            if engine is not None:
                # 发送系统和故事状态
                status = await engine.get_system_status()

                # 包含更多详细的工作流和故事信息
                response = {
                    "system_status": status,
                    "current_story": None,
                    "is_running": engine.is_running
                }

                if engine.current_story:
                    response["current_story"] = {
                        "title": engine.current_story.title,
                        "status": engine.current_story.story_status,
                        "current_phase": engine.current_story.current_phase,
                        "current_hierarchical_phase": engine.current_story.current_hierarchical_phase,
                        "completed_chapters": len(engine.current_story.completed_chapters),
                        "total_chapters": len(engine.current_story.chapters),
                        "needs_human_review": engine.current_story.needs_human_review,
                        "human_review_status": engine.current_story.human_review_status
                    }

                await websocket.send_text(json.dumps(response, ensure_ascii=False))
            else:
                # 尝试初始化
                await startup_event()
                status = {"status": "disconnected", "timestamp": "unknown"}
                await websocket.send_text(json.dumps(status, ensure_ascii=False))

            await asyncio.sleep(2)  # 增加更新频率以获得更实时的反馈
    except WebSocketDisconnect:
        logger.info("WebSocket连接已断开")

# 前端静态文件服务（可选，在开发时使用）
import os
frontend_dist_path = os.path.join(os.path.dirname(__file__), 'frontend', 'dist')

if os.path.exists(frontend_dist_path):
    logger.info(f"提供前端静态文件: {frontend_dist_path}")
    app.mount("/", StaticFiles(directory=frontend_dist_path, html=True), name="frontend")