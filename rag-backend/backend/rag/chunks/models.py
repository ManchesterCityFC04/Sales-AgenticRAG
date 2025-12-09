"""RAG系统数据模型定义"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
from langchain_core.documents import Document


class ChunkStrategy(Enum):
    """分块策略枚举"""
    CHARACTER = "character"          # 字符级分块
    SEMANTIC = "semantic"           # 语义分块
    RECURSIVE = "recursive"         # 递归分块
    MARKDOWN_HEADER = "markdown_header"  # Markdown标题分块


@dataclass
class DocumentContent:
    """文档内容数据类型"""
    content: str        # 文档文本内容
    document_name: str  # 文档名称


@dataclass
class ChunkConfig:
    """分块配置"""
    strategy: ChunkStrategy
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # 字符分块专用参数
    separator: str = ""
    is_separator_regex: bool = False
    
    # 语义分块专用参数
    breakpoint_threshold_type: str = "percentile"
    breakpoint_threshold_amount: float = 95
    min_chunk_size: Optional[int] = None
    sentence_split_regex: str = r'[。！？.\n]'
    
    # 递归分块专用参数
    separators: List[str] = None
    
    # Markdown分块专用参数
    headers_to_split_on: List[tuple] = None

    def __post_init__(self):
        """初始化默认值"""
        if self.separators is None and self.strategy == ChunkStrategy.RECURSIVE:
            self.separators = ["\n\n", "。", "，", " ", ""]
            
        if self.headers_to_split_on is None and self.strategy == ChunkStrategy.MARKDOWN_HEADER:
            self.headers_to_split_on = [
                ("#", "Header_1"),
                ("##", "Header_2"), 
                ("###", "Header_3"),
                ("####", "Header_4"),
                ("#####", "Header_5"),
                ("######", "Header_6")
            ]


@dataclass
class ChunkResult:
    """分块结果"""
    chunks: List[Document]           # 分块后的文档列表
    strategy: ChunkStrategy          # 使用的分块策略
    total_chunks: int               # 总块数
    document_name: str              # 原文档名称