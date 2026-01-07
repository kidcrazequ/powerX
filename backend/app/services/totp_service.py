"""
PowerX TOTP 服务
创建日期: 2026-01-07
作者: zhi.qu

时间一次性密码 (TOTP) 双因素认证服务
"""
import secrets
import base64
from typing import Optional, Tuple, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

try:
    import pyotp
    HAS_PYOTP = True
except ImportError:
    HAS_PYOTP = False
    logger.warning("pyotp 未安装，TOTP 功能不可用")

from app.models.two_factor import TwoFactorConfig, TwoFactorLog, TwoFactorType


class TOTPService:
    """TOTP 服务"""
    
    ISSUER = "PowerX"
    BACKUP_CODE_COUNT = 10
    BACKUP_CODE_LENGTH = 8
    
    def __init__(self, db: AsyncSession = None):
        self.db = db
    
    def generate_secret(self) -> str:
        """生成 TOTP 密钥"""
        if not HAS_PYOTP:
            raise RuntimeError("pyotp 未安装")
        return pyotp.random_base32()
    
    def generate_backup_codes(self) -> List[str]:
        """生成备用码"""
        codes = []
        for _ in range(self.BACKUP_CODE_COUNT):
            code = secrets.token_hex(self.BACKUP_CODE_LENGTH // 2).upper()
            codes.append(code)
        return codes
    
    def get_provisioning_uri(self, secret: str, user_email: str) -> str:
        """获取二维码 URI"""
        if not HAS_PYOTP:
            raise RuntimeError("pyotp 未安装")
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=user_email, issuer_name=self.ISSUER)
    
    def verify_totp(self, secret: str, code: str) -> bool:
        """验证 TOTP 码"""
        if not HAS_PYOTP:
            return False
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)  # 允许前后各1个时间窗口
    
    async def setup_totp(self, user_id: str, user_email: str) -> Tuple[str, str, List[str]]:
        """设置 TOTP
        
        返回: (secret, qr_uri, backup_codes)
        """
        secret = self.generate_secret()
        qr_uri = self.get_provisioning_uri(secret, user_email)
        backup_codes = self.generate_backup_codes()
        
        # 检查是否已存在配置
        query = select(TwoFactorConfig).where(TwoFactorConfig.user_id == user_id)
        result = await self.db.execute(query)
        config = result.scalars().first()
        
        if config:
            config.totp_secret = secret
            config.backup_codes = ",".join(backup_codes)
            config.is_verified = False
        else:
            config = TwoFactorConfig(
                user_id=user_id,
                factor_type=TwoFactorType.TOTP.value,
                totp_secret=secret,
                backup_codes=",".join(backup_codes),
                is_enabled=False,
                is_verified=False
            )
            self.db.add(config)
        
        await self.db.commit()
        logger.info(f"用户 {user_id} 设置 TOTP")
        
        return secret, qr_uri, backup_codes
    
    async def verify_and_enable(self, user_id: str, code: str) -> bool:
        """验证并启用 TOTP"""
        query = select(TwoFactorConfig).where(TwoFactorConfig.user_id == user_id)
        result = await self.db.execute(query)
        config = result.scalars().first()
        
        if not config or not config.totp_secret:
            return False
        
        if self.verify_totp(config.totp_secret, code):
            config.is_enabled = True
            config.is_verified = True
            config.last_used_at = datetime.now()
            await self.db.commit()
            
            await self._log_action(user_id, "setup", True)
            logger.info(f"用户 {user_id} 启用 TOTP")
            return True
        
        await self._log_action(user_id, "setup", False)
        return False
    
    async def verify_code(self, user_id: str, code: str, ip: str = None) -> bool:
        """验证登录时的 TOTP 码"""
        query = select(TwoFactorConfig).where(
            TwoFactorConfig.user_id == user_id,
            TwoFactorConfig.is_enabled == True
        )
        result = await self.db.execute(query)
        config = result.scalars().first()
        
        if not config:
            return True  # 未启用 2FA
        
        # 验证 TOTP
        if self.verify_totp(config.totp_secret, code):
            config.last_used_at = datetime.now()
            await self.db.commit()
            await self._log_action(user_id, "verify", True, ip)
            return True
        
        # 验证备用码
        if config.backup_codes:
            codes = config.backup_codes.split(",")
            if code.upper() in codes:
                codes.remove(code.upper())
                config.backup_codes = ",".join(codes)
                config.last_used_at = datetime.now()
                await self.db.commit()
                await self._log_action(user_id, "verify_backup", True, ip)
                logger.info(f"用户 {user_id} 使用备用码验证")
                return True
        
        await self._log_action(user_id, "verify", False, ip)
        return False
    
    async def disable_totp(self, user_id: str, code: str) -> bool:
        """禁用 TOTP"""
        query = select(TwoFactorConfig).where(TwoFactorConfig.user_id == user_id)
        result = await self.db.execute(query)
        config = result.scalars().first()
        
        if not config:
            return False
        
        # 验证码正确才能禁用
        if not self.verify_totp(config.totp_secret, code):
            return False
        
        config.is_enabled = False
        config.totp_secret = None
        config.backup_codes = None
        await self.db.commit()
        
        await self._log_action(user_id, "disable", True)
        logger.info(f"用户 {user_id} 禁用 TOTP")
        return True
    
    async def is_2fa_enabled(self, user_id: str) -> bool:
        """检查是否启用 2FA"""
        query = select(TwoFactorConfig).where(
            TwoFactorConfig.user_id == user_id,
            TwoFactorConfig.is_enabled == True
        )
        result = await self.db.execute(query)
        return result.scalars().first() is not None
    
    async def get_config(self, user_id: str) -> Optional[TwoFactorConfig]:
        """获取 2FA 配置"""
        query = select(TwoFactorConfig).where(TwoFactorConfig.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def regenerate_backup_codes(self, user_id: str, code: str) -> Optional[List[str]]:
        """重新生成备用码"""
        query = select(TwoFactorConfig).where(TwoFactorConfig.user_id == user_id)
        result = await self.db.execute(query)
        config = result.scalars().first()
        
        if not config or not self.verify_totp(config.totp_secret, code):
            return None
        
        new_codes = self.generate_backup_codes()
        config.backup_codes = ",".join(new_codes)
        await self.db.commit()
        
        logger.info(f"用户 {user_id} 重新生成备用码")
        return new_codes
    
    async def _log_action(self, user_id: str, action: str, success: bool, ip: str = None):
        """记录操作日志"""
        log = TwoFactorLog(
            user_id=user_id,
            factor_type=TwoFactorType.TOTP.value,
            action=action,
            success=success,
            ip_address=ip
        )
        self.db.add(log)
        await self.db.commit()


def get_totp_service(db: AsyncSession) -> TOTPService:
    """获取 TOTP 服务"""
    return TOTPService(db)
