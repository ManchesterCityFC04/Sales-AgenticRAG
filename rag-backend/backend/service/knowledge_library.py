#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库服务层
提供知识库相关的业务逻辑处理
"""
import uuid
import time
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from backend.model.knowledge_library import KnowledgeLibrary, KnowledgeDocument
from backend.param.knowledge_library import (
    CreateLibraryRequest, UpdateLibraryRequest, AddDocumentRequest, UpdateDocumentRequest
)
from backend.param.common import Response
from backend.config.log import get_logger
from backend.config.database import DatabaseFactory

logger = get_logger(__name__)


async def get_user_libraries(user_id: str) -> Response:
    """获取用户的知识库列表"""
    db = None
    try:
        logger.info(f"开始获取用户 {user_id} 的知识库列表")
        db = DatabaseFactory.create_session()
        
        libraries = db.query(KnowledgeLibrary).filter(
            KnowledgeLibrary.user_id == user_id,
            KnowledgeLibrary.is_active == True
        ).order_by(KnowledgeLibrary.updated_at.desc()).all()
        
        result = []
        for library in libraries:
            library_dict = library.to_dict()
            # 添加文档数量统计
            library_dict['document_count'] = len(library.documents) if library.documents else 0
            result.append(library_dict)
        
        logger.info(f"成功获取用户 {user_id} 的知识库列表，共 {len(result)} 个")
        return Response.success(result)
        
    except Exception as e:
        logger.error(f"获取用户知识库列表失败: {str(e)}")
        return Response.error(f"获取知识库列表失败: {str(e)}")
    finally:
        if db:
            db.close()


async def get_library_detail(library_id: int, user_id: str) -> Response:
    """获取知识库详情"""
    try:
        db_factory = DatabaseFactory()
        session = db_factory.create_session()
        
        try:
            library = session.query(KnowledgeLibrary).filter(
                KnowledgeLibrary.id == library_id,
                KnowledgeLibrary.user_id == user_id,
                KnowledgeLibrary.is_active == True
            ).first()
            
            if not library:
                return Response.error("知识库不存在或无权限访问")
            
            logger.info(f"成功获取知识库详情: {library.title}")
            return Response.success(library.to_dict())
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"获取知识库详情失败: {str(e)}")
        return Response.error(f"获取知识库详情失败: {str(e)}")


async def create_library(request: CreateLibraryRequest, user_id: str) -> Response:
    """创建知识库"""
    try:
        db_factory = DatabaseFactory()
        session = db_factory.create_session()
        
        try:
            # 检查同名知识库
            existing = session.query(KnowledgeLibrary).filter(
                KnowledgeLibrary.title == request.title,
                KnowledgeLibrary.user_id == user_id,
                KnowledgeLibrary.is_active == True
            ).first()
            
            if existing:
                return Response.error("已存在同名知识库")
            
            # 创建新知识库
            library = KnowledgeLibrary(
                title=request.title,
                description=request.description,
                user_id=user_id
            )
            
            session.add(library)
            session.commit()
            session.refresh(library)
            
            # 生成collection_id: kb + 知识库ID + 下划线 + 时间戳
            timestamp = str(int(time.time() * 1000))  # 毫秒级时间戳
            collection_id = f"kb{library.id}_{timestamp}"
            
            # 更新collection_id
            library.collection_id = collection_id
            session.commit()
            session.refresh(library)
            
            logger.info(f"成功创建知识库: {library.title}")
            return Response.success(library.to_dict())
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"创建知识库失败: {str(e)}")
        return Response.error(f"创建知识库失败: {str(e)}")


async def update_library(library_id: int, request: UpdateLibraryRequest, user_id: str) -> Response:
    """更新知识库"""
    try:
        db_factory = DatabaseFactory()
        session = db_factory.create_session()
        
        try:
            library = session.query(KnowledgeLibrary).filter(
                KnowledgeLibrary.id == library_id,
                KnowledgeLibrary.user_id == user_id,
                KnowledgeLibrary.is_active == True
            ).first()
            
            if not library:
                return Response.error("知识库不存在或无权限访问")
            
            # 更新字段
            if request.title is not None:
                # 检查同名知识库（排除当前库）
                existing = session.query(KnowledgeLibrary).filter(
                    KnowledgeLibrary.title == request.title,
                    KnowledgeLibrary.user_id == user_id,
                    KnowledgeLibrary.id != library_id,
                    KnowledgeLibrary.is_active == True
                ).first()
                
                if existing:
                    return Response.error("已存在同名知识库")
                
                library.title = request.title
            
            if request.description is not None:
                library.description = request.description
            
            session.commit()
            session.refresh(library)
            
            logger.info(f"成功更新知识库: {library.title}")
            return Response.success(library.to_dict())
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"更新知识库失败: {str(e)}")
        return Response.error(f"更新知识库失败: {str(e)}")


async def delete_library(library_id: int, user_id: str) -> Response:
    """删除知识库"""
    try:
        db_factory = DatabaseFactory()
        session = db_factory.create_session()
        
        try:
            library = session.query(KnowledgeLibrary).filter(
                KnowledgeLibrary.id == library_id,
                KnowledgeLibrary.user_id == user_id,
                KnowledgeLibrary.is_active == True
            ).first()
            
            if not library:
                return Response.error("知识库不存在或无权限访问")
            
            # 软删除
            library.is_active = False
            session.commit()
            
            logger.info(f"成功删除知识库: {library.title}")
            return Response.success({"message": "知识库删除成功"})
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"删除知识库失败: {str(e)}")
        return Response.error(f"删除知识库失败: {str(e)}")


async def add_document(request: AddDocumentRequest, user_id: str) -> Response:
    """添加文档到知识库"""
    try:
        db_factory = DatabaseFactory()
        session = db_factory.create_session()
        
        try:
            # 验证知识库权限
            library = session.query(KnowledgeLibrary).filter(
                KnowledgeLibrary.id == request.library_id,
                KnowledgeLibrary.user_id == user_id,
                KnowledgeLibrary.is_active == True
            ).first()
            
            if not library:
                return Response.error("知识库不存在或无权限访问")
            
            # 创建文档
            document = KnowledgeDocument(
                library_id=request.library_id,
                name=request.name,
                type=request.type,
                url=request.url,
                file_path=request.file_path,
                file_size=request.file_size
            )
            
            session.add(document)
            session.commit()
            session.refresh(document)
            
            logger.info(f"成功添加文档到知识库 {library.title}: {document.name}")
            return Response.success(document.to_dict())
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"添加文档失败: {str(e)}")
        return Response.error(f"添加文档失败: {str(e)}")


async def update_document(document_id: int, request: UpdateDocumentRequest, user_id: str) -> Response:
    """更新文档"""
    try:
        db_factory = DatabaseFactory()
        session = db_factory.create_session()
        
        try:
            # 查询文档并验证权限
            document = session.query(KnowledgeDocument).join(KnowledgeLibrary).filter(
                KnowledgeDocument.id == document_id,
                KnowledgeLibrary.user_id == user_id,
                KnowledgeLibrary.is_active == True
            ).first()
            
            if not document:
                return Response.error("文档不存在或无权限访问")
            
            # 更新字段
            if request.name is not None:
                document.name = request.name
            if request.type is not None:
                document.type = request.type
            if request.url is not None:
                document.url = request.url
            if request.file_path is not None:
                document.file_path = request.file_path
            if request.file_size is not None:
                document.file_size = request.file_size
            
            session.commit()
            session.refresh(document)
            
            logger.info(f"成功更新文档: {document.name}")
            return Response.success(document.to_dict())
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"更新文档失败: {str(e)}")
        return Response.error(f"更新文档失败: {str(e)}")


async def delete_document(document_id: int, user_id: str) -> Response:
    """删除文档"""
    try:
        db_factory = DatabaseFactory()
        session = db_factory.create_session()
        
        try:
            # 查询文档并验证权限
            document = session.query(KnowledgeDocument).join(KnowledgeLibrary).filter(
                KnowledgeDocument.id == document_id,
                KnowledgeLibrary.user_id == user_id,
                KnowledgeLibrary.is_active == True
            ).first()
            
            if not document:
                return Response.error("文档不存在或无权限访问")
            
            # 物理删除文档
            session.delete(document)
            session.commit()
            
            logger.info(f"成功删除文档: {document.name}")
            return Response.success({"message": "文档删除成功"})
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"删除文档失败: {str(e)}")
        return Response.error(f"删除文档失败: {str(e)}")