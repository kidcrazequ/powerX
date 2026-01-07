"""
PowerX 报告 API

创建日期: 2026-01-07
作者: zhi.qu

报告相关 API 端点
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel
from enum import Enum

from app.ai.report_generator import ReportGenerator
from app.api.deps import get_current_user, get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


# ============ 枚举类型 ============

class ReportType(str, Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    ANALYSIS = "ANALYSIS"


class ReportStatus(str, Enum):
    GENERATING = "GENERATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# ============ 请求/响应模型 ============

class ReportGenerateRequest(BaseModel):
    """生成报告请求"""
    report_type: ReportType
    target_date: Optional[date] = None
    include_sections: Optional[List[str]] = None


class ReportResponse(BaseModel):
    """报告响应"""
    id: str
    title: str
    report_type: str
    created_at: str
    status: str
    summary: Optional[str] = None


class ReportDetailResponse(BaseModel):
    """报告详情响应"""
    id: str
    title: str
    report_type: str
    content: str
    created_at: str
    status: str


# ============ API 端点 ============

@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    生成报告
    
    使用 AI 自动生成交易分析报告
    """
    generator = ReportGenerator()
    
    try:
        report = await generator.generate(
            report_type=request.report_type.value,
            target_date=request.target_date or date.today(),
            sections=request.include_sections,
            user_id=current_user.id
        )
        
        return ReportResponse(
            id=report["id"],
            title=report["title"],
            report_type=report["report_type"],
            created_at=report["created_at"],
            status=report["status"],
            summary=report.get("summary")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成失败: {str(e)}")


@router.get("/", response_model=List[ReportResponse])
async def get_reports(
    report_type: Optional[ReportType] = None,
    status: Optional[ReportStatus] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取报告列表
    """
    # 模拟报告数据
    mock_reports = [
        {
            "id": "RPT20260107001",
            "title": "2026年1月第一周交易周报",
            "report_type": "WEEKLY",
            "created_at": "2026-01-07 09:00:00",
            "status": "COMPLETED",
            "summary": "本周累计交易电量 125,000 MWh"
        },
        {
            "id": "RPT20260106001",
            "title": "2026年1月6日交易日报",
            "report_type": "DAILY",
            "created_at": "2026-01-06 20:00:00",
            "status": "COMPLETED",
            "summary": "今日交易电量 18,500 MWh"
        }
    ]
    
    return [
        ReportResponse(
            id=r["id"],
            title=r["title"],
            report_type=r["report_type"],
            created_at=r["created_at"],
            status=r["status"],
            summary=r.get("summary")
        )
        for r in mock_reports
    ]


@router.get("/{report_id}", response_model=ReportDetailResponse)
async def get_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取报告详情
    """
    # 模拟报告内容
    mock_content = """
# 2026年1月第一周交易周报

**生成时间**: 2026-01-07 09:00:00

---

## 一、交易概况

本周累计交易电量 125,000 MWh，交易金额 5,812.5 万元。

## 二、市场分析

日前现货均价 488.32 元/MWh，环比上涨 2.1%。

## 三、AI 建议

建议增加中长期锁定比例，将月度合同占比提高至 75%。
"""
    
    return ReportDetailResponse(
        id=report_id,
        title="2026年1月第一周交易周报",
        report_type="WEEKLY",
        content=mock_content,
        created_at="2026-01-07 09:00:00",
        status="COMPLETED"
    )


@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    format: str = "pdf",
    current_user = Depends(get_current_user)
):
    """
    下载报告
    """
    # 模拟下载链接
    return {
        "download_url": f"/static/reports/{report_id}.{format}",
        "filename": f"report_{report_id}.{format}"
    }


@router.get("/templates")
async def get_report_templates(
    current_user = Depends(get_current_user)
):
    """
    获取报告模板列表
    """
    templates = [
        {
            "id": "daily_standard",
            "name": "标准日报模板",
            "description": "包含交易、行情、风险"
        },
        {
            "id": "weekly_detailed",
            "name": "详细周报模板",
            "description": "含图表和趋势分析"
        },
        {
            "id": "monthly_business",
            "name": "月度经营报告",
            "description": "经营数据全面汇总"
        },
        {
            "id": "market_analysis",
            "name": "市场专题分析",
            "description": "深度行情分析报告"
        }
    ]
    
    return {"templates": templates}
