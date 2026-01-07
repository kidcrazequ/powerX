"""
PowerX 链路追踪
创建日期: 2026-01-07
作者: zhi.qu

支持 OpenTelemetry 和 Jaeger
"""
from typing import Optional, Dict, Any
from contextlib import contextmanager
import uuid
from loguru import logger

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.sdk.resources import Resource
    HAS_OTEL = True
except ImportError:
    HAS_OTEL = False
    logger.warning("OpenTelemetry 未安装，链路追踪不可用")


class TracingManager:
    """追踪管理器"""
    
    def __init__(self):
        self._tracer: Optional[Any] = None
        self._enabled = False
    
    def init(
        self,
        service_name: str = "powerx",
        jaeger_host: str = "localhost",
        jaeger_port: int = 6831
    ):
        """初始化追踪"""
        if not HAS_OTEL:
            logger.warning("OpenTelemetry 未安装，跳过追踪初始化")
            return
        
        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)
        
        jaeger_exporter = JaegerExporter(
            agent_host_name=jaeger_host,
            agent_port=jaeger_port,
        )
        
        provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
        trace.set_tracer_provider(provider)
        
        self._tracer = trace.get_tracer(service_name)
        self._enabled = True
        
        logger.info(f"链路追踪已启用, Jaeger: {jaeger_host}:{jaeger_port}")
    
    @property
    def tracer(self):
        return self._tracer
    
    @property
    def enabled(self) -> bool:
        return self._enabled
    
    @contextmanager
    def start_span(self, name: str, attributes: Dict[str, Any] = None):
        """开始追踪 span"""
        if not self._enabled or not self._tracer:
            yield None
            return
        
        with self._tracer.start_as_current_span(name) as span:
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, str(value))
            yield span
    
    def get_current_trace_id(self) -> Optional[str]:
        """获取当前 trace ID"""
        if not self._enabled:
            return str(uuid.uuid4())
        
        span = trace.get_current_span()
        if span:
            ctx = span.get_span_context()
            return format(ctx.trace_id, '032x')
        return None


# 单例
tracing = TracingManager()


def init_tracing(
    service_name: str = "powerx",
    jaeger_host: str = "localhost",
    jaeger_port: int = 6831
):
    """初始化追踪"""
    tracing.init(service_name, jaeger_host, jaeger_port)


def get_tracer():
    """获取追踪器"""
    return tracing


# 装饰器
def traced(name: str = None, attributes: Dict[str, Any] = None):
    """追踪装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            span_name = name or f"{func.__module__}.{func.__name__}"
            with tracing.start_span(span_name, attributes):
                return await func(*args, **kwargs)
        return wrapper
    return decorator
