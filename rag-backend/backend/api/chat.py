from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from backend.param.chat import ChatRequest, CreateConversationRequest, UpdateConversationTitleRequest
from backend.param.common import Response
from backend.service import chat as chat_service
from backend.service import conversation as conversation_service
from backend.service import export as export_service
from backend.config.log import get_logger
from backend.config.dependencies import get_current_user
from backend.config.database import DatabaseFactory
from fastapi.responses import Response as FastAPIResponse
import json
from typing import Optional
from urllib.parse import quote

logger = get_logger(__name__)

router = APIRouter(
    prefix="/llm",
    tags=["CHAT"]
)

@router.post('/chat')
async def chat(
    chat_param: ChatRequest, 
    current_user: str = Depends(get_current_user)
):
    """
    聊天接口 - 非流式响应
    
    Args:
        chat_param: 聊天请求参数
        current_user: 当前用户邮箱
        
    Returns:
        聊天响应结果
    """
    try:
        logger.info(f"用户 {current_user} 发起聊天请求: {chat_param.content}")
        
        # 验证请求参数
        if not chat_param.content:
            raise HTTPException(status_code=400, detail="聊天内容不能为空")
        
        # 调用服务层处理聊天
        result = await chat_service.chat(chat_param)
        
        if result.get("success"):
            logger.info("聊天请求处理成功")
            return result
        else:
            logger.error(f"聊天请求处理失败: {result.get('error')}")
            raise HTTPException(status_code=500, detail=result.get("message", "聊天处理失败"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"聊天接口异常: {str(e)}")
        logger.exception("详细错误信息:")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.post('/chat/stream')
async def chat_stream(
    chat_param: ChatRequest,
    current_user: str = Depends(get_current_user)
):
    """
    聊天接口 - 流式响应
    
    Args:
        chat_param: 聊天请求参数
        current_user: 当前用户邮箱
        
    Returns:
        StreamingResponse: 流式聊天响应
    """
    try:
        logger.info(f"用户 {current_user} 发起流式聊天请求: {chat_param.content}")
        
        # 验证请求参数
        if not chat_param.content:
            raise HTTPException(status_code=400, detail="聊天内容不能为空")
        
        async def generate_response():
            """生成流式响应数据"""
            try:
                async for chunk in chat_service.chat_stream(chat_param):
                    # 将数据转换为 JSON 格式并添加换行符
                    yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
            except Exception as e:
                logger.error(f"流式响应生成失败: {str(e)}")
                error_chunk = {
                    "type": "error",
                    "error": str(e),
                    "message": "流式响应生成失败"
                }
                yield f"data: {json.dumps(error_chunk, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/plain; charset=utf-8"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"流式聊天接口异常: {str(e)}")
        logger.exception("详细错误信息:")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.get('/history/{user_id}')
async def get_chat_history(
    user_id: str,
    conversation_id: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """
    获取聊天历史
    
    Args:
        user_id: 用户ID
        conversation_id: 会话ID（可选）
        current_user: 当前用户邮箱
        
    Returns:
        聊天历史数据
    """
    try:
        logger.info(f"用户 {current_user} 获取用户 {user_id} 的聊天历史")
        
        result = await chat_service.get_chat_history_list(user_id, conversation_id)
        
        if result.get("success"):
            return Response.success(result)
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "获取聊天历史失败"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取聊天历史接口异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.get('/history/single/{conversation_id}')
async def get_single_conversation_history(
    conversation_id: str,
    current_user: str = Depends(get_current_user)
) -> Response:
    """
    查询一轮对话历史记录的接口
    
    Args:
        conversation_id: 会话ID
        current_user: 当前用户邮箱
        
    Returns:
        Response: 包含单轮对话历史记录的响应
    """
    try:
        logger.info(f"用户 {current_user} 查询会话 {conversation_id} 的历史记录")
        
        # 调用服务层获取单轮对话历史
        result = await chat_service.get_chat_history_list(current_user, conversation_id)
        
        if result.get("success"):
            return Response.success(result)
        else:
            return Response.error(result.get("message", "获取对话历史失败"))
            
    except Exception as e:
        logger.error(f"查询单轮对话历史接口异常: {str(e)}")
        return Response.error(f"服务器内部错误: {str(e)}")


@router.get('/history/titles/{user_id}')
async def get_chat_history_titles(
    user_id: str,
    current_user: str = Depends(get_current_user)
) -> Response:
    """
    查询所有历史记录标题列表的接口
    
    Args:
        user_id: 用户ID
        current_user: 当前用户邮箱
        
    Returns:
        Response: 包含所有历史记录标题列表的响应
    """
    try:
        logger.info(f"用户 {current_user} 查询用户 {user_id} 的所有历史记录标题")
        
        # 调用服务层获取用户的所有会话列表
        result = await chat_service.get_user_conversations(user_id)
        
        if result.get("success"):
            return Response.success(result.get("data"))
        else:
            return Response.error(result.get("message", "获取会话列表失败"))
        
    except Exception as e:
        logger.error(f"查询历史记录标题列表接口异常: {str(e)}")
        return Response.error(f"服务器内部错误: {str(e)}")


@router.post('/conversation')
async def create_conversation(
    request: CreateConversationRequest,
    current_user: str = Depends(get_current_user)
) -> Response:
    """
    创建新的会话
    
    Args:
        request: 创建会话请求体
        current_user: 当前用户邮箱
        
    Returns:
        Response: 包含新创建会话信息的响应
    """
    try:
        logger.info(f"用户 {current_user} 为用户 {request.user_id} 创建新会话")
        
        result = await chat_service.create_conversation(request.user_id, request.title)
        
        if result.get("success"):
            return Response.success(result.get("data"))
        else:
            return Response.error(result.get("message", "创建会话失败"))
            
    except Exception as e:
        logger.error(f"创建会话接口异常: {str(e)}")
        return Response.error(f"服务器内部错误: {str(e)}")


@router.put('/conversation/{conversation_id}/title')
async def update_conversation_title(
    conversation_id: str,
    request: UpdateConversationTitleRequest,
    current_user: str = Depends(get_current_user)
) -> Response:
    """
    更新会话标题
    
    Args:
        conversation_id: 会话ID
        request: 更新标题请求体
        current_user: 当前用户邮箱
        
    Returns:
        Response: 更新结果响应
    """
    try:
        logger.info(f"用户 {current_user} 更新会话 {conversation_id} 的标题为: {request.title}")
        
        result = await chat_service.update_conversation_title(conversation_id, request.title)
        
        if result.get("success"):
            return Response.success(result.get("data"))
        else:
            return Response.error(result.get("message", "更新会话标题失败"))
            
    except Exception as e:
        logger.error(f"更新会话标题接口异常: {str(e)}")
        return Response.error(f"服务器内部错误: {str(e)}")


@router.delete('/conversation/{conversation_id}')
async def delete_conversation(
    conversation_id: str,
    current_user: str = Depends(get_current_user)
) -> Response:
    """
    删除会话
    
    Args:
        conversation_id: 会话ID
        current_user: 当前用户邮箱
        
    Returns:
        Response: 删除结果响应
    """
    try:
        logger.info(f"用户 {current_user} 删除会话 {conversation_id}")
        
        result = await chat_service.delete_conversation(conversation_id)
        
        if result.get("success"):
            return Response.success(result.get("data"))
        else:
            return Response.error(result.get("message", "删除会话失败"))
            
    except Exception as e:
        logger.error(f"删除会话接口异常: {str(e)}")
        return Response.error(f"服务器内部错误: {str(e)}")


@router.delete('/conversations/{user_id}')
async def delete_user_conversations(
    user_id: str,
    current_user: str = Depends(get_current_user)
) -> Response:
    """
    删除用户的所有会话
    
    Args:
        user_id: 用户ID
        current_user: 当前用户邮箱
        
    Returns:
        Response: 删除结果响应
    """
    try:
        logger.info(f"用户 {current_user} 删除用户 {user_id} 的所有会话")
        
        result = await chat_service.delete_user_conversations(user_id)
        
        if result.get("success"):
            return Response.success(result.get("data"))
        else:
            return Response.error(result.get("message", "删除用户会话失败"))
            
    except Exception as e:
        logger.error(f"删除用户会话接口异常: {str(e)}")
        return Response.error(f"服务器内部错误: {str(e)}")


@router.post('/get-url')
async def get_signature():
    """
    获取签名URL（原有接口保留）
    
    Returns:
        签名URL信息
    """
    try:
        # TODO: 实现实际的签名URL生成逻辑
        return {
            "success": True,
            "message": "签名URL获取成功",
            "url": "https://example.com/upload"
        }
    except Exception as e:
        logger.error(f"获取签名URL失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取签名URL失败: {str(e)}")


@router.get('/conversation/{conversation_id}/export')
async def export_conversation(
    conversation_id: str,
    format: str = "markdown",
    current_user: str = Depends(get_current_user)
) -> FastAPIResponse:
    """
    导出对话历史
    
    Args:
        conversation_id: 对话ID
        format: 导出格式 (markdown/json/text)，默认为markdown
        current_user: 当前用户邮箱
        
    Returns:
        FastAPIResponse: 文件下载响应
    """
    try:
        logger.info(f"用户 {current_user} 请求导出对话 {conversation_id}，格式: {format}")
        
        # 验证格式
        if format.lower() not in ["markdown", "json", "text"]:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的导出格式: {format}，支持的格式: markdown, json, text"
            )
        
        # 调用导出服务
        export_result = await export_service.export_conversation(
            conversation_id=conversation_id,
            export_format=format.lower()
        )
        
        if not export_result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=export_result.get("message", "导出失败")
            )
        
        # 准备响应内容
        content = export_result.get("content")
        filename = export_result.get("filename")
        content_type = export_result.get("content_type")
        
        # 如果是JSON格式，需要序列化
        if format.lower() == "json":
            content = json.dumps(content, ensure_ascii=False, indent=2)
        
        # 对文件名进行编码，支持中文文件名
        # 只使用 RFC 5987 格式，避免 latin-1 编码错误
        encoded_filename = quote(filename, safe='')
        # 只使用 filename*=UTF-8'' 格式，不包含 filename="..." 以避免 latin-1 编码问题
        content_disposition = f"attachment; filename*=UTF-8''{encoded_filename}"
        
        # 返回文件下载响应
        return FastAPIResponse(
            content=content.encode('utf-8'),
            media_type=content_type,
            headers={
                "Content-Disposition": content_disposition,
                "Content-Type": f"{content_type}; charset=utf-8"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出对话接口异常: {str(e)}")
        logger.exception("详细错误信息:")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")
