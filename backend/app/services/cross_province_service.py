"""
PowerX 跨省交易服务
创建日期: 2026-01-07
作者: zhi.qu
"""
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from loguru import logger

from app.models.cross_province_order import (
    CrossProvinceOrder, CrossProvinceOrderStatus, TransmissionChannel
)


class CrossProvinceService:
    """跨省交易服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_order(
        self,
        user_id: str,
        order_type: str,
        source_province: str,
        target_province: str,
        quantity: float,
        price: float,
        delivery_start: datetime,
        delivery_end: datetime,
        transmission_channel: str = None
    ) -> CrossProvinceOrder:
        """创建跨省交易订单"""
        order_id = f"CRO-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        # 获取输电费用
        channel = await self.get_best_channel(source_province, target_province)
        transmission_fee = channel.transmission_fee if channel else 20.0
        
        order = CrossProvinceOrder(
            order_id=order_id,
            user_id=user_id,
            order_type=order_type,
            source_province=source_province,
            target_province=target_province,
            transmission_channel=channel.channel_id if channel else None,
            quantity=quantity,
            price=price,
            transmission_fee=transmission_fee,
            total_price=price + transmission_fee,
            delivery_start=delivery_start,
            delivery_end=delivery_end,
            status=CrossProvinceOrderStatus.PENDING.value
        )
        
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        
        logger.info(f"创建跨省订单: {order_id}, {source_province} -> {target_province}")
        return order
    
    async def get_best_channel(
        self,
        from_province: str,
        to_province: str
    ) -> Optional[TransmissionChannel]:
        """获取最佳输电通道"""
        query = select(TransmissionChannel).where(
            and_(
                TransmissionChannel.from_province == from_province,
                TransmissionChannel.to_province == to_province,
                TransmissionChannel.is_active == True,
                TransmissionChannel.available_capacity > 0
            )
        ).order_by(TransmissionChannel.transmission_fee)
        
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def match_orders(self) -> List[Dict[str, Any]]:
        """撮合订单"""
        # 获取待撮合的买卖订单
        buy_query = select(CrossProvinceOrder).where(
            CrossProvinceOrder.status == CrossProvinceOrderStatus.PENDING.value,
            CrossProvinceOrder.order_type == "buy"
        ).order_by(CrossProvinceOrder.price.desc())
        
        sell_query = select(CrossProvinceOrder).where(
            CrossProvinceOrder.status == CrossProvinceOrderStatus.PENDING.value,
            CrossProvinceOrder.order_type == "sell"
        ).order_by(CrossProvinceOrder.price)
        
        buy_result = await self.db.execute(buy_query)
        sell_result = await self.db.execute(sell_query)
        
        buy_orders = list(buy_result.scalars().all())
        sell_orders = list(sell_result.scalars().all())
        
        matches = []
        
        for buy in buy_orders:
            for sell in sell_orders:
                # 检查省份匹配
                if buy.source_province != sell.target_province:
                    continue
                if buy.target_province != sell.source_province:
                    continue
                
                # 检查价格
                if buy.total_price >= sell.total_price:
                    # 撮合
                    match_qty = min(
                        buy.quantity - buy.filled_quantity,
                        sell.quantity - sell.filled_quantity
                    )
                    
                    if match_qty > 0:
                        await self._execute_match(buy, sell, match_qty)
                        matches.append({
                            "buy_order_id": buy.order_id,
                            "sell_order_id": sell.order_id,
                            "quantity": match_qty,
                            "price": (buy.total_price + sell.total_price) / 2
                        })
        
        logger.info(f"跨省撮合完成: {len(matches)} 笔成交")
        return matches
    
    async def _execute_match(
        self,
        buy_order: CrossProvinceOrder,
        sell_order: CrossProvinceOrder,
        quantity: float
    ):
        """执行撮合"""
        buy_order.filled_quantity += quantity
        sell_order.filled_quantity += quantity
        
        buy_order.matched_order_id = sell_order.order_id
        sell_order.matched_order_id = buy_order.order_id
        buy_order.match_time = datetime.now()
        sell_order.match_time = datetime.now()
        
        # 更新状态
        for order in [buy_order, sell_order]:
            if order.filled_quantity >= order.quantity:
                order.status = CrossProvinceOrderStatus.COMPLETED.value
            else:
                order.status = CrossProvinceOrderStatus.PARTIAL.value
        
        await self.db.commit()
    
    async def get_order(self, order_id: str) -> Optional[CrossProvinceOrder]:
        """获取订单"""
        query = select(CrossProvinceOrder).where(
            CrossProvinceOrder.order_id == order_id
        )
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_user_orders(
        self,
        user_id: str,
        status: str = None
    ) -> List[CrossProvinceOrder]:
        """获取用户订单"""
        query = select(CrossProvinceOrder).where(
            CrossProvinceOrder.user_id == user_id
        )
        if status:
            query = query.where(CrossProvinceOrder.status == status)
        query = query.order_by(CrossProvinceOrder.created_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        order = await self.get_order(order_id)
        if not order:
            return False
        
        if order.status not in [
            CrossProvinceOrderStatus.PENDING.value,
            CrossProvinceOrderStatus.MATCHING.value
        ]:
            return False
        
        order.status = CrossProvinceOrderStatus.CANCELLED.value
        await self.db.commit()
        
        logger.info(f"取消跨省订单: {order_id}")
        return True
    
    async def get_available_channels(
        self,
        from_province: str = None,
        to_province: str = None
    ) -> List[TransmissionChannel]:
        """获取可用通道"""
        query = select(TransmissionChannel).where(
            TransmissionChannel.is_active == True
        )
        
        if from_province:
            query = query.where(TransmissionChannel.from_province == from_province)
        if to_province:
            query = query.where(TransmissionChannel.to_province == to_province)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())


def get_cross_province_service(db: AsyncSession) -> CrossProvinceService:
    """获取跨省交易服务"""
    return CrossProvinceService(db)
