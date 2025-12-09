"""
测试RAGGraph图检索模式(LightRAG)
初始化向量模型和大模型，设置检索模式为graph_only，然后调用invoke API
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

def test_raggraph_lightrag_mode():
    """测试RAGGraph的图检索模式(LightRAG)"""
    logger.info("开始测试RAGGraph图检索模式(LightRAG)...")

    try:
        # 初始化模型
        chat_model, embeddings_model = init_models()

        # 创建RAGGraph实例
        logger.info("创建RAGGraph实例...")
        rag_graph = RAGGraph(llm=chat_model, embedding_model=embeddings_model)
        logger.info("RAGGraph实例创建成功")

        # 设置图检索模式
        logger.info("设置检索模式为graph_only...")
        context = RAGContext(
            user_id="test_user_lightrag",
            session_id="test_conv_lightrag_001",
            retrieval_mode=RetrievalMode.GRAPH_ONLY
        )

        # 创建测试消息
        test_query = "lightrag是什么"
        messages = [HumanMessage(content=test_query)]
        logger.info(f"测试查询: {test_query}")
        inputdata={
            "messages": messages
        }
        # 调用RAGGraph进行图检索
        logger.info("开始调用RAGGraph进行图检索...")
        result = rag_graph.invoke(
            input_data=inputdata,
            context=context
        )

        # 打印结果
        logger.info("=== RAGGraph图检索模式测试结果 ===")
        logger.info(f"检索模式: {context.retrieval_mode}")
        logger.info(f"结果: {result}")
        # logger.info(f"用户ID: {context.user_id}")
        # logger.info(f"对话ID: {context.conversation_id}")

        # if "messages" in result:
        #     final_response = result["messages"][-1]
        #     logger.info(f"最终回答: {final_response.content}")
        # else:
        #     logger.warning("未找到回答消息")

        # # 检查是否使用了图检索
        # if "graph_search_results" in result:
        #     graph_results = result["graph_search_results"]
        #     logger.info(f"图检索结果数量: {len(graph_results) if graph_results else 0}")
        #     if graph_results:
        #         for i, doc in enumerate(graph_results[:3]):  # 只显示前3个结果
        #             logger.info(f"图检索结果 {i+1}: {doc.page_content[:200]}...")
        # else:
        #     logger.warning("未找到图检索结果")

        # # 检查检索决策
        # if "retrieval_decision" in result:
        #     decision = result["retrieval_decision"]
        #     logger.info(f"检索决策: {decision}")

        logger.info("RAGGraph图检索模式测试完成!")
        return True

    except Exception as e:
        logger.error(f"测试过程中发生错误: {str(e)}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    logger.info("开始执行RAGGraph LightRAG模式测试...")

    # 测试基本图检索功能
    logger.info("=" * 50)
    logger.info("测试1: 基本图检索功能")
    logger.info("=" * 50)
    success1 = test_raggraph_lightrag_mode()

    # if success1 and success2:
    #     logger.info("所有LightRAG图检索模式测试通过! ✅")
    # else:
    #     logger.error("部分测试失败，请检查错误日志 ❌")