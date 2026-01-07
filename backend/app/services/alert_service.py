"""
PowerX 预警服务

创建日期: 2026-01-07
作者: zhi.qu

提供预警规则管理和预警触发功能
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy import select, func, and_, or_, desc, update
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.alert import AlertRule, AlertRecord, AlertType, AlertLevel, AlertStatus
from app.core.websocket import pubsub_manager
from app.services.market_service import market_service


class AlertService:
    """
    预警服务
    
    功能：
    - 预警规则管理
    - 预警触发和记录
    - 预警处理
    - 实时推送
    """
    
    def __init__(self, db: Optional[AsyncSession] = None):
        """
        初始化预警服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self._running = False
        self._check_interval = 30  # 检查间隔（秒）
        logger.info("预警服务初始化")
    
    # ============ 预警规则管理 ============
    
    async def create_rule(
        self,
        name: str,
        alert_type: AlertType,
        condition_type: str,
        condition_value: float,
        condition_operator: str = ">=",
        level: AlertLevel = AlertLevel.WARNING,
        province: Optional[str] = None,
        description: Optional[str] = None,
        notify_methods: Optional[List[str]] = None,
        notify_users: Optional[List[str]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建预警规则
        """
        logger.info(f"创建预警规则: name={name}, type={alert_type}")
        
        if not self.db:
            return self._mock_create_rule(name, alert_type, condition_type, condition_value)
        
        rule = AlertRule(
            name=name,
            description=description,
            alert_type=alert_type.value if isinstance(alert_type, AlertType) else alert_type,
            level=level.value if isinstance(level, AlertLevel) else level,
            province=province,
            condition_type=condition_type,
            condition_value=condition_value,
            condition_operator=condition_operator,
            notify_methods=notify_methods or ["websocket"],
            notify_users=notify_users,
            user_id=user_id
        )
        
        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)
        
        return rule.to_dict()
    
    async def get_rule(self, rule_id: int) -> Optional[Dict[str, Any]]:
        """获取规则详情"""
        if not self.db:
            return self._mock_get_rule(rule_id)
        
        result = await self.db.execute(
            select(AlertRule).where(AlertRule.id == rule_id)
        )
        rule = result.scalar()
        return rule.to_dict() if rule else None
    
    async def list_rules(
        self,
        alert_type: Optional[str] = None,
        province: Optional[str] = None,
        is_active: Optional[bool] = True,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取规则列表"""
        if not self.db:
            return self._mock_list_rules()
        
        query = select(AlertRule)
        conditions = []
        
        if alert_type:
            conditions.append(AlertRule.alert_type == alert_type)
        if province:
            conditions.append(or_(AlertRule.province == province, AlertRule.province.is_(None)))
        if is_active is not None:
            conditions.append(AlertRule.is_active == is_active)
        if user_id:
            conditions.append(AlertRule.user_id == user_id)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(desc(AlertRule.created_at))
        
        result = await self.db.execute(query)
        rules = result.scalars().all()
        
        return [r.to_dict() for r in rules]
    
    async def update_rule(
        self,
        rule_id: int,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """更新规则"""
        logger.info(f"更新预警规则: rule_id={rule_id}")
        
        if not self.db:
            return self._mock_get_rule(rule_id)
        
        result = await self.db.execute(
            select(AlertRule).where(AlertRule.id == rule_id)
        )
        rule = result.scalar()
        
        if not rule:
            return None
        
        for key, value in kwargs.items():
            if hasattr(rule, key) and value is not None:
                setattr(rule, key, value)
        
        await self.db.commit()
        await self.db.refresh(rule)
        
        return rule.to_dict()
    
    async def delete_rule(self, rule_id: int) -> bool:
        """删除规则"""
        logger.info(f"删除预警规则: rule_id={rule_id}")
        
        if not self.db:
            return True
        
        result = await self.db.execute(
            select(AlertRule).where(AlertRule.id == rule_id)
        )
        rule = result.scalar()
        
        if not rule:
            return False
        
        await self.db.delete(rule)
        await self.db.commit()
        
        return True
    
    # ============ 预警触发 ============
    
    async def trigger_alert(
        self,
        alert_type: AlertType,
        level: AlertLevel,
        title: str,
        message: str,
        province: Optional[str] = None,
        current_value: Optional[float] = None,
        threshold_value: Optional[float] = None,
        context: Optional[Dict] = None,
        user_id: Optional[str] = None,
        rule_id: Optional[int] = None,
        rule_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        触发预警
        """
        logger.warning(f"触发预警: {level} - {title}")
        
        alert_data = {
            "rule_id": rule_id,
            "rule_name": rule_name,
            "alert_type": alert_type.value if isinstance(alert_type, AlertType) else alert_type,
            "level": level.value if isinstance(level, AlertLevel) else level,
            "title": title,
            "message": message,
            "province": province,
            "current_value": current_value,
            "threshold_value": threshold_value,
            "context": context,
            "user_id": user_id,
            "status": AlertStatus.PENDING.value,
            "created_at": datetime.now().isoformat()
        }
        
        # 保存到数据库
        if self.db:
            record = AlertRecord(**{k: v for k, v in alert_data.items() if k != 'created_at'})
            self.db.add(record)
            await self.db.commit()
            await self.db.refresh(record)
            alert_data["id"] = record.id
        else:
            alert_data["id"] = int(datetime.now().timestamp() * 1000)
        
        # 通过 WebSocket 推送
        await self._push_alert(alert_data)
        
        return alert_data
    
    async def _push_alert(self, alert_data: Dict) -> None:
        """推送预警到 WebSocket"""
        message = {
            "type": "alert",
            "data": alert_data,
            "timestamp": datetime.now().isoformat()
        }
        
        # 推送到通知频道
        await pubsub_manager.publish("notifications", json.dumps(message))
        
        # 如果有特定省份，也推送到省份频道
        if alert_data.get("province"):
            await pubsub_manager.publish(
                f"market:{alert_data['province']}", 
                json.dumps(message)
            )
    
    # ============ 预警处理 ============
    
    async def acknowledge_alert(
        self,
        alert_id: int,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """确认预警"""
        logger.info(f"确认预警: alert_id={alert_id}, user={user_id}")
        
        if not self.db:
            return {"id": alert_id, "status": AlertStatus.ACKNOWLEDGED.value}
        
        result = await self.db.execute(
            select(AlertRecord).where(AlertRecord.id == alert_id)
        )
        record = result.scalar()
        
        if not record:
            return None
        
        record.status = AlertStatus.ACKNOWLEDGED.value
        record.acknowledged_by = user_id
        record.acknowledged_at = datetime.now()
        
        await self.db.commit()
        await self.db.refresh(record)
        
        return record.to_dict()
    
    async def resolve_alert(
        self,
        alert_id: int,
        user_id: str,
        note: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """解决预警"""
        logger.info(f"解决预警: alert_id={alert_id}, user={user_id}")
        
        if not self.db:
            return {"id": alert_id, "status": AlertStatus.RESOLVED.value}
        
        result = await self.db.execute(
            select(AlertRecord).where(AlertRecord.id == alert_id)
        )
        record = result.scalar()
        
        if not record:
            return None
        
        record.status = AlertStatus.RESOLVED.value
        record.resolved_by = user_id
        record.resolved_at = datetime.now()
        record.resolution_note = note
        
        await self.db.commit()
        await self.db.refresh(record)
        
        return record.to_dict()
    
    async def list_alerts(
        self,
        status: Optional[str] = None,
        level: Optional[str] = None,
        alert_type: Optional[str] = None,
        province: Optional[str] = None,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取预警列表"""
        if not self.db:
            return self._mock_list_alerts(page, page_size)
        
        query = select(AlertRecord)
        conditions = []
        
        if status:
            conditions.append(AlertRecord.status == status)
        if level:
            conditions.append(AlertRecord.level == level)
        if alert_type:
            conditions.append(AlertRecord.alert_type == alert_type)
        if province:
            conditions.append(AlertRecord.province == province)
        if user_id:
            conditions.append(AlertRecord.user_id == user_id)
        if start_time:
            conditions.append(AlertRecord.created_at >= start_time)
        if end_time:
            conditions.append(AlertRecord.created_at <= end_time)
        
        # 计数
        count_query = select(func.count(AlertRecord.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 查询
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(desc(AlertRecord.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        records = result.scalars().all()
        
        return {
            "items": [r.to_dict() for r in records],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    async def get_alert_statistics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """获取预警统计"""
        if not self.db:
            return self._mock_get_statistics()
        
        if not end_time:
            end_time = datetime.now()
        if not start_time:
            start_time = end_time - timedelta(days=7)
        
        conditions = [
            AlertRecord.created_at >= start_time,
            AlertRecord.created_at <= end_time
        ]
        
        # 按状态统计
        status_query = select(
            AlertRecord.status,
            func.count(AlertRecord.id)
        ).where(and_(*conditions)).group_by(AlertRecord.status)
        
        status_result = await self.db.execute(status_query)
        by_status = {row[0]: row[1] for row in status_result.all()}
        
        # 按级别统计
        level_query = select(
            AlertRecord.level,
            func.count(AlertRecord.id)
        ).where(and_(*conditions)).group_by(AlertRecord.level)
        
        level_result = await self.db.execute(level_query)
        by_level = {row[0]: row[1] for row in level_result.all()}
        
        # 按类型统计
        type_query = select(
            AlertRecord.alert_type,
            func.count(AlertRecord.id)
        ).where(and_(*conditions)).group_by(AlertRecord.alert_type)
        
        type_result = await self.db.execute(type_query)
        by_type = {row[0]: row[1] for row in type_result.all()}
        
        total = sum(by_status.values())
        
        return {
            "total": total,
            "by_status": by_status,
            "by_level": by_level,
            "by_type": by_type,
            "pending_count": by_status.get(AlertStatus.PENDING.value, 0),
            "resolved_count": by_status.get(AlertStatus.RESOLVED.value, 0)
        }
    
    # ============ 自动检查 ============
    
    async def check_price_alerts(self) -> List[Dict]:
        """检查价格预警"""
        triggered = []
        
        provinces = market_service.get_supported_provinces()
        
        for province in provinces:
            try:
                price_data = await market_service.get_realtime_price(province)
                current_price = price_data.get("price", 0)
                
                # 获取该省份的价格预警规则
                rules = await self.list_rules(
                    alert_type=AlertType.PRICE_HIGH.value,
                    province=province,
                    is_active=True
                )
                
                for rule in rules:
                    if self._check_condition(current_price, rule):
                        alert = await self.trigger_alert(
                            alert_type=AlertType(rule["alert_type"]),
                            level=AlertLevel(rule["level"]),
                            title=f"{province}电价预警: {rule['name']}",
                            message=f"当前价格 {current_price:.2f} 元/MWh 触发预警规则",
                            province=province,
                            current_value=current_price,
                            threshold_value=rule["condition_value"],
                            rule_id=rule["id"],
                            rule_name=rule["name"]
                        )
                        triggered.append(alert)
                
            except Exception as e:
                logger.error(f"检查 {province} 价格预警失败: {e}")
        
        return triggered
    
    def _check_condition(self, value: float, rule: Dict) -> bool:
        """检查是否满足条件"""
        threshold = rule["condition_value"]
        operator = rule.get("condition_operator", ">=")
        
        operators = {
            ">=": lambda v, t: v >= t,
            ">": lambda v, t: v > t,
            "<=": lambda v, t: v <= t,
            "<": lambda v, t: v < t,
            "==": lambda v, t: v == t,
            "!=": lambda v, t: v != t
        }
        
        check_func = operators.get(operator, lambda v, t: False)
        return check_func(value, threshold)
    
    # ============ Mock 数据 ============
    
    def _mock_create_rule(self, name: str, alert_type: AlertType, 
                          condition_type: str, condition_value: float) -> Dict:
        return {
            "id": 100,
            "name": name,
            "alert_type": alert_type.value if isinstance(alert_type, AlertType) else alert_type,
            "condition_type": condition_type,
            "condition_value": condition_value,
            "is_active": True,
            "created_at": datetime.now().isoformat()
        }
    
    def _mock_get_rule(self, rule_id: int) -> Dict:
        return {
            "id": rule_id,
            "name": "价格上限预警",
            "alert_type": AlertType.PRICE_HIGH.value,
            "level": AlertLevel.WARNING.value,
            "condition_type": "price",
            "condition_value": 600.0,
            "condition_operator": ">=",
            "is_active": True
        }
    
    def _mock_list_rules(self) -> List[Dict]:
        return [
            {"id": 1, "name": "价格上限预警", "alert_type": "PRICE_HIGH", "level": "WARNING", "condition_value": 600, "is_active": True, "trigger_count": 5},
            {"id": 2, "name": "价格下限预警", "alert_type": "PRICE_LOW", "level": "INFO", "condition_value": 200, "is_active": True, "trigger_count": 2},
            {"id": 3, "name": "价格波动预警", "alert_type": "PRICE_CHANGE", "level": "DANGER", "condition_value": 10, "is_active": True, "trigger_count": 8},
            {"id": 4, "name": "持仓风险预警", "alert_type": "POSITION_RISK", "level": "CRITICAL", "condition_value": 80, "is_active": True, "trigger_count": 1}
        ]
    
    def _mock_list_alerts(self, page: int, page_size: int) -> Dict:
        alerts = [
            {"id": 1, "title": "广东电价触发上限预警", "level": "WARNING", "status": "PENDING", "province": "guangdong", "current_value": 620.5, "threshold_value": 600, "created_at": datetime.now().isoformat()},
            {"id": 2, "title": "浙江电价波动过大", "level": "DANGER", "status": "ACKNOWLEDGED", "province": "zhejiang", "current_value": 15.5, "threshold_value": 10, "created_at": (datetime.now() - timedelta(hours=2)).isoformat()},
            {"id": 3, "title": "山东电价偏低", "level": "INFO", "status": "RESOLVED", "province": "shandong", "current_value": 180.0, "threshold_value": 200, "created_at": (datetime.now() - timedelta(days=1)).isoformat()},
            {"id": 4, "title": "持仓风险预警", "level": "CRITICAL", "status": "PENDING", "current_value": 85.0, "threshold_value": 80, "created_at": (datetime.now() - timedelta(hours=1)).isoformat()}
        ]
        return {
            "items": alerts,
            "total": len(alerts),
            "page": page,
            "page_size": page_size
        }
    
    def _mock_get_statistics(self) -> Dict:
        return {
            "total": 125,
            "by_status": {"PENDING": 15, "ACKNOWLEDGED": 20, "RESOLVED": 85, "IGNORED": 5},
            "by_level": {"INFO": 40, "WARNING": 50, "DANGER": 25, "CRITICAL": 10},
            "by_type": {"PRICE_HIGH": 35, "PRICE_LOW": 20, "PRICE_CHANGE": 40, "POSITION_RISK": 15, "CONTRACT_EXPIRE": 15},
            "pending_count": 15,
            "resolved_count": 85
        }


# 全局预警服务实例
alert_service = AlertService()
