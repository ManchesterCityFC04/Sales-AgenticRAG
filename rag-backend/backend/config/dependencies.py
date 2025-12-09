from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.config.jwt import verify_token


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """获取当前用户的依赖函数"""
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Token无效或已过期")
    
    current_user_id = payload.get("sub")
    if not current_user_id:
        raise HTTPException(status_code=401, detail="无法获取用户信息")
    
    # 将字符串ID转换为整数
    try:
        return int(current_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="用户ID格式错误")


def get_optional_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))):
    """可选的当前用户依赖函数（不强制要求登录）"""
    if not credentials:
        return None
    
    payload = verify_token(credentials.credentials)
    if not payload:
        return None
    
    current_user_id = payload.get("sub")
    if not current_user_id:
        return None
    
    # 将字符串ID转换为整数
    try:
        return int(current_user_id)
    except ValueError:
        return None