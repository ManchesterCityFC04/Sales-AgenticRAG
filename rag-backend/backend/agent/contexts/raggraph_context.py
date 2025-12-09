from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from ..models.raggraph_models import RetrievalMode


@dataclass
class RAGContext:
    """RAG图计算的运行时上下文配置
    
    该类定义了RAG系统运行时需要的所有配置参数，
    符合LangGraph的context模式规范。
    """
    
    # 用户相关配置
    user_id: str = field(
        default="default_user",
        metadata={
            "description": "用户唯一标识符。"
            "用于区分不同用户的会话和配置。",
        },
    )
    session_id: Optional[str] = field(
        default=None,
        metadata={
            "description": "会话唯一标识符。"
            "用于跟踪用户的对话会话。",
        },
    )

    # 检索配置
    retrieval_mode: str = field(
        default=RetrievalMode.AUTO,
        metadata={
            "description": "检索模式配置。"
            "决定使用向量检索、图检索还是自动选择。",
        },
    )
    max_retrieval_docs: int = field(
        default=3,
        metadata={
            "description": "最大检索文档数量。"
            "限制每次检索返回的文档数量。",
        },
    )

    # 系统配置
    system_prompt: str = field(
        default="你是一个专业的RAG助手，能够基于检索到的信息提供准确的回答。",
        metadata={
            "description": "系统提示词配置。"
            "定义AI助手的角色和行为准则。",
        },
    )
    
    def get_retrieval_config(self) -> Dict[str, Any]:
        """获取检索配置字典
        
        Returns:
            检索配置参数
        """
        return {
            "mode": self.retrieval_mode,
            "max_docs": self.max_retrieval_docs
        }
    
    def get_system_prompt(self) -> str:
        """获取系统提示词
        
        Returns:`
            完整的系统提示词
        """
        return self.system_prompt
    
    def get_langgraph_config(self) -> Dict[str, Any]:
        """获取LangGraph配置字典

        Returns:
            LangGraph配置参数，包含thread_id和user_id等checkpoint相关配置
        """
        config = {}

        # 配置用户和会话信息
        configurable = {}

        # 添加用户ID
        configurable["user_id"] = self.user_id

        # 如果有session_id，使用它作为thread_id
        if self.session_id:
            configurable["thread_id"] = self.session_id

        config["configurable"] = configurable

        return config
    

