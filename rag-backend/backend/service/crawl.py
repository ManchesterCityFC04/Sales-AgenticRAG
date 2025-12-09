import asyncio
import json
from datetime import datetime
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig, DefaultMarkdownGenerator, BrowserConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy, DFSDeepCrawlStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling.filters import FilterChain, URLPatternFilter
from crawl4ai.content_filter_strategy import LLMContentFilter, PruningContentFilter, RelevantContentFilter
from backend.param.crawl import CrawlRequest
from backend.rag.storage.milvus_storage import MilvusStorage
from backend.rag.storage.lightrag_storage import LightRAGStorage
from backend.config.embedding import get_embedding_model
from backend.rag.chunks.chunks import ChunkResult, TextChunker
from backend.rag.chunks.models import ChunkConfig, ChunkStrategy, DocumentContent
from backend.rag.chunks.document_extraction import DocumentExtractor
from backend.config.log import get_logger
from backend.config.redis import get_redis_client
import asyncio
import subprocess
import requests
import tempfile
import os


# 获取logger实例
logger = get_logger("crawl_service")

# 定义爬虫状态常量
CRAWL_STATUS_PROCESSING = "processing"
CRAWL_STATUS_COMPLETED = "completed"
CRAWL_STATUS_ERROR = "error"

async def initialize_collection_and_store(request: CrawlRequest):
    milvus_storage = MilvusStorage(
        embedding_function=get_embedding_model(),
        collection_name=request.collection_id,
    )

    lightrag_storage = LightRAGStorage(workspace=request.collection_id)
    
    
    # 初始化爬虫状态
    await init_crawl_status(request.collection_id)
    
    # 为对应的知识库添加文档记录
    from backend.service.knowledge_library import add_document
    from backend.param.knowledge_library import AddDocumentRequest
    from backend.config.database import DatabaseFactory
    from backend.model.knowledge_library import KnowledgeLibrary
    
    try:
        # 根据collection_id查找知识库
        db = DatabaseFactory.create_session()
        library = db.query(KnowledgeLibrary).filter(
            KnowledgeLibrary.collection_id == request.collection_id,
            KnowledgeLibrary.is_active == True
        ).first()
        
        if library:
            # 创建文档记录
            doc_request = AddDocumentRequest(
                library_id=library.id,
                name=request.title or "爬虫文档",
                type="link",  # 爬虫类型为链接
                url=request.url
            )
            
            # 添加文档到知识库
            await add_document(doc_request, library.user_id)
            logger.info(f"成功为知识库 {library.title} 添加文档记录: {request.title or '爬虫文档'}")
        else:
            logger.warning(f"未找到collection_id为 {request.collection_id} 的知识库")
            
    except Exception as e:
        logger.error(f"添加文档记录失败: {str(e)}")
    finally:
        if db:
            db.close()
    
    try:
        await crawl_doc(request.url, request.prefix, request.if_llm, request.model_id, request.provider, request.base_url, request.api_key, milvus_storage, lightrag_storage, request.collection_id)
        # await test_crawl_doc(request.url, request.prefix, request.if_llm, request.model_id, request.provider, request.base_url, request.api_key)
        # 爬虫完成，更新状态为已完成
        await update_crawl_status(request.collection_id, CRAWL_STATUS_COMPLETED)
    except Exception as e:
        # 爬虫异常，更新状态为错误
        await update_crawl_status(request.collection_id, CRAWL_STATUS_ERROR, str(e))
        raise


async def init_crawl_status(collection_id: str):
    """初始化爬虫状态"""
    try:
        redis_client = await get_redis_client()
        status_data = {
            "status": CRAWL_STATUS_PROCESSING,
            "count": 0,
            "message": "爬虫任务开始",
            "start_time": datetime.now().isoformat(),
            "last_update": datetime.now().isoformat()
        }
        await redis_client.set(f"crawl_status:{collection_id}", json.dumps(status_data))
        logger.info(f"初始化爬虫状态: {collection_id}")
    except Exception as e:
        logger.warning(f"Redis连接失败，跳过状态存储: {e}")


async def update_crawl_status(collection_id: str, status: str, message: str = None, count: int = None):
    """更新爬虫状态"""
    try:
        redis_client = await get_redis_client()
        
        # 获取当前状态
        current_status = await redis_client.get(f"crawl_status:{collection_id}")
        if current_status:
            status_data = json.loads(current_status)
        else:
            status_data = {
                "status": status,
                "count": 0,
                "message": message or "",
                "start_time": datetime.now().isoformat(),
                "last_update": datetime.now().isoformat()
            }
        
        # 更新状态数据
        status_data["status"] = status
        status_data["last_update"] = datetime.now().isoformat()
        
        if message:
            status_data["message"] = message
        
        if count is not None:
            status_data["count"] = count
        
        await redis_client.set(f"crawl_status:{collection_id}", json.dumps(status_data))
        logger.info(f"更新爬虫状态: {collection_id} - {status}")
    except Exception as e:
        logger.warning(f"Redis连接失败，跳过状态更新: {e}")


async def increment_crawl_count(collection_id: str):
    """增加爬虫计数"""
    redis_client = await get_redis_client()
    
    current_status = await redis_client.get(f"crawl_status:{collection_id}")
    if current_status:
        status_data = json.loads(current_status)
        status_data["count"] = status_data.get("count", 0) + 1
        status_data["last_update"] = datetime.now().isoformat()
        await redis_client.set(f"crawl_status:{collection_id}", json.dumps(status_data))


async def get_crawl_status(collection_id: str) -> dict:
    """
    获取爬虫状态
    
    Args:
        collection_id: 集合ID
        
    Returns:
        dict: 爬虫状态信息，包含status, count, message, start_time, last_update字段
              如果不存在该集合的状态，返回空字典
    """
    redis_client = await get_redis_client()
    
    status_data = await redis_client.get(f"crawl_status:{collection_id}")
    if status_data:
        return json.loads(status_data)
    else:
        return {}


async def get_all_crawl_status() -> dict:
    """
    获取所有爬虫状态
    
    Returns:
        dict: 所有爬虫状态，key为集合ID，value为状态信息
    """
    redis_client = await get_redis_client()
    
    # 获取所有以crawl_status:开头的key
    keys = await redis_client.keys("crawl_status:*")
    
    status_dict = {}
    for key in keys:
        # 提取集合ID
        collection_id = key.replace("crawl_status:", "")
        status_data = await redis_client.get(key)
        if status_data:
            status_dict[collection_id] = json.loads(status_data)
    
    return status_dict

async def test_crawl_doc(site: str, prefix: str, if_llm: bool, model_id: str, provider: str, base_url: str, api_token: str):
    content_filter: RelevantContentFilter
    if if_llm:
        content_filter = LLMContentFilter(
                llm_config = LLMConfig(provider=f"{provider}/{model_id}",api_token=api_token,base_url=base_url), #or use environment variable
                instruction="""
                Focus on extracting the core educational content.
                Include:
                - Key concepts and explanations
                - Important code examples
                - Essential technical details
                Exclude:
                - Navigation elements
                - Sidebars
                - Footer content
                Format the output as clean markdown with proper code blocks and headers.
                """,
                chunk_token_threshold=4096,  # Adjust based on your needs
                verbose=True # 生产时关掉
        )
    else:
        content_filter = PruningContentFilter(
                    threshold=0.4,
                    threshold_type="fixed"
                )
    md_generator = DefaultMarkdownGenerator(
        content_filter=content_filter,
        options={"ignore_links": True,"ignore_images": True}
    )

    browser_conf = BrowserConfig(
        browser_type="chromium",
        headless=True,
        text_mode=True
    )

    prefix_filter = URLPatternFilter(
    patterns=[f"{prefix}*"]
    )
    filter_chain = FilterChain([prefix_filter])

    # Basic configuration
    bfsstrategy = BFSDeepCrawlStrategy(
        max_depth=4,               # Crawl initial page + 2 levels deep
        include_external=False,    # Stay within the same domain
        max_pages=200,              # Maximum number of pages to crawl (optional)
        # filter_chain=filter_chain
    )

        # Basic configuration
    dfsstrategy = DFSDeepCrawlStrategy(
        max_depth=8,               # Crawl initial page + 2 levels deep
        include_external=False,    # Stay within the same domain
        max_pages=200,              # Maximum number of pages to crawl (optional)
        #score_threshold=0.5,       # Minimum score for URLs to be crawled (optional)
    )

    # Configure a 2-level deep crawl
    config = CrawlerRunConfig(
        deep_crawl_strategy=bfsstrategy,
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True, #上线时关闭
        stream=True,
        markdown_generator=md_generator,
    )

    async with AsyncWebCrawler(config=browser_conf) as crawler:
            async for result in await crawler.arun(site, config=config):
                print(f"URL: {result.url}")
                # print(result.markdown.fit_markdown) 
                # handle_md(result.markdown.fit_markdown, type="print", path=f"{result}.md")
    print("测试完成")


async def crawl_doc(site: str, prefix: str, if_llm: bool, model_id: str, provider: str, base_url: str, api_token: str, milvus_storage: MilvusStorage, lightrag_storage: LightRAGStorage, collection_id: str):
    # 检测URL是否是文档文件（PDF、DOCX等）
    url_lower = site.lower()
    is_document_file = any(url_lower.endswith(ext) for ext in ['.pdf', '.docx', '.doc', '.md', '.txt'])
    
    if is_document_file:
        # 处理文档文件：使用DocumentExtractor提取内容
        logger.info(f"检测到文档文件URL，使用DocumentExtractor处理: {site}")
        try:
            extractor = DocumentExtractor()
            
            # 判断文件类型
            file_ext = url_lower.split('.')[-1]
            
            if file_ext == 'pdf':
                # PDF使用mineru API（需要URL）
                logger.info("使用MinerU API提取PDF内容...")
                doc_content = extractor.read_document(site, pdf_extract_method="mineru")
            elif file_ext in ['doc', 'docx']:
                # DOCX需要先下载到本地
                logger.info("下载DOCX文件到本地...")
                response = requests.get(site, timeout=300)
                response.raise_for_status()
                
                # 创建临时文件
                with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_ext}') as tmp_file:
                    tmp_file.write(response.content)
                    tmp_path = tmp_file.name
                
                try:
                    doc_content = extractor.read_document(tmp_path)
                finally:
                    # 清理临时文件
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
            else:
                # 其他格式（md, txt）直接下载
                logger.info(f"下载{file_ext}文件...")
                response = requests.get(site, timeout=300)
                response.raise_for_status()
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_ext}', mode='w', encoding='utf-8') as tmp_file:
                    tmp_file.write(response.text)
                    tmp_path = tmp_file.name
                
                try:
                    doc_content = extractor.read_document(tmp_path)
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
            
            # 将提取的内容转换为markdown格式（或直接使用文本）
            md_content = doc_content.content
            
            if not md_content or not md_content.strip():
                raise Exception("文档内容提取为空")
            
            logger.info(f"成功提取文档内容，长度: {len(md_content)} 字符")
            
            # 使用handle_md处理提取的内容
            await handle_md(
                md_content=md_content,
                storage_type="light_and_milvus",
                param=[milvus_storage, lightrag_storage],
                collection_id=collection_id
            )
            
            logger.info(f"成功处理文档文件: {site}")
            return
            
        except Exception as e:
            error_msg = f"处理文档文件失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    # 如果不是文档文件，使用爬虫处理网页
    content_filter: RelevantContentFilter
    if if_llm:
        content_filter = LLMContentFilter(
                llm_config = LLMConfig(provider=f"{provider}/{model_id}",api_token=api_token,base_url=base_url), #or use environment variable
                instruction="""
                Focus on extracting the core educational content.
                Include:
                - Key concepts and explanations
                - Important code examples
                - Essential technical details
                Exclude:
                - Navigation elements
                - Sidebars
                - Footer content
                Format the output as clean markdown with proper code blocks and headers.
                """,
                chunk_token_threshold=4096,  # Adjust based on your needs
                verbose=True # 生产时关掉
        )
    else:
        content_filter = PruningContentFilter(
                    threshold=0.4,
                    threshold_type="fixed"
                )
    md_generator = DefaultMarkdownGenerator(
        content_filter=content_filter,
        options={"ignore_links": True,"ignore_images": True}
    )

    browser_conf = BrowserConfig(
        browser_type="chromium",
        headless=True,
        text_mode=True
    )

    prefix_filter = URLPatternFilter(
        patterns=[f"{prefix}*"]
    )
    filter_chain = FilterChain([prefix_filter])

    # Basic configuration
    bfsstrategy = BFSDeepCrawlStrategy(
        max_depth=4,               # Crawl initial page + 2 levels deep
        include_external=False,    # Stay within the same domain
        max_pages=200,              # Maximum number of pages to crawl (optional)
        filter_chain=filter_chain
    )

    # Configure a 2-level deep crawl
    config = CrawlerRunConfig(
        deep_crawl_strategy=bfsstrategy,
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True, #上线时关闭
        stream=True,
        markdown_generator=md_generator,
    )

    async with AsyncWebCrawler(config=browser_conf) as crawler:
            try:
                async for result in await crawler.arun(site, config=config):
                    try:
                        logger.info(f"URL: {result.url}")
                        
                        # 检查result.markdown是否存在且不为None
                        if result.markdown is None:
                            logger.warning(f"URL {result.url} 的markdown内容为空，跳过处理")
                            continue
                            
                        # 检查fit_markdown是否存在且不为空
                        if not hasattr(result.markdown, 'fit_markdown') or result.markdown.fit_markdown is None:
                            logger.warning(f"URL {result.url} 的fit_markdown内容为空，跳过处理")
                            continue
                            
                        # 检查内容是否为空字符串
                        if not result.markdown.fit_markdown.strip():
                            logger.warning(f"URL {result.url} 的内容为空，跳过处理")
                            continue
                            
                        await handle_md(md_content=result.markdown.fit_markdown, storage_type="light_and_milvus", param=[milvus_storage, lightrag_storage], collection_id=collection_id)
                        # await handle_md(md_content=result.markdown.fit_markdown, storage_type="milvus", param=[milvus_storage], collection_id=collection_id)
                        logger.info(f"成功处理: {result.url}")
                        
                    except Exception as e:
                        error_msg = f"处理URL {result.url} 时发生错误: {str(e)}"
                        logger.error(error_msg)
                        logger.info("跳过此URL，继续处理下一个...")
                        # 更新状态为错误
                        await update_crawl_status(collection_id, CRAWL_STATUS_ERROR, error_msg)
                        continue
                        
            except Exception as e:
                error_msg = f"爬虫运行时发生错误: {str(e)}"
                logger.error(error_msg)
                logger.info("爬虫任务中断，但程序继续运行...")
                # 更新状态为错误
                await update_crawl_status(collection_id, CRAWL_STATUS_ERROR, error_msg)
            logger.info("爬虫运行完成")


async def handle_md(md_content, storage_type="print", param=None, collection_id: str = None):
    try:
        if storage_type == "print":
            logger.info(md_content)
        elif storage_type == "stdio":
            with open(param, 'w') as f:
                f.write(md_content)
        elif storage_type == "milvus":
            if param is None:
                logger.error("Milvus存储参数为空")
                return
                
            chunker = TextChunker()
            md_config = ChunkConfig(
                strategy=ChunkStrategy.MARKDOWN_HEADER
            )
            document = DocumentContent(content=md_content, document_name="crawled_document")
            md_result = chunker.chunk_document(document, md_config)
            
            # 检查分块结果
            if md_result is None or not md_result.chunks:
                logger.warning("文档分块结果为空，跳过存储")
                return
                
            param[0].store_chunks_batch([md_result])
            logger.info(f"成功存储文档分块，共 {len(md_result.chunks)} 个分块")
            
            # 更新爬虫计数
            if collection_id:
                await increment_crawl_count(collection_id)
                
        elif storage_type == "light_and_milvus":
            if param is None:
                logger.error("Milvus存储参数为空")
                return
                
            chunker = TextChunker()
            md_config = ChunkConfig(
                strategy=ChunkStrategy.MARKDOWN_HEADER
            )
            document = DocumentContent(content=md_content, document_name="crawled_document")
            md_result = chunker.chunk_document(document, md_config)
            
            # 检查分块结果
            if md_result is None or not md_result.chunks:
                logger.warning("文档分块结果为空，跳过存储")
                return
            
            param[0].store_chunks_batch([md_result])
            logger.info(f"成功存储文档分块到Milvus，共 {len(md_result.chunks)} 个分块")
            # 将Document对象转换为字符串列表
            text_chunks = [chunk.page_content for chunk in md_result.chunks]
            try:
                logger.info(f"开始存储 {len(text_chunks)} 个文本块到LightRAG...")
                await param[1].insert_texts(text_chunks)
                logger.info("成功存储文档到LightRAG")
            except Exception as lightrag_error:
                # 捕获LightRAG存储错误，记录详细信息但不中断整个流程
                error_type = type(lightrag_error).__name__
                error_msg = str(lightrag_error)
                logger.error(f"LightRAG存储失败: {error_type}: {error_msg}")
                
                # 检查是否是连接错误
                is_connection_error = any(keyword in error_msg.lower() for keyword in [
                    'connection', '连接', '10054', 'reset', 'closed', 'timeout', '远程主机'
                ])
                
                # 检查是否是pgvector扩展缺失
                is_pgvector_error = any(keyword in error_msg.lower() for keyword in [
                    'type "vector" does not exist', 'extension "vector" is not available',
                    'pgvector', 'vector extension'
                ])
                
                if is_pgvector_error:
                    logger.error(
                        "检测到PostgreSQL pgvector扩展缺失！\n"
                        "LightRAG需要pgvector扩展来存储向量数据。\n"
                        "请按照以下步骤安装：\n"
                        "1. 下载pgvector扩展（如果使用Windows，需要编译或使用预编译版本）\n"
                        "2. 在PostgreSQL中执行：CREATE EXTENSION IF NOT EXISTS vector;\n"
                        "3. 或者使用Docker镜像：pgvector/pgvector:pg16（已包含扩展）\n"
                        "参考文档：https://github.com/pgvector/pgvector\n"
                        "注意: Milvus存储已成功，但LightRAG存储失败"
                    )
                elif is_connection_error:
                    logger.error(
                        "检测到数据库连接错误！可能的原因：\n"
                        "1. Neo4j服务未运行或连接被关闭\n"
                        "   - 检查Neo4j服务是否启动\n"
                        "   - 检查环境变量: NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD\n"
                        "2. PostgreSQL服务未运行或连接被关闭\n"
                        "   - 检查PostgreSQL服务是否启动\n"
                        "   - 检查环境变量: POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DATABASE等\n"
                        "3. 网络连接问题或防火墙阻止\n"
                        "注意: Milvus存储已成功，但LightRAG存储失败"
                    )
                
                # 重新抛出异常，让外层catch处理
                raise
            
            # 更新爬虫计数
            if collection_id:
                await increment_crawl_count(collection_id)
        
            
    except Exception as e:
        import traceback
        error_type = type(e).__name__
        error_msg = str(e)
        error_traceback = traceback.format_exc()
        
        logger.error(f"处理markdown内容时发生错误: {error_type}: {error_msg}")
        logger.debug(f"错误堆栈跟踪:\n{error_traceback}")
        logger.info("跳过此内容的处理...")
        
        # 更新状态为错误，包含更详细的信息
        detailed_error_msg = f"{error_type}: {error_msg}"
        if collection_id:
            await update_crawl_status(collection_id, CRAWL_STATUS_ERROR, detailed_error_msg)
