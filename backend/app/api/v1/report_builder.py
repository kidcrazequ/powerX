"""
PowerX 报表构建 API
创建日期: 2026-01-07
作者: zhi.qu
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.api.deps import get_db, get_current_user
from app.services.report_builder_service import ReportBuilderService
from app.schemas.response import APIResponse

router = APIRouter()


class TemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    report_type: str = "custom"
    layout: List[Dict] = Field(default_factory=list)


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    layout: Optional[List[Dict]] = None
    is_public: Optional[bool] = None


class WidgetCreate(BaseModel):
    widget_type: str
    title: str
    x: int = 0
    y: int = 0
    w: int = 6
    h: int = 4
    data_source: Optional[str] = None
    query_config: Dict = Field(default_factory=dict)
    chart_config: Dict = Field(default_factory=dict)


class ReportGenerate(BaseModel):
    parameters: Dict = Field(default_factory=dict)


@router.get("/templates", response_model=APIResponse[List[Dict[str, Any]]])
async def list_templates(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """获取报表模板列表"""
    service = ReportBuilderService(db)
    templates = await service.list_templates(current_user.id)
    return APIResponse.success_response([
        {"id": t.id, "name": t.name, "description": t.description, 
         "type": t.report_type, "is_public": t.is_public, "created_by": t.created_by}
        for t in templates
    ])


@router.post("/templates", response_model=APIResponse[Dict[str, Any]])
async def create_template(request: TemplateCreate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """创建报表模板"""
    service = ReportBuilderService(db)
    template = await service.create_template(
        name=request.name, created_by=current_user.id, report_type=request.report_type,
        description=request.description, layout=request.layout
    )
    return APIResponse.success_response({"id": template.id, "name": template.name}, message="模板已创建")


@router.get("/templates/{template_id}", response_model=APIResponse[Dict[str, Any]])
async def get_template(template_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """获取模板详情"""
    service = ReportBuilderService(db)
    template = await service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    widgets = await service.get_widgets(template_id)
    return APIResponse.success_response({
        "id": template.id, "name": template.name, "description": template.description,
        "type": template.report_type, "layout": template.layout, "is_public": template.is_public,
        "widgets": [{"id": w.id, "type": w.widget_type, "title": w.title,
                    "x": w.position_x, "y": w.position_y, "w": w.width, "h": w.height,
                    "data_source": w.data_source, "query_config": w.query_config,
                    "chart_config": w.chart_config} for w in widgets]
    })


@router.put("/templates/{template_id}", response_model=APIResponse[bool])
async def update_template(template_id: int, request: TemplateUpdate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """更新模板"""
    service = ReportBuilderService(db)
    update_data = request.model_dump(exclude_unset=True)
    result = await service.update_template(template_id, **update_data)
    if not result:
        raise HTTPException(status_code=404, detail="模板不存在")
    return APIResponse.success_response(True, message="已更新")


@router.delete("/templates/{template_id}", response_model=APIResponse[bool])
async def delete_template(template_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """删除模板"""
    service = ReportBuilderService(db)
    success = await service.delete_template(template_id)
    if not success:
        raise HTTPException(status_code=404, detail="模板不存在")
    return APIResponse.success_response(True, message="已删除")


@router.post("/templates/{template_id}/widgets", response_model=APIResponse[Dict[str, Any]])
async def add_widget(template_id: int, request: WidgetCreate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """添加组件到模板"""
    service = ReportBuilderService(db)
    widget = await service.add_widget(
        template_id, request.widget_type, request.title,
        request.x, request.y, request.w, request.h,
        request.data_source, request.query_config, request.chart_config
    )
    return APIResponse.success_response({"id": widget.id}, message="组件已添加")


@router.post("/templates/{template_id}/generate", response_model=APIResponse[Dict[str, Any]])
async def generate_report(template_id: int, request: ReportGenerate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """生成报表"""
    service = ReportBuilderService(db)
    try:
        report = await service.generate_report(template_id, current_user.id, request.parameters)
        return APIResponse.success_response({
            "id": report.id, "name": report.name, "data": report.data
        }, message="报表已生成")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/data-sources", response_model=APIResponse[List[Dict[str, str]]])
async def get_data_sources(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """获取可用数据源"""
    service = ReportBuilderService(db)
    return APIResponse.success_response(service.get_available_data_sources())


@router.get("/chart-types", response_model=APIResponse[List[Dict[str, str]]])
async def get_chart_types(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """获取可用图表类型"""
    service = ReportBuilderService(db)
    return APIResponse.success_response(service.get_available_chart_types())
