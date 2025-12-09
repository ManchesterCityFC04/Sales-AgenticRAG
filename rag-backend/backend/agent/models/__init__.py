"""智能体模块 - 聊天模型和嵌入模型管理"""

# 从 chat_model 模块导出
from .chat_model import (
    load_chat_model,
    register_model_provider
)

# 从 embeddings 模块导出  
from .embeddings import (
    load_embeddings,
    register_embeddings_provider
)

__all__ = [
    # 聊天模型相关
    "load_chat_model",
    "register_model_provider",
    
    # 嵌入模型相关
    "load_embeddings", 
    "register_embeddings_provider"
]