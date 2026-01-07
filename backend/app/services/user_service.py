"""
PowerX 用户服务

创建日期: 2026-01-07
作者: zhi.qu

提供用户注册、登录、信息管理等功能
"""

from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.models.participant import MarketParticipant
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.core.constants import ParticipantType, UserLevel


class UserService:
    """用户服务类"""
    
    def __init__(self, db: AsyncSession):
        """
        初始化用户服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    async def get_by_id(self, user_id: int) -> Optional[MarketParticipant]:
        """
        根据 ID 获取用户
        
        Args:
            user_id: 用户 ID
            
        Returns:
            Optional[MarketParticipant]: 用户对象或 None
        """
        result = await self.db.execute(
            select(MarketParticipant).where(MarketParticipant.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[MarketParticipant]:
        """
        根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            Optional[MarketParticipant]: 用户对象或 None
        """
        result = await self.db.execute(
            select(MarketParticipant).where(MarketParticipant.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[MarketParticipant]:
        """
        根据邮箱获取用户
        
        Args:
            email: 邮箱
            
        Returns:
            Optional[MarketParticipant]: 用户对象或 None
        """
        result = await self.db.execute(
            select(MarketParticipant).where(MarketParticipant.email == email)
        )
        return result.scalar_one_or_none()
    
    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        name: str,
        participant_type: ParticipantType,
        province: str = "广东"
    ) -> MarketParticipant:
        """
        创建新用户
        
        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            name: 企业/机构名称
            participant_type: 参与主体类型
            province: 所属省份
            
        Returns:
            MarketParticipant: 创建的用户对象
        """
        logger.info(f"创建用户: username={username}, type={participant_type}")
        
        user = MarketParticipant(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            name=name,
            participant_type=participant_type,
            province=province,
            level=UserLevel.BEGINNER,
            is_active=True,
            is_verified=False
        )
        
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        
        logger.info(f"用户创建成功: user_id={user.id}")
        return user
    
    async def authenticate(self, username: str, password: str) -> Optional[MarketParticipant]:
        """
        验证用户凭据
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            Optional[MarketParticipant]: 验证成功返回用户对象，失败返回 None
        """
        user = await self.get_by_username(username)
        if user is None:
            logger.warning(f"用户不存在: username={username}")
            return None
        
        if not verify_password(password, user.hashed_password):
            logger.warning(f"密码验证失败: username={username}")
            return None
        
        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        await self.db.flush()
        
        logger.info(f"用户认证成功: user_id={user.id}")
        return user
    
    async def update_user(
        self,
        user: MarketParticipant,
        **kwargs
    ) -> MarketParticipant:
        """
        更新用户信息
        
        Args:
            user: 用户对象
            **kwargs: 要更新的字段
            
        Returns:
            MarketParticipant: 更新后的用户对象
        """
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        await self.db.flush()
        await self.db.refresh(user)
        
        logger.info(f"用户信息更新: user_id={user.id}")
        return user
    
    async def change_password(
        self,
        user: MarketParticipant,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        修改密码
        
        Args:
            user: 用户对象
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            bool: 是否成功
        """
        if not verify_password(old_password, user.hashed_password):
            logger.warning(f"旧密码验证失败: user_id={user.id}")
            return False
        
        user.hashed_password = get_password_hash(new_password)
        await self.db.flush()
        
        logger.info(f"密码修改成功: user_id={user.id}")
        return True
    
    def create_tokens(self, user: MarketParticipant) -> dict:
        """
        为用户创建访问令牌和刷新令牌
        
        Args:
            user: 用户对象
            
        Returns:
            dict: 包含 access_token 和 refresh_token
        """
        access_token = create_access_token(
            subject=str(user.id),
            additional_claims={
                "username": user.username,
                "participant_type": user.participant_type.value,
                "level": user.level.value
            }
        )
        refresh_token = create_refresh_token(subject=str(user.id))
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
