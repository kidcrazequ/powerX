"""
PowerX 电子签章 API
创建日期: 2026-01-07
作者: zhi.qu
"""
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.signature_service import get_signature_service

router = APIRouter(prefix="/signatures", tags=["电子签章"])


class CreateCertificateRequest(BaseModel):
    """创建证书请求"""
    subject_name: str
    valid_years: int = 3


class SignDocumentRequest(BaseModel):
    """签署文档请求"""
    document_id: str
    document_type: str


class CertificateResponse(BaseModel):
    """证书响应"""
    certificate_id: str
    subject_name: str
    issuer: str
    valid_from: datetime
    valid_until: datetime
    is_active: bool


class SignatureResponse(BaseModel):
    """签名响应"""
    signature_id: str
    document_id: str
    document_type: str
    signer_name: str
    status: str
    created_at: datetime


@router.post("/certificates", response_model=CertificateResponse)
async def create_certificate(
    request: CreateCertificateRequest,
    db: AsyncSession = Depends(get_db)
):
    """创建签章证书"""
    service = get_signature_service(db)
    
    certificate = await service.create_certificate(
        user_id="user-001",
        subject_name=request.subject_name,
        valid_years=request.valid_years
    )
    
    return CertificateResponse(
        certificate_id=certificate.certificate_id,
        subject_name=certificate.subject_name,
        issuer=certificate.issuer,
        valid_from=certificate.valid_from,
        valid_until=certificate.valid_until,
        is_active=certificate.is_active
    )


@router.get("/certificates/me", response_model=CertificateResponse)
async def get_my_certificate(
    db: AsyncSession = Depends(get_db)
):
    """获取我的证书"""
    service = get_signature_service(db)
    certificate = await service.get_certificate(user_id="user-001")
    
    if not certificate:
        raise HTTPException(status_code=404, detail="没有有效的证书")
    
    return CertificateResponse(
        certificate_id=certificate.certificate_id,
        subject_name=certificate.subject_name,
        issuer=certificate.issuer,
        valid_from=certificate.valid_from,
        valid_until=certificate.valid_until,
        is_active=certificate.is_active
    )


@router.post("/sign", response_model=SignatureResponse)
async def sign_document(
    document_id: str,
    document_type: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """签署文档"""
    service = get_signature_service(db)
    
    # 读取文件内容
    content = await file.read()
    
    try:
        signature = await service.sign_document(
            user_id="user-001",
            document_id=document_id,
            document_type=document_type,
            document_content=content
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return SignatureResponse(
        signature_id=signature.signature_id,
        document_id=signature.document_id,
        document_type=signature.document_type,
        signer_name=signature.signer_name,
        status=signature.status,
        created_at=signature.created_at
    )


@router.post("/verify/{signature_id}")
async def verify_signature(
    signature_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """验证签名"""
    service = get_signature_service(db)
    
    content = await file.read()
    
    result = await service.verify_signature(
        signature_id=signature_id,
        document_content=content,
        verifier_id="user-001"
    )
    
    return result


@router.get("/documents/{document_id}", response_model=List[SignatureResponse])
async def get_document_signatures(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取文档的签名记录"""
    service = get_signature_service(db)
    signatures = await service.get_document_signatures(document_id)
    
    return [
        SignatureResponse(
            signature_id=s.signature_id,
            document_id=s.document_id,
            document_type=s.document_type,
            signer_name=s.signer_name,
            status=s.status,
            created_at=s.created_at
        )
        for s in signatures
    ]


@router.post("/certificates/{certificate_id}/revoke")
async def revoke_certificate(
    certificate_id: str,
    db: AsyncSession = Depends(get_db)
):
    """吊销证书"""
    service = get_signature_service(db)
    success = await service.revoke_certificate(certificate_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="证书不存在")
    
    return {"success": True, "message": "证书已吊销"}
