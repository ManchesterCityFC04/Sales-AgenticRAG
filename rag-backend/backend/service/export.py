#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对话导出服务层
提供对话历史的导出功能，支持多种格式
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.service.chat_history import get_chat_messages
from backend.service import conversation as conversation_service
from backend.config.log import get_logger

logger = get_logger(__name__)


def export_to_markdown(conversation_history: List[Dict[str, Any]], conversation_title: str = "对话记录") -> str:
    """
    导出对话历史为Markdown格式
    
    Args:
        conversation_history: 对话历史记录列表
        conversation_title: 对话标题
        
    Returns:
        str: Markdown格式的对话内容
    """
    try:
        md_content = f"# {conversation_title}\n\n"
        md_content += f"**导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md_content += f"**消息总数**: {len(conversation_history)}\n\n"
        md_content += "---\n\n"
        
        for msg in conversation_history:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            message_type = msg.get('type', 'messages')
            node_name = None
            
            # 提取节点名称（如果有）
            if msg.get('extra_data') and isinstance(msg.get('extra_data'), dict):
                node_name = msg.get('extra_data', {}).get('node_name')
            
            # 根据角色和类型格式化内容
            if role == 'user':
                md_content += f"## 👤 用户\n\n{content}\n\n"
            elif role == 'assistant':
                md_content += f"## 🤖 助手\n\n{content}\n\n"
            elif role == 'system' or message_type == 'updates':
                # 系统消息或节点更新
                if node_name:
                    md_content += f"## ⚙️ 系统 - {node_name}\n\n{content}\n\n"
                else:
                    md_content += f"## ⚙️ 系统\n\n{content}\n\n"
            else:
                md_content += f"## {role}\n\n{content}\n\n"
            
            md_content += "---\n\n"
        
        return md_content
        
    except Exception as e:
        logger.error(f"导出Markdown失败: {str(e)}")
        raise


def export_to_json(conversation_history: List[Dict[str, Any]], conversation_title: str = "对话记录") -> Dict[str, Any]:
    """
    导出对话历史为JSON格式
    
    Args:
        conversation_history: 对话历史记录列表
        conversation_title: 对话标题
        
    Returns:
        Dict[str, Any]: JSON格式的对话数据
    """
    try:
        return {
            "title": conversation_title,
            "export_time": datetime.now().isoformat(),
            "total_messages": len(conversation_history),
            "messages": conversation_history
        }
        
    except Exception as e:
        logger.error(f"导出JSON失败: {str(e)}")
        raise


def export_to_text(conversation_history: List[Dict[str, Any]], conversation_title: str = "对话记录") -> str:
    """
    导出对话历史为纯文本格式
    
    Args:
        conversation_history: 对话历史记录列表
        conversation_title: 对话标题
        
    Returns:
        str: 纯文本格式的对话内容
    """
    try:
        text_content = f"{conversation_title}\n"
        text_content += f"{'=' * len(conversation_title)}\n\n"
        text_content += f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        text_content += f"消息总数: {len(conversation_history)}\n\n"
        text_content += "-" * 50 + "\n\n"
        
        for msg in conversation_history:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            message_type = msg.get('type', 'messages')
            node_name = None
            
            # 提取节点名称（如果有）
            if msg.get('extra_data') and isinstance(msg.get('extra_data'), dict):
                node_name = msg.get('extra_data', {}).get('node_name')
            
            # 根据角色格式化
            if role == 'user':
                text_content += f"[用户]\n{content}\n\n"
            elif role == 'assistant':
                text_content += f"[助手]\n{content}\n\n"
            elif role == 'system' or message_type == 'updates':
                if node_name:
                    text_content += f"[系统 - {node_name}]\n{content}\n\n"
                else:
                    text_content += f"[系统]\n{content}\n\n"
            else:
                text_content += f"[{role}]\n{content}\n\n"
            
            text_content += "-" * 50 + "\n\n"
        
        return text_content
        
    except Exception as e:
        logger.error(f"导出文本失败: {str(e)}")
        raise


async def export_conversation(
    conversation_id: str,
    export_format: str = "markdown"
) -> Dict[str, Any]:
    """
    导出对话历史
    
    Args:
        conversation_id: 对话ID
        export_format: 导出格式 (markdown/json/text)
        
    Returns:
        Dict[str, Any]: 导出结果，包含格式化的内容和元数据
    """
    try:
        logger.info(f"开始导出对话: {conversation_id}, 格式: {export_format}")
        
        # 验证对话是否存在
        conv_result = await conversation_service.get_conversation_by_id(conversation_id)
        if not conv_result.get("success"):
            return {
                "success": False,
                "error": "对话不存在",
                "message": "指定的对话不存在"
            }
        
        conversation_data = conv_result.get("data", {})
        conversation_title = conversation_data.get("title", "对话记录")
        
        # 获取对话历史
        conversation_history = get_chat_messages(conversation_id)
        
        if not conversation_history:
            return {
                "success": False,
                "error": "对话历史为空",
                "message": "该对话没有历史记录"
            }
        
        # 根据格式导出
        if export_format.lower() == "markdown":
            content = export_to_markdown(conversation_history, conversation_title)
            content_type = "text/markdown"
            file_extension = "md"
        elif export_format.lower() == "json":
            content = export_to_json(conversation_history, conversation_title)
            content_type = "application/json"
            file_extension = "json"
        elif export_format.lower() == "text":
            content = export_to_text(conversation_history, conversation_title)
            content_type = "text/plain"
            file_extension = "txt"
        else:
            return {
                "success": False,
                "error": f"不支持的导出格式: {export_format}",
                "message": "支持的格式: markdown, json, text"
            }
        
        # 生成文件名
        safe_title = "".join(c for c in conversation_title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')[:50]  # 限制长度
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_title}_{timestamp}.{file_extension}"
        
        logger.info(f"成功导出对话: {conversation_id}, 格式: {export_format}, 消息数: {len(conversation_history)}")
        
        return {
            "success": True,
            "content": content,
            "filename": filename,
            "content_type": content_type,
            "format": export_format,
            "total_messages": len(conversation_history),
            "conversation_title": conversation_title,
            "export_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"导出对话失败: {str(e)}")
        logger.exception("详细错误信息:")
        return {
            "success": False,
            "error": str(e),
            "message": "导出对话失败"
        }

