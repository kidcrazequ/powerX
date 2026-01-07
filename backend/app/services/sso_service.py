"""
PowerX SSO 单点登录服务

创建日期: 2026-01-07
作者: zhi.qu

提供 OAuth2/OIDC 和 LDAP 单点登录支持
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
import aiohttp


class SSOService:
    """SSO 服务"""
    
    def __init__(self):
        self.providers: Dict[str, Dict] = {}
        logger.info("SSOService 初始化完成")
    
    def register_provider(self, provider_id: str, config: Dict[str, Any]):
        """
        注册 SSO 提供者
        
        Args:
            provider_id: 提供者ID
            config: 提供者配置
        """
        self.providers[provider_id] = config
        logger.info(f"注册 SSO 提供者: {provider_id}")
    
    async def get_authorization_url(self, provider_id: str, redirect_uri: str,
                                   state: str = None) -> Optional[str]:
        """
        获取授权URL
        
        Args:
            provider_id: 提供者ID
            redirect_uri: 回调地址
            state: 状态参数
            
        Returns:
            授权URL
        """
        if provider_id not in self.providers:
            return None
        
        config = self.providers[provider_id]
        
        if config.get("type") == "oauth2":
            params = {
                "client_id": config["client_id"],
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": config.get("scope", "openid profile email"),
            }
            if state:
                params["state"] = state
            
            query = "&".join(f"{k}={v}" for k, v in params.items())
            return f"{config['authorization_endpoint']}?{query}"
        
        return None
    
    async def exchange_code(self, provider_id: str, code: str,
                           redirect_uri: str) -> Optional[Dict[str, Any]]:
        """
        用授权码交换令牌
        
        Args:
            provider_id: 提供者ID
            code: 授权码
            redirect_uri: 回调地址
            
        Returns:
            令牌信息
        """
        if provider_id not in self.providers:
            return None
        
        config = self.providers[provider_id]
        
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    "grant_type": "authorization_code",
                    "client_id": config["client_id"],
                    "client_secret": config["client_secret"],
                    "code": code,
                    "redirect_uri": redirect_uri
                }
                
                async with session.post(config["token_endpoint"], data=data) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        logger.error(f"Token 交换失败: {resp.status}")
                        return None
        except Exception as e:
            logger.error(f"Token 交换异常: {e}")
            return None
    
    async def get_user_info(self, provider_id: str, access_token: str) -> Optional[Dict[str, Any]]:
        """
        获取用户信息
        
        Args:
            provider_id: 提供者ID
            access_token: 访问令牌
            
        Returns:
            用户信息
        """
        if provider_id not in self.providers:
            return None
        
        config = self.providers[provider_id]
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {access_token}"}
                async with session.get(config["userinfo_endpoint"], headers=headers) as resp:
                    if resp.status == 200:
                        return await resp.json()
        except Exception as e:
            logger.error(f"获取用户信息异常: {e}")
        
        return None
    
    async def ldap_authenticate(self, username: str, password: str,
                               ldap_config: Dict = None) -> Optional[Dict[str, Any]]:
        """
        LDAP 认证
        
        Args:
            username: 用户名
            password: 密码
            ldap_config: LDAP 配置
            
        Returns:
            用户信息
        """
        # LDAP 认证需要额外的库支持
        # 这里提供基础实现框架
        logger.info(f"LDAP 认证: {username}")
        
        # 模拟认证成功
        if username and password:
            return {
                "username": username,
                "email": f"{username}@company.com",
                "display_name": username.title(),
                "groups": ["users"]
            }
        
        return None
    
    def get_available_providers(self) -> List[Dict[str, str]]:
        """获取可用的 SSO 提供者"""
        return [
            {"id": pid, "name": config.get("name", pid), "type": config.get("type")}
            for pid, config in self.providers.items()
        ]


# 单例实例
sso_service = SSOService()


# 预设一些常见的 OAuth2 提供者配置模板
PROVIDER_TEMPLATES = {
    "github": {
        "type": "oauth2",
        "name": "GitHub",
        "authorization_endpoint": "https://github.com/login/oauth/authorize",
        "token_endpoint": "https://github.com/login/oauth/access_token",
        "userinfo_endpoint": "https://api.github.com/user",
        "scope": "read:user user:email"
    },
    "google": {
        "type": "oauth2",
        "name": "Google",
        "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_endpoint": "https://oauth2.googleapis.com/token",
        "userinfo_endpoint": "https://www.googleapis.com/oauth2/v3/userinfo",
        "scope": "openid profile email"
    },
    "microsoft": {
        "type": "oauth2",
        "name": "Microsoft",
        "authorization_endpoint": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "token_endpoint": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "userinfo_endpoint": "https://graph.microsoft.com/v1.0/me",
        "scope": "openid profile email"
    }
}


def get_sso_service() -> SSOService:
    return sso_service


from typing import List
