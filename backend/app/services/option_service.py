"""
PowerX 期权交易服务
创建日期: 2026-01-07
作者: zhi.qu
"""
import uuid
import math
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from loguru import logger

from app.models.option_contract import (
    OptionContract, OptionOrder, OptionPosition,
    OptionType, OptionStyle, OptionOrderStatus
)


class OptionService:
    """期权交易服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_contract(
        self,
        name: str,
        underlying: str,
        option_type: str,
        option_style: str,
        strike_price: float,
        expiration_date: datetime,
        contract_size: float = 1,
        premium: float = None
    ) -> OptionContract:
        """创建期权合约"""
        contract_id = f"OPT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        contract = OptionContract(
            contract_id=contract_id,
            name=name,
            underlying=underlying,
            option_type=option_type,
            option_style=option_style,
            strike_price=strike_price,
            expiration_date=expiration_date,
            contract_size=contract_size,
            premium=premium or self._calculate_premium(
                option_type, strike_price, expiration_date
            ),
            is_active=True
        )
        
        self.db.add(contract)
        await self.db.commit()
        await self.db.refresh(contract)
        
        logger.info(f"创建期权合约: {contract_id}")
        return contract
    
    def _calculate_premium(
        self,
        option_type: str,
        strike_price: float,
        expiration_date: datetime,
        spot_price: float = None,
        volatility: float = 0.2,
        risk_free_rate: float = 0.03
    ) -> float:
        """使用 Black-Scholes 模型计算权利金（简化版）"""
        spot_price = spot_price or strike_price * 1.02
        
        days_to_expiry = (expiration_date - datetime.now()).days
        t = days_to_expiry / 365
        
        if t <= 0:
            return 0
        
        # 简化计算
        d1 = (math.log(spot_price / strike_price) + 
              (risk_free_rate + 0.5 * volatility ** 2) * t) / (volatility * math.sqrt(t))
        
        # 简化的期权价格
        if option_type == OptionType.CALL.value:
            premium = max(0, spot_price - strike_price) + 5 * math.sqrt(t)
        else:
            premium = max(0, strike_price - spot_price) + 5 * math.sqrt(t)
        
        return round(premium, 2)
    
    async def list_contracts(
        self,
        underlying: str = None,
        option_type: str = None,
        active_only: bool = True
    ) -> List[OptionContract]:
        """获取期权合约列表"""
        query = select(OptionContract)
        
        if active_only:
            query = query.where(OptionContract.is_active == True)
        if underlying:
            query = query.where(OptionContract.underlying == underlying)
        if option_type:
            query = query.where(OptionContract.option_type == option_type)
        
        query = query.order_by(OptionContract.expiration_date)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_contract(self, contract_id: str) -> Optional[OptionContract]:
        """获取合约详情"""
        query = select(OptionContract).where(
            OptionContract.contract_id == contract_id
        )
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def place_order(
        self,
        user_id: str,
        contract_id: str,
        side: str,
        position_effect: str,
        quantity: float,
        price: float = None
    ) -> OptionOrder:
        """下单"""
        order_id = f"OPO-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        contract = await self.get_contract(contract_id)
        if not contract:
            raise ValueError("合约不存在")
        
        if price is None:
            price = contract.premium
        
        total_premium = price * quantity * contract.contract_size
        
        order = OptionOrder(
            order_id=order_id,
            user_id=user_id,
            contract_id=contract_id,
            side=side,
            position_effect=position_effect,
            quantity=quantity,
            price=price,
            total_premium=total_premium,
            status=OptionOrderStatus.PENDING.value
        )
        
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        
        # 自动成交（模拟）
        await self._execute_order(order)
        
        logger.info(f"期权订单: {order_id}, {side} {quantity} @ {price}")
        return order
    
    async def _execute_order(self, order: OptionOrder):
        """执行订单"""
        order.filled_quantity = order.quantity
        order.status = OptionOrderStatus.OPEN.value
        
        # 更新持仓
        await self._update_position(order)
        await self.db.commit()
    
    async def _update_position(self, order: OptionOrder):
        """更新持仓"""
        query = select(OptionPosition).where(
            and_(
                OptionPosition.user_id == order.user_id,
                OptionPosition.contract_id == order.contract_id
            )
        )
        result = await self.db.execute(query)
        position = result.scalars().first()
        
        if order.position_effect == "open":
            # 开仓
            if order.side == "buy":
                side = "long"
            else:
                side = "short"
            
            if position:
                # 更新现有持仓
                old_value = position.quantity * position.avg_price
                new_value = order.quantity * order.price
                position.quantity += order.quantity
                position.avg_price = (old_value + new_value) / position.quantity
            else:
                # 创建新持仓
                position = OptionPosition(
                    user_id=order.user_id,
                    contract_id=order.contract_id,
                    side=side,
                    quantity=order.quantity,
                    avg_price=order.price
                )
                self.db.add(position)
        
        elif order.position_effect == "close" and position:
            # 平仓
            position.quantity -= order.quantity
            if position.quantity <= 0:
                await self.db.delete(position)
    
    async def get_positions(self, user_id: str) -> List[OptionPosition]:
        """获取用户持仓"""
        query = select(OptionPosition).where(
            OptionPosition.user_id == user_id
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def exercise_option(
        self,
        order_id: str,
        settlement_price: float
    ) -> Dict[str, Any]:
        """行权"""
        query = select(OptionOrder).where(OptionOrder.order_id == order_id)
        result = await self.db.execute(query)
        order = result.scalars().first()
        
        if not order:
            raise ValueError("订单不存在")
        
        contract = await self.get_contract(order.contract_id)
        
        # 计算盈亏
        if contract.option_type == OptionType.CALL.value:
            intrinsic_value = max(0, settlement_price - contract.strike_price)
        else:
            intrinsic_value = max(0, contract.strike_price - settlement_price)
        
        if order.side == "buy":
            profit_loss = (intrinsic_value - order.price) * order.quantity * contract.contract_size
        else:
            profit_loss = (order.price - intrinsic_value) * order.quantity * contract.contract_size
        
        order.status = OptionOrderStatus.EXERCISED.value
        order.exercise_date = datetime.now()
        order.settlement_price = settlement_price
        order.profit_loss = profit_loss
        
        await self.db.commit()
        
        logger.info(f"行权: {order_id}, 盈亏: {profit_loss}")
        
        return {
            "order_id": order_id,
            "settlement_price": settlement_price,
            "intrinsic_value": intrinsic_value,
            "profit_loss": profit_loss
        }


def get_option_service(db: AsyncSession) -> OptionService:
    """获取期权服务"""
    return OptionService(db)
