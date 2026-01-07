"""
PowerX 交易服务

创建日期: 2026-01-07
作者: zhi.qu

交易订单相关业务逻辑
"""

import uuid
import random
from datetime import date, datetime
from typing import List, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.china_market.price_cap import validate_price
from app.china_market.trading_rules import validate_order


class TradingService:
    """交易服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        # 模拟订单存储
        self._orders: Dict[str, Dict] = {}
        self._positions: Dict[str, List[Dict]] = {}
    
    async def create_order(
        self,
        user_id: int,
        province: str,
        market_type: str,
        direction: str,
        price: float,
        quantity_mwh: float
    ) -> Dict:
        """
        创建交易订单
        
        Args:
            user_id: 用户ID
            province: 省份
            market_type: 市场类型 (DAY_AHEAD, INTRADAY)
            direction: 方向 (BUY, SELL)
            price: 价格
            quantity_mwh: 数量
            
        Returns:
            订单信息
            
        Raises:
            ValueError: 验证失败
        """
        # 验证价格
        price_result = validate_price(province, price)
        if not price_result["valid"]:
            raise ValueError(price_result["error"])
        
        # 验证订单
        order_result = validate_order(
            province=province,
            market_type=market_type,
            price=price,
            quantity_mwh=quantity_mwh,
            base_price=480  # 模拟基准价
        )
        if not order_result["valid"]:
            raise ValueError("; ".join(order_result["errors"]))
        
        # 创建订单
        order_id = f"SPT{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
        
        order = {
            "id": order_id,
            "user_id": user_id,
            "province": province,
            "market_type": market_type,
            "direction": direction,
            "price": price,
            "quantity_mwh": quantity_mwh,
            "filled_quantity": 0,
            "filled_price": None,
            "status": "PENDING",
            "created_at": datetime.now().isoformat()
        }
        
        # 模拟部分成交
        if random.random() > 0.3:
            fill_ratio = random.uniform(0.5, 1.0)
            order["filled_quantity"] = round(quantity_mwh * fill_ratio, 1)
            order["filled_price"] = price + random.uniform(-5, 5)
            order["status"] = "FILLED" if fill_ratio == 1.0 else "PARTIAL"
        
        self._orders[order_id] = order
        return order
    
    async def get_orders(
        self,
        user_id: int,
        market_type: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict]:
        """
        获取订单列表
        
        Args:
            user_id: 用户ID
            market_type: 市场类型筛选
            status: 状态筛选
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            订单列表
        """
        # 返回模拟数据
        mock_orders = [
            {
                "id": "SPT20260107001",
                "province": "广东",
                "market_type": "DAY_AHEAD",
                "direction": "BUY",
                "price": 485.00,
                "quantity_mwh": 100,
                "filled_quantity": 100,
                "filled_price": 482.50,
                "status": "FILLED",
                "created_at": "2026-01-07 10:00:00"
            },
            {
                "id": "SPT20260107002",
                "province": "广东",
                "market_type": "DAY_AHEAD",
                "direction": "BUY",
                "price": 490.00,
                "quantity_mwh": 50,
                "filled_quantity": 30,
                "filled_price": 488.00,
                "status": "PARTIAL",
                "created_at": "2026-01-07 10:15:00"
            }
        ]
        
        # 合并实际创建的订单
        for order in self._orders.values():
            if order["user_id"] == user_id:
                mock_orders.append(order)
        
        return mock_orders
    
    async def get_order(self, order_id: str, user_id: int) -> Optional[Dict]:
        """
        获取订单详情
        
        Args:
            order_id: 订单ID
            user_id: 用户ID
            
        Returns:
            订单信息
        """
        return self._orders.get(order_id)
    
    async def cancel_order(self, order_id: str, user_id: int) -> bool:
        """
        撤销订单
        
        Args:
            order_id: 订单ID
            user_id: 用户ID
            
        Returns:
            是否成功
            
        Raises:
            ValueError: 订单不存在或无法撤销
        """
        order = self._orders.get(order_id)
        if not order:
            raise ValueError("订单不存在")
        
        if order["status"] == "FILLED":
            raise ValueError("已成交订单无法撤销")
        
        order["status"] = "CANCELLED"
        return True
    
    async def get_positions(self, user_id: int) -> List[Dict]:
        """
        获取持仓列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            持仓列表
        """
        # 返回模拟持仓数据
        return [
            {
                "id": "POS001",
                "contract": "广东现货2026Q1",
                "direction": "买入",
                "quantity_mwh": 500,
                "avg_price": 478.50,
                "current_price": 485.32,
                "pnl": 3410,
                "pnl_percent": 1.42
            },
            {
                "id": "POS002",
                "contract": "浙江中长期月度",
                "direction": "卖出",
                "quantity_mwh": 300,
                "avg_price": 495.00,
                "current_price": 488.15,
                "pnl": 2055,
                "pnl_percent": 1.38
            }
        ]
    
    async def get_statistics(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict:
        """
        获取交易统计
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            统计数据
        """
        return {
            "total_orders": 156,
            "total_volume_mwh": 125840,
            "total_amount": 58125000,
            "avg_price": 461.87,
            "win_rate": 0.68,
            "total_pnl": 4785
        }
