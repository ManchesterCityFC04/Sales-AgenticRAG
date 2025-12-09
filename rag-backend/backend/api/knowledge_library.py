from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.param.knowledge_library import (
    CreateLibraryRequest, UpdateLibraryRequest, AddDocumentRequest, UpdateDocumentRequest
)
from backend.param.common import Response
from backend.service import knowledge_library as library_service
from backend.config.log import get_logger
from backend.config.dependencies import get_current_user
from backend.param.crawl import UploadDocRequest
from backend.config.oss import get_presigned_url_for_upload
import os

logger = get_logger(__name__)

router = APIRouter(
    prefix="/knowledge",
    tags=["KNOWLEDGE_LIBRARY"]
)


@router.get("/libraries")
async def get_libraries(current_user: int = Depends(get_current_user)):
    """获取用户的知识库列表"""
    logger.info(f"用户 {current_user} 请求获取知识库列表")
    return await library_service.get_user_libraries(current_user)


@router.get("/libraries/{library_id}")
async def get_library(library_id: int, current_user: int = Depends(get_current_user)):
    """获取知识库详情"""
    logger.info(f"用户 {current_user} 请求获取知识库详情: {library_id}")
    return await library_service.get_library_detail(library_id, current_user)


@router.post("/libraries")
async def create_library(request: CreateLibraryRequest, current_user: int = Depends(get_current_user)):
    """创建知识库"""
    logger.info(f"用户 {current_user} 请求创建知识库: {request.title}")
    return await library_service.create_library(request, current_user)


@router.put("/libraries/{library_id}")
async def update_library(
    library_id: int,
    request: UpdateLibraryRequest,
    current_user: int = Depends(get_current_user)
):
    """更新知识库"""
    logger.info(f"用户 {current_user} 请求更新知识库: {library_id}")
    return await library_service.update_library(library_id, request, current_user)


@router.delete("/libraries/{library_id}")
async def delete_library(library_id: int, current_user: int = Depends(get_current_user)):
    """删除知识库"""
    logger.info(f"用户 {current_user} 请求删除知识库: {library_id}")
    return await library_service.delete_library(library_id, current_user)


@router.post("/documents")
async def add_document(
    request: AddDocumentRequest,
    current_user: int = Depends(get_current_user)
):
    """添加文档到知识库"""
    logger.info(f"用户 {current_user} 请求添加文档到知识库: {request.library_id}")
    return await library_service.add_document(request, current_user)


@router.put("/documents/{document_id}")
async def update_document(
    document_id: int,
    request: UpdateDocumentRequest,
    current_user: int = Depends(get_current_user)
):
    """更新文档"""
    logger.info(f"用户 {current_user} 请求更新文档: {document_id}")
    return await library_service.update_document(document_id, request, current_user)


@router.delete("/documents/{document_id}")
async def delete_document(document_id: int, current_user: int = Depends(get_current_user)):
    """删除文档"""
    logger.info(f"用户 {current_user} 请求删除文档: {document_id}")
    return await library_service.delete_document(document_id, current_user)


@router.post("/upload-url")
async def get_upload_url(request: dict, current_user: int = Depends(get_current_user)):
    """获取文件上传URL"""
    logger.info(f"用户 {current_user} 请求获取上传URL")
    
    # 从请求中获取文档名称
    document_name = request.get("document_name")
    if not document_name:
        return Response.error("文档名称不能为空")
    
    try:
        # 使用环境变量中的bucket名称
        bucket_name = os.getenv("OSS_BUCKET_NAME", "ragagent-file")
        
        # 调用服务层获取上传签名URL
        upload_result = get_presigned_url_for_upload(
            bucket=bucket_name, 
            key=document_name
        )
        
        if upload_result:
            logger.info(f"成功获取OSS上传签名URL, 使用的key: {upload_result.get('key', document_name)}")
            # 返回完整的结果，包括URL和实际使用的key
            return Response.success({
                "url": upload_result["url"],
                "key": upload_result.get("key", document_name),
                "original_name": document_name
            })
        else:
            logger.warning(f"获取OSS上传签名URL失败")
            return Response.error("获取OSS上传签名URL失败")
            
    except Exception as e:
        logger.error(f"获取OSS上传签名URL异常: {str(e)}")
        return Response.error(f"获取OSS上传签名URL失败: {str(e)}")
