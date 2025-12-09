# 导入必要的模块
from backend.agent.models import (
    load_chat_model,
    load_embeddings,
    register_embeddings_provider,
    register_model_provider
)
from backend.config.log import setup_default_logging, get_logger
setup_default_logging()
logger = get_logger(__name__)
def test_model():
    logger.info("注册大模型提供商...")
    register_model_provider(
        provider_name="modelscope",
        chat_model="openai",
        base_url="https://api-inference.modelscope.cn/v1"
    )
    
    logger.info("加载大模型...")
    chat_model = load_chat_model(
        "modelscope:deepseek-ai/DeepSeek-V3.1",
        api_key="ms-051829f9-88bc-48ac-9e0f-b5e0a595a3c4",
        temperature=0.7,
        max_tokens=2048
    )
    
    response = chat_model.invoke("你好")
    logger.info(f"模型回复: {response}")

if __name__ == "__main__":
    test_model()
