#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG Backend 主入口
"""

from backend.config.log import setup_default_logging, get_logger
from fastapi import FastAPI
from backend.api import rag, chat, auth, crawl, knowledge_library,visual_graph
from dotenv import load_dotenv
import uvicorn
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 生命周期管理"""
    # 启动时执行
    load_dotenv()    # 加载环境变量
    setup_default_logging() # 初始化日志

    logger = get_logger(__name__)
    logger.info("FastAPI 应用启动中...")
    yield
    # 关闭时执行（如果需要清理资源）

app = FastAPI(title="Sales-AgenticRAG API", version="1.0.0", lifespan=lifespan)

# 添加 /api 前缀到所有路由
app.include_router(rag.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(crawl.router, prefix="/api")
app.include_router(knowledge_library.router, prefix="/api")
app.include_router(visual_graph.router, prefix="/api")

@app.get("/health")
async def read_root():
    return {"message": "Hello, FastAPI!"}    

def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
