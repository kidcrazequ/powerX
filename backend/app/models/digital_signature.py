"""
PowerX 电子签章模型
创建日期: 2026-01-07
作者: zhi.qu
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, LargeBinary
from sqlalchemy.sql import func
from enum import Enum

from app.core.database import Base


class SignatureStatus(str, Enum):
    """签章状态"""
    PENDING = "pending"
    SIGNED = "signed"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class DigitalSignature(Base):
    """电子签章记录"""
    
    __tablename__ = "digital_signatures"
    
    id = Column(Integer, primary_key=True, index=True)
    signature_id = Column(String(50), unique=True, index=True)
    
    # 文档信息
    document_id = Column(String(50), index=True)  # 关联的合同/文档ID
    document_type = Column(String(50))  # contract/agreement/report
    document_hash = Column(String(100))  # 文档哈希
    
    # 签署人
    signer_id = Column(String(50), index=True)
    signer_name = Column(String(100))
    
    # 签章信息
    certificate_id = Column(String(100))  # 证书ID
    signature_data = Column(LargeBinary)  # 签名数据
    
    # 时间戳
    timestamp_token = Column(Text)  # 时间戳令牌
    
    # 状态
    status = Column(String(20), default=SignatureStatus.PENDING.value)
    
    # 验证信息
    verified_at = Column(DateTime(timezone=True))
    verified_by = Column(String(50))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SignatureCertificate(Base):
    """签章证书"""
    
    __tablename__ = "signature_certificates"
    
    id = Column(Integer, primary_key=True, index=True)
    certificate_id = Column(String(50), unique=True, index=True)
    
    user_id = Column(String(50), index=True)
    
    # 证书信息
    subject_name = Column(String(200))  # 主体名称
    issuer = Column(String(200))  # 颁发机构
    
    # 有效期
    valid_from = Column(DateTime(timezone=True))
    valid_until = Column(DateTime(timezone=True))
    
    # 公钥
    public_key = Column(Text)
    
    # 状态
    is_active = Column(Boolean, default=True)
    is_revoked = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
