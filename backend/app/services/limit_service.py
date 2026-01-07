"""
PowerX 交易限额服务

创建日期: 2026-01-07
作者: zhi.qu

提供交易限额检查和管理功能
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from loguru import logger

from app.models.trading_limit import TradingLimit, LimitViolation, DailyUsage, LimitType


class LimitCheckResult:
    """限额检查结果"""
    
    def __init__(self, passed: bool, limit_type: Optional[str] = None,
                 limit_value: Optional[float] = None, current_usage: Optional[float] = None,
                 attempted_value: Optional[float] = None, message: str = ""):
        self.passed = passed
        self.limit_type = limit_type
        self.limit_value = limit_value
        self.current_usage = current_usage
        self.attempted_value = attempted_value
        self.message = message
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed, "limit_type": self.limit_type,
            "limit_value": self.limit_value, "current_usage": self.current_usage,
            "attempted_value": self.attempted_value, "message": self.message
        }


class LimitService:
    """限额服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_limit(self, limit_type: str, limit_value: float,
                          user_id: Optional[str] = None, province: Optional[str] = None,
                          market_type: Optional[str] = None, direction: Optional[str] = None,
                          name: Optional[str] = None, description: Optional[str] = None,
                          created_by: Optional[str] = None) -> TradingLimit:
        """创建交易限额"""
        limit = TradingLimit(
            user_id=user_id, limit_type=limit_type, limit_value=limit_value,
            province=province, market_type=market_type, direction=direction,
            name=name or f"{limit_type}限额", description=description, created_by=created_by
        )
        self.db.add(limit)
        await self.db.commit()
        await self.db.refresh(limit)
        logger.info(f"创建交易限额: ID={limit.id}, 类型={limit_type}, 值={limit_value}")
        return limit
    
    async def get_applicable_limits(self, user_id: str, province: Optional[str] = None,
                                    market_type: Optional[str] = None,
                                    direction: Optional[str] = None) -> List[TradingLimit]:
        """获取适用的限额配置"""
        query = select(TradingLimit).where(
            and_(TradingLimit.is_enabled == True,
                 or_(TradingLimit.user_id == user_id, TradingLimit.user_id == None)))
        result = await self.db.execute(query)
        all_limits = result.scalars().all()
        applicable = []
        for limit in all_limits:
            if limit.province and province and limit.province != province:
                continue
            if limit.market_type and market_type and limit.market_type != market_type:
                continue
            if limit.direction and direction and limit.direction != direction:
                continue
            applicable.append(limit)
        return applicable
    
    async def get_daily_usage(self, user_id: str, target_date: Optional[str] = None) -> Optional[DailyUsage]:
        """获取每日使用量"""
        if target_date is None:
            target_date = date.today().isoformat()
        query = select(DailyUsage).where(and_(DailyUsage.user_id == user_id, DailyUsage.date == target_date))
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def check_limit(self, user_id: str, direction: str, quantity: float, price: float,
                         province: Optional[str] = None, market_type: Optional[str] = None) -> LimitCheckResult:
        """检查交易是否超过限额"""
        amount = quantity * price
        limits = await self.get_applicable_limits(user_id, province, market_type, direction)
        usage = await self.get_daily_usage(user_id)
        
        for limit in limits:
            result = self._check_single_limit(limit, direction, quantity, amount, usage)
            if not result.passed:
                await self._record_violation(user_id, limit, result.attempted_value,
                    result.current_usage, {"direction": direction, "quantity": quantity, "price": price})
                return result
        return LimitCheckResult(passed=True, message="通过所有限额检查")
    
    def _check_single_limit(self, limit: TradingLimit, direction: str, quantity: float,
                           amount: float, usage: Optional[DailyUsage]) -> LimitCheckResult:
        """检查单个限额"""
        if limit.limit_type == LimitType.SINGLE_QUANTITY.value:
            if quantity > limit.limit_value:
                return LimitCheckResult(False, limit.limit_type, limit.limit_value, 
                    attempted_value=quantity, message=f"单笔数量{quantity}超过限额{limit.limit_value}")
        elif limit.limit_type == LimitType.SINGLE_AMOUNT.value:
            if amount > limit.limit_value:
                return LimitCheckResult(False, limit.limit_type, limit.limit_value,
                    attempted_value=amount, message=f"单笔金额{amount:.2f}超过限额{limit.limit_value:.2f}")
        elif limit.limit_type == LimitType.DAILY_QUANTITY.value:
            current = (usage.total_buy_quantity + usage.total_sell_quantity) if usage else 0
            if current + quantity > limit.limit_value:
                return LimitCheckResult(False, limit.limit_type, limit.limit_value, current,
                    quantity, f"日交易量{current}+{quantity}将超限额{limit.limit_value}")
        elif limit.limit_type == LimitType.DAILY_AMOUNT.value:
            current = (usage.total_buy_amount + usage.total_sell_amount) if usage else 0
            if current + amount > limit.limit_value:
                return LimitCheckResult(False, limit.limit_type, limit.limit_value, current,
                    amount, f"日交易额{current:.2f}+{amount:.2f}将超限额{limit.limit_value:.2f}")
        return LimitCheckResult(passed=True)
    
    async def _record_violation(self, user_id: str, limit: TradingLimit, attempted_value: float,
                               current_usage: Optional[float], order_data: Dict[str, Any]):
        """记录违规"""
        violation = LimitViolation(user_id=user_id, limit_id=limit.id, attempted_value=attempted_value,
            limit_value=limit.limit_value, current_usage=current_usage, order_data=order_data)
        self.db.add(violation)
        await self.db.commit()
        logger.warning(f"限额违规: 用户={user_id}, 限额ID={limit.id}")
    
    async def get_violations(self, user_id: Optional[str] = None, limit: int = 50,
                            include_resolved: bool = False) -> List[LimitViolation]:
        """获取违规记录"""
        query = select(LimitViolation)
        if user_id:
            query = query.where(LimitViolation.user_id == user_id)
        if not include_resolved:
            query = query.where(LimitViolation.is_resolved == False)
        query = query.order_by(LimitViolation.violation_time.desc()).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_all_limits(self, user_id: Optional[str] = None) -> List[TradingLimit]:
        """获取所有限额配置"""
        query = select(TradingLimit)
        if user_id:
            query = query.where(or_(TradingLimit.user_id == user_id, TradingLimit.user_id == None))
        result = await self.db.execute(query.order_by(TradingLimit.created_at.desc()))
        return result.scalars().all()
    
    async def update_limit(self, limit_id: int, limit_value: Optional[float] = None,
                          is_enabled: Optional[bool] = None) -> Optional[TradingLimit]:
        """更新限额"""
        limit = await self.db.get(TradingLimit, limit_id)
        if not limit:
            return None
        if limit_value is not None:
            limit.limit_value = limit_value
        if is_enabled is not None:
            limit.is_enabled = is_enabled
        await self.db.commit()
        await self.db.refresh(limit)
        return limit
    
    async def delete_limit(self, limit_id: int) -> bool:
        """删除限额"""
        limit = await self.db.get(TradingLimit, limit_id)
        if not limit:
            return False
        await self.db.delete(limit)
        await self.db.commit()
        return True


def get_limit_service(db: AsyncSession) -> LimitService:
    return LimitService(db)
