"""
PowerX IP 过滤中间件
创建日期: 2026-01-07
作者: zhi.qu
"""
import ipaddress
from typing import Set, Optional
from datetime import datetime
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger


class IPFilterMiddleware(BaseHTTPMiddleware):
    """IP 过滤中间件"""
    
    def __init__(self, app, whitelist_mode: bool = False):
        super().__init__(app)
        self.whitelist_mode = whitelist_mode
        self._whitelist: Set[str] = set()
        self._blacklist: Set[str] = set()
        self._networks: list = []
    
    def add_to_whitelist(self, ip: str):
        """添加到白名单"""
        if '/' in ip:
            self._networks.append(('whitelist', ipaddress.ip_network(ip, strict=False)))
        else:
            self._whitelist.add(ip)
    
    def add_to_blacklist(self, ip: str):
        """添加到黑名单"""
        if '/' in ip:
            self._networks.append(('blacklist', ipaddress.ip_network(ip, strict=False)))
        else:
            self._blacklist.add(ip)
    
    def remove_from_whitelist(self, ip: str):
        """从白名单移除"""
        self._whitelist.discard(ip)
    
    def remove_from_blacklist(self, ip: str):
        """从黑名单移除"""
        self._blacklist.discard(ip)
    
    def is_ip_allowed(self, ip: str) -> bool:
        """检查 IP 是否允许"""
        try:
            ip_addr = ipaddress.ip_address(ip)
        except ValueError:
            return False
        
        # 检查黑名单
        if ip in self._blacklist:
            return False
        
        for list_type, network in self._networks:
            if ip_addr in network:
                if list_type == 'blacklist':
                    return False
                elif list_type == 'whitelist':
                    return True
        
        # 白名单模式
        if self.whitelist_mode:
            return ip in self._whitelist
        
        # 默认允许
        return True
    
    def get_client_ip(self, request: Request) -> str:
        """获取客户端 IP"""
        # 检查代理头
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "0.0.0.0"
    
    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        client_ip = self.get_client_ip(request)
        
        # 跳过健康检查
        if request.url.path in ["/health", "/api/v1/health"]:
            return await call_next(request)
        
        if not self.is_ip_allowed(client_ip):
            logger.warning(f"IP 被拒绝: {client_ip}")
            raise HTTPException(status_code=403, detail="IP 地址被禁止访问")
        
        response = await call_next(request)
        return response


# 创建全局实例
ip_filter = IPFilterMiddleware(None)


def get_ip_filter() -> IPFilterMiddleware:
    """获取 IP 过滤器"""
    return ip_filter
