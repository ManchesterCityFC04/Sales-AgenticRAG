from typing import Dict, Any, List, TypedDict, Annotated, Optional
from enum import Enum
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from ..contexts.raggraph_context import RAGContext
from ..models.raggraph_models import RetrievalMode, RetrievedDocument


class RAGGraphState(TypedDict, total=False):
    """RAG图状态管理
    
    使用TypedDict定义状态结构，确保与LangGraph兼容
    total=False表示所有字段都是可选的
    """
    # ==================== 核心字段 ====================
    messages: Annotated[List[BaseMessage], add_messages]  # 消息历史（LangGraph核心字段）
    
    # ==================== 基础信息 ====================
    session_id: str                    # 会话ID
    user_id: str                       # 用户ID（从context获取）
    original_question: str             # 原始问题
    
    # ==================== Context相关 ====================
    retrieval_config: Dict[str, Any]   # 检索配置（从context获取）
    system_prompt: str                 # 系统提示（从context获取）
    
    # ==================== 流程控制 ====================
    retrieval_mode: str                # 检索模式（vector_only/graph_only/no_retrieval/auto）
    need_retrieval: bool               # 是否需要检索
    need_retrieval_reason: Optional[str] = ""    # 需要检索的理由
    retrieval_mode_reason: Optional[str] = ""    # 检索模式的理由
    # ==================== 问题处理 ====================
    original_question: str             # 原始问题
    subquestions: List[str]            # 扩展的子问题列表
    processed_questions: List[str]     # 已处理的问题列表
    
    # ==================== 检索结果 ====================
    retrieved_docs: List[RetrievedDocument]  # 检索到的文档列表
    vector_db_results: List[RetrievedDocument]  # 向量数据库检索结果
    graph_db_results: List[RetrievedDocument]   # 图数据库检索结果
    
    # ==================== 答案生成 ====================
    final_answer: str                  # 最终答案
    answer_sources: List[str]          # 答案来源列表
    
    # ==================== 销售场景专用字段 ====================
    sales_mode: bool                   # 是否启用销售模式
    sales_intent: str                  # 销售意图（product_inquiry/price_negotiation/competitor_comparison等）
    customer_needs: Dict[str, Any]     # 客户需求画像
    product_recommendation: Dict[str, Any]  # 产品推荐结果
    competitor_analysis: Optional[Dict[str, Any]]  # 竞品对比分析
    sales_script: str                  # 生成的销售话术
    web_crawl_results: List[Dict[str, Any]]  # 网页爬取结果（竞品信息等）


def create_initial_rag_state(
    context: RAGContext,
    input_data: Dict[str, Any],
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    sales_mode: bool = False
) -> RAGGraphState:
    """创建初始化的RAGGraphState
    
    Args:
        context: RAG上下文配置
        input_data: 输入数据，包含messages等字段
        session_id: 会话ID，如果为None则使用context中的session_id
        user_id: 用户ID，如果为None则使用context中的user_id
        sales_mode: 是否启用销售模式
        
    Returns:
        初始化的RAGGraphState实例
    """
    return RAGGraphState(
        # ==================== 核心字段 ====================
        messages=input_data.get("messages", []),
        
        # ==================== 基础信息 ====================
        session_id=session_id or context.session_id or "default",
        user_id=user_id or context.user_id or "anonymous",
        
        
        # ==================== Context相关 ====================
        retrieval_config=context.get_retrieval_config(),
        system_prompt=context.get_system_prompt(),
        
        # ==================== 流程控制 ====================
        retrieval_mode=context.retrieval_mode,
        
        # ==================== 问题处理 ====================
        original_question="",
        subquestions=[],
        processed_questions=[],
        
        # ==================== 检索结果 ====================
        retrieved_docs=[],
        vector_db_results=[],
        graph_db_results=[],
        
        # ==================== 答案生成 ====================
        final_answer="",
        answer_sources=[],
        
        # ==================== 销售场景专用字段 ====================
        sales_mode=sales_mode,
        sales_intent="unknown",
        customer_needs={},
        product_recommendation={},
        competitor_analysis=None,
        sales_script="",
        web_crawl_results=[]
    )
    

