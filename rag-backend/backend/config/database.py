import os
from threading import Lock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# 加载 .env 后面应该可以只保留main文件里的
load_dotenv()

Base = declarative_base()

class DatabaseFactory:
    _engine = None
    _Session = None
    _lock = Lock()

    @classmethod
    def get_engine(cls):
        # 第一次检查：避免不必要的锁竞争，提高性能
        # 如果引擎已经创建，直接返回，无需获取锁
        if cls._engine is None:
            # 获取线程锁，确保只有一个线程能进入临界区
            with cls._lock:
                # 第二次检查：防止多个线程同时通过第一次检查后重复创建引擎
                # 这是双重检查锁定模式(Double-Checked Locking Pattern)的核心
                if cls._engine is None:
                    db_url = os.getenv("DB_URL")
                    if not db_url:
                        raise RuntimeError("❌ DB_URL not found in environment variables")
                    cls._engine = create_engine(
                        db_url,
                        pool_pre_ping=True,       # 防止连接失效
                        pool_recycle=3600,        # 定时回收连接
                        echo=False                # 调试时可设 True 打印 SQL
                    )
        return cls._engine

    @classmethod
    def get_session(cls):
        # 同样使用双重检查锁定模式确保Session工厂的单例创建
        # 第一次检查：快速路径，避免锁竞争
        if cls._Session is None:
            # 获取线程锁，确保线程安全
            with cls._lock:
                # 第二次检查：防止重复创建Session工厂
                if cls._Session is None:
                    engine = cls.get_engine()
                    cls._Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        return cls._Session

    @classmethod
    def create_session(cls):
        """创建一个新的数据库会话实例"""
        engine = cls.get_engine()
        Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        return Session()

    @classmethod
    def get_base(cls):
        return Base
