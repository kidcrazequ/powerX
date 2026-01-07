"""
PowerX 政策文档模型

创建日期: 2026-01-07
作者: zhi.qu

定义政策法规文档的数据模型，用于 RAG 知识库
"""

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date

from app.core.database import Base


class PolicyDocument(Base):
    """
    政策文档模型
    
    存储电力市场政策法规文档，供 AI 问答使用
    """
    __tablename__ = "policy_documents"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 文档基本信息
    title = Column(String(200), nullable=False, comment="文档标题")
    doc_no = Column(String(100), nullable=True, comment="文号")
    doc_type = Column(String(50), nullable=False, comment="文档类型（法规/规则/通知等）")
    
    # 省份（全国性文档为"全国"）
    province = Column(String(20), nullable=False, default="全国", index=True, comment="适用省份")
    
    # 发布信息
    issuer = Column(String(100), nullable=True, comment="发布机构")
    publish_date = Column(Date, nullable=True, comment="发布日期")
    effective_date = Column(Date, nullable=True, comment="生效日期")
    
    # 文档内容
    content = Column(Text, nullable=False, comment="文档内容")
    summary = Column(Text, nullable=True, comment="内容摘要")
    
    # 关键词（用于检索）
    keywords = Column(String(500), nullable=True, comment="关键词，逗号分隔")
    
    # 向量嵌入 ID（用于 RAG）
    embedding_id = Column(String(100), nullable=True, comment="向量数据库中的嵌入ID")
    
    # 状态
    is_active = Column(String(10), default="YES", comment="是否有效")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    def __repr__(self):
        return f"<PolicyDocument(id={self.id}, title='{self.title[:30]}...')>"


class AIPrediction(Base):
    """
    AI 预测记录模型
    
    存储 AI 预测的历史记录
    """
    __tablename__ = "ai_predictions"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 预测信息
    prediction_type = Column(String(50), nullable=False, comment="预测类型")
    province = Column(String(20), nullable=False, index=True, comment="省份")
    trading_date = Column(Date, nullable=True, comment="交易日期")
    
    # 预测结果（JSON 格式）
    result = Column(Text, nullable=False, comment="预测结果（JSON）")
    
    # 置信度
    confidence = Column(String(20), nullable=True, comment="置信度")
    
    # 评估（与实际对比）
    actual_result = Column(Text, nullable=True, comment="实际结果（JSON）")
    accuracy = Column(String(20), nullable=True, comment="准确度")
    
    # 模型信息
    model_name = Column(String(50), nullable=True, comment="使用的模型")
    model_version = Column(String(20), nullable=True, comment="模型版本")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    def __repr__(self):
        return f"<AIPrediction(id={self.id}, type='{self.prediction_type}', province='{self.province}')>"
