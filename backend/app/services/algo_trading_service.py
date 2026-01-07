"""
PowerX 算法交易服务
创建日期: 2026-01-07
作者: zhi.qu

支持 TWAP, VWAP, 冰山订单等算法交易策略
"""
import uuid
import math
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.models.algo_order import AlgoOrder, AlgoSlice, AlgoType, AlgoOrderStatus
from app.services.queue_service import get_queue_service


class AlgoTradingService:
    """算法交易服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_twap_order(
        self,
        user_id: str,
        order_type: str,
        target_quantity: float,
        duration_minutes: int,
        slice_count: int = None,
        price_limit_upper: float = None,
        price_limit_lower: float = None,
        province: str = "guangdong",
        market_type: str = "spot"
    ) -> AlgoOrder:
        """
        创建 TWAP 订单
        时间加权平均价格 - 在指定时间内均匀分配订单
        """
        algo_id = f"TWAP-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        # 默认切片数
        if slice_count is None:
            slice_count = min(duration_minutes, 20)  # 最多20个切片
        
        now = datetime.now()
        end_time = now + timedelta(minutes=duration_minutes)
        
        order = AlgoOrder(
            algo_id=algo_id,
            user_id=user_id,
            algo_type=AlgoType.TWAP.value,
            algo_params={
                "duration_minutes": duration_minutes,
                "slice_count": slice_count
            },
            province=province,
            market_type=market_type,
            order_type=order_type,
            target_quantity=target_quantity,
            price_limit_upper=price_limit_upper,
            price_limit_lower=price_limit_lower,
            start_time=now,
            end_time=end_time,
            status=AlgoOrderStatus.CREATED.value,
            slices_total=slice_count
        )
        
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        
        # 创建切片
        await self._create_twap_slices(order.id, algo_id, target_quantity, now, duration_minutes, slice_count)
        
        logger.info(f"创建 TWAP 订单: {algo_id}, 目标 {target_quantity} MWh, {slice_count} 切片")
        return order
    
    async def create_vwap_order(
        self,
        user_id: str,
        order_type: str,
        target_quantity: float,
        duration_minutes: int,
        volume_profile: List[float] = None,
        price_limit_upper: float = None,
        price_limit_lower: float = None,
        province: str = "guangdong",
        market_type: str = "spot"
    ) -> AlgoOrder:
        """
        创建 VWAP 订单
        成交量加权平均价格 - 根据历史成交量分布分配订单
        """
        algo_id = f"VWAP-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        # 默认成交量分布 (模拟早高峰、午间平稳、晚高峰)
        if volume_profile is None:
            volume_profile = [0.15, 0.10, 0.08, 0.12, 0.10, 0.10, 0.08, 0.12, 0.15]
        
        # 归一化
        total = sum(volume_profile)
        volume_profile = [v / total for v in volume_profile]
        
        now = datetime.now()
        end_time = now + timedelta(minutes=duration_minutes)
        
        order = AlgoOrder(
            algo_id=algo_id,
            user_id=user_id,
            algo_type=AlgoType.VWAP.value,
            algo_params={
                "duration_minutes": duration_minutes,
                "volume_profile": volume_profile
            },
            province=province,
            market_type=market_type,
            order_type=order_type,
            target_quantity=target_quantity,
            price_limit_upper=price_limit_upper,
            price_limit_lower=price_limit_lower,
            start_time=now,
            end_time=end_time,
            status=AlgoOrderStatus.CREATED.value,
            slices_total=len(volume_profile)
        )
        
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        
        # 创建切片
        await self._create_vwap_slices(order.id, algo_id, target_quantity, now, duration_minutes, volume_profile)
        
        logger.info(f"创建 VWAP 订单: {algo_id}, 目标 {target_quantity} MWh")
        return order
    
    async def create_iceberg_order(
        self,
        user_id: str,
        order_type: str,
        target_quantity: float,
        visible_quantity: float,
        price: float,
        province: str = "guangdong",
        market_type: str = "spot"
    ) -> AlgoOrder:
        """
        创建冰山订单
        只显示部分订单量，成交后自动补充
        """
        algo_id = f"ICE-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        slice_count = math.ceil(target_quantity / visible_quantity)
        
        order = AlgoOrder(
            algo_id=algo_id,
            user_id=user_id,
            algo_type=AlgoType.ICEBERG.value,
            algo_params={
                "visible_quantity": visible_quantity
            },
            province=province,
            market_type=market_type,
            order_type=order_type,
            target_quantity=target_quantity,
            target_price=price,
            status=AlgoOrderStatus.CREATED.value,
            slices_total=slice_count
        )
        
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        
        # 创建切片
        remaining = target_quantity
        for i in range(slice_count):
            qty = min(visible_quantity, remaining)
            slice_obj = AlgoSlice(
                algo_order_id=order.id,
                slice_id=f"{algo_id}-{i+1:03d}",
                sequence=i + 1,
                quantity=qty,
                price=price
            )
            self.db.add(slice_obj)
            remaining -= qty
        
        await self.db.commit()
        
        logger.info(f"创建冰山订单: {algo_id}, 目标 {target_quantity} MWh, 显示 {visible_quantity} MWh")
        return order
    
    async def _create_twap_slices(
        self,
        order_id: int,
        algo_id: str,
        total_quantity: float,
        start_time: datetime,
        duration_minutes: int,
        slice_count: int
    ):
        """创建 TWAP 切片"""
        quantity_per_slice = total_quantity / slice_count
        interval = timedelta(minutes=duration_minutes / slice_count)
        
        for i in range(slice_count):
            scheduled_time = start_time + interval * i
            slice_obj = AlgoSlice(
                algo_order_id=order_id,
                slice_id=f"{algo_id}-{i+1:03d}",
                sequence=i + 1,
                scheduled_time=scheduled_time,
                quantity=quantity_per_slice
            )
            self.db.add(slice_obj)
        
        await self.db.commit()
    
    async def _create_vwap_slices(
        self,
        order_id: int,
        algo_id: str,
        total_quantity: float,
        start_time: datetime,
        duration_minutes: int,
        volume_profile: List[float]
    ):
        """创建 VWAP 切片"""
        slice_count = len(volume_profile)
        interval = timedelta(minutes=duration_minutes / slice_count)
        
        for i, ratio in enumerate(volume_profile):
            scheduled_time = start_time + interval * i
            quantity = total_quantity * ratio
            slice_obj = AlgoSlice(
                algo_order_id=order_id,
                slice_id=f"{algo_id}-{i+1:03d}",
                sequence=i + 1,
                scheduled_time=scheduled_time,
                quantity=quantity
            )
            self.db.add(slice_obj)
        
        await self.db.commit()
    
    async def start_algo_order(self, algo_id: str) -> AlgoOrder:
        """启动算法订单"""
        order = await self.get_algo_order(algo_id)
        if not order:
            raise ValueError(f"算法订单不存在: {algo_id}")
        
        if order.status not in [AlgoOrderStatus.CREATED.value, AlgoOrderStatus.PAUSED.value]:
            raise ValueError(f"订单状态不允许启动: {order.status}")
        
        order.status = AlgoOrderStatus.RUNNING.value
        await self.db.commit()
        
        # 发送到队列执行
        queue_service = get_queue_service()
        await queue_service.publish_order_execution(
            algo_id,
            {
                "type": "algo_order",
                "algo_id": algo_id,
                "algo_type": order.algo_type
            }
        )
        
        logger.info(f"启动算法订单: {algo_id}")
        return order
    
    async def pause_algo_order(self, algo_id: str) -> AlgoOrder:
        """暂停算法订单"""
        order = await self.get_algo_order(algo_id)
        if not order:
            raise ValueError(f"算法订单不存在: {algo_id}")
        
        if order.status != AlgoOrderStatus.RUNNING.value:
            raise ValueError(f"订单状态不允许暂停: {order.status}")
        
        order.status = AlgoOrderStatus.PAUSED.value
        await self.db.commit()
        
        logger.info(f"暂停算法订单: {algo_id}")
        return order
    
    async def cancel_algo_order(self, algo_id: str) -> AlgoOrder:
        """取消算法订单"""
        order = await self.get_algo_order(algo_id)
        if not order:
            raise ValueError(f"算法订单不存在: {algo_id}")
        
        if order.status in [AlgoOrderStatus.COMPLETED.value, AlgoOrderStatus.CANCELLED.value]:
            raise ValueError(f"订单无法取消: {order.status}")
        
        order.status = AlgoOrderStatus.CANCELLED.value
        order.completed_at = datetime.now()
        await self.db.commit()
        
        logger.info(f"取消算法订单: {algo_id}")
        return order
    
    async def get_algo_order(self, algo_id: str) -> Optional[AlgoOrder]:
        """获取算法订单"""
        query = select(AlgoOrder).where(AlgoOrder.algo_id == algo_id)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_user_algo_orders(self, user_id: str, status: str = None) -> List[AlgoOrder]:
        """获取用户的算法订单"""
        query = select(AlgoOrder).where(AlgoOrder.user_id == user_id)
        if status:
            query = query.where(AlgoOrder.status == status)
        query = query.order_by(AlgoOrder.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_order_slices(self, algo_id: str) -> List[AlgoSlice]:
        """获取订单切片"""
        order = await self.get_algo_order(algo_id)
        if not order:
            return []
        
        query = select(AlgoSlice).where(
            AlgoSlice.algo_order_id == order.id
        ).order_by(AlgoSlice.sequence)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_slice_status(
        self,
        slice_id: str,
        status: str,
        filled_quantity: float = None,
        filled_price: float = None
    ):
        """更新切片状态"""
        query = select(AlgoSlice).where(AlgoSlice.slice_id == slice_id)
        result = await self.db.execute(query)
        slice_obj = result.scalars().first()
        
        if not slice_obj:
            return
        
        slice_obj.status = status
        if filled_quantity is not None:
            slice_obj.filled_quantity = filled_quantity
        if filled_price is not None:
            slice_obj.filled_price = filled_price
        if status == "filled":
            slice_obj.executed_at = datetime.now()
        
        await self.db.commit()
        
        # 更新主订单状态
        await self._update_algo_order_status(slice_obj.algo_order_id)
    
    async def _update_algo_order_status(self, order_id: int):
        """更新算法订单状态"""
        query = select(AlgoOrder).where(AlgoOrder.id == order_id)
        result = await self.db.execute(query)
        order = result.scalars().first()
        
        if not order:
            return
        
        # 获取切片统计
        slices_query = select(AlgoSlice).where(AlgoSlice.algo_order_id == order_id)
        slices_result = await self.db.execute(slices_query)
        slices = slices_result.scalars().all()
        
        filled_count = sum(1 for s in slices if s.status == "filled")
        total_filled = sum(s.filled_quantity or 0 for s in slices)
        
        # 计算平均价格
        total_value = sum((s.filled_quantity or 0) * (s.filled_price or 0) for s in slices)
        avg_price = total_value / total_filled if total_filled > 0 else None
        
        order.slices_filled = filled_count
        order.filled_quantity = total_filled
        order.avg_price = avg_price
        
        if filled_count == order.slices_total:
            order.status = AlgoOrderStatus.COMPLETED.value
            order.completed_at = datetime.now()
        
        await self.db.commit()


def get_algo_trading_service(db: AsyncSession) -> AlgoTradingService:
    """获取算法交易服务"""
    return AlgoTradingService(db)
