from pydantic import BaseModel
from typing import Any, Optional

class Response(BaseModel):
    status: int = 0
    data: Optional[Any] = None
    msg: Optional[str] = None
    
    def __str__(self):
        return f"status: {self.status}, data: {self.data}, msg: {self.msg}"

    @staticmethod # 静态方法，可以在不创建类实例的情况下调用，通常用于与类或实例状态无关的工具函数。
    def success(data: Any) -> 'Response':
        return Response(status=200, data=data)

    @staticmethod
    def success_with_msg(data: Any, msg: str) -> 'Response':
        return Response(status=200, data=data, msg=msg)
    
    @staticmethod
    def error(msg: str) -> 'Response':
        return Response(status=500, msg=msg)