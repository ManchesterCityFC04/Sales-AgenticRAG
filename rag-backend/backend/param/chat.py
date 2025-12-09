from pydantic import BaseModel
from typing import Optional
from backend.agent.models.raggraph_models import RetrievalMode

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    content: Optional[str] = None
    img_url: Optional[str] = None
    user_id: Optional[str] = None
    collection_id: Optional[str] = None  # 添加知识库集合ID
    retrieval_mode: Optional[str] = RetrievalMode.AUTO  # 添加检索模式配置
    max_retrieval_docs: Optional[int] = 3
    # 系统配置
    system_prompt: Optional[str] = "你是一个专业的RAG助手，能够基于检索到的信息提供准确的回答。"
    # 销售模式配置
    sales_mode: Optional[bool] = False  # 是否启用销售模式
    sales_scenario: Optional[str] = "automotive"  # 销售场景（automotive/real_estate/finance等）

class RetrieverRequest(BaseModel):
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    query: Optional[str] = None

class OssRequest(BaseModel):
    bucket_name: Optional[str] = None
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    file_url: Optional[str] = None

# Conversation相关的请求参数
class CreateConversationRequest(BaseModel):
    user_id: str
    title: Optional[str] = None

class UpdateConversationTitleRequest(BaseModel):
    title: str

class GetConversationsRequest(BaseModel):
    user_id: str
    limit: Optional[int] = 50
    offset: Optional[int] = 0