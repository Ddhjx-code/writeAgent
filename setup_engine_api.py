#!/usr/bin/env python
"""
独立启动AI协同小说写作系统API服务器
"""
from src.config import Config
from src.core.engine import WritingEngine
from src.api.server import app
import asyncio


async def main():
    """初始化引擎并将其附加到FastAPI应用"""
    config = Config()
    engine = WritingEngine(config)
    await engine.initialize()

    # 将引擎实例赋值给app，供API端点使用
    app.engine = engine
    print("AI 协同小说写作系统引擎已初始化")
    print("请使用以下命令在另一个终端启动服务器：")
    print("uvicorn src.api.server:app --host 0.0.0.0 --port 8000")


if __name__ == "__main__":
    asyncio.run(main())