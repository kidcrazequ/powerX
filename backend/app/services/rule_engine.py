"""
PowerX 交易规则引擎

创建日期: 2026-01-07
作者: zhi.qu

提供规则评估、执行和管理功能
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, date
from loguru import logger
import operator
import re

from app.models.trading_rule import TradingRule, RuleExecution, RuleStatus, ActionType


class RuleParser:
    """规则表达式解析器"""
    
    # 支持的操作符
    OPERATORS = {
        ">": operator.gt,
        "<": operator.lt,
        ">=": operator.ge,
        "<=": operator.le,
        "==": operator.eq,
        "!=": operator.ne,
        "contains": lambda a, b: b in a if isinstance(a, (list, str)) else False,
        "in": lambda a, b: a in b if isinstance(b, (list, str)) else False,
    }
    
    @classmethod
    def evaluate_condition(cls, condition: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """
        评估单个条件
        
        Args:
            condition: 条件配置 {"field": "price", "op": ">", "value": 500}
            data: 待评估的数据
            
        Returns:
            条件是否满足
        """
        field = condition.get("field")
        op = condition.get("op")
        value = condition.get("value")
        
        if not field or not op:
            return False
        
        # 获取字段值 (支持嵌套字段，如 "market.price")
        field_value = cls._get_nested_value(data, field)
        
        if field_value is None:
            return False
        
        # 获取操作符函数
        op_func = cls.OPERATORS.get(op)
        if not op_func:
            logger.warning(f"未知操作符: {op}")
            return False
        
        try:
            return op_func(field_value, value)
        except Exception as e:
            logger.error(f"条件评估错误: {e}")
            return False
    
    @classmethod
    def evaluate_expression(cls, expression: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """
        评估复合表达式
        
        Args:
            expression: 表达式配置
                {
                    "operator": "AND",  # AND/OR
                    "conditions": [
                        {"field": "price", "op": ">", "value": 500},
                        {"field": "province", "op": "==", "value": "广东"}
                    ]
                }
            data: 待评估的数据
            
        Returns:
            表达式是否满足
        """
        logic_op = expression.get("operator", "AND").upper()
        conditions = expression.get("conditions", [])
        
        if not conditions:
            return True
        
        results = []
        for cond in conditions:
            # 支持嵌套表达式
            if "operator" in cond:
                result = cls.evaluate_expression(cond, data)
            else:
                result = cls.evaluate_condition(cond, data)
            results.append(result)
        
        if logic_op == "AND":
            return all(results)
        elif logic_op == "OR":
            return any(results)
        else:
            logger.warning(f"未知逻辑操作符: {logic_op}")
            return False
    
    @staticmethod
    def _get_nested_value(data: Dict[str, Any], field: str) -> Any:
        """获取嵌套字段值"""
        keys = field.split(".")
        value = data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
            
            if value is None:
                return None
        
        return value


class RuleEngine:
    """规则引擎"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.parser = RuleParser()
    
    async def create_rule(
        self,
        user_id: str,
        name: str,
        condition_expression: Dict[str, Any],
        action_type: str,
        action_params: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        provinces: Optional[List[str]] = None,
        market_types: Optional[List[str]] = None,
        priority: int = 0,
        max_executions_per_day: int = 10,
        min_interval_seconds: int = 60
    ) -> TradingRule:
        """
        创建交易规则
        
        Args:
            user_id: 用户ID
            name: 规则名称
            condition_expression: 条件表达式
            action_type: 动作类型
            action_params: 动作参数
            description: 规则描述
            provinces: 适用省份
            market_types: 适用市场类型
            priority: 优先级
            max_executions_per_day: 每日最大执行次数
            min_interval_seconds: 最小执行间隔
            
        Returns:
            创建的规则
        """
        rule = TradingRule(
            user_id=user_id,
            name=name,
            description=description,
            condition_expression=condition_expression,
            action_type=action_type,
            action_params=action_params,
            provinces=provinces,
            market_types=market_types,
            priority=priority,
            max_executions_per_day=max_executions_per_day,
            min_interval_seconds=min_interval_seconds,
            status=RuleStatus.INACTIVE.value
        )
        
        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)
        
        logger.info(f"创建交易规则: ID={rule.id}, 名称={name}")
        return rule
    
    async def get_user_rules(
        self,
        user_id: str,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[TradingRule]:
        """获取用户的交易规则列表"""
        query = select(TradingRule).where(
            TradingRule.user_id == user_id
        )
        
        if status:
            query = query.where(TradingRule.status == status)
        
        query = query.order_by(desc(TradingRule.priority), desc(TradingRule.created_at)).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_rule_by_id(self, rule_id: int) -> Optional[TradingRule]:
        """根据ID获取规则"""
        return await self.db.get(TradingRule, rule_id)
    
    async def update_rule_status(self, rule_id: int, status: str) -> Optional[TradingRule]:
        """更新规则状态"""
        rule = await self.get_rule_by_id(rule_id)
        if rule:
            rule.status = status
            rule.updated_at = datetime.now()
            await self.db.commit()
            await self.db.refresh(rule)
            logger.info(f"更新规则状态: ID={rule_id}, 状态={status}")
        return rule
    
    async def delete_rule(self, rule_id: int) -> bool:
        """删除规则"""
        rule = await self.get_rule_by_id(rule_id)
        if rule:
            await self.db.delete(rule)
            await self.db.commit()
            logger.info(f"删除规则: ID={rule_id}")
            return True
        return False
    
    async def get_active_rules(
        self,
        province: Optional[str] = None,
        market_type: Optional[str] = None
    ) -> List[TradingRule]:
        """获取所有激活的规则"""
        query = select(TradingRule).where(
            TradingRule.status == RuleStatus.ACTIVE.value
        )
        
        result = await self.db.execute(query)
        rules = result.scalars().all()
        
        # 过滤省份和市场类型
        filtered_rules = []
        for rule in rules:
            if province and rule.provinces and province not in rule.provinces:
                continue
            if market_type and rule.market_types and market_type not in rule.market_types:
                continue
            filtered_rules.append(rule)
        
        # 按优先级排序
        return sorted(filtered_rules, key=lambda r: r.priority, reverse=True)
    
    async def evaluate_rules(
        self,
        data: Dict[str, Any],
        province: Optional[str] = None,
        market_type: Optional[str] = None
    ) -> List[TradingRule]:
        """
        评估所有激活的规则
        
        Args:
            data: 市场数据
            province: 省份
            market_type: 市场类型
            
        Returns:
            满足条件的规则列表
        """
        active_rules = await self.get_active_rules(province, market_type)
        matched_rules = []
        
        for rule in active_rules:
            if not rule.can_execute():
                continue
            
            # 评估条件表达式
            if self.parser.evaluate_expression(rule.condition_expression, data):
                matched_rules.append(rule)
        
        return matched_rules
    
    async def execute_rule(
        self,
        rule: TradingRule,
        trigger_data: Dict[str, Any]
    ) -> RuleExecution:
        """
        执行规则
        
        Args:
            rule: 规则
            trigger_data: 触发数据
            
        Returns:
            执行记录
        """
        execution = RuleExecution(
            rule_id=rule.id,
            trigger_data=trigger_data,
            action_executed=rule.action_type
        )
        
        try:
            # 执行动作
            result = await self._execute_action(rule, trigger_data)
            
            execution.success = True
            execution.action_result = result
            
            # 更新规则统计
            rule.execution_count += 1
            rule.today_execution_count += 1
            rule.last_executed_at = datetime.now()
            
            logger.info(f"执行规则成功: ID={rule.id}, 动作={rule.action_type}")
            
        except Exception as e:
            execution.success = False
            execution.error_message = str(e)
            logger.error(f"执行规则失败: ID={rule.id}, 错误={e}")
        
        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(execution)
        
        return execution
    
    async def _execute_action(
        self,
        rule: TradingRule,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行规则动作"""
        action_type = rule.action_type
        action_params = rule.action_params or {}
        
        if action_type == ActionType.PLACE_ORDER.value:
            # 下单动作
            return await self._action_place_order(action_params, data)
        
        elif action_type == ActionType.SEND_ALERT.value:
            # 发送预警
            return await self._action_send_alert(action_params, data)
        
        elif action_type == ActionType.CANCEL_ORDER.value:
            # 取消订单
            return await self._action_cancel_order(action_params, data)
        
        else:
            logger.warning(f"未知动作类型: {action_type}")
            return {"status": "unknown_action"}
    
    async def _action_place_order(
        self,
        params: Dict[str, Any],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """下单动作"""
        # 模拟下单
        order_id = f"ORD-RULE-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return {
            "order_id": order_id,
            "direction": params.get("direction", "BUY"),
            "quantity": params.get("quantity", 100),
            "price": data.get("price"),
            "status": "SUBMITTED"
        }
    
    async def _action_send_alert(
        self,
        params: Dict[str, Any],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """发送预警动作"""
        # 这里应该调用预警服务
        return {
            "alert_sent": True,
            "message": params.get("message", "规则触发预警"),
            "data": data
        }
    
    async def _action_cancel_order(
        self,
        params: Dict[str, Any],
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """取消订单动作"""
        order_id = params.get("order_id")
        return {
            "order_id": order_id,
            "cancelled": True
        }
    
    async def get_rule_executions(
        self,
        rule_id: int,
        limit: int = 50
    ) -> List[RuleExecution]:
        """获取规则执行历史"""
        query = select(RuleExecution).where(
            RuleExecution.rule_id == rule_id
        ).order_by(desc(RuleExecution.executed_at)).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def reset_daily_counters(self):
        """重置所有规则的每日计数器（应在每日凌晨调用）"""
        query = select(TradingRule).where(
            TradingRule.today_execution_count > 0
        )
        
        result = await self.db.execute(query)
        rules = result.scalars().all()
        
        for rule in rules:
            rule.today_execution_count = 0
        
        await self.db.commit()
        logger.info(f"重置 {len(rules)} 条规则的每日计数器")


# 工厂函数
def get_rule_engine(db: AsyncSession) -> RuleEngine:
    return RuleEngine(db)
