#!/usr/bin/env python3
"""
数据库初始化脚本
创建所有必要的表
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config.database import DatabaseFactory
from backend.model.user import User
from backend.model.conversation import Conversation
from backend.model.knowledge_library import KnowledgeLibrary, KnowledgeDocument
from backend.model.chat_history import ChatHistory


def create_tables():
    """创建所有表"""
    engine = DatabaseFactory.get_engine()
    Base = DatabaseFactory.get_base()
    
    print("正在创建数据库表...")
    Base.metadata.create_all(engine)
    print("数据库表创建完成!")


def init_database():
    """初始化数据库"""
    print("开始初始化数据库...")
    
    # 创建表
    create_tables()
    
    print("数据库初始化完成!")


if __name__ == "__main__":
    init_database()