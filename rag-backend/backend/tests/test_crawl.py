from backend.service.crawl import initialize_collection_and_store
from backend.config.log import setup_default_logging, get_logger
from backend.config.agent import initialize_rag_graph
from backend.param.crawl import CrawlRequest


async def test(param: CrawlRequest):
    setup_default_logging()
    logger = get_logger(__name__)
    initialize_rag_graph()
    logger.info("测试开始")
    await initialize_collection_and_store(param)
    logger.info("测试完成")

if __name__ == "__main__":
    param = CrawlRequest(
        url="https://istio.io/latest/zh/docs/",
        prefix="https://istio.io/latest/zh/docs/",
        if_llm=False,
        base_url="https://api.openai.com/v1",
        api_key="sk-",
        provider="openai",
        model_id="gpt-3.5-turbo",
        user_id="1",
        title="测试文档",
        collection_id="test_collection",
    )

    import asyncio
    asyncio.run(test(param))
