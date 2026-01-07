"""
PowerX 自定义异常

创建日期: 2026-01-07
作者: zhi.qu

统一的异常处理机制
"""

from typing import Any, Dict, Optional


class PowerXException(Exception):
    """PowerX 基础异常类"""
    
    def __init__(
        self,
        message: str = "服务器内部错误",
        code: int = 500,
        detail: Optional[Any] = None
    ):
        self.message = message
        self.code = code
        self.detail = detail
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "code": self.code,
            "message": self.message,
            "success": False
        }
        if self.detail is not None:
            result["detail"] = self.detail
        return result


class ValidationError(PowerXException):
    """数据验证错误"""
    
    def __init__(
        self,
        message: str = "数据验证失败",
        detail: Optional[Any] = None
    ):
        super().__init__(message=message, code=400, detail=detail)


class AuthenticationError(PowerXException):
    """认证错误"""
    
    def __init__(
        self,
        message: str = "认证失败，请重新登录",
        detail: Optional[Any] = None
    ):
        super().__init__(message=message, code=401, detail=detail)


class AuthorizationError(PowerXException):
    """授权错误"""
    
    def __init__(
        self,
        message: str = "权限不足，无法执行此操作",
        detail: Optional[Any] = None
    ):
        super().__init__(message=message, code=403, detail=detail)


class NotFoundError(PowerXException):
    """资源不存在错误"""
    
    def __init__(
        self,
        message: str = "请求的资源不存在",
        detail: Optional[Any] = None
    ):
        super().__init__(message=message, code=404, detail=detail)


class ConflictError(PowerXException):
    """资源冲突错误"""
    
    def __init__(
        self,
        message: str = "资源已存在或状态冲突",
        detail: Optional[Any] = None
    ):
        super().__init__(message=message, code=409, detail=detail)


class RateLimitError(PowerXException):
    """请求频率限制错误"""
    
    def __init__(
        self,
        message: str = "请求过于频繁，请稍后再试",
        detail: Optional[Any] = None,
        retry_after: Optional[int] = None
    ):
        self.retry_after = retry_after
        if retry_after:
            detail = detail or {}
            if isinstance(detail, dict):
                detail["retry_after"] = retry_after
        super().__init__(message=message, code=429, detail=detail)


class ExternalServiceError(PowerXException):
    """外部服务错误"""
    
    def __init__(
        self,
        message: str = "外部服务暂时不可用",
        service_name: Optional[str] = None,
        detail: Optional[Any] = None
    ):
        self.service_name = service_name
        if service_name:
            message = f"{service_name} 服务暂时不可用"
        super().__init__(message=message, code=502, detail=detail)


class DatabaseError(PowerXException):
    """数据库错误"""
    
    def __init__(
        self,
        message: str = "数据库操作失败",
        detail: Optional[Any] = None
    ):
        super().__init__(message=message, code=500, detail=detail)


class TradingError(PowerXException):
    """交易错误"""
    
    def __init__(
        self,
        message: str = "交易操作失败",
        detail: Optional[Any] = None
    ):
        super().__init__(message=message, code=400, detail=detail)


class OrderError(TradingError):
    """订单错误"""
    
    def __init__(
        self,
        message: str = "订单操作失败",
        order_id: Optional[str] = None,
        detail: Optional[Any] = None
    ):
        self.order_id = order_id
        if order_id:
            detail = detail or {}
            if isinstance(detail, dict):
                detail["order_id"] = order_id
        super().__init__(message=message, detail=detail)


class MarketClosedError(TradingError):
    """市场已关闭错误"""
    
    def __init__(
        self,
        message: str = "当前市场已关闭，无法进行交易",
        market_type: Optional[str] = None,
        detail: Optional[Any] = None
    ):
        self.market_type = market_type
        if market_type:
            detail = detail or {}
            if isinstance(detail, dict):
                detail["market_type"] = market_type
        super().__init__(message=message, detail=detail)


class PriceLimitError(TradingError):
    """价格限制错误"""
    
    def __init__(
        self,
        message: str = "价格超出限制范围",
        price: Optional[float] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        detail: Optional[Any] = None
    ):
        detail = detail or {}
        if isinstance(detail, dict):
            if price is not None:
                detail["price"] = price
            if min_price is not None:
                detail["min_price"] = min_price
            if max_price is not None:
                detail["max_price"] = max_price
        super().__init__(message=message, detail=detail)


class InsufficientBalanceError(TradingError):
    """余额不足错误"""
    
    def __init__(
        self,
        message: str = "账户余额不足",
        required: Optional[float] = None,
        available: Optional[float] = None,
        detail: Optional[Any] = None
    ):
        detail = detail or {}
        if isinstance(detail, dict):
            if required is not None:
                detail["required"] = required
            if available is not None:
                detail["available"] = available
        super().__init__(message=message, detail=detail)
