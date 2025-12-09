from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    """登录请求参数"""
    email: str
    password: str


class RegisterRequest(BaseModel):
    """注册请求参数"""
    username: str
    password: str
    email: str