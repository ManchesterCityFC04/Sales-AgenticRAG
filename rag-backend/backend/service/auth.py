import os
import bcrypt
from typing import Optional
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.param.auth import LoginRequest, RegisterRequest
from backend.param.common import Response
from backend.model.user import User
from backend.config.jwt import create_token, verify_token
from backend.config.database import DatabaseFactory
from backend.config.log import get_logger


async def hash_password(password: str) -> str:
    """密码哈希"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


async def authenticate_user(email: str, password: str) -> Optional[User]:
    """用户认证"""
    logger = get_logger(__name__)
    logger.info(f"开始用户认证 - 邮箱: {email}")
    
    try:
        logger.info("获取数据库会话")
        session = DatabaseFactory.create_session()
        logger.info("数据库会话创建成功")
        
        try:
            # 从数据库查询用户
            logger.info(f"查询用户 - 邮箱: {email}")
            user = session.query(User).filter_by(email=email, is_active=True).first()
            logger.info(f"用户查询完成 - 找到用户: {user is not None}")
            
            if not user:
                logger.warning(f"未找到用户 - 邮箱: {email}")
                return None
            
            # 验证密码
            logger.info("开始密码验证")
            if await verify_password(password, user.password_hash):
                logger.info("密码验证成功")
                return user
            else:
                logger.warning("密码验证失败")
                return None
        finally:
            logger.info("关闭数据库会话")
            session.close()
            logger.info("数据库会话已关闭")
    except Exception as e:
        logger.error(f"用户认证过程中发生错误: {str(e)}")
        raise


async def create_user(username: str, password: str, email: str) -> User:
    """创建用户"""
    Session = DatabaseFactory.get_session()
    session = Session()
    
    try:
        # 检查用户是否已存在
        existing_user = session.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            if existing_user.username == username:
                raise HTTPException(status_code=400, detail="用户名已存在")
            else:
                raise HTTPException(status_code=400, detail="邮箱已存在")
        
        # 创建新用户
        hashed_password = await hash_password(password)
        user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            is_active=True
        )
        
        session.add(user)
        session.commit()
        session.refresh(user)  # 获取数据库生成的ID等字段
        
        return user
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"创建用户失败: {str(e)}")
    finally:
        session.close()


async def get_user_by_username(username: str) -> Optional[User]:
    """根据用户名获取用户"""
    Session = DatabaseFactory.get_session()
    session = Session()
    
    try:
        return session.query(User).filter_by(username=username, is_active=True).first()
    finally:
        session.close()


async def get_user_by_id(user_id: int) -> Optional[User]:
    """根据用户ID获取用户"""
    Session = DatabaseFactory.get_session()
    session = Session()
    
    try:
        return session.query(User).filter_by(id=user_id, is_active=True).first()
    finally:
        session.close()


async def get_user_by_email(email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    Session = DatabaseFactory.get_session()
    session = Session()
    
    try:
        return session.query(User).filter_by(email=email, is_active=True).first()
    finally:
        session.close()


async def login(login_request: LoginRequest) -> Response:
    """用户登录"""
    logger = get_logger(__name__)
    logger.info(f"开始登录请求 - 邮箱: {login_request.email}")
    
    try:
        logger.info("开始用户认证")
        user = await authenticate_user(login_request.email, login_request.password)
        if not user:
            logger.warning(f"用户认证失败 - 邮箱: {login_request.email}")
            return Response.error("邮箱或密码错误")
        
        logger.info(f"用户认证成功 - 用户: {user.username}")
        
        # 生成token，使用user.id作为subject
        logger.info("开始生成token")
        token = create_token(data={"sub": str(user.id)})
        logger.info("token生成成功")
        
        result = Response.success({
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "username": user.username,
                "email": user.email
            }
        })
        logger.info("登录成功，返回响应")
        return result
    except Exception as e:
        logger.error(f"登录过程中发生错误: {str(e)}")
        return Response.error(f"登录失败: {str(e)}")


async def register(register_request: RegisterRequest) -> Response:
    """用户注册"""
    try:
        user = await create_user(
            register_request.username,
            register_request.password,
            register_request.email
        )
        
        return Response.success({
            "message": "注册成功",
            "user": {
                "username": user.username,
                "email": user.email
            }
        })
    except HTTPException as e:
        return Response.error(e.detail)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> Response:
    """获取当前用户信息"""
    try:
        payload = verify_token(credentials.credentials)
        current_email = payload.get("sub")
    except Exception:
        return Response.error("Token无效或已过期")
    
    user = await get_user_by_email(current_email)
    
    if not user:
        return Response.error("用户不存在")
    
    return Response.success({
        "username": user.username,
        "email": user.email
    })