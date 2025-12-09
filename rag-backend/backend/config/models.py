#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型初始化配置模块
包含大模型和向量模型的初始化逻辑
"""

import os
from typing import Tuple

from backend.agent.models import (
    load_chat_model,
    load_embeddings,
    register_embeddings_provider,
    register_model_provider
)
from backend.config.log import get_logger
from langchain_qwq import ChatQwen

# 初始化日志
logger = get_logger(__name__)


def initialize_chat_model():
    """
    初始化大模型 (通义千问)

    Returns:
        chat_model: 初始化后的聊天模型实例
    """
    logger.info("注册大模型提供商...")
    register_model_provider(
        provider_name="qwen",
        chat_model=ChatQwen
    )

    logger.info("加载大模型...")
    # 从环境变量获取大语言模型配置
    api_key = os.getenv("LLM_DASHSCOPE_API_KEY")
    api_base = os.getenv("LLM_DASHSCOPE_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    model_name = os.getenv("LLM_DASHSCOPE_CHAT_MODEL", "qwen3-max-preview")

    if not api_key:
        raise ValueError("LLM_DASHSCOPE_API_KEY 环境变量未设置")

    # 设置环境变量以供模型加载使用
    os.environ["DASHSCOPE_API_KEY"] = api_key
    os.environ["DASHSCOPE_API_BASE"] = api_base

    chat_model = load_chat_model(f"qwen:{model_name}")
    logger.info(f"大模型加载成功: {type(chat_model)}")

    return chat_model


def initialize_embeddings_model():
    """
    初始化向量模型 (阿里云)

    Returns:
        embeddings_model: 初始化后的向量模型实例

    Raises:
        ValueError: 当VECTOR_DASHSCOPE_API_KEY环境变量未设置时
    """
    logger.info("注册向量模型提供商...")
    # 从环境变量获取向量模型配置
    api_base = os.getenv("VECTOR_DASHSCOPE_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    embedding_model = os.getenv("VECTOR_DASHSCOPE_EMBEDDING_MODEL", "text-embedding-v4")

    register_embeddings_provider(
        provider_name="ali",
        embeddings_model="openai",
        base_url=api_base
    )

    logger.info("加载向量模型...")
    # 从环境变量获取向量模型 API Key
    api_key = os.getenv("VECTOR_DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("VECTOR_DASHSCOPE_API_KEY 环境变量未设置")

    embeddings_model = load_embeddings(
        f"ali:{embedding_model}",
        api_key=api_key,
        check_embedding_ctx_length=False,
        dimensions=1536
    )
    logger.info(f"向量模型加载成功: {type(embeddings_model)}")

    return embeddings_model


def initialize_models() -> Tuple:
    """
    初始化所有模型
    
    Returns:
        Tuple: (chat_model, embeddings_model) 包含聊天模型和向量模型的元组
    """
    logger.info("开始初始化所有模型...")
    
    # 初始化大模型
    chat_model = initialize_chat_model()
    
    # 初始化向量模型
    embeddings_model = initialize_embeddings_model()
    
    logger.info("所有模型初始化完成")
    return chat_model, embeddings_model