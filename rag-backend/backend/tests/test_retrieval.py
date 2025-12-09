#!/usr/bin/env python3
"""
测试RAG检索功能
测试Milvus向量数据库的文档检索、混合检索器等功能
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入必要的模块
from backend.agent.models import (
    load_embeddings,
    register_embeddings_provider
)
from backend.rag.storage.milvus_storage import MilvusStorage
from backend.config.log import setup_default_logging, get_logger
from langchain_core.documents import Document

# 初始化日志
setup_default_logging()
logger = get_logger(__name__)

def init_embedding_model():
    """初始化向量模型"""
    logger.info("开始初始化向量模型...")

    # 注册并加载向量模型 (阿里云)
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

    return embeddings_model

def setup_test_data():
    """设置测试数据"""
    logger.info("开始设置测试数据...")

    try:
        # 初始化向量模型
        embeddings_model = init_embedding_model()

        # 创建MilvusStorage实例
        logger.info("创建MilvusStorage实例...")
        storage = MilvusStorage(
            embedding_function=embeddings_model,
            collection_name="test_retrieval_chunks"
        )
        logger.info("MilvusStorage实例创建成功")

        # 准备测试文档
        test_documents = [
            Document(
                page_content="Python是一种高级编程语言，具有简洁的语法和强大的功能。Python广泛应用于Web开发、数据科学、人工智能等领域。",
                metadata={"source": "python_intro.txt", "page": 1, "type": "programming"}
            ),
            Document(
                page_content="机器学习是人工智能的一个分支，通过算法让计算机自动学习数据模式。常用的机器学习算法包括线性回归、决策树、神经网络等。",
                metadata={"source": "ml_intro.txt", "page": 1, "type": "ai"}
            ),
            Document(
                page_content="向量数据库是专门用于存储和检索高维向量数据的数据库系统。Milvus是一个开源的向量数据库，支持大规模向量检索。",
                metadata={"source": "vector_db.txt", "page": 1, "type": "database"}
            ),
            Document(
                page_content="深度学习是机器学习的一个子集，使用神经网络模型来模拟人脑的学习过程。深度学习在图像识别、自然语言处理等领域取得了突破性进展。",
                metadata={"source": "deep_learning.txt", "page": 1, "type": "ai"}
            ),
            Document(
                page_content="FastAPI是一个现代、快速的Web框架，用于构建Python API。它基于标准Python类型提示，具有自动文档生成等特性。",
                metadata={"source": "fastapi_intro.txt", "page": 1, "type": "programming"}
            )
        ]

        logger.info(f"准备存储 {len(test_documents)} 个测试文档...")

        # 存储文档
        logger.info("开始存储测试文档...")
        doc_ids = storage.add_documents(test_documents)
        logger.info(f"测试文档存储成功，文档ID: {doc_ids}")

        return storage

    except Exception as e:
        logger.error(f"测试数据设置失败: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        raise

def test_basic_similarity_search():
    """测试基本相似性检索"""
    logger.info("开始测试基本相似性检索...")

    try:
        # 设置测试数据
        storage = setup_test_data()

        # 测试查询
        test_queries = [
            "什么是Python编程语言？",
            "机器学习算法有哪些？",
            "向量数据库的作用是什么？"
        ]

        for i, query in enumerate(test_queries):
            logger.info(f"\n--- 测试查询 {i+1}: {query} ---")

            # 执行相似性检索
            results = storage.similarity_search(query, k=3)
            logger.info(f"检索到 {len(results)} 个相关文档:")

            for j, doc in enumerate(results):
                content_preview = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
                logger.info(f"  文档 {j+1}:")
                logger.info(f"    内容: {content_preview}")
                logger.info(f"    元数据: {doc.metadata}")

        logger.info("========== 基本相似性检索测试完成 ==========")
        return storage

    except Exception as e:
        logger.error(f"基本相似性检索测试失败: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        raise

def test_similarity_search_with_score():
    """测试带分数的相似性检索"""
    logger.info("开始测试带分数的相似性检索...")

    try:
        # 复用之前的存储实例
        storage = test_basic_similarity_search()

        # 测试查询
        query = "深度学习和神经网络"
        logger.info(f"查询: {query}")

        # 执行带分数的相似性检索
        logger.info("执行带分数的相似性检索...")
        results_with_scores = storage.similarity_search_with_score(query, k=3)
        logger.info(f"检索到 {len(results_with_scores)} 个相关文档（带分数）:")

        for i, (doc, score) in enumerate(results_with_scores):
            content_preview = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
            logger.info(f"  文档 {i+1} (相似度分数: {score:.4f}):")
            logger.info(f"    内容: {content_preview}")
            logger.info(f"    元数据: {doc.metadata}")

        logger.info("========== 带分数的相似性检索测试完成 ==========")
        return storage

    except Exception as e:
        logger.error(f"带分数的相似性检索测试失败: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        raise

def test_hybrid_retriever():
    """测试混合检索器"""
    logger.info("开始测试混合检索器...")

    try:
        # 复用之前的存储实例
        storage = test_similarity_search_with_score()

        # 创建混合检索器
        logger.info("创建混合检索器...")
        hybrid_retriever = storage.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": 5,
                "score_threshold": 0.3  # 设置相似度阈值
            }
        )
        logger.info("混合检索器创建成功")

        # 测试检索器
        test_queries = [
            "Python Web开发框架",
            "人工智能和机器学习的区别",
            "数据库存储技术"
        ]

        for i, query in enumerate(test_queries):
            logger.info(f"\n--- 混合检索测试 {i+1}: {query} ---")

            # 使用检索器检索
            retrieved_docs = hybrid_retriever.invoke(query)
            logger.info(f"检索到 {len(retrieved_docs)} 个相关文档:")

            for j, doc in enumerate(retrieved_docs):
                content_preview = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
                logger.info(f"  文档 {j+1}:")
                logger.info(f"    内容: {content_preview}")
                logger.info(f"    类型: {doc.metadata.get('type', 'unknown')}")
                logger.info(f"    来源: {doc.metadata.get('source', 'unknown')}")

        logger.info("========== 混合检索器测试完成 ==========")
        return storage

    except Exception as e:
        logger.error(f"混合检索器测试失败: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        raise

def test_advanced_retrieval_features():
    """测试高级检索功能"""
    logger.info("开始测试高级检索功能...")

    try:
        # 复用之前的存储实例
        storage = test_hybrid_retriever()

        # 测试不同的检索参数
        query = "编程语言和框架"
        logger.info(f"查询: {query}")

        # 测试1: 增加检索数量
        logger.info("\n--- 测试1: 大量检索 (k=5) ---")
        results_large = storage.similarity_search(query, k=5)
        logger.info(f"检索到 {len(results_large)} 个文档")
        for i, doc in enumerate(results_large):
            logger.info(f"  文档 {i+1} 类型: {doc.metadata.get('type', 'unknown')}")

        # 测试2: 基于元数据过滤（如果支持）
        logger.info("\n--- 测试2: 检索结果分析 ---")
        doc_types = {}
        for doc in results_large:
            doc_type = doc.metadata.get('type', 'unknown')
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1

        logger.info("文档类型分布:")
        for doc_type, count in doc_types.items():
            logger.info(f"  {doc_type}: {count} 个文档")

        logger.info("========== 高级检索功能测试完成 ==========")

    except Exception as e:
        logger.error(f"高级检索功能测试失败: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    logger.info("开始检索功能测试...")

    # 测试1: 基本相似性检索
    logger.info("\n" + "="*50)
    logger.info("测试1: 基本相似性检索")
    logger.info("="*50)
    test_basic_similarity_search()

    # 测试2: 带分数的相似性检索
    logger.info("\n" + "="*50)
    logger.info("测试2: 带分数的相似性检索")
    logger.info("="*50)
    test_similarity_search_with_score()

    # 测试3: 混合检索器
    logger.info("\n" + "="*50)
    logger.info("测试3: 混合检索器")
    logger.info("="*50)
    test_hybrid_retriever()

    # 测试4: 高级检索功能
    logger.info("\n" + "="*50)
    logger.info("测试4: 高级检索功能")
    logger.info("="*50)
    test_advanced_retrieval_features()

    logger.info("\n检索功能测试全部完成!")