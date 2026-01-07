"""
PowerX API 响应模型

创建日期: 2026-01-07
作者: zhi.qu

统一的 API 响应格式
"""

from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """
    统一 API 响应模型
    
    所有 API 响应都使用此格式，确保前后端交互一致性
    """
    code: int = Field(default=200, description="状态码")
    message: str = Field(default="success", description="响应消息")
    success: bool = Field(default=True, description="是否成功")
    data: Optional[T] = Field(default=None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PaginatedData(BaseModel, Generic[T]):
    """分页数据模型"""
    items: List[T] = Field(default_factory=list, description="数据列表")
    total: int = Field(default=0, description="总数量")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=20, description="每页数量")
    total_pages: int = Field(default=0, description="总页数")
    has_next: bool = Field(default=False, description="是否有下一页")
    has_prev: bool = Field(default=False, description="是否有上一页")


class PaginatedResponse(APIResponse[PaginatedData[T]], Generic[T]):
    """分页响应模型"""
    pass


class ErrorDetail(BaseModel):
    """错误详情模型"""
    field: Optional[str] = Field(default=None, description="错误字段")
    message: str = Field(..., description="错误消息")
    type: Optional[str] = Field(default=None, description="错误类型")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    code: int = Field(..., description="错误码")
    message: str = Field(..., description="错误消息")
    success: bool = Field(default=False, description="是否成功")
    detail: Optional[Any] = Field(default=None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")


# ============ 响应工厂函数 ============

def success_response(
    data: Any = None,
    message: str = "success",
    code: int = 200
) -> dict:
    """
    创建成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
        code: 状态码
        
    Returns:
        dict: 响应字典
    """
    return {
        "code": code,
        "message": message,
        "success": True,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }


def error_response(
    message: str = "操作失败",
    code: int = 400,
    detail: Any = None
) -> dict:
    """
    创建错误响应
    
    Args:
        message: 错误消息
        code: 错误码
        detail: 错误详情
        
    Returns:
        dict: 响应字典
    """
    return {
        "code": code,
        "message": message,
        "success": False,
        "detail": detail,
        "timestamp": datetime.now().isoformat()
    }


def paginated_response(
    items: List[Any],
    total: int,
    page: int = 1,
    page_size: int = 20,
    message: str = "success"
) -> dict:
    """
    创建分页响应
    
    Args:
        items: 数据列表
        total: 总数量
        page: 当前页码
        page_size: 每页数量
        message: 响应消息
        
    Returns:
        dict: 分页响应字典
    """
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    
    return {
        "code": 200,
        "message": message,
        "success": True,
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        },
        "timestamp": datetime.now().isoformat()
    }
