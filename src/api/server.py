import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
import json

from ..config import Config
from ..core.engine import WritingEngine
from .types import StoryConfig, StoryStateResponse, AgentStatus, SystemStatus

app = FastAPI(title="AI 协同小说写作系统 API")

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
        print("API服务器已启动，写作引擎已初始化")
    except Exception as e:
        print(f"引擎初始化错误: {e}")

@app.get("/")
async def read_root():
    return {"message": "AI 协同小说写作系统 API"}

@app.post("/api/stories/create")
async def create_story(config: StoryConfig):
    """创建新故事"""
    try:
        if engine is None:
            return {"success": False, "error": "Engine not initialized"}
        # 初始化故事配置
        story = await engine.create_story(config)
        return {"success": True, "story_id": story.id, "message": "故事创建成功"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/stories/start")
async def start_writing(story_id: str):
    """开始写作过程"""
    try:
        if engine is None:
            return {"success": False, "error": "Engine not initialized"}
        # 开始AI协作文本生成
        result = await engine.start_writing(story_id)
        return {"success": True, "message": "写作过程已启动", "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/stories/{story_id}")
async def get_story(story_id: str):
    """获取故事状态"""
    try:
        if engine is None:
            return {"success": False, "error": "Engine not initialized"}
        story = await engine.get_story(story_id)
        return {"success": True, "story": story}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/agents/status")
async def get_agent_status():
    """获取AI代理状态"""
    try:
        if engine is None:
            return {"success": False, "error": "Engine not initialized"}
        status = await engine.get_agent_status()
        return {"success": True, "status": status}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/status")
async def get_system_status():
    """获取系统状态"""
    try:
        if engine is None:
            await startup_event()  # 尝试初始化引擎

        if engine is None:
            return {"success": False, "error": "Engine not initialized"}
        status = await engine.get_system_status()
        return {"success": True, "status": status}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.websocket("/ws/updates")
async def websocket_updates(websocket: WebSocket):
    """WebSocket连接用于实时更新"""
    await websocket.accept()
    try:
        while True:
            if engine is not None:
                # 发送系统状态
                status = await engine.get_system_status()
                await websocket.send_text(json.dumps(status))
            else:
                # 尝试初始化
                await startup_event()
                if engine is not None:
                    status = await engine.get_system_status()
                    await websocket.send_text(json.dumps(status))
                else:
                    await websocket.send_text(json.dumps({"error": "Engine not initialized"}))
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("WebSocket disconnected")

# 静态文件服务
import os
frontend_dist_path = os.path.join(os.path.dirname(__file__), 'frontend', 'dist')

if os.path.exists(frontend_dist_path):
    app.mount("/", StaticFiles(directory=frontend_dist_path, html=True), name="frontend")