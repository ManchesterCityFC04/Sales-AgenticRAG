#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试RAGGraph invoke方法
初始化向量模型和大模型，然后调用invoke API
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
from backend.config.log import setup_default_logging, get_logger
from langchain_qwq import ChatQwen
# 初始化日志
setup_default_logging()
logger = get_logger(__name__)

def init_models():
    """初始化大模型和向量模型"""
    logger.info("开始初始化模型...")
    
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

def test_raggraph_invoke():
    """测试RAGGraph的invoke方法"""
    logger.info("开始测试RAGGraph invoke方法...")
    
    try:
        # 初始化模型
        chat_model, embeddings_model = init_models()
        
        # 创建RAGGraph实例
        logger.info("创建RAGGraph实例...")
        rag_graph = RAGGraph(llm=chat_model, embedding_model=embeddings_model)
        logger.info("RAGGraph实例创建成功")
        
        # 创建RAG上下文
        logger.info("创建RAG上下文...")
        context = RAGContext(
            session_id="tessasaasasassas2",
            user_id="test_user_020",
            retrieval_mode="no_retrieval"
        )
        logger.info("RAG上下文创建成功")
        
        # 准备输入数据
        input_data = {
            "messages": [
                {"role": "user", "content": "我上一个问题是什么"}
            ]
        }
        logger.info(f"输入问题: {input_data['messages'][0]['content']}")
        
        # 调用invoke方法
        logger.info("调用RAGGraph.invoke方法...")
        result = rag_graph.invoke(input_data, context)

        # 输出结果
        logger.info("RAGGraph invoke调用成功!")
        #logger.info(f"结果类型: {type(result)}")

        logger.info(f"最终答案: {result}")

        return result
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {str(e)}")
        logger.exception("详细错误信息:")
        raise

def test_raggraph_stream():
    """测试RAGGraph的stream流式输出方法"""
    logger.info("开始测试RAGGraph stream流式输出...")

    try:
        # 初始化模型
        chat_model, embeddings_model = init_models()

        # 创建RAGGraph实例
        logger.info("创建RAGGraph实例...")
        rag_graph = RAGGraph(llm=chat_model, embedding_model=embeddings_model)
        logger.info("RAGGraph实例创建成功")

        # # 创建RAG上下文
        # logger.info("创建RAG上下文...")
        # context = RAGContext(
        #     session_id="test_stream_session_0011",
        #     user_id="test_user_stream"
        # )
        # logger.info("RAG上下文创建成功")

        # # 准备输入数据
        # input_data = {
        #     "messages": [
        #         {"role": "user", "content": "请介绍一下Python编程语言的特点"}
        #     ]
        # }
        # logger.info(f"输入问题: {input_data['messages'][0]['content']}")

        final_result = None

        # 方法1: 使用 stream_mode="updates" 查看节点更新
        # logger.info("🔄 方法1: 节点更新流式输出 (stream_mode='updates')")
        

        # for chunk in rag_graph.stream(input_data, context, stream_mode="updates"):
        #     print(chunk)
        #     print("\n")

        # 方法2: 使用 stream_mode="values" 查看完整状态
        # logger.info("="*60)
        # logger.info("🔄 方法2: 完整状态流式输出 (stream_mode='values')")

        # # 使用新的会话ID避免冲突
        # context_values = RAGContext(
        #     session_id="test_stream_values_0501",
        #     user_id="test_user_stream"
        # )

        # input_data_values = {
        #     "messages": [
        #         {"role": "user", "content": "1+1等于多少？"}
        #     ]
        # }

        # for state_snapshot in rag_graph.stream(input_data_values, context_values, stream_mode="values"):
        #     logger.info(f"状态快照: {state_snapshot}")

        # 方法3: 如果支持，尝试使用 stream_mode="messages" 获取LLM token
        # logger.info("\n" + "="*60)
        # logger.info("🔄 方法3: LLM Token流式输出 (stream_mode='messages')")

        # # 使用新的会话ID避免冲突
        # context_values = RAGContext(
        #     session_id="test_stream_valuess_01",
        #     user_id="test_user_stream"
        # )

        # input_data_messages = {
        #     "messages": [
        #         {"role": "user", "content": "你是什么模型"}
        #     ]
        # }

        # for state_snapshot in rag_graph.stream(input_data_messages, context_values, stream_mode="values"):
        #     logger.info(f"状态快照: {state_snapshot}")

        # 方法3: 如果支持，尝试使用 stream_mode="messages" 获取LLM token
        # logger.info("\n" + "="*60)
        # logger.info("🔄 方法3: LLM Token流式输出 (stream_mode='messages')")

        context_messages = RAGContext(
            session_id="tesessasssge1s_01",
            user_id="test_user_stresam"
        )

        input_data_messages = {
            "messages": [
                {"role": "user", "content": "查找知识库为我介绍istio"}
            ]
        }

        logger.info("🎯 尝试捕获LLM token流...")
        
        
        for mode,chunk in rag_graph.stream(input_data_messages, context_messages, stream_mode="mix"):
            if mode == "updates":
                node_name = list(chunk.keys())[0]
                print(f"节点名称: {node_name}")
                if node_name == "generate_answer" or node_name == "direct_answer":
                    print(f"{chunk}")
            if mode == "messages":
                chunkmessage,metadata=chunk
                if chunkmessage.content:
                    print(f"消息: {chunkmessage.content}")
            #     if chunkmessage.content and len(chunkmessage.content.strip())<=10:
            #         print(f"消息: {chunkmessage.content}")
            #         #print(f"元数据: {metadata}")
        

        # for mode,chunk in rag_graph.stream(input_data_messages, context_messages, stream_mode="mix"):
        #     # print(metadata)
        #     # print(chunk)
        #     # print(f"[{mode}]")
        #     if mode == "updates":
        #         # 显示节点名称
                
        #         node_name = list(chunk.keys())[0]
        #         node_output = chunk[node_name]
        #         print(f"节点名称: {node_name}")
        #         print(f"节点输出: {node_output}")
        #     print("============")
        #     if mode == "messages":
        #         chunkmessage,metadata=chunk
        #         print(f"消息: {chunkmessage}")
        #     #     if chunkmessage.content and len(chunkmessage.content.strip())<=10:
        #     #         print(f"消息: {chunkmessage.content}")
        #     #         #print(f"元数据: {metadata}")

                            

        return final_result

    except Exception as e:
        logger.error(f"流式输出测试过程中发生错误: {str(e)}")
        logger.exception("详细错误信息:")
        raise

if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("开始RAGGraph测试")
    logger.info("=" * 80)

    try:
        # 测试1: invoke方法
        # logger.info("\n" + "=" * 50)
        logger.info("测试1: invoke方法")
        logger.info("=" * 50)
        #result1 = test_raggraph_invoke()

        # 测试2: stream流式输出方法
        # logger.info("\n" + "=" * 50)
        # logger.info("测试2: stream流式输出方法")
        # logger.info("=" * 50)
        result2 = test_raggraph_stream()

        logger.info("\n" + "=" * 80)
        logger.info("所有测试完成!")
        # logger.info("=" * 80)
        # logger.info("测试总结:")
        # logger.info(f"1. invoke方法测试: {'成功' if result1 else '失败'}")
        #logger.info(f"2. stream方法测试: {'成功' if result2 else '失败'}")

    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
        exit(1)