"""
PowerX 队列服务
创建日期: 2026-01-07
作者: zhi.qu

封装消息队列的业务操作
"""
from typing import Dict, Any, Callable, List
from datetime import datetime
from loguru import logger

from app.core.message_queue import get_mq_manager, QUEUES, QueuePriority


class QueueService:
    """队列服务"""
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
    
    async def publish_order_execution(self, order_id: str, order_data: Dict[str, Any]):
        """发布订单执行任务"""
        mq = get_mq_manager()
        await mq.publish("order_execution", {
            "type": "order_execution",
            "order_id": order_id,
            "data": order_data,
            "timestamp": datetime.now().isoformat()
        }, priority=QueuePriority.HIGH.value)
        logger.info(f"订单执行任务已发布: {order_id}")
    
    async def publish_notification(self, user_id: str, title: str, content: str,
                                   channel: str = "system"):
        """发布通知任务"""
        mq = get_mq_manager()
        await mq.publish("notification", {
            "type": "notification",
            "user_id": user_id,
            "title": title,
            "content": content,
            "channel": channel,
            "timestamp": datetime.now().isoformat()
        })
        logger.debug(f"通知任务已发布: {user_id}")
    
    async def publish_report_generation(self, report_id: str, template_id: int,
                                        parameters: Dict[str, Any], user_id: str):
        """发布报表生成任务"""
        mq = get_mq_manager()
        await mq.publish("report_generation", {
            "type": "report_generation",
            "report_id": report_id,
            "template_id": template_id,
            "parameters": parameters,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }, priority=QueuePriority.LOW.value)
        logger.info(f"报表生成任务已发布: {report_id}")
    
    async def publish_ai_prediction(self, task_id: str, model: str,
                                    input_data: Dict[str, Any]):
        """发布AI预测任务"""
        mq = get_mq_manager()
        await mq.publish("ai_prediction", {
            "type": "ai_prediction",
            "task_id": task_id,
            "model": model,
            "input_data": input_data,
            "timestamp": datetime.now().isoformat()
        })
        logger.debug(f"AI预测任务已发布: {task_id}")
    
    async def publish_data_sync(self, sync_type: str, data: Dict[str, Any]):
        """发布数据同步任务"""
        mq = get_mq_manager()
        await mq.publish("data_sync", {
            "type": "data_sync",
            "sync_type": sync_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
    
    async def publish_audit_log(self, user_id: str, action: str,
                                module: str, details: Dict[str, Any] = None):
        """发布审计日志"""
        mq = get_mq_manager()
        await mq.publish("audit_log", {
            "type": "audit_log",
            "user_id": user_id,
            "action": action,
            "module": module,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }, priority=QueuePriority.LOW.value)
    
    async def subscribe_queue(self, queue_name: str, handler: Callable):
        """订阅队列"""
        if queue_name not in QUEUES:
            raise ValueError(f"未知队列: {queue_name}")
        
        mq = get_mq_manager()
        await mq.subscribe(queue_name, handler)
        
        if queue_name not in self._handlers:
            self._handlers[queue_name] = []
        self._handlers[queue_name].append(handler)
        
        logger.info(f"已注册队列处理器: {queue_name}")
    
    def get_queue_info(self) -> List[Dict[str, Any]]:
        """获取队列信息"""
        return [
            {
                "name": config.name,
                "description": config.description,
                "priority": config.priority.name,
                "durable": config.durable,
                "max_length": config.max_length
            }
            for config in QUEUES.values()
        ]


# 单例
queue_service = QueueService()


def get_queue_service() -> QueueService:
    """获取队列服务"""
    return queue_service
