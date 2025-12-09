from fastapi import APIRouter

router = APIRouter(
    prefix="/rag",
    tags=["RAG"]
)

@router.get("/query")
async def query_rag(q: str):
    return {"query": q, "results": []}

@router.post("/index")
async def index_document(document: str):
    return {"status": "success", "document": document}
