from typing import Dict, Any
from dataclasses import dataclass, field


class RetrievalMode:
    """检索模式常量类

    使用字符串常量而不是枚举，避免LangGraph状态序列化问题
    """
    VECTOR_ONLY = "vector_only"
    GRAPH_ONLY = "graph_only"
    NO_RETRIEVAL = "no_retrieval"
    AUTO = "auto"


@dataclass
class RetrievedDocument:
    """检索到的文档"""
    page_content: str  # 文档内容
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据，包含document_name, chunk_index, chunk_size, pk等