from backend.agent.models import (
    load_embeddings,
    register_embeddings_provider,
)
from backend.config.log import setup_default_logging, get_logger
import os



def get_embedding_model():
    setup_default_logging()
    logger = get_logger(__name__)
    logger.info("初始化模型...")
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