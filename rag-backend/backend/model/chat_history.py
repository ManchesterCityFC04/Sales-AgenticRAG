from sqlalchemy import Column, Integer, String, Text, JSON
from backend.config.database import DatabaseFactory

Base = DatabaseFactory.get_base()

class ChatHistory(Base):
    __tablename__ = 'chat_history'
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 对话ID，关联到conversation表
    conversation_id = Column(String(36), nullable=False, index=True)
    
    # 消息角色：user, assistant, system
    role = Column(String(20), nullable=False)
    
    # 消息类型：text, image, file, function_call等
    type = Column(String(20), nullable=False, default='text')
    
    # 消息内容
    content = Column(Text, nullable=False)
    
    # 额外数据，存储元信息（如模型参数、token数量等）
    extra_data = Column(JSON, nullable=True)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'role': self.role,
            'type': self.type,
            'content': self.content,
            'extra_data': self.extra_data
        }
    
    def __repr__(self):
        return f"<ChatHistory(id={self.id}, conversation_id='{self.conversation_id}', role='{self.role}')>"