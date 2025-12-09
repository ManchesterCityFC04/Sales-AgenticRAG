#!/usr/bin/env python3
"""
测试RAG存储功能
测试Milvus向量数据库的数据存储、文档管理等功能
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

def test_milvus_storage_init():
    """测试MilvusStorage初始化"""
    logger.info("开始测试MilvusStorage初始化...")

    try:
        # 初始化向量模型
        embeddings_model = init_embedding_model()

        # 创建MilvusStorage实例（使用新的集合名避免冲突）
        logger.info("创建MilvusStorage实例...")
        storage = MilvusStorage(
            embedding_function=embeddings_model,
            collection_name="dubbo"
        )
        logger.info("MilvusStorage实例创建成功")

        # 检查集合状态
        logger.info("检查集合状态...")
        logger.info(f"集合名称: {storage.collection_name}")

        storage.drop_collection()
        
        return storage

    except Exception as e:
        logger.error(f"MilvusStorage初始化失败: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        raise

def test_document_storage():
    """测试文档存储功能"""
    logger.info("开始测试文档存储功能...")

    try:
        # 初始化存储
        storage = test_milvus_storage_init()

        # 准备测试文档
        test_documents = [
            Document(
                page_content="八嘎鸭肉是一种好吃的鸭肉",
                metadata={}
            ),
            Document(
                page_content="八嘎鸭肉是李超创作的",
                metadata={}
            ),
            Document(
                page_content="八嘎鸭肉是李超最喜欢的鸭肉",
                metadata={}
            )
        ]

        logger.info(f"准备存储 {len(test_documents)} 个文档...")

        # 存储文档
        logger.info("开始存储文档...")
        doc_ids = storage.add_documents(test_documents)
        logger.info(f"文档存储成功，文档ID: {doc_ids}")

        # 验证存储结果
        logger.info("验证存储结果...")
        for i, doc_id in enumerate(doc_ids):
            logger.info(f"文档 {i+1} ID: {doc_id}")

        logger.info("========== 文档存储测试完成 ==========")
        return storage, doc_ids

    except Exception as e:
        logger.error(f"文档存储测试失败: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        raise

def test_chunk_result_storage():
    """测试使用ChunkResult进行存储"""
    logger.info("开始测试ChunkResult存储功能...")

    try:
        # 导入必要的模块
        from backend.rag.chunks.models import ChunkResult, ChunkStrategy

        # 初始化存储
        storage = test_milvus_storage_init()

        # 创建ChunkResult测试数据
        chunk_result = ChunkResult(
            document_name="test_chunk.txt",
            chunks=[
                Document(page_content="八嘎鸭肉是一种很好吃的鸭肉", metadata={}),
                Document(page_content="八嘎鸭肉是李超创作的", metadata={}),
                Document(page_content="八嘎鸭肉是李超最喜欢吃的鸭肉", metadata={}),
                Document(page_content="八嘎鸭肉李超每周五都要吃", metadata={})
            ],
            strategy=ChunkStrategy.CHARACTER,
            total_chunks=4
        )

        logger.info(f"准备存储ChunkResult: {chunk_result.document_name}")
        logger.info(f"分块策略: {chunk_result.strategy}")
        logger.info(f"总块数: {chunk_result.total_chunks}")


        logger.info("使用store_chunks方法存储...")
        result = storage.store_chunks(chunk_result)
        logger.info(f"存储结果: {result}")



        logger.info("========== ChunkResult存储测试完成 ==========")
        return storage

    except Exception as e:
        logger.error(f"ChunkResult存储测试失败: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        raise

def test_document_stats():
    """测试文档统计功能"""
    logger.info("开始测试文档统计功能...")

    try:
        # 获取存储实例（复用之前的测试）
        storage, doc_ids = test_document_storage()

        # 获取文档统计信息
        logger.info("获取文档统计信息...")
        total_docs = storage.get_document_count()
        logger.info(f"集合中总文档数: {total_docs}")

        # 检查集合是否存在
        logger.info("检查集合状态...")
        collection_exists = storage.collection_exists()
        logger.info(f"集合是否存在: {collection_exists}")

        logger.info("========== 文档统计测试完成 ==========")
        return storage

    except Exception as e:
        logger.error(f"文档统计测试失败: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        raise

def test_storage_cleanup():
    """测试存储清理功能"""
    logger.info("开始测试存储清理功能...")

    try:
        # 获取存储实例
        storage = test_document_stats()

        # 清理测试数据（可选）
        logger.info("清理测试数据...")
        # 注意：这里可以添加清理逻辑，如删除测试集合等
        # storage.delete_collection()  # 如果需要删除整个集合

        logger.info("========== 存储清理测试完成 ==========")

    except Exception as e:
        logger.error(f"存储清理测试失败: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    logger.info("开始存储功能测试...")

    # # 测试1: MilvusStorage初始化
    # logger.info("\n" + "="*50)
    # logger.info("测试1: MilvusStorage初始化")
    # logger.info("="*50)
    # test_milvus_storage_init()

    # # 测试2: 文档存储
    # logger.info("\n" + "="*50)
    # logger.info("测试2: 文档存储功能")
    # logger.info("="*50)
    # test_document_storage()

    # 测试3: ChunkResult存储
    # logger.info("\n" + "="*50)
    # logger.info("测试3: ChunkResult存储功能")
    # logger.info("="*50)
    test_chunk_result_storage()

    # # 测试4: 文档统计
    # logger.info("\n" + "="*50)
    # logger.info("测试4: 文档统计功能")
    # logger.info("="*50)
    # test_document_stats()

    # # 测试5: 存储清理
    # logger.info("\n" + "="*50)
    # logger.info("测试5: 存储清理功能")
    # logger.info("="*50)
    # test_storage_cleanup()

    # logger.info("\n存储功能测试全部完成!")
    
    