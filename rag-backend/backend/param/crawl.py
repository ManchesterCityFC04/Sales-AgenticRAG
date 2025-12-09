from pydantic import BaseModel
from typing import Optional

class CrawlRequest(BaseModel):
    url: Optional[str] = None
    prefix: Optional[str] = None
    if_llm: Optional[bool] = None
    base_url: Optional[str] = True
    api_key: Optional[str] = True
    provider: Optional[str] = True
    model_id: Optional[str] = True
    user_id: Optional[str] = None
    title: Optional[str] = None
    collection_id: Optional[str] = None

class CrawlStatusRequest(BaseModel):
    collection_id: Optional[str] = None

class UploadDocRequest(BaseModel):
    user_id: Optional[str] = None
    collection_id: Optional[str] = None
    document_name: Optional[str] = None
