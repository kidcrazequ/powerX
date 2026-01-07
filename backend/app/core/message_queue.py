"""
PowerX 消息队列管理
创建日期: 2026-01-07
作者: zhi.qu

基于 RabbitMQ 的异步消息队列系统
"""
import asyncio
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import json
from loguru import logger

try:
    import aio_pika
    from aio_pika import Message, DeliveryMode, ExchangeType
    from aio_pika.abc import AbstractConnection, AbstractChannel, AbstractQueue
    HAS_RABBITMQ = True
except ImportError:
    HAS_RABBITMQ = False
    logger.warning("aio-pika 未安装，使用内存队列模式")


class QueuePriority(int, Enum):
    """队列优先级"""
    LOW = 1
    NORMAL = 5
    HIGH = 10


@dataclass
class QueueConfig:
    """队列配置"""
    name: str
    description: str
    priority: QueuePriority = QueuePriority.NORMAL
    durable: bool = True
    auto_delete: bool = False
    max_length: int = 10000


# 预定义队列
QUEUES: Dict[str, QueueConfig] = {
    "order_execution": QueueConfig(
        name="order_execution",
        description="高优先级订单执行",
        priority=QueuePriority.HIGH
    ),
    "notification": QueueConfig(
        name="notification", 
        description="通知推送",
        priority=QueuePriority.NORMAL
    ),
    "report_generation": QueueConfig(
        name="report_generation",
        description="报表生成",
        priority=QueuePriority.LOW
    ),
    "ai_prediction": QueueConfig(
        name="ai_prediction",
        description="AI预测任务",
        priority=QueuePriority.NORMAL
    ),
    "data_sync": QueueConfig(
        name="data_sync",
        description="数据同步",
        priority=QueuePriority.NORMAL
    ),
    "audit_log": QueueConfig(
        name="audit_log",
        description="审计日志",
        priority=QueuePriority.LOW
    )
}


class MemoryQueue:
    """内存队列 (开发/测试用)"""
    
    def __init__(self):
        self._queues: Dict[str, asyncio.Queue] = {}
        self._handlers: Dict[str, Callable] = {}
        self._running = False
        self._tasks: list = []
    
    async def connect(self):
        """连接 (无操作)"""
        logger.info("使用内存队列模式")
        self._running = True
    
    async def disconnect(self):
        """断开连接"""
        self._running = False
        for task in self._tasks:
            task.cancel()
    
    def get_queue(self, name: str) -> asyncio.Queue:
        """获取队列"""
        if name not in self._queues:
            self._queues[name] = asyncio.Queue(maxsize=10000)
        return self._queues[name]
    
    async def publish(self, queue_name: str, message: Dict[str, Any], priority: int = 5):
        """发布消息"""
        queue = self.get_queue(queue_name)
        await queue.put({"data": message, "priority": priority})
        logger.debug(f"消息已发布到队列 {queue_name}")
    
    async def subscribe(self, queue_name: str, handler: Callable):
        """订阅队列"""
        self._handlers[queue_name] = handler
        task = asyncio.create_task(self._consume(queue_name, handler))
        self._tasks.append(task)
        logger.info(f"已订阅队列: {queue_name}")
    
    async def _consume(self, queue_name: str, handler: Callable):
        """消费消息"""
        queue = self.get_queue(queue_name)
        while self._running:
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=1.0)
                try:
                    await handler(msg["data"])
                except Exception as e:
                    logger.error(f"处理消息失败: {e}")
            except asyncio.TimeoutError:
                continue


class RabbitMQClient:
    """RabbitMQ 客户端"""
    
    def __init__(self, url: str = "amqp://guest:guest@localhost/"):
        self.url = url
        self._connection: Optional[AbstractConnection] = None
        self._channel: Optional[AbstractChannel] = None
        self._queues: Dict[str, AbstractQueue] = {}
        self._consumers: list = []
    
    async def connect(self):
        """建立连接"""
        if not HAS_RABBITMQ:
            raise RuntimeError("aio-pika 未安装")
        
        self._connection = await aio_pika.connect_robust(self.url)
        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=10)
        
        # 声明所有预定义队列
        for queue_name, config in QUEUES.items():
            queue = await self._channel.declare_queue(
                config.name,
                durable=config.durable,
                auto_delete=config.auto_delete,
                arguments={"x-max-length": config.max_length}
            )
            self._queues[queue_name] = queue
        
        logger.info("RabbitMQ 连接成功")
    
    async def disconnect(self):
        """断开连接"""
        for consumer in self._consumers:
            await consumer.cancel()
        if self._connection:
            await self._connection.close()
        logger.info("RabbitMQ 连接已关闭")
    
    async def publish(self, queue_name: str, message: Dict[str, Any], priority: int = 5):
        """发布消息"""
        if not self._channel:
            raise RuntimeError("未连接到 RabbitMQ")
        
        body = json.dumps(message, ensure_ascii=False).encode()
        msg = Message(
            body,
            delivery_mode=DeliveryMode.PERSISTENT,
            priority=priority
        )
        
        await self._channel.default_exchange.publish(
            msg,
            routing_key=queue_name
        )
        logger.debug(f"消息已发布到 {queue_name}")
    
    async def subscribe(self, queue_name: str, handler: Callable):
        """订阅队列"""
        if queue_name not in self._queues:
            raise ValueError(f"队列不存在: {queue_name}")
        
        queue = self._queues[queue_name]
        
        async def on_message(message: aio_pika.IncomingMessage):
            async with message.process():
                try:
                    data = json.loads(message.body.decode())
                    await handler(data)
                except Exception as e:
                    logger.error(f"处理消息失败: {e}")
        
        consumer = await queue.consume(on_message)
        self._consumers.append(consumer)
        logger.info(f"已订阅队列: {queue_name}")


class MessageQueueManager:
    """消息队列管理器"""
    
    _instance: Optional["MessageQueueManager"] = None
    
    def __init__(self, rabbitmq_url: str = None):
        self._use_rabbitmq = HAS_RABBITMQ and rabbitmq_url
        if self._use_rabbitmq:
            self._client = RabbitMQClient(rabbitmq_url)
        else:
            self._client = MemoryQueue()
    
    @classmethod
    def get_instance(cls, rabbitmq_url: str = None) -> "MessageQueueManager":
        """获取单例"""
        if cls._instance is None:
            cls._instance = cls(rabbitmq_url)
        return cls._instance
    
    async def connect(self):
        """连接"""
        await self._client.connect()
    
    async def disconnect(self):
        """断开连接"""
        await self._client.disconnect()
    
    async def publish(self, queue_name: str, message: Dict[str, Any], priority: int = None):
        """发布消息"""
        if priority is None:
            config = QUEUES.get(queue_name)
            priority = config.priority.value if config else QueuePriority.NORMAL.value
        await self._client.publish(queue_name, message, priority)
    
    async def subscribe(self, queue_name: str, handler: Callable):
        """订阅队列"""
        await self._client.subscribe(queue_name, handler)
    
    @property
    def is_rabbitmq(self) -> bool:
        """是否使用 RabbitMQ"""
        return self._use_rabbitmq


# 便捷函数
mq_manager: Optional[MessageQueueManager] = None


async def init_message_queue(rabbitmq_url: str = None):
    """初始化消息队列"""
    global mq_manager
    mq_manager = MessageQueueManager.get_instance(rabbitmq_url)
    await mq_manager.connect()
    return mq_manager


async def close_message_queue():
    """关闭消息队列"""
    global mq_manager
    if mq_manager:
        await mq_manager.disconnect()
        mq_manager = None


def get_mq_manager() -> MessageQueueManager:
    """获取消息队列管理器"""
    if mq_manager is None:
        raise RuntimeError("消息队列未初始化")
    return mq_manager
