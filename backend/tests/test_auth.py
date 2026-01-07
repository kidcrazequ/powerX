"""
PowerX 认证模块测试

创建日期: 2026-01-07
作者: zhi.qu

测试用户认证相关功能
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token
)


class TestPasswordHashing:
    """密码哈希测试"""
    
    def test_password_hash_is_different(self):
        """测试密码哈希值不同于原密码"""
        password = "test_password_123"
        hashed = get_password_hash(password)
        assert hashed != password
    
    def test_password_verify_success(self):
        """测试密码验证成功"""
        password = "test_password_123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True
    
    def test_password_verify_failure(self):
        """测试密码验证失败"""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)
        assert verify_password(wrong_password, hashed) is False


class TestJWTToken:
    """JWT 令牌测试"""
    
    def test_create_access_token(self):
        """测试创建访问令牌"""
        subject = "1"
        token = create_access_token(subject)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_refresh_token(self):
        """测试创建刷新令牌"""
        subject = "1"
        token = create_refresh_token(subject)
        assert token is not None
        assert isinstance(token, str)
    
    def test_verify_access_token(self):
        """测试验证访问令牌"""
        subject = "123"
        token = create_access_token(subject)
        verified_subject = verify_token(token, token_type="access")
        assert verified_subject == subject
    
    def test_verify_refresh_token(self):
        """测试验证刷新令牌"""
        subject = "123"
        token = create_refresh_token(subject)
        verified_subject = verify_token(token, token_type="refresh")
        assert verified_subject == subject
    
    def test_verify_wrong_token_type(self):
        """测试验证错误的令牌类型"""
        subject = "123"
        access_token = create_access_token(subject)
        # 用 refresh 类型验证 access 令牌
        result = verify_token(access_token, token_type="refresh")
        assert result is None
    
    def test_verify_invalid_token(self):
        """测试验证无效令牌"""
        result = verify_token("invalid_token", token_type="access")
        assert result is None
