from sqlalchemy import Column, Integer, String, Text, DateTime, func
from backend.utils.timezone import to_china_time
from backend.config.database import DatabaseFactory
import uuid

Base = DatabaseFactory.get_base()

class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String(36), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'title': self.title,
            'user_id': self.user_id,
            'created_at': to_china_time(self.created_at).isoformat() if self.created_at else None,
            'updated_at': to_china_time(self.updated_at).isoformat() if self.updated_at else None
        }