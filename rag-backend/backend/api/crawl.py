from fastapi import APIRouter, HTTPException
from backend.param.common import Response
from backend.service.crawl import get_crawl_status, get_all_crawl_status
from backend.config.log import get_logger
from typing import Optional
from backend.param.crawl import CrawlRequest, UploadDocRequest
from backend.service.crawl import initialize_collection_and_store
from backend.config.oss import get_presigned_url_for_upload, get_presigned_url_for_download
import asyncio
import os


logger = get_logger(__name__)

router = APIRouter(
    prefix="/crawl",
    tags=["CRAWL"]
)

def run_task(request: CrawlRequest):
    asyncio.run(initialize_collection_and_store(request))

@router.post('/site')
async def crawl_site_and_store(request: CrawlRequest) -> Response:
    """
    触发指定URL的网站爬取并存储到数据库
    
    Args:
        request: 包含爬取参数的请求体
        
    Returns:
        Response: 包含操作结果的响应
    """
    try:
        logger.info(f"触发爬取任务: {request.url}")
        
        # 初始化集合并存储数据,走异步调用非等待，直接返回
        asyncio.create_task(initialize_collection_and_store(request))
        
        return Response.success_with_msg({
            "collection_id": request.collection_id,
        }, f"接收到爬取任务: {request.url}")
        
    except Exception as e:
        logger.error(f"触发爬取任务异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"触发爬取任务失败: {str(e)}")

@router.post('/load-document')
async def get_oss_doc_and_store(request: CrawlRequest) -> Response:
    """
    从OSS获取文档并存储到数据库
    
    Args:
        request: 包含文档URL和集合名称的请求体
        
    Returns:
        Response: 包含操作结果的响应
    """
    try:
        logger.info(f"触发从OSS获取文档任务: {request.url}")
        
        # 初始化集合并存储数据,走异步调用非等待，直接返回
        asyncio.create_task(initialize_collection_and_store(request))
        
        return Response.success_with_msg({
            "collection_id": request.collection_id,
        }, f"接收到从OSS获取文档任务: {request.url}")
        
    except Exception as e:
        logger.error(f"触发从OSS获取文档任务异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"触发从OSS获取文档任务失败: {str(e)}")


@router.post('/get-upload-url')
async def get_oss_upload_url(request: UploadDocRequest) -> Response:
    """
    获取OSS上传签名URL
    
    Args:
        document_name: 文档名称
        
    Returns:
        Response: 包含上传签名URL的响应
    """
    try:
        logger.info(f"获取OSS上传签名URL")
        
        # 使用环境变量中的bucket名称
        bucket_name = os.getenv("OSS_BUCKET_NAME", "ragagent-file")
        
        # 调用服务层获取上传签名URL
        upload_result = get_presigned_url_for_upload(bucket=bucket_name, key=request.document_name)
        
        if upload_result:
            logger.info(f"成功获取OSS上传签名URL, 使用的key: {upload_result.get('key', request.document_name)}")
            #logger.info(f"上传URL: {upload_result}")
            # 返回完整结果，包括URL和实际使用的key
            return Response.success({
                "url": upload_result["url"],
                "key": upload_result.get("key", request.document_name),
                "original_name": request.document_name
            })
        else:
            logger.warning(f"获取OSS上传签名URL失败")
            return Response.error("获取OSS上传签名URL失败")
            
    except Exception as e:
        logger.error(f"获取OSS上传签名URL异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取OSS上传签名URL失败: {str(e)}")

@router.get('/status/{collection_name}')
async def get_crawl_status_api(collection_name: str) -> Response:
    """
    获取指定集合的爬虫状态
    
    Args:
        collection_name: 集合名称
        
    Returns:
        Response: 包含爬虫状态信息的响应
    """
    try:
        logger.info(f"查询集合 {collection_name} 的爬虫状态")
        
        # 验证参数
        if not collection_name or not collection_name.strip():
            raise HTTPException(status_code=400, detail="集合名称不能为空")
        
        # 调用服务层获取状态
        status_data = await get_crawl_status(collection_name.strip())
        
        if status_data:
            logger.info(f"成功获取集合 {collection_name} 的爬虫状态")
            return Response.success({
                "collection_name": collection_name,
                "status": status_data
            })
        else:
            logger.warning(f"集合 {collection_name} 的爬虫状态不存在")
            return Response.success({
                "collection_name": collection_name,
                "status": {},
                "message": "该集合的爬虫状态不存在"
            })
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取爬虫状态接口异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


