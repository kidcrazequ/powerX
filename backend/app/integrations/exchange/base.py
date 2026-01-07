"""
PowerX 交易所基类
创建日期: 2026-01-07
作者: zhi.qu

交易所对接抽象基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class OrderSide(str, Enum):
    """订单方向"""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, Enum):
    """订单状态"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class MarketQuote:
    """市场报价"""
    province: str
    price: float
    volume: float
    timestamp: datetime
    bid_price: Optional[float] = None
    ask_price: Optional[float] = None
    bid_volume: Optional[float] = None
    ask_volume: Optional[float] = None


@dataclass
class OrderResult:
    """订单结果"""
    order_id: str
    exchange_order_id: str
    status: OrderStatus
    filled_quantity: float
    filled_price: Optional[float]
    message: str
    timestamp: datetime


@dataclass
class TradeRecord:
    """成交记录"""
    trade_id: str
    order_id: str
    side: OrderSide
    quantity: float
    price: float
    fee: float
    timestamp: datetime


class ExchangeBase(ABC):
    """交易所抽象基类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._connected = False
    
    @property
    @abstractmethod
    def name(self) -> str:
        """交易所名称"""
        pass
    
    @property
    @abstractmethod
    def province(self) -> str:
        """所属省份"""
        pass
    
    @abstractmethod
    async def connect(self) -> bool:
        """建立连接"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """断开连接"""
        pass
    
    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._connected
    
    # 行情接口
    @abstractmethod
    async def get_market_quote(self) -> MarketQuote:
        """获取实时行情"""
        pass
    
    @abstractmethod
    async def get_order_book(self, depth: int = 10) -> Dict[str, Any]:
        """获取订单簿"""
        pass
    
    @abstractmethod
    async def get_trades(self, limit: int = 50) -> List[TradeRecord]:
        """获取成交记录"""
        pass
    
    # 交易接口
    @abstractmethod
    async def submit_order(
        self,
        side: OrderSide,
        quantity: float,
        price: float,
        order_type: str = "limit"
    ) -> OrderResult:
        """提交订单"""
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str) -> OrderResult:
        """取消订单"""
        pass
    
    @abstractmethod
    async def get_order_status(self, order_id: str) -> OrderResult:
        """查询订单状态"""
        pass
    
    @abstractmethod
    async def get_open_orders(self) -> List[OrderResult]:
        """获取未成交订单"""
        pass
    
    # 账户接口
    @abstractmethod
    async def get_balance(self) -> Dict[str, float]:
        """获取账户余额"""
        pass
    
    @abstractmethod
    async def get_positions(self) -> Dict[str, float]:
        """获取持仓"""
        pass
