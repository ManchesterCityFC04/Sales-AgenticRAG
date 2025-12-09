from pydantic import BaseModel
from typing import Optional, List


class CreateLibraryRequest(BaseModel):
    """创建知识库请求参数"""
    title: str
    description: Optional[str] = None


class UpdateLibraryRequest(BaseModel):
    """更新知识库请求参数"""
    title: Optional[str] = None
    description: Optional[str] = None


class AddDocumentRequest(BaseModel):
    """添加文档请求参数"""
    library_id: int
    name: str
    type: str  # link, file, pdf等
    url: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None


class UpdateDocumentRequest(BaseModel):
    """更新文档请求参数"""
    name: Optional[str] = None
    type: Optional[str] = None
    url: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None


class LibraryListResponse(BaseModel):
    """知识库列表响应"""
    id: int
    collection_id: str
    title: str
    description: Optional[str]
    user_id: str
    is_active: bool
    document_count: int
    created_at: str
    updated_at: str


class DocumentResponse(BaseModel):
    """文档响应"""
    id: int
    library_id: int
    name: str
    type: str
    url: Optional[str]
    file_path: Optional[str]
    file_size: Optional[int]
    is_processed: bool
    created_at: str
    updated_at: str


class LibraryDetailResponse(BaseModel):
    """知识库详情响应"""
    id: int
    collection_id: str
    title: str
    description: Optional[str]
    user_id: str
    is_active: bool
    documents: List[DocumentResponse]
    created_at: str
    updated_at: str