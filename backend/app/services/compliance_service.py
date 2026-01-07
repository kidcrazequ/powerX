"""
PowerX 合规检查服务
创建日期: 2026-01-07
作者: zhi.qu
"""
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from loguru import logger


class ComplianceLevel(str, Enum):
    """合规级别"""
    PASS = "pass"
    WARNING = "warning"
    VIOLATION = "violation"
    BLOCKED = "blocked"


@dataclass
class ComplianceRule:
    """合规规则"""
    rule_id: str
    name: str
    description: str
    check_func: str  # 检查函数名
    level: ComplianceLevel  # 违规级别
    is_blocking: bool = False  # 是否阻止交易


@dataclass
class ComplianceResult:
    """合规检查结果"""
    rule_id: str
    rule_name: str
    passed: bool
    level: ComplianceLevel
    message: str
    details: Dict[str, Any] = None


class ComplianceService:
    """合规检查服务"""
    
    def __init__(self):
        self._rules: Dict[str, ComplianceRule] = {}
        self._init_default_rules()
    
    def _init_default_rules(self):
        """初始化默认规则"""
        self.add_rule(ComplianceRule(
            rule_id="max_single_order",
            name="单笔订单限额",
            description="单笔订单不能超过10000 MWh",
            check_func="check_single_order_limit",
            level=ComplianceLevel.BLOCKED,
            is_blocking=True
        ))
        
        self.add_rule(ComplianceRule(
            rule_id="daily_limit",
            name="日交易限额",
            description="每日交易总量不能超过50000 MWh",
            check_func="check_daily_limit",
            level=ComplianceLevel.VIOLATION,
            is_blocking=True
        ))
        
        self.add_rule(ComplianceRule(
            rule_id="position_limit",
            name="持仓限额",
            description="单一方向持仓不能超过100000 MWh",
            check_func="check_position_limit",
            level=ComplianceLevel.WARNING,
            is_blocking=False
        ))
        
        self.add_rule(ComplianceRule(
            rule_id="price_deviation",
            name="价格偏离度",
            description="订单价格不能偏离市场价超过10%",
            check_func="check_price_deviation",
            level=ComplianceLevel.VIOLATION,
            is_blocking=True
        ))
        
        self.add_rule(ComplianceRule(
            rule_id="frequency_limit",
            name="交易频率限制",
            description="每分钟订单数不能超过100笔",
            check_func="check_frequency_limit",
            level=ComplianceLevel.WARNING,
            is_blocking=False
        ))
    
    def add_rule(self, rule: ComplianceRule):
        """添加规则"""
        self._rules[rule.rule_id] = rule
    
    def remove_rule(self, rule_id: str):
        """移除规则"""
        self._rules.pop(rule_id, None)
    
    async def check_order(
        self,
        order_data: Dict[str, Any],
        user_context: Dict[str, Any] = None
    ) -> List[ComplianceResult]:
        """检查订单合规性"""
        results = []
        
        for rule in self._rules.values():
            result = await self._run_check(rule, order_data, user_context or {})
            results.append(result)
            
            if not result.passed and rule.is_blocking:
                logger.warning(f"订单被合规规则阻止: {rule.rule_id}")
                break
        
        return results
    
    async def _run_check(
        self,
        rule: ComplianceRule,
        order_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> ComplianceResult:
        """执行检查"""
        try:
            check_method = getattr(self, rule.check_func, None)
            if check_method:
                passed, message, details = await check_method(order_data, user_context)
            else:
                passed, message, details = True, "规则未实现", {}
            
            return ComplianceResult(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                passed=passed,
                level=ComplianceLevel.PASS if passed else rule.level,
                message=message,
                details=details
            )
        except Exception as e:
            logger.error(f"合规检查失败: {rule.rule_id}, {e}")
            return ComplianceResult(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                passed=False,
                level=ComplianceLevel.WARNING,
                message=f"检查异常: {str(e)}"
            )
    
    # 检查方法
    async def check_single_order_limit(
        self, order_data: Dict, context: Dict
    ) -> tuple:
        """检查单笔限额"""
        quantity = order_data.get("quantity", 0)
        limit = 10000
        
        if quantity > limit:
            return False, f"订单数量 {quantity} 超过限额 {limit}", {"quantity": quantity, "limit": limit}
        return True, "通过", {}
    
    async def check_daily_limit(
        self, order_data: Dict, context: Dict
    ) -> tuple:
        """检查日限额"""
        daily_total = context.get("daily_total", 0)
        quantity = order_data.get("quantity", 0)
        limit = 50000
        
        if daily_total + quantity > limit:
            return False, f"超过日交易限额", {"current": daily_total, "new": quantity, "limit": limit}
        return True, "通过", {}
    
    async def check_position_limit(
        self, order_data: Dict, context: Dict
    ) -> tuple:
        """检查持仓限额"""
        position = context.get("position", 0)
        limit = 100000
        
        if position > limit:
            return False, f"持仓超限", {"position": position, "limit": limit}
        return True, "通过", {}
    
    async def check_price_deviation(
        self, order_data: Dict, context: Dict
    ) -> tuple:
        """检查价格偏离"""
        order_price = order_data.get("price", 0)
        market_price = context.get("market_price", order_price)
        
        if market_price == 0:
            return True, "无市场价格参考", {}
        
        deviation = abs(order_price - market_price) / market_price * 100
        limit = 10
        
        if deviation > limit:
            return False, f"价格偏离度 {deviation:.2f}% 超过限制", {
                "order_price": order_price,
                "market_price": market_price,
                "deviation": deviation,
                "limit": limit
            }
        return True, "通过", {}
    
    async def check_frequency_limit(
        self, order_data: Dict, context: Dict
    ) -> tuple:
        """检查交易频率"""
        orders_per_minute = context.get("orders_per_minute", 0)
        limit = 100
        
        if orders_per_minute > limit:
            return False, f"交易频率过高", {"count": orders_per_minute, "limit": limit}
        return True, "通过", {}
    
    def is_order_allowed(self, results: List[ComplianceResult]) -> bool:
        """检查订单是否允许"""
        blocking_violations = [
            r for r in results
            if not r.passed and r.level in [ComplianceLevel.BLOCKED, ComplianceLevel.VIOLATION]
        ]
        return len(blocking_violations) == 0
    
    def get_all_rules(self) -> List[Dict[str, Any]]:
        """获取所有规则"""
        return [
            {
                "rule_id": r.rule_id,
                "name": r.name,
                "description": r.description,
                "level": r.level.value,
                "is_blocking": r.is_blocking
            }
            for r in self._rules.values()
        ]


# 单例
compliance_service = ComplianceService()


def get_compliance_service() -> ComplianceService:
    """获取合规服务"""
    return compliance_service
