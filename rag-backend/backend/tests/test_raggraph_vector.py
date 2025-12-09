#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试RAGGraph向量检索模式
初始化向量模型和大模型，设置检索模式为vector_only，然后调用invoke API
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入必要的模块
from backend.agent.models import (
    load_chat_model,
    load_embeddings,
    register_embeddings_provider,
    register_model_provider
)
from backend.agent.graph import RAGGraph
from backend.agent.contexts.raggraph_context import RAGContext
from backend.agent.models.raggraph_models import RetrievalMode
from backend.config.log import setup_default_logging, get_logger
from langchain_core.messages import HumanMessage
from langchain_qwq import ChatQwen

# 初始化日志
setup_default_logging()
logger = get_logger(__name__)

def init_models():
    """初始化大模型和向量模型"""
    logger.info("开始初始化模型...")

    # 1. 注册并加载聊天模型
    register_model_provider(
        provider_name="qwen",
        chat_model=ChatQwen
    )

    chat_model = load_chat_model(
        "qwen:qwen3-max-preview"
    )
    logger.info(f"大模型加载成功: {type(chat_model)}")

    # 2. 注册并加载向量模型 (阿里云)
    logger.info("注册向量模型提供商...")
    register_embeddings_provider(
        provider_name="ali",
        embeddings_model="openai",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    logger.info("加载向量模型...")
    embeddings_model = load_embeddings(
        "ali:text-embedding-v4",
        api_key="sk-",
        check_embedding_ctx_length=False,
        dimensions=1536
    )
    logger.info(f"向量模型加载成功: {type(embeddings_model)}")

    return chat_model, embeddings_model

def test_raggraph_vector_mode():
    """测试RAGGraph的向量检索模式"""
    logger.info("开始测试RAGGraph向量检索模式...")

    try:
        # 初始化模型
        chat_model, embeddings_model = init_models()

        # 创建RAGGraph实例
        logger.info("创建RAGGraph实例...")
        rag_graph = RAGGraph(llm=chat_model, embedding_model=embeddings_model)
        logger.info("RAGGraph实例创建成功")

        # 创建RAG上下文 - 设置检索模式为vector_only
        logger.info("创建RAG上下文（向量检索模式）...")
        context = RAGContext(
            session_id="test_vector_session001",
            user_id="test_user_vector",
            retrieval_mode=RetrievalMode.VECTOR_ONLY,  # 设置为向量检索模式
            max_retrieval_docs=4,
            system_prompt="你是一个专业的RAG助手，能够基于向量检索到的信息提供准确的回答。"
        )
        logger.info(f"RAG上下文创建成功，检索模式: {context.retrieval_mode}")

        # 准备输入数据
        test_question = "八嘎鸭肉是什么？"
        input_data = {
            "messages": [HumanMessage(content=test_question)]
        }
        logger.info(f"测试问题: {test_question}")

        # 调用RAGGraph的invoke方法
        logger.info("调用RAGGraph invoke方法...")
        result = rag_graph.invoke(input_data, context)
        logger.info("RAGGraph invoke调用成功!")

        # 输出结果
        logger.info("========== 测试结果 ==========")
        logger.info(f"检索模式: {result.get('retrieval_mode', 'unknown')}")
        logger.info(f"是否需要检索: {result.get('need_retrieval', 'unknown')}")
        logger.info(f"检索到的文档数量: {len(result.get('retrieved_docs', []))}")
        logger.info(f"向量检索结果数量: {len(result.get('vector_db_results', []))}")
        logger.info(f"文档相关性: {result.get('docs_relevant', 'unknown')}")
        logger.info(f"最终答案: {result.get('final_answer', '未生成答案')}")

        # 打印消息历史
        messages = result.get('messages', [])
        logger.info(f"消息历史数量: {len(messages)}")
        for i, msg in enumerate(messages):
            msg_type = type(msg).__name__
            content_preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            logger.info(f"消息 {i+1} ({msg_type}): {content_preview}")

        logger.info("========== 测试完成 ==========")

        return result

    except Exception as e:
        logger.error(f"测试过程中出现错误: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        raise

def test_raggraph_vector_with_docs():
    """测试RAGGraph向量检索模式（期望有检索到的文档）"""
    logger.info("开始测试RAGGraph向量检索模式（带文档检索）...")

    try:
        # 初始化模型
        chat_model, embeddings_model = init_models()

        # 创建RAGGraph实例
        logger.info("创建RAGGraph实例...")
        rag_graph = RAGGraph(llm=chat_model, embedding_model=embeddings_model)
        logger.info("RAGGraph实例创建成功")

        # 创建RAG上下文 - 设置检索模式为vector_only
        logger.info("创建RAG上下文（向量检索模式）...")
        context = RAGContext(
            session_id="test_vector_docs_session_001",
            user_id="test_user_vector_docs",
            retrieval_mode=RetrievalMode.VECTOR_ONLY,
            max_retrieval_docs=3,
            system_prompt="你是一个专业的RAG助手，请基于检索到的文档内容回答用户问题。"
        )

        # 准备一个更具体的技术问题，更可能检索到相关文档
        test_question = "Python中如何使用装饰器？"
        input_data = {
            "messages": [HumanMessage(content=test_question)]
        }
        logger.info(f"测试问题: {test_question}")

        # 调用RAGGraph的invoke方法
        logger.info("调用RAGGraph invoke方法...")
        result = rag_graph.invoke(input_data, context)
        logger.info("RAGGraph invoke调用成功!")

        # 详细输出检索结果
        logger.info("========== 向量检索测试结果 ==========")
        logger.info(f"检索模式: {result.get('retrieval_mode', 'unknown')}")
        logger.info(f"是否需要检索: {result.get('need_retrieval', 'unknown')}")

        # 检索文档详情
        retrieved_docs = result.get('retrieved_docs', [])
        vector_docs = result.get('vector_db_results', [])
        logger.info(f"检索到的文档数量: {len(retrieved_docs)}")
        logger.info(f"向量检索结果数量: {len(vector_docs)}")

        if retrieved_docs:
            logger.info("检索到的文档详情:")
            for i, doc in enumerate(retrieved_docs[:3]):  # 只显示前3个
                content_preview = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                metadata = doc.metadata
                logger.info(f"文档 {i+1}:")
                logger.info(f"  内容预览: {content_preview}")
                logger.info(f"  元数据: {metadata}")
        else:
            logger.info("未检索到任何文档")

        logger.info(f"文档相关性评估: {result.get('docs_relevant', 'unknown')}")
        logger.info(f"最终答案: {result.get('final_answer', '未生成答案')}")

        # 检查子问题扩展
        subquestions = result.get('subquestions', [])
        if subquestions:
            logger.info(f"扩展的子问题数量: {len(subquestions)}")
            for i, sq in enumerate(subquestions):
                logger.info(f"  子问题 {i+1}: {sq}")

        logger.info("========== 测试完成 ==========")

        return result

    except Exception as e:
        logger.error(f"测试过程中出现错误: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    logger.info("开始向量检索模式测试...")

    # 测试1: 基本向量检索模式
    logger.info("\n" + "="*50)
    logger.info("测试1: 基本向量检索模式")
    logger.info("="*50)
    test_raggraph_vector_mode()

    # # 测试2: 向量检索模式（期望有文档）
    # logger.info("\n" + "="*50)
    # logger.info("测试2: 向量检索模式（期望有文档）")
    # logger.info("="*50)
    # test_raggraph_vector_with_docs()

    logger.info("\n向量检索模式测试全部完成!")