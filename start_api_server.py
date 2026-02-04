#!/usr/bin/env python
"""
AI 协同小说写作系统 API 服务器启动脚本
"""
import uvicorn
from src.config import Config
from src.core.engine import WritingEngine
from src.api.server import app


async def initialize_engine():
    """初始化写作引擎并将其设置到FastAPI应用"""
    config = Config()
    engine = WritingEngine(config)
    await engine.initialize()

    # 将引擎实例赋值给app，供API端点使用
    app.engine = engine
    return engine


if __name__ == "__main__":
    import asyncio

    async def setup_and_run():
        # 初始化引擎
        engine = await initialize_engine()
        print("AI 协同小说写作系统引擎已初始化")

        # 启动服务器
        print("正在启动 FastAPI 服务器... 请访问 http://localhost:8000")
        uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=False)

    asyncio.run(setup_and_run())