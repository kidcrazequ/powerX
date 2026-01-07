"""
PowerX 条件单服务

创建日期: 2026-01-07
作者: zhi.qu

提供条件单的创建、监控和触发功能
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

from app.models.conditional_order import (
    ConditionalOrder, TriggerLog, ConditionType, ConditionStatus
)
from app.services.market_service import market_service


class ConditionalOrderService:
    """条件单服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_order(
        self,
        user_id: str,
        condition_type: str,
        province: str,
        order_direction: str,
        order_quantity: float,
        trigger_price: Optional[float] = None,
        trigger_change_pct: Optional[float] = None,
        trigger_time: Optional[datetime] = None,
        trigger_volume: Optional[float] = None,
        condition_params: Optional[Dict[str, Any]] = None,
        order_price_type: str = "MARKET",
        order_limit_price: Optional[float] = None,
        market_type: str = "DAY_AHEAD",
        name: Optional[str] = None,
        valid_until: Optional[datetime] = None
    ) -> ConditionalOrder:
        """
        创建条件单
        
        Args:
            user_id: 用户ID
            condition_type: 条件类型
            province: 省份
            order_direction: 订单方向 (BUY/SELL)
            order_quantity: 交易数量
            trigger_price: 触发价格
            trigger_change_pct: 触发变动百分比
            trigger_time: 触发时间
            trigger_volume: 触发交易量
            condition_params: 其他条件参数
            order_price_type: 订单价格类型 (MARKET/LIMIT)
            order_limit_price: 限价单价格
            market_type: 市场类型
            name: 条件单名称
            valid_until: 有效期截止时间
            
        Returns:
            创建的条件单
        """
        order = ConditionalOrder(
            user_id=user_id,
            name=name or f"{province}{condition_type}条件单",
            condition_type=condition_type,
            province=province,
            market_type=market_type,
            trigger_price=trigger_price,
            trigger_change_pct=trigger_change_pct,
            trigger_time=trigger_time,
            trigger_volume=trigger_volume,
            condition_params=condition_params,
            order_direction=order_direction,
            order_quantity=order_quantity,
            order_price_type=order_price_type,
            order_limit_price=order_limit_price,
            valid_until=valid_until or datetime.now() + timedelta(days=7),
            status=ConditionStatus.PENDING.value
        )
        
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        
        logger.info(f"创建条件单: ID={order.id}, 类型={condition_type}, 省份={province}")
        return order
    
    async def get_user_orders(
        self,
        user_id: str,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[ConditionalOrder]:
        """获取用户的条件单列表"""
        query = select(ConditionalOrder).where(
            ConditionalOrder.user_id == user_id
        )
        
        if status:
            query = query.where(ConditionalOrder.status == status)
        
        query = query.order_by(desc(ConditionalOrder.created_at)).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_order_by_id(self, order_id: int) -> Optional[ConditionalOrder]:
        """根据ID获取条件单"""
        return await self.db.get(ConditionalOrder, order_id)
    
    async def cancel_order(self, order_id: int, user_id: str) -> bool:
        """取消条件单"""
        order = await self.get_order_by_id(order_id)
        
        if not order:
            return False
        
        if order.user_id != user_id:
            raise PermissionError("无权操作此条件单")
        
        if order.status != ConditionStatus.PENDING.value:
            raise ValueError(f"条件单状态为 {order.status}，无法取消")
        
        order.status = ConditionStatus.CANCELLED.value
        order.updated_at = datetime.now()
        
        await self.db.commit()
        logger.info(f"取消条件单: ID={order_id}")
        return True
    
    async def get_pending_orders(self) -> List[ConditionalOrder]:
        """获取所有待触发的条件单"""
        query = select(ConditionalOrder).where(
            and_(
                ConditionalOrder.status == ConditionStatus.PENDING.value,
                ConditionalOrder.is_enabled == True
            )
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def check_and_trigger(self, market_data: Dict[str, Any]) -> List[ConditionalOrder]:
        """
        检查市场数据并触发满足条件的条件单
        
        Args:
            market_data: 市场数据 {"province": str, "price": float, "volume": float, ...}
            
        Returns:
            被触发的条件单列表
        """
        province = market_data.get("province")
        current_price = market_data.get("price")
        current_volume = market_data.get("volume")
        
        pending_orders = await self.get_pending_orders()
        triggered_orders = []
        
        for order in pending_orders:
            # 检查省份匹配
            if order.province != province:
                continue
            
            # 检查是否过期
            if order.is_expired():
                order.status = ConditionStatus.EXPIRED.value
                await self.db.commit()
                continue
            
            # 检查触发条件
            should_trigger = False
            trigger_reason = ""
            
            if order.condition_type == ConditionType.PRICE_ABOVE.value:
                if current_price and order.trigger_price and current_price > order.trigger_price:
                    should_trigger = True
                    trigger_reason = f"价格 {current_price} > 触发价 {order.trigger_price}"
                    
            elif order.condition_type == ConditionType.PRICE_BELOW.value:
                if current_price and order.trigger_price and current_price < order.trigger_price:
                    should_trigger = True
                    trigger_reason = f"价格 {current_price} < 触发价 {order.trigger_price}"
                    
            elif order.condition_type == ConditionType.TIME_TRIGGER.value:
                if order.trigger_time and datetime.now() >= order.trigger_time:
                    should_trigger = True
                    trigger_reason = f"到达触发时间 {order.trigger_time}"
                    
            elif order.condition_type == ConditionType.VOLUME_ABOVE.value:
                if current_volume and order.trigger_volume and current_volume > order.trigger_volume:
                    should_trigger = True
                    trigger_reason = f"成交量 {current_volume} > 触发量 {order.trigger_volume}"
            
            if should_trigger:
                # 触发条件单
                order.status = ConditionStatus.TRIGGERED.value
                order.triggered_at = datetime.now()
                order.triggered_price = current_price
                
                # 记录触发日志
                trigger_log = TriggerLog(
                    conditional_order_id=order.id,
                    trigger_reason=trigger_reason,
                    market_price=current_price,
                    market_data=market_data
                )
                self.db.add(trigger_log)
                
                triggered_orders.append(order)
                logger.info(f"触发条件单: ID={order.id}, 原因={trigger_reason}")
        
        if triggered_orders:
            await self.db.commit()
        
        return triggered_orders
    
    async def execute_triggered_order(self, order: ConditionalOrder) -> Dict[str, Any]:
        """
        执行已触发的条件单
        
        Args:
            order: 条件单
            
        Returns:
            执行结果
        """
        if order.status != ConditionStatus.TRIGGERED.value:
            raise ValueError(f"条件单状态为 {order.status}，无法执行")
        
        try:
            # 这里应该调用实际的交易服务下单
            # 目前使用模拟结果
            execution_result = {
                "order_id": f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{order.id}",
                "direction": order.order_direction,
                "quantity": order.order_quantity,
                "price": order.triggered_price or order.order_limit_price,
                "status": "SUBMITTED",
                "executed_at": datetime.now().isoformat()
            }
            
            order.status = ConditionStatus.EXECUTED.value
            order.executed_at = datetime.now()
            order.executed_order_id = execution_result["order_id"]
            order.execution_result = execution_result
            
            # 更新触发日志
            query = select(TriggerLog).where(
                TriggerLog.conditional_order_id == order.id
            ).order_by(desc(TriggerLog.trigger_time)).limit(1)
            
            result = await self.db.execute(query)
            trigger_log = result.scalars().first()
            if trigger_log:
                trigger_log.success = True
                trigger_log.order_id = execution_result["order_id"]
            
            await self.db.commit()
            
            logger.info(f"执行条件单成功: ID={order.id}, 订单号={execution_result['order_id']}")
            return execution_result
            
        except Exception as e:
            order.status = ConditionStatus.FAILED.value
            order.error_message = str(e)
            
            await self.db.commit()
            
            logger.error(f"执行条件单失败: ID={order.id}, 错误={e}")
            raise
    
    async def get_trigger_logs(self, order_id: int) -> List[TriggerLog]:
        """获取条件单的触发日志"""
        query = select(TriggerLog).where(
            TriggerLog.conditional_order_id == order_id
        ).order_by(desc(TriggerLog.trigger_time))
        
        result = await self.db.execute(query)
        return result.scalars().all()


# 单例实例
def get_conditional_order_service(db: AsyncSession) -> ConditionalOrderService:
    return ConditionalOrderService(db)
