"""
PowerX 电子签章服务
创建日期: 2026-01-07
作者: zhi.qu
"""
import uuid
import hashlib
import base64
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.models.digital_signature import (
    DigitalSignature, SignatureCertificate, SignatureStatus
)


class SignatureService:
    """电子签章服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_certificate(
        self,
        user_id: str,
        subject_name: str,
        valid_years: int = 3
    ) -> SignatureCertificate:
        """创建签章证书"""
        certificate_id = f"CERT-{uuid.uuid4().hex[:12].upper()}"
        
        # 模拟生成密钥对
        public_key = base64.b64encode(
            hashlib.sha512(f"{user_id}-{datetime.now()}".encode()).digest()
        ).decode()
        
        certificate = SignatureCertificate(
            certificate_id=certificate_id,
            user_id=user_id,
            subject_name=subject_name,
            issuer="PowerX CA",
            valid_from=datetime.now(),
            valid_until=datetime.now() + timedelta(days=365 * valid_years),
            public_key=public_key,
            is_active=True
        )
        
        self.db.add(certificate)
        await self.db.commit()
        await self.db.refresh(certificate)
        
        logger.info(f"创建签章证书: {certificate_id}")
        return certificate
    
    async def get_certificate(
        self,
        user_id: str
    ) -> Optional[SignatureCertificate]:
        """获取用户证书"""
        query = select(SignatureCertificate).where(
            SignatureCertificate.user_id == user_id,
            SignatureCertificate.is_active == True,
            SignatureCertificate.is_revoked == False
        )
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def sign_document(
        self,
        user_id: str,
        document_id: str,
        document_type: str,
        document_content: bytes
    ) -> DigitalSignature:
        """签署文档"""
        # 获取证书
        certificate = await self.get_certificate(user_id)
        if not certificate:
            raise ValueError("用户没有有效的签章证书")
        
        # 检查证书有效性
        if certificate.valid_until < datetime.now():
            raise ValueError("证书已过期")
        
        signature_id = f"SIG-{uuid.uuid4().hex[:12].upper()}"
        
        # 计算文档哈希
        document_hash = hashlib.sha256(document_content).hexdigest()
        
        # 模拟签名
        signature_data = hashlib.sha512(
            f"{document_hash}-{certificate.public_key}-{datetime.now()}".encode()
        ).digest()
        
        # 模拟时间戳令牌
        timestamp_token = base64.b64encode(
            f"TST-{datetime.now().isoformat()}".encode()
        ).decode()
        
        signature = DigitalSignature(
            signature_id=signature_id,
            document_id=document_id,
            document_type=document_type,
            document_hash=document_hash,
            signer_id=user_id,
            signer_name=certificate.subject_name,
            certificate_id=certificate.certificate_id,
            signature_data=signature_data,
            timestamp_token=timestamp_token,
            status=SignatureStatus.SIGNED.value
        )
        
        self.db.add(signature)
        await self.db.commit()
        await self.db.refresh(signature)
        
        logger.info(f"文档签署: {signature_id}, 文档: {document_id}")
        return signature
    
    async def verify_signature(
        self,
        signature_id: str,
        document_content: bytes,
        verifier_id: str
    ) -> Dict[str, Any]:
        """验证签名"""
        query = select(DigitalSignature).where(
            DigitalSignature.signature_id == signature_id
        )
        result = await self.db.execute(query)
        signature = result.scalars().first()
        
        if not signature:
            return {
                "valid": False,
                "error": "签名不存在"
            }
        
        # 计算文档哈希
        document_hash = hashlib.sha256(document_content).hexdigest()
        
        # 验证哈希
        if signature.document_hash != document_hash:
            return {
                "valid": False,
                "error": "文档已被篡改"
            }
        
        # 获取证书
        cert_query = select(SignatureCertificate).where(
            SignatureCertificate.certificate_id == signature.certificate_id
        )
        cert_result = await self.db.execute(cert_query)
        certificate = cert_result.scalars().first()
        
        if not certificate:
            return {
                "valid": False,
                "error": "证书不存在"
            }
        
        if certificate.is_revoked:
            return {
                "valid": False,
                "error": "证书已被吊销"
            }
        
        # 更新验证状态
        signature.status = SignatureStatus.VERIFIED.value
        signature.verified_at = datetime.now()
        signature.verified_by = verifier_id
        await self.db.commit()
        
        logger.info(f"签名验证通过: {signature_id}")
        
        return {
            "valid": True,
            "signature_id": signature_id,
            "signer_name": signature.signer_name,
            "signed_at": signature.created_at.isoformat(),
            "verified_at": signature.verified_at.isoformat()
        }
    
    async def get_document_signatures(
        self,
        document_id: str
    ) -> List[DigitalSignature]:
        """获取文档的所有签名"""
        query = select(DigitalSignature).where(
            DigitalSignature.document_id == document_id
        ).order_by(DigitalSignature.created_at)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def revoke_certificate(
        self,
        certificate_id: str
    ) -> bool:
        """吊销证书"""
        query = select(SignatureCertificate).where(
            SignatureCertificate.certificate_id == certificate_id
        )
        result = await self.db.execute(query)
        certificate = result.scalars().first()
        
        if not certificate:
            return False
        
        certificate.is_revoked = True
        certificate.is_active = False
        await self.db.commit()
        
        logger.info(f"证书已吊销: {certificate_id}")
        return True


def get_signature_service(db: AsyncSession) -> SignatureService:
    """获取签章服务"""
    return SignatureService(db)
