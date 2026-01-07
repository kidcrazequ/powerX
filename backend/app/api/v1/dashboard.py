"""
PowerX 仪表盘 API
创建日期: 2026-01-07
作者: zhi.qu
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.api.deps import get_db, get_current_user
from app.services.dashboard_service import DashboardService
from app.schemas.response import APIResponse

router = APIRouter()


class LayoutSave(BaseModel):
    layout: List[Dict] = Field(..., description="布局配置")


class WidgetAdd(BaseModel):
    widget_type: str
    widget_name: str
    config: Dict = Field(default_factory=dict)
    x: int = 0
    y: int = 0


class WidgetUpdate(BaseModel):
    config: Optional[Dict] = None
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None


@router.get("/layout", response_model=APIResponse[Dict[str, Any]])
async def get_layout(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """获取用户仪表盘布局"""
    service = DashboardService(db)
    layout = await service.get_user_layout(current_user.id)
    if not layout:
        return APIResponse.success_response({"layout": [], "widgets": []})
    return APIResponse.success_response({"id": layout.id, "layout": layout.layout, "name": layout.name})


@router.post("/layout", response_model=APIResponse[Dict[str, Any]])
async def save_layout(request: LayoutSave, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """保存仪表盘布局"""
    service = DashboardService(db)
    layout = await service.save_layout(current_user.id, request.layout)
    return APIResponse.success_response({"id": layout.id}, message="布局已保存")


@router.get("/widgets", response_model=APIResponse[List[Dict[str, Any]]])
async def get_widgets(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """获取用户组件列表"""
    service = DashboardService(db)
    widgets = await service.get_user_widgets(current_user.id)
    return APIResponse.success_response([
        {"id": w.id, "type": w.widget_type, "name": w.widget_name, "config": w.config,
         "x": w.position_x, "y": w.position_y, "w": w.width, "h": w.height}
        for w in widgets
    ])


@router.post("/widgets", response_model=APIResponse[Dict[str, Any]])
async def add_widget(request: WidgetAdd, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """添加组件"""
    service = DashboardService(db)
    widget = await service.add_widget(
        current_user.id, request.widget_type, request.widget_name, request.config, request.x, request.y
    )
    return APIResponse.success_response({"id": widget.id}, message="组件已添加")


@router.put("/widgets/{widget_id}", response_model=APIResponse[bool])
async def update_widget(widget_id: int, request: WidgetUpdate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """更新组件"""
    service = DashboardService(db)
    update_data = request.model_dump(exclude_unset=True)
    result = await service.update_widget(widget_id, **update_data)
    if not result:
        raise HTTPException(status_code=404, detail="组件不存在")
    return APIResponse.success_response(True, message="已更新")


@router.delete("/widgets/{widget_id}", response_model=APIResponse[bool])
async def remove_widget(widget_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """移除组件"""
    service = DashboardService(db)
    success = await service.remove_widget(widget_id)
    if not success:
        raise HTTPException(status_code=404, detail="组件不存在")
    return APIResponse.success_response(True, message="已移除")


@router.get("/widgets/available", response_model=APIResponse[List[Dict[str, str]]])
async def get_available_widgets(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """获取可用组件列表"""
    service = DashboardService(db)
    return APIResponse.success_response(service.get_available_widgets())
