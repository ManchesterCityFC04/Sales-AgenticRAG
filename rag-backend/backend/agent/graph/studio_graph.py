#!/usr/bin/env python3
"""
LangGraph Studio 图定义文件

此文件专门为 LangGraph Studio 提供图实例，
参考 test_raggraph_simple.py 的模型初始化方式。
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

try:
    # 导入必要的模块
    from backend.agent.models import (
        load_chat_model,
        load_embeddings,
        register_embeddings_provider,
        register_model_provider
    )
    from backend.agent.graph import RAGGraph
    from langchain_qwq import ChatQwen
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"导入失败: {e}")
    print("请确保已安装所有依赖：uv sync")
    IMPORTS_SUCCESSFUL = False
    RAGGraph = None

def init_models():
    """初始化大模型和向量模型"""
    print("开始初始化模型...")

    # 1. 注册并加载大模型 (DeepSeek-V3.1)
    register_model_provider(
        provider_name="qwen",
        chat_model=ChatQwen
    )

    chat_model = load_chat_model(
        "qwen:qwen3-max-preview"
    )
    print(f"大模型加载成功: {type(chat_model)}")

    # 2. 注册并加载向量模型 (阿里云)
    print("注册向量模型提供商...")
    register_embeddings_provider(
        provider_name="ali",
        embeddings_model="openai",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    print("加载向量模型...")
    embeddings_model = load_embeddings(
        "ali:text-embedding-v4",
        api_key="sk-",
        check_embedding_ctx_length=False,
        dimensions=1536
    )
    print(f"向量模型加载成功: {type(embeddings_model)}")

    return chat_model, embeddings_model

# 初始化和导出图
if IMPORTS_SUCCESSFUL and RAGGraph:
    try:
        # 初始化模型
        llm, embeddings = init_models()
        print("模型初始化成功")

        # 创建 RAG 图实例（LangGraph Studio模式，禁用checkpointer）
        print("创建RAGGraph实例（LangGraph Studio模式）...")
        rag_graph = RAGGraph(llm=llm, embedding_model=embeddings, enable_checkpointer=False)
        print("RAGGraph实例创建成功")

        # 导出编译后的图给 LangGraph Studio 使用
        graph = rag_graph.graph

    except Exception as e:
        print(f"图初始化失败: {e}")
        print("创建空图实例")
        rag_graph = None
        graph = None
else:
    print("导入失败，无法创建图实例")
    rag_graph = None
    graph = None

# 导出组件
__all__ = ["graph", "rag_graph", "RAGGraph"]