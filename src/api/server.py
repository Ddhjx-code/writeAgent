import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
import json
import logging

from ..config import Config
from ..core.engine import WritingEngine
from .types import StoryConfig, StoryStateResponse, AgentStatus, SystemStatus, AgentMessage, StoryProgress

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

# 故事管理相关API
@app.post("/api/stories/create")
async def create_story(config: StoryConfig):
    """
    创建新故事
    - **title**: 故事标题
    - **genre**: 故事类型
    - **description**: 故事描述
    - **target_length**: 目标字数
    """
    try:
        if engine is None:
            return {"success": False, "error": "Engine not initialized"}
        # 初始化故事配置
        story = await engine.create_story(config)
        logger.info(f"创建故事成功: {story.id}")
        return {
            "success": True,
            "story_id": story.id,
            "message": "故事创建成功",
            "data": {"story_id": story.id}
        }
    except Exception as e:
        logger.error(f"创建故事失败: {str(e)}")
        return {"success": False, "error": str(e)}

@app.post("/api/stories/{story_id}/start")
async def start_writing(story_id: str):
    """
    开始写作过程
    - **story_id**: 要开始写作的故事ID
    """
    try:
        if engine is None:
            return {"success": False, "error": "Engine not initialized"}
        # 开始AI协作文本生成
        result = await engine.start_writing(story_id)
        logger.info(f"启动写作过程: {story_id}")
        return {
            "success": True,
            "message": "写作过程已启动",
            "result": result,
            "data": {"story_id": story_id}
        }
    except Exception as e:
        logger.error(f"启动写作过程失败: {str(e)}")
        return {"success": False, "error": str(e)}

@app.get("/api/stories/{story_id}")
async def get_story(story_id: str):
    """
    获取故事状态
    - **story_id**: 要查询的故事ID
    """
    try:
        if engine is None:
            return {"success": False, "error": "Engine not initialized"}
        story = await engine.get_story(story_id)
        logger.debug(f"获取故事状态: {story_id}")
        return {
            "success": True,
            "data": {"story": story}
        }
    except Exception as e:
        logger.error(f"获取故事失败: {str(e)}")
        return {"success": False, "error": str(e)}

@app.get("/api/stories/{story_id}/progress")
async def get_story_progress(story_id: str):
    """
    获取故事写作进度
    - **story_id**: 要查询的故事ID
    """
    try:
        if engine is None:
            return {"success": False, "error": "Engine not initialized"}
        # 这里需要实现获取故事进度的逻辑
        progress = StoryProgress(
            current_chapter=1,
            total_chapters=10,
            progress_percentage=10.0,
            status="writing",
            current_phase="planning",
            last_updated="2026-02-04T17:15:00Z"
        )
        return {
            "success": True,
            "data": {"progress": progress}
        }
    except Exception as e:
        logger.error(f"获取故事进度失败: {str(e)}")
        return {"success": False, "error": str(e)}

# 代理和状态管理API
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

# 实时通信
@app.websocket("/ws/updates")
async def websocket_updates(websocket: WebSocket):
    """
    WebSocket连接用于实时更新
    提供实时的故事进度、代理状态等更新
    """
    await websocket.accept()
    logger.info("WebSocket连接已建立")
    try:
        while True:
            if engine is not None:
                # 发送系统状态
                status = await engine.get_system_status()
                await websocket.send_text(json.dumps(status, ensure_ascii=False))
            else:
                # 尝试初始化
                await startup_event()
                if engine is not None:
                    status = await engine.get_system_status()
                    await websocket.send_text(json.dumps(status, ensure_ascii=False))
                else:
                    await websocket.send_text(json.dumps({"error": "Engine not initialized"}))
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logger.info("WebSocket连接已断开")

@app.websocket("/ws/agent-messages")
async def websocket_agent_messages(websocket: WebSocket):
    """
    WebSocket连接用于获取代理消息
    接收AI代理生成的消息和反馈
    """
    await websocket.accept()
    logger.info("代理消息WebSocket连接已建立")
    try:
        while True:
            # 发送示例代理消息 - 在真实实现中这应该来自于实际的代理系统
            message = AgentMessage(
                agent_id="sample_agent_001",
                agent_name="PlannerAgent",
                message="已完成故事大纲规划",
                timestamp="2026-02-04T17:15:00Z",
                level="info"
            )
            await websocket.send_text(json.dumps(message.dict(), ensure_ascii=False))
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        logger.info("代理消息WebSocket连接已断开")

# 角色管理API
@app.post("/api/stories/{story_id}/characters")
async def create_character(story_id: str, character_data: Dict[str, Any]):
    """
    为故事创建新角色
    """
    try:
        if engine is None:
            return {"success": False, "error": "Engine not initialized"}
        # 在真实实现中，这里应该调用引擎的相应方法
        return {
            "success": True,
            "message": "角色创建成功",
            "data": {"character_id": "char_001", "character": character_data}
        }
    except Exception as e:
        logger.error(f"创建角色失败: {str(e)}")
        return {"success": False, "error": str(e)}

# 章节管理API
@app.get("/api/stories/{story_id}/chapters")
async def get_chapters(story_id: str):
    """
    获取故事的所有章节
    """
    try:
        if engine is None:
            return {"success": False, "error": "Engine not initialized"}
        # 在真实实现中，这里应该从引擎获取实际数据
        return {
            "success": True,
            "data": {"chapters": []}
        }
    except Exception as e:
        logger.error(f"获取章节失败: {str(e)}")
        return {"success": False, "error": str(e)}

# 前端静态文件服务（可选，在开发时使用）
import os
frontend_dist_path = os.path.join(os.path.dirname(__file__), 'frontend', 'dist')

if os.path.exists(frontend_dist_path):
    logger.info(f"提供前端静态文件: {frontend_dist_path}")
    app.mount("/", StaticFiles(directory=frontend_dist_path, html=True), name="frontend")