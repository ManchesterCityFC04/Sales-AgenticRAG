from fastapi import APIRouter, Depends, Query
from backend.config.log import get_logger
from backend.config.dependencies import get_current_user
from backend.service.visual_graph import VisualGraphService

logger = get_logger(__name__)

router = APIRouter(
    prefix="/visual",
    tags=["VISUAL_GRAPH"]
)

@router.get("/graph/{collection_id}")
async def get_visual_graph(
    collection_id: str,
    label: str = Query(..., description="Label to get knowledge graph for"),
    current_user: int = Depends(get_current_user),
):
    """获取知识库的可视化图"""
    logger.info(f"用户 {current_user} 请求获取知识库 {collection_id} 的可视化图，label={label}")
    visualgraph = VisualGraphService(collection_id)
    return await visualgraph.get_knowledge_graph(node_label=label)
