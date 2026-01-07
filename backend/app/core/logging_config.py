"""
PowerX 日志配置
创建日期: 2026-01-07
作者: zhi.qu

支持 Loki 集成的结构化日志
"""
import sys
import json
from typing import Dict, Any
from datetime import datetime
from loguru import logger


class LokiHandler:
    """Loki 日志处理器"""
    
    def __init__(self, loki_url: str = "http://localhost:3100"):
        self.loki_url = loki_url
        self.labels = {
            "app": "powerx",
            "env": "production"
        }
    
    def write(self, message):
        """写入日志到 Loki"""
        record = message.record
        
        log_entry = {
            "streams": [{
                "stream": self.labels,
                "values": [[
                    str(int(datetime.now().timestamp() * 1e9)),
                    self._format_message(record)
                ]]
            }]
        }
        
        # 异步发送到 Loki (实际实现需要 aiohttp)
        # 这里仅作结构示例
        pass
    
    def _format_message(self, record) -> str:
        """格式化日志消息"""
        return json.dumps({
            "level": record["level"].name,
            "message": record["message"],
            "time": record["time"].isoformat(),
            "module": record["module"],
            "function": record["function"],
            "line": record["line"],
            "extra": dict(record["extra"])
        })


def setup_logging(
    log_level: str = "INFO",
    log_file: str = None,
    loki_url: str = None,
    json_format: bool = False
):
    """配置日志系统"""
    # 移除默认处理器
    logger.remove()
    
    # 日志格式
    if json_format:
        fmt = "{message}"
        serialize = True
    else:
        fmt = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        serialize = False
    
    # 控制台输出
    logger.add(
        sys.stderr,
        format=fmt,
        level=log_level,
        colorize=True,
        serialize=serialize
    )
    
    # 文件输出
    if log_file:
        logger.add(
            log_file,
            format=fmt,
            level=log_level,
            rotation="100 MB",
            retention="30 days",
            compression="gz",
            serialize=serialize
        )
    
    # Loki 输出
    if loki_url:
        loki_handler = LokiHandler(loki_url)
        logger.add(
            loki_handler.write,
            format="{message}",
            level=log_level,
            serialize=True
        )
    
    logger.info(f"日志系统初始化完成, 级别: {log_level}")
    return logger


def get_logger(name: str = None):
    """获取日志记录器"""
    if name:
        return logger.bind(module=name)
    return logger


# 日志上下文
class LogContext:
    """日志上下文管理器"""
    
    def __init__(self, **kwargs):
        self.context = kwargs
    
    def __enter__(self):
        return logger.bind(**self.context)
    
    def __exit__(self, *args):
        pass


def log_request(request_id: str, user_id: str = None):
    """请求日志装饰器"""
    return logger.bind(request_id=request_id, user_id=user_id)
