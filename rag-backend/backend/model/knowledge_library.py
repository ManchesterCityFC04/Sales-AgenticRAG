from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, func
from sqlalchemy.orm import relationship
import uuid
from backend.utils.timezone import to_china_time
from backend.config.database import DatabaseFactory

Base = DatabaseFactory.get_base()

class KnowledgeLibrary(Base):
    """知识库模型"""
    __tablename__ = 'knowledge_libraries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    collection_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False, comment='知识库唯一标识UUID')
    title = Column(String(200), nullable=False, comment='知识库标题')
    description = Column(Text, nullable=True, comment='知识库描述')
    user_id = Column(String(100), nullable=False, comment='创建用户ID')
    is_active = Column(Boolean, default=True, nullable=False, comment='是否激活')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    
    # 关联文档
    documents = relationship("KnowledgeDocument", back_populates="library", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'collection_id': self.collection_id,
            'title': self.title,
            'description': self.description,
            'user_id': self.user_id,
            'is_active': self.is_active,
            'documents': [doc.to_dict() for doc in self.documents] if self.documents else [],
            'created_at': to_china_time(self.created_at).isoformat() if self.created_at else None,
            'updated_at': to_china_time(self.updated_at).isoformat() if self.updated_at else None
        }


class KnowledgeDocument(Base):
    """知识库文档模型"""
    __tablename__ = 'knowledge_documents'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    library_id = Column(Integer, ForeignKey('knowledge_libraries.id'), nullable=False, comment='所属知识库ID')
    name = Column(String(200), nullable=False, comment='文档名称')
    type = Column(String(20), nullable=False, comment='文档类型：link, file, pdf等')
    url = Column(String(500), nullable=True, comment='文档链接地址')
    file_path = Column(String(500), nullable=True, comment='文件存储路径')
    file_size = Column(Integer, nullable=True, comment='文件大小（字节）')
    is_processed = Column(Boolean, default=False, nullable=False, comment='是否已处理')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    
    # 关联知识库
    library = relationship("KnowledgeLibrary", back_populates="documents")
    
    def to_dict(self):
        return {
            'id': self.id,
            'library_id': self.library_id,
            'name': self.name,
            'type': self.type,
            'url': self.url,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'is_processed': self.is_processed,
            'created_at': to_china_time(self.created_at).isoformat() if self.created_at else None,
            'updated_at': to_china_time(self.updated_at).isoformat() if self.updated_at else None
        }