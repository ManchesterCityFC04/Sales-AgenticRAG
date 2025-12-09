from sqlalchemy import Column, Integer, String, DateTime, Boolean, func
from backend.utils.timezone import to_china_time
from backend.config.database import DatabaseFactory

Base = DatabaseFactory.get_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': to_china_time(self.created_at).isoformat() if self.created_at else None,
            'updated_at': to_china_time(self.updated_at).isoformat() if self.updated_at else None
        }