import os
import redis.asyncio as redis
from typing import Optional


class RedisClientFactory:
    """
    Redis客户端全局单例工厂类
    提供线程/协程安全的异步Redis客户端
    """
    
    _instance: Optional[redis.Redis] = None
    _lock = None
    
    @classmethod
    async def get_instance(cls) -> redis.Redis:
        """
        获取全局单例Redis客户端实例
        
        Returns:
            redis.Redis: 异步Redis客户端实例
        """
        if cls._instance is None:
            cls._create_instance()
        return cls._instance
    
    @classmethod
    def _create_instance(cls):
        """创建Redis客户端实例"""
        cls._instance = redis.Redis(
            host=os.getenv("REDIS_HOST", "127.0.0.1"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=int(os.getenv("REDIS_DB", "0")),
            password=os.getenv("REDIS_PASSWORD"),
            decode_responses=True,
            socket_connect_timeout=5,
            socket_keepalive=True,
            retry_on_timeout=True,
            max_connections=20
        )
    
    @classmethod
    async def close_instance(cls):
        """
        关闭Redis客户端连接
        """
        if cls._instance is not None:
            await cls._instance.close()
            cls._instance = None
    
    @classmethod
    def is_connected(cls) -> bool:
        """
        检查Redis连接状态
        
        Returns:
            bool: 连接是否正常
        """
        return cls._instance is not None
    
    @classmethod
    async def ping(cls) -> bool:
        """
        测试Redis连接
        
        Returns:
            bool: 连接是否正常
        """
        if cls._instance is None:
            return False
        try:
            await cls._instance.ping()
            return True
        except Exception:
            return False



async def get_redis_client() -> redis.Redis:
    """
    获取Redis客户端实例（函数形式，便于使用）
    
    Returns:
        redis.Redis: 异步Redis客户端实例
    """
    return await RedisClientFactory.get_instance()


async def close_redis_connection():
    """关闭Redis连接"""
    await RedisClientFactory.close_instance()