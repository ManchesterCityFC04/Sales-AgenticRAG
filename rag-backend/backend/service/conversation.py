#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对话服务层
提供对话相关的业务逻辑处理
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from backend.model.conversation import Conversation
from backend.config.log import get_logger
from backend.config.database import DatabaseFactory
from backend.param.common import Response

logger = get_logger(__name__)


async def create_conversation(user_id: str, title: str = None) -> Dict[str, Any]:
    """
    创建新对话
    
    Args:
        user_id: 用户ID
        title: 对话标题（可选）
        
    Returns:
        Dict[str, Any]: 创建结果
    """
    db = None
    try:
        logger.info(f"为用户 {user_id} 创建新对话")
        
        # 验证用户ID
        if not user_id or not str(user_id).strip():
            return {
                "success": False,
                "error": "用户ID不能为空",
                "message": "创建对话失败"
            }
        
        # 转换用户ID为整数
        try:
            user_id_int = int(user_id) if str(user_id).isdigit() else None
            if user_id_int is None or user_id_int <= 0:
                return {
                    "success": False,
                    "error": "无效的用户ID",
                    "message": "创建对话失败"
                }
        except ValueError:
            return {
                "success": False,
                "error": "用户ID格式错误",
                "message": "创建对话失败"
            }
        
        db = DatabaseFactory.create_session()
        
        conversation = Conversation(
            user_id=user_id_int,
            title=title or "新对话"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        logger.info(f"成功创建对话: {conversation.conversation_id}")
        
        return {
            "success": True,
            "data": conversation.to_dict(),
            "message": "对话创建成功"
        }
            
    except Exception as e:
        if db:
            db.rollback()
        logger.error(f"创建对话失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "创建对话失败"
        }
    finally:
        if db:
            db.close()


async def get_conversation_by_id(conversation_id: str) -> Dict[str, Any]:
    """
    根据conversation_id获取对话
    
    Args:
        conversation_id: 对话ID
        
    Returns:
        Dict[str, Any]: 查询结果
    """
    db = None
    try:
        logger.info(f"获取对话: {conversation_id}")
        
        # 验证对话ID
        if not conversation_id or not str(conversation_id).strip():
            return {
                "success": False,
                "error": "对话ID不能为空",
                "message": "获取对话失败"
            }
        
        db = DatabaseFactory.create_session()
        
        conversation = db.query(Conversation).filter(
            Conversation.conversation_id == conversation_id
        ).first()
        
        if conversation:
            return {
                "success": True,
                "data": conversation.to_dict(),
                "message": "获取对话成功"
            }
        else:
            return {
                "success": False,
                "error": "对话不存在",
                "message": "对话不存在"
            }
            
    except Exception as e:
        logger.error(f"获取对话失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "获取对话失败"
        }
    finally:
        if db:
            db.close()


async def get_conversations_by_user(user_id: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """
    获取用户的所有对话列表
    
    Args:
        user_id: 用户ID
        limit: 限制数量
        offset: 偏移量
        
    Returns:
        Dict[str, Any]: 查询结果
    """
    db = None
    try:
        logger.info(f"获取用户 {user_id} 的对话列表")
        
        # 验证用户ID
        if not user_id or not str(user_id).strip():
            return {
                "success": False,
                "error": "用户ID不能为空",
                "message": "获取用户对话列表失败"
            }
        
        # 转换用户ID为整数
        try:
            user_id_int = int(user_id) if str(user_id).isdigit() else None
            if user_id_int is None or user_id_int <= 0:
                return {
                    "success": False,
                    "error": "无效的用户ID",
                    "message": "获取用户对话列表失败"
                }
        except ValueError:
            return {
                "success": False,
                "error": "用户ID格式错误",
                "message": "获取用户对话列表失败"
            }
        
        # 验证分页参数
        if limit <= 0 or limit > 100:
            limit = 50
        if offset < 0:
            offset = 0
        
        db = DatabaseFactory.create_session()
        
        # 获取总数
        total_count = db.query(Conversation).filter(
            Conversation.user_id == user_id_int
        ).count()
        
        # 获取对话列表
        conversations = db.query(Conversation).filter(
            Conversation.user_id == user_id_int
        ).order_by(Conversation.updated_at.desc()).offset(offset).limit(limit).all()
        
        conversation_list = []
        for conv in conversations:
            conversation_list.append(conv.to_dict())
        
        logger.info(f"成功获取用户 {user_id} 的 {len(conversation_list)} 个对话")
        
        return {
            "success": True,
            "data": {
                "conversations": conversation_list,
                "total_count": total_count,
                "current_count": len(conversation_list),
                "limit": limit,
                "offset": offset
            },
            "message": f"成功获取 {len(conversation_list)} 个对话"
        }
            
    except Exception as e:
        logger.error(f"获取用户对话列表失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "获取用户对话列表失败"
        }
    finally:
        if db:
            db.close()


async def update_conversation_title(conversation_id: str, title: str) -> Dict[str, Any]:
    """
    更新对话标题
    
    Args:
        conversation_id: 对话ID
        title: 新标题
        
    Returns:
        Dict[str, Any]: 更新结果
    """
    db = None
    try:
        logger.info(f"更新对话 {conversation_id} 的标题")
        
        # 验证参数
        if not conversation_id or not str(conversation_id).strip():
            return {
                "success": False,
                "error": "对话ID不能为空",
                "message": "更新对话标题失败"
            }
        
        if not title or not str(title).strip():
            return {
                "success": False,
                "error": "标题不能为空",
                "message": "更新对话标题失败"
            }
        
        # 限制标题长度
        title = str(title).strip()
        if len(title) > 100:
            title = title[:100]
        
        db = DatabaseFactory.create_session()
        
        conversation = db.query(Conversation).filter(
            Conversation.conversation_id == conversation_id
        ).first()
        
        if conversation:
            conversation.title = title
            conversation.updated_at = func.now()
            db.commit()
            db.refresh(conversation)
            
            return {
                "success": True,
                "data": conversation.to_dict(),
                "message": "对话标题更新成功"
            }
        else:
            return {
                "success": False,
                "error": "对话不存在",
                "message": "对话不存在"
            }
            
    except Exception as e:
        if db:
            db.rollback()
        logger.error(f"更新对话标题失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "更新对话标题失败"
        }
    finally:
        if db:
            db.close()


async def delete_conversation(conversation_id: str) -> Dict[str, Any]:
    """
    删除对话
    
    Args:
        conversation_id: 对话ID
        
    Returns:
        Dict[str, Any]: 删除结果
    """
    db = None
    try:
        logger.info(f"删除对话: {conversation_id}")
        
        # 验证对话ID
        if not conversation_id or not str(conversation_id).strip():
            return {
                "success": False,
                "error": "对话ID不能为空",
                "message": "删除对话失败"
            }
        
        db = DatabaseFactory.create_session()
        
        conversation = db.query(Conversation).filter(
            Conversation.conversation_id == conversation_id
        ).first()
        
        if conversation:
            db.delete(conversation)
            db.commit()
            
            return {
                "success": True,
                "data": {"conversation_id": conversation_id},
                "message": "对话删除成功"
            }
        else:
            return {
                "success": False,
                "error": "对话不存在",
                "message": "对话不存在"
            }
            
    except Exception as e:
        if db:
            db.rollback()
        logger.error(f"删除对话失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "删除对话失败"
        }
    finally:
        if db:
            db.close()


async def delete_user_conversations(user_id: str) -> Dict[str, Any]:
    """
    删除用户的所有对话
    
    Args:
        user_id: 用户ID
        
    Returns:
        Dict[str, Any]: 删除结果
    """
    try:
        logger.info(f"删除用户 {user_id} 的所有对话")
        
        db = DatabaseFactory.create_session()
        try:
            count = db.query(Conversation).filter(
                Conversation.user_id == int(user_id) if user_id.isdigit() else 1
            ).count()
            
            db.query(Conversation).filter(
                Conversation.user_id == int(user_id) if user_id.isdigit() else 1
            ).delete()
            db.commit()
            
            return {
                "success": True,
                "data": {"deleted_count": count},
                "message": f"成功删除 {count} 个对话"
            }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"删除用户对话失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "删除用户对话失败"
        }


async def get_conversation_count_by_user(user_id: str) -> Dict[str, Any]:
    """
    获取用户的对话总数
    
    Args:
        user_id: 用户ID
        
    Returns:
        Dict[str, Any]: 统计结果
    """
    try:
        logger.info(f"获取用户 {user_id} 的对话总数")
        
        db = DatabaseFactory.create_session()
        try:
            count = db.query(Conversation).filter(
                Conversation.user_id == int(user_id) if user_id.isdigit() else 1
            ).count()
            
            return {
                "success": True,
                "data": {"count": count},
                "message": f"用户共有 {count} 个对话"
            }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"获取用户对话总数失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "获取用户对话总数失败"
        }


async def update_conversation_timestamp(conversation_id: str) -> Dict[str, Any]:
    """
    更新对话的最后更新时间
    
    Args:
        conversation_id: 对话ID
        
    Returns:
        Dict[str, Any]: 更新结果
    """
    try:
        logger.info(f"更新对话 {conversation_id} 的时间戳")
        
        db = DatabaseFactory.create_session()
        try:
            conversation = db.query(Conversation).filter(
                Conversation.conversation_id == conversation_id
            ).first()
            
            if conversation:
                from sqlalchemy.sql import func
                conversation.updated_at = func.now()
                db.commit()
                db.refresh(conversation)
                
                return {
                    "success": True,
                    "data": conversation.to_dict(),
                    "message": "对话时间戳更新成功"
                }
            else:
                return {
                    "success": False,
                    "message": "对话不存在"
                }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"更新对话时间戳失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "更新对话时间戳失败"
        }