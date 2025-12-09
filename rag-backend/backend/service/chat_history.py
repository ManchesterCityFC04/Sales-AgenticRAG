#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天历史存储服务层
提供聊天消息的数据库存储功能
"""
from typing import Dict, Any, Optional
from backend.config.database import DatabaseFactory
from backend.model.chat_history import ChatHistory
from backend.config.log import get_logger

logger = get_logger(__name__)


def save_chat_message(
    conversation_id: str,
    role: str,
    message_type: str,
    content: str,
    extra_data: Optional[Dict[str, Any]] = None
) -> bool:
    """
    保存聊天消息到数据库
    
    Args:
        conversation_id: 对话ID
        role: 角色 (user/assistant/system)
        message_type: 消息类型 (updates/messages)
        content: 消息内容
        extra_data: 额外数据，用于存储node_name等信息
        
    Returns:
        bool: 保存是否成功
    """
    db = None
    try:
        db = DatabaseFactory.create_session()
        
        # 创建ChatHistory对象
        chat_message = ChatHistory(
            conversation_id=conversation_id,
            role=role,
            type=message_type,
            content=content,
            extra_data=extra_data
        )
        
        # 保存到数据库
        db.add(chat_message)
        db.commit()
        
        logger.info(f"成功保存聊天消息: conversation_id={conversation_id}, type={message_type}, role={role}")
        return True
        
    except Exception as e:
        logger.error(f"保存聊天消息失败: {str(e)}")
        if db:
            db.rollback()
        return False
        
    finally:
        if db:
            db.close()


def get_chat_messages(
    conversation_id: str,
    limit: Optional[int] = None,
    offset: Optional[int] = None
) -> list:
    """
    获取对话的聊天消息
    
    Args:
        conversation_id: 对话ID
        limit: 限制返回数量
        offset: 偏移量
        
    Returns:
        list: 聊天消息列表
    """
    db = None
    try:
        db = DatabaseFactory.create_session()
        
        query = db.query(ChatHistory).filter(
            ChatHistory.conversation_id == conversation_id
        ).order_by(ChatHistory.id.asc())
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
            
        messages = query.all()
        
        # 转换为字典格式
        result = [message.to_dict() for message in messages]
        
        logger.info(f"获取聊天消息成功: conversation_id={conversation_id}, count={len(result)}")
        return result
        
    except Exception as e:
        logger.error(f"获取聊天消息失败: {str(e)}")
        return []
        
    finally:
        if db:
            db.close()


def get_message_count(conversation_id: str) -> int:
    """
    获取对话的消息数量
    
    Args:
        conversation_id: 对话ID
        
    Returns:
        int: 消息数量
    """
    db = None
    try:
        db = DatabaseFactory.create_session()
        
        count = db.query(ChatHistory).filter(
            ChatHistory.conversation_id == conversation_id
        ).count()
        
        return count
        
    except Exception as e:
        logger.error(f"获取消息数量失败: {str(e)}")
        return 0
        
    finally:
        if db:
            db.close()


def delete_conversation_messages(conversation_id: str) -> bool:
    """
    删除对话的所有消息
    
    Args:
        conversation_id: 对话ID
        
    Returns:
        bool: 删除是否成功
    """
    db = None
    try:
        db = DatabaseFactory.create_session()
        
        # 删除该对话的所有消息
        deleted_count = db.query(ChatHistory).filter(
            ChatHistory.conversation_id == conversation_id
        ).delete()
        
        db.commit()
        
        logger.info(f"成功删除对话消息: conversation_id={conversation_id}, count={deleted_count}")
        return True
        
    except Exception as e:
        logger.error(f"删除对话消息失败: {str(e)}")
        if db:
            db.rollback()
        return False
        
    finally:
        if db:
            db.close()