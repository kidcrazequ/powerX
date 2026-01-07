"""
PowerX 数据导入导出 API

创建日期: 2026-01-07
作者: zhi.qu

数据导入和导出接口
"""

from datetime import datetime, date
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from loguru import logger
import io

from app.api.deps import get_current_user, get_db
from app.services.export_service import ExportService, export_service
from app.services.import_service import ImportService, import_service, ImportError
from app.services.market_service import market_service
from app.schemas.response import success_response

router = APIRouter()


# ============ 请求模型 ============

class ExportRequest(BaseModel):
    """导出请求"""
    data_type: str = Field(..., description="数据类型: orders, contracts, settlements, prices")
    format: str = Field(default="excel", description="导出格式: csv, excel, json")
    province: Optional[str] = Field(None, description="省份筛选")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")


# ============ 导出 API ============

@router.post("/export")
async def export_data(
    request: ExportRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    导出数据
    
    支持导出交易订单、合同、结算记录、市场价格
    """
    logger.info(f"导出数据: type={request.data_type}, format={request.format}")
    
    service = ExportService()
    
    # 根据数据类型获取数据
    if request.data_type == "orders":
        data = _get_mock_orders()
        content = service.export_trading_orders(data)
        filename = f"trading_orders_{datetime.now().strftime('%Y%m%d')}"
        
    elif request.data_type == "contracts":
        data = _get_mock_contracts()
        content = service.export_contracts(data)
        filename = f"contracts_{datetime.now().strftime('%Y%m%d')}"
        
    elif request.data_type == "settlements":
        data = _get_mock_settlements()
        content = service.export_settlement_records(data)
        filename = f"settlements_{datetime.now().strftime('%Y%m%d')}"
        
    elif request.data_type == "prices":
        data = await _get_market_prices(request.province, request.start_date)
        content = service.export_market_prices(data)
        filename = f"market_prices_{datetime.now().strftime('%Y%m%d')}"
        
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的数据类型: {request.data_type}"
        )
    
    # 确定 MIME 类型和扩展名
    if request.format == "csv":
        media_type = "text/csv"
        ext = "csv"
    elif request.format == "json":
        content = service.export_to_json(data)
        media_type = "application/json"
        ext = "json"
    else:
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ext = "xlsx"
    
    return StreamingResponse(
        io.BytesIO(content),
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}.{ext}"
        }
    )


@router.get("/export/templates/{template_type}")
async def get_export_template(
    template_type: str,
    current_user = Depends(get_current_user)
):
    """
    获取导入模板
    """
    logger.info(f"获取导入模板: type={template_type}")
    
    service = ExportService()
    
    if template_type == "orders":
        sample_data = [
            {"订单类型": "日前", "方向": "买入", "数量(MWh)": 100, "价格(元/MWh)": 450, "省份": "广东"},
            {"订单类型": "日前", "方向": "卖出", "数量(MWh)": 50, "价格(元/MWh)": 480, "省份": "广东"}
        ]
        filename = "order_import_template"
        
    elif template_type == "contracts":
        sample_data = [
            {"合同类型": "年度双边", "交易对手": "示例发电企业", "总电量(MWh)": 10000, "单价(元/MWh)": 420, "开始日期": "2026-01-01", "结束日期": "2026-12-31"},
        ]
        filename = "contract_import_template"
        
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的模板类型: {template_type}"
        )
    
    content = service.export_to_excel(sample_data)
    
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}.xlsx"
        }
    )


# ============ 导入 API ============

@router.post("/import")
async def import_data(
    data_type: str = Query(..., description="数据类型: orders, contracts"),
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    导入数据
    
    支持 CSV、Excel、JSON 格式
    """
    logger.info(f"导入数据: type={data_type}, file={file.filename}")
    
    # 读取文件内容
    file_content = await file.read()
    
    try:
        if data_type == "orders":
            success_data, errors = import_service.import_trading_orders(file_content, file.filename)
        elif data_type == "contracts":
            success_data, errors = import_service.import_contracts(file_content, file.filename)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的数据类型: {data_type}"
            )
    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return success_response(
        data={
            "success_count": len(success_data),
            "error_count": len(errors),
            "errors": errors[:10] if errors else []  # 只返回前10条错误
        },
        message=f"导入完成: 成功 {len(success_data)} 条, 失败 {len(errors)} 条"
    )


@router.post("/import/validate")
async def validate_import_file(
    data_type: str = Query(..., description="数据类型"),
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """
    验证导入文件（不实际导入）
    """
    logger.info(f"验证导入文件: type={data_type}, file={file.filename}")
    
    file_content = await file.read()
    
    try:
        if data_type == "orders":
            success_data, errors = import_service.import_trading_orders(file_content, file.filename)
        elif data_type == "contracts":
            success_data, errors = import_service.import_contracts(file_content, file.filename)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的数据类型: {data_type}"
            )
    except ImportError as e:
        return success_response(
            data={
                "valid": False,
                "message": str(e),
                "preview": []
            }
        )
    
    return success_response(
        data={
            "valid": len(errors) == 0,
            "total_rows": len(success_data) + len(errors),
            "valid_rows": len(success_data),
            "error_rows": len(errors),
            "preview": success_data[:5],  # 预览前5条
            "errors": errors[:5]  # 前5条错误
        }
    )


# ============ 辅助函数 ============

def _get_mock_orders() -> List[dict]:
    """获取模拟订单数据"""
    return [
        {"order_id": "ORD-001", "order_type": "日前", "direction": "买入", "quantity": 100, "price": 450.5, "status": "已成交", "created_at": "2026-01-07 09:30:00"},
        {"order_id": "ORD-002", "order_type": "日前", "direction": "卖出", "quantity": 50, "price": 480.0, "status": "部分成交", "created_at": "2026-01-07 10:15:00"},
        {"order_id": "ORD-003", "order_type": "实时", "direction": "买入", "quantity": 30, "price": 520.0, "status": "待成交", "created_at": "2026-01-07 11:00:00"}
    ]


def _get_mock_contracts() -> List[dict]:
    """获取模拟合同数据"""
    return [
        {"contract_id": "CON-001", "contract_type": "年度双边", "counterparty": "粤电集团", "total_quantity": 50000, "price": 420, "start_date": "2026-01-01", "end_date": "2026-12-31", "status": "执行中"},
        {"contract_id": "CON-002", "contract_type": "月度集中", "counterparty": "国电投", "total_quantity": 5000, "price": 450, "start_date": "2026-01-01", "end_date": "2026-01-31", "status": "执行中"}
    ]


def _get_mock_settlements() -> List[dict]:
    """获取模拟结算数据"""
    return [
        {"settlement_id": "SET-001", "period": "2026年1月", "electricity_fee": 450000, "capacity_fee": 25000, "ancillary_fee": 5000, "total_amount": 480000, "status": "已确认"},
        {"settlement_id": "SET-002", "period": "2025年12月", "electricity_fee": 420000, "capacity_fee": 25000, "ancillary_fee": 4500, "total_amount": 449500, "status": "已结算"}
    ]


async def _get_market_prices(province: Optional[str], target_date: Optional[date]) -> List[dict]:
    """获取市场价格数据"""
    prov = province or "guangdong"
    prices = await market_service.get_historical_prices(prov, target_date)
    return prices
