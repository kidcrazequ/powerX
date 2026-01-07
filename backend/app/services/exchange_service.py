"""
PowerX 交易所服务
创建日期: 2026-01-07
作者: zhi.qu

统一管理多个交易所连接
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from app.integrations.exchange.base import (
    ExchangeBase, MarketQuote, OrderResult, TradeRecord, OrderSide
)
from app.integrations.exchange.guangdong import GuangdongExchange


class ExchangeService:
    """交易所服务"""
    
    def __init__(self):
        self._exchanges: Dict[str, ExchangeBase] = {}
        self._initialized = False
    
    async def initialize(self):
        """初始化所有交易所连接"""
        if self._initialized:
            return
        
        # 注册交易所
        self._exchanges["guangdong"] = GuangdongExchange()
        # 未来可添加更多交易所
        # self._exchanges["zhejiang"] = ZhejiangExchange()
        # self._exchanges["jiangsu"] = JiangsuExchange()
        
        # 建立连接
        for name, exchange in self._exchanges.items():
            try:
                await exchange.connect()
                logger.info(f"交易所 {name} 连接成功")
            except Exception as e:
                logger.error(f"交易所 {name} 连接失败: {e}")
        
        self._initialized = True
    
    async def shutdown(self):
        """关闭所有连接"""
        for exchange in self._exchanges.values():
            try:
                await exchange.disconnect()
            except Exception as e:
                logger.error(f"断开连接失败: {e}")
        self._initialized = False
    
    def get_exchange(self, province: str) -> Optional[ExchangeBase]:
        """获取交易所实例"""
        return self._exchanges.get(province)
    
    def list_exchanges(self) -> List[Dict[str, Any]]:
        """列出所有交易所"""
        return [
            {
                "province": province,
                "name": exchange.name,
                "connected": exchange.is_connected
            }
            for province, exchange in self._exchanges.items()
        ]
    
    async def get_all_quotes(self) -> Dict[str, MarketQuote]:
        """获取所有交易所行情"""
        quotes = {}
        for province, exchange in self._exchanges.items():
            if exchange.is_connected:
                try:
                    quote = await exchange.get_market_quote()
                    quotes[province] = quote
                except Exception as e:
                    logger.error(f"获取 {province} 行情失败: {e}")
        return quotes
    
    async def get_quote(self, province: str) -> Optional[MarketQuote]:
        """获取指定交易所行情"""
        exchange = self.get_exchange(province)
        if exchange and exchange.is_connected:
            return await exchange.get_market_quote()
        return None
    
    async def get_order_book(self, province: str, depth: int = 10) -> Optional[Dict[str, Any]]:
        """获取订单簿"""
        exchange = self.get_exchange(province)
        if exchange and exchange.is_connected:
            return await exchange.get_order_book(depth)
        return None
    
    async def submit_order(
        self,
        province: str,
        side: str,
        quantity: float,
        price: float,
        order_type: str = "limit"
    ) -> OrderResult:
        """提交订单"""
        exchange = self.get_exchange(province)
        if not exchange:
            raise ValueError(f"交易所不存在: {province}")
        if not exchange.is_connected:
            raise ValueError(f"交易所未连接: {province}")
        
        order_side = OrderSide.BUY if side == "buy" else OrderSide.SELL
        return await exchange.submit_order(order_side, quantity, price, order_type)
    
    async def cancel_order(self, province: str, order_id: str) -> OrderResult:
        """取消订单"""
        exchange = self.get_exchange(province)
        if not exchange:
            raise ValueError(f"交易所不存在: {province}")
        return await exchange.cancel_order(order_id)
    
    async def get_order_status(self, province: str, order_id: str) -> OrderResult:
        """查询订单状态"""
        exchange = self.get_exchange(province)
        if not exchange:
            raise ValueError(f"交易所不存在: {province}")
        return await exchange.get_order_status(order_id)
    
    async def get_balance(self, province: str) -> Dict[str, float]:
        """获取账户余额"""
        exchange = self.get_exchange(province)
        if exchange and exchange.is_connected:
            return await exchange.get_balance()
        return {}
    
    async def get_positions(self, province: str) -> Dict[str, float]:
        """获取持仓"""
        exchange = self.get_exchange(province)
        if exchange and exchange.is_connected:
            return await exchange.get_positions()
        return {}


# 单例
exchange_service = ExchangeService()


async def init_exchange_service():
    """初始化交易所服务"""
    await exchange_service.initialize()


async def close_exchange_service():
    """关闭交易所服务"""
    await exchange_service.shutdown()


def get_exchange_service() -> ExchangeService:
    """获取交易所服务"""
    return exchange_service
