import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel


class JWTSettings(BaseModel):
    secret_key: str = os.environ.get("JWT_SECRET_KEY", "secretsecretsecretsecretsecretsecret")
    algorithm: str = os.environ.get("JWT_ALGORITHM", "HS256")
    # 延长token有效期到24小时，因为不再有refresh机制
    token_expire_hours: int = int(os.environ.get("JWT_TOKEN_EXPIRES", "86400")) // 3600


# JWT设置实例
jwt_settings = JWTSettings()

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建token（单token机制）"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=jwt_settings.token_expire_hours)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, jwt_settings.secret_key, algorithm=jwt_settings.algorithm)
    return encoded_jwt


def verify_token(token: str):
    """验证token"""
    try:
        payload = jwt.decode(token, jwt_settings.secret_key, algorithms=[jwt_settings.algorithm])
        return payload
    except JWTError:
        return None


def hash_password(password: str) -> str:
    """密码哈希"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)