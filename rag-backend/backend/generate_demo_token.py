#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成演示用的默认用户和访问令牌脚本
用于跳过注册步骤直接体验系统功能
"""

import sys
import os

# 添加项目路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.service.auth import create_user
from backend.config.jwt import create_token
from backend.model.user import User
from backend.config.database import DatabaseFactory
from sqlalchemy.orm import sessionmaker


async def create_demo_user():
    """创建演示用户并生成访问令牌"""
    try:
        # 创建用户
        username = "demo"
        email = "demo@example.com"
        password = "demo123456"
        
        # 获取数据库会话
        session = DatabaseFactory.create_session()
        
        try:
            # 检查用户是否已存在
            existing_user = session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                print(f"演示用户已存在: {existing_user.username} ({existing_user.email})")
                user = existing_user
            else:
                # 创建新用户
                from bcrypt import hashpw, gensalt
                hashed_password = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')
                
                user = User(
                    username=username,
                    email=email,
                    password_hash=hashed_password,
                    is_active=True
                )
                
                session.add(user)
                session.commit()
                session.refresh(user)
                print(f"演示用户创建成功: {user.username} ({user.email})")
            
            # 生成访问令牌
            token = create_token(data={"sub": str(user.id)})
            
            print("\n" + "="*50)
            print("演示用户信息:")
            print(f"  用户名: {user.username}")
            print(f"  邮箱: {user.email}")
            print(f"  密码: {password}")
            print("\n访问令牌:")
            print(f"  {token}")
            print("="*50)
            
            # 提供前端使用说明
            print("\n前端使用说明:")
            print("1. 在浏览器控制台中执行以下代码设置token:")
            print(f"   localStorage.setItem('auth_token', '{token}');")
            print(f"   localStorage.setItem('user_info', JSON.stringify({{email: '{user.email}', id: '{user.id}', username: '{user.username}'}}));")
            print("2. 刷新页面即可跳过登录直接体验功能")
            
            return token
            
        finally:
            session.close()
            
    except Exception as e:
        print(f"创建演示用户时出错: {str(e)}")
        return None


if __name__ == "__main__":
    import asyncio
    asyncio.run(create_demo_user())