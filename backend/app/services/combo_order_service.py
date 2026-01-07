"""
PowerX 组合订单服务
创建日期: 2026-01-07
作者: zhi.qu
"""
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from loguru import logger

from app.models.combo_order import (
    ComboOrder, ComboOrderItem, 
    ComboOrderStatus, ComboExecutionStrategy
)
from app.services.queue_service import get_queue_service


class ComboOrderService:
    """组合订单服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_combo(
        self, 
        user_id: str, 
        name: str,
        items: List[Dict[str, Any]],
        execution_strategy: str = ComboExecutionStrategy.ALL_OR_NONE.value,
        description: str = None
    ) -> ComboOrder:
        """创建组合订单"""
        combo_id = f"CMB-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        combo = ComboOrder(
            combo_id=combo_id,
            user_id=user_id,
            name=name,
            description=description,
            execution_strategy=execution_strategy,
            status=ComboOrderStatus.DRAFT.value,
            total_orders=len(items)
        )
        
        total_quantity = 0
        total_amount = 0
        
        for idx, item_data in enumerate(items):
            item = ComboOrderItem(
                order_id=f"{combo_id}-{idx+1:03d}",
                province=item_data.get("province", "guangdong"),
                market_type=item_data.get("market_type", "spot"),
                order_type=item_data["order_type"],
                quantity=item_data["quantity"],
                price=item_data.get("price"),
                priority=item_data.get("priority", idx)
            )
            combo.items.append(item)
            total_quantity += item.quantity
            total_amount += (item.quantity * (item.price or 0))
        
        combo.total_quantity = total_quantity
        combo.total_amount = total_amount
        
        self.db.add(combo)
        await self.db.commit()
        await self.db.refresh(combo)
        
        logger.info(f"创建组合订单: {combo_id}, 包含 {len(items)} 个子订单")
        return combo
    
    async def get_combo(self, combo_id: str) -> Optional[ComboOrder]:
        """获取组合订单"""
        query = select(ComboOrder).options(
            selectinload(ComboOrder.items)
        ).where(ComboOrder.combo_id == combo_id)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_user_combos(self, user_id: str, status: str = None) -> List[ComboOrder]:
        """获取用户的组合订单"""
        query = select(ComboOrder).options(
            selectinload(ComboOrder.items)
        ).where(ComboOrder.user_id == user_id)
        
        if status:
            query = query.where(ComboOrder.status == status)
        
        query = query.order_by(ComboOrder.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def submit_combo(self, combo_id: str) -> ComboOrder:
        """提交组合订单"""
        combo = await self.get_combo(combo_id)
        if not combo:
            raise ValueError(f"组合订单不存在: {combo_id}")
        
        if combo.status != ComboOrderStatus.DRAFT.value:
            raise ValueError(f"订单状态不允许提交: {combo.status}")
        
        combo.status = ComboOrderStatus.SUBMITTED.value
        combo.submitted_at = datetime.now()
        
        await self.db.commit()
        
        # 发送到消息队列执行
        queue_service = get_queue_service()
        await queue_service.publish_order_execution(
            combo_id,
            {
                "type": "combo_order",
                "combo_id": combo_id,
                "strategy": combo.execution_strategy,
                "items": [
                    {
                        "order_id": item.order_id,
                        "province": item.province,
                        "market_type": item.market_type,
                        "order_type": item.order_type,
                        "quantity": item.quantity,
                        "price": item.price,
                        "priority": item.priority
                    }
                    for item in sorted(combo.items, key=lambda x: x.priority)
                ]
            }
        )
        
        logger.info(f"提交组合订单: {combo_id}")
        return combo
    
    async def cancel_combo(self, combo_id: str) -> ComboOrder:
        """取消组合订单"""
        combo = await self.get_combo(combo_id)
        if not combo:
            raise ValueError(f"组合订单不存在: {combo_id}")
        
        if combo.status in [ComboOrderStatus.FILLED.value, ComboOrderStatus.CANCELLED.value]:
            raise ValueError(f"订单无法取消: {combo.status}")
        
        combo.status = ComboOrderStatus.CANCELLED.value
        combo.completed_at = datetime.now()
        
        # 取消所有未成交的子订单
        for item in combo.items:
            if item.status not in ["filled", "cancelled"]:
                item.status = "cancelled"
        
        await self.db.commit()
        logger.info(f"取消组合订单: {combo_id}")
        return combo
    
    async def update_item_status(
        self, 
        order_id: str, 
        status: str,
        filled_quantity: float = None,
        filled_price: float = None,
        error_message: str = None
    ) -> ComboOrderItem:
        """更新子订单状态"""
        query = select(ComboOrderItem).where(ComboOrderItem.order_id == order_id)
        result = await self.db.execute(query)
        item = result.scalars().first()
        
        if not item:
            raise ValueError(f"子订单不存在: {order_id}")
        
        item.status = status
        if filled_quantity is not None:
            item.filled_quantity = filled_quantity
        if filled_price is not None:
            item.filled_price = filled_price
        if error_message:
            item.error_message = error_message
        if status == "filled":
            item.executed_at = datetime.now()
        
        await self.db.commit()
        
        # 更新组合订单状态
        await self._update_combo_status(item.combo_order_id)
        
        return item
    
    async def _update_combo_status(self, combo_order_id: int):
        """更新组合订单状态"""
        query = select(ComboOrder).options(
            selectinload(ComboOrder.items)
        ).where(ComboOrder.id == combo_order_id)
        result = await self.db.execute(query)
        combo = result.scalars().first()
        
        if not combo:
            return
        
        filled_count = sum(1 for item in combo.items if item.status == "filled")
        failed_count = sum(1 for item in combo.items if item.status in ["failed", "cancelled"])
        
        combo.filled_orders = filled_count
        
        if filled_count == combo.total_orders:
            combo.status = ComboOrderStatus.FILLED.value
            combo.completed_at = datetime.now()
        elif filled_count > 0:
            combo.status = ComboOrderStatus.PARTIAL.value
        elif failed_count == combo.total_orders:
            combo.status = ComboOrderStatus.FAILED.value
            combo.completed_at = datetime.now()
        
        await self.db.commit()
    
    async def add_item(self, combo_id: str, item_data: Dict[str, Any]) -> ComboOrderItem:
        """添加子订单"""
        combo = await self.get_combo(combo_id)
        if not combo:
            raise ValueError(f"组合订单不存在: {combo_id}")
        
        if combo.status != ComboOrderStatus.DRAFT.value:
            raise ValueError("只能在草稿状态添加子订单")
        
        item = ComboOrderItem(
            combo_order_id=combo.id,
            order_id=f"{combo_id}-{combo.total_orders + 1:03d}",
            province=item_data.get("province", "guangdong"),
            market_type=item_data.get("market_type", "spot"),
            order_type=item_data["order_type"],
            quantity=item_data["quantity"],
            price=item_data.get("price"),
            priority=item_data.get("priority", combo.total_orders)
        )
        
        combo.total_orders += 1
        combo.total_quantity += item.quantity
        combo.total_amount += (item.quantity * (item.price or 0))
        
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        
        return item
    
    async def remove_item(self, combo_id: str, order_id: str) -> bool:
        """移除子订单"""
        combo = await self.get_combo(combo_id)
        if not combo:
            raise ValueError(f"组合订单不存在: {combo_id}")
        
        if combo.status != ComboOrderStatus.DRAFT.value:
            raise ValueError("只能在草稿状态移除子订单")
        
        for item in combo.items:
            if item.order_id == order_id:
                combo.total_orders -= 1
                combo.total_quantity -= item.quantity
                combo.total_amount -= (item.quantity * (item.price or 0))
                await self.db.delete(item)
                await self.db.commit()
                return True
        
        return False


def get_combo_order_service(db: AsyncSession) -> ComboOrderService:
    """获取组合订单服务"""
    return ComboOrderService(db)
