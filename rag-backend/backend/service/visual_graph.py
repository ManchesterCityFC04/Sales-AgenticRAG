from typing import Optional
import logging
from backend.param.visual_graph import KnowledgeGraph
from backend.rag.storage.lightrag_storage import LightRAGStorage

logger = logging.getLogger(__name__)


class VisualGraphService:
    """可视化图服务类，用于处理知识图谱的可视化相关功能"""
    
    def __init__(self, collection_id: str, max_graph_nodes: int = 1000):
        """
        初始化可视化图服务
        
        Args:
            collection_id: 知识库集合ID，用作workspace
            max_graph_nodes: 最大图节点数量，默认1000
        """
        self.collection_id = collection_id
        self.max_graph_nodes = max_graph_nodes
        
        # 初始化 LightRAGStorage
        self.lightrag_storage = LightRAGStorage(workspace=collection_id)
        self.lightrag = None  # 将在 _ensure_lightrag_initialized 中初始化
        
        logger.info(f"VisualGraphService initialized with collection_id={collection_id}, max_graph_nodes={max_graph_nodes}")
    
    async def _ensure_lightrag_initialized(self):
        """确保 LightRAG 实例已初始化"""
        if self.lightrag is None:
            logger.info(f"Initializing LightRAG instance for collection_id={self.collection_id}")
            # 异步初始化 lightrag_storage
            await self.lightrag_storage.initialize()
            # 从 lightrag_storage 获取 rag 实例
            self.lightrag = self.lightrag_storage.rag
    
    async def get_knowledge_graph(
        self,
        node_label: str,
        max_depth: int = 3,
        max_nodes: Optional[int] = None
    ) -> KnowledgeGraph:
        """
        获取知识图谱数据
        
        Args:
            node_label: 节点标签，用于筛选起始节点
            max_depth: 最大深度，默认为3
            max_nodes: 最大节点数量，如果为None则使用实例的max_graph_nodes
            
        Returns:
            KnowledgeGraph: 包含节点、边和截断标志的知识图谱对象
            
        Raises:
            ValueError: 当参数无效时抛出
            Exception: 当获取图数据失败时抛出
        """
        try:
            # 参数验证
            if max_depth < 1:
                raise ValueError("max_depth must be at least 1")
            
            if max_nodes is None:
                max_nodes = self.max_graph_nodes
            elif max_nodes < 1:
                raise ValueError("max_nodes must be at least 1")
            
            logger.info(f"Getting knowledge graph: node_label={node_label}, max_depth={max_depth}, max_nodes={max_nodes}")
            
            # 确保 LightRAG 实例已初始化
            await self._ensure_lightrag_initialized()
            
            # 直接使用 LightRAG 的 get_knowledge_graph 方法
            knowledge_graph = await self.lightrag.get_knowledge_graph(
                node_label=node_label,
                max_depth=max_depth,
                max_nodes=max_nodes
            )
            
            logger.info(f"Knowledge graph retrieved: {len(knowledge_graph.nodes)} nodes, {len(knowledge_graph.edges)} edges, truncated={knowledge_graph.is_truncated}")
            
            return knowledge_graph
            
        except ValueError as e:
            logger.error(f"Parameter validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to get knowledge graph: {e}")
            raise Exception(f"Failed to retrieve knowledge graph: {str(e)}")