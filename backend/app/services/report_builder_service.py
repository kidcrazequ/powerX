"""
PowerX 报表构建服务
创建日期: 2026-01-07
作者: zhi.qu
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
import random

from app.models.report_template import ReportTemplate, ReportWidget, GeneratedReport


class ReportBuilderService:
    """报表构建服务"""
    
    def __init__(self, db: AsyncSession = None):
        self.db = db
    
    async def create_template(self, name: str, created_by: str, report_type: str = "custom",
                             description: str = None, layout: List = None) -> ReportTemplate:
        """创建报表模板"""
        template = ReportTemplate(
            name=name, created_by=created_by, report_type=report_type,
            description=description, layout=layout or []
        )
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        logger.info(f"创建报表模板: {name}")
        return template
    
    async def get_template(self, template_id: int) -> Optional[ReportTemplate]:
        """获取报表模板"""
        return await self.db.get(ReportTemplate, template_id)
    
    async def list_templates(self, user_id: str = None) -> List[ReportTemplate]:
        """获取模板列表"""
        query = select(ReportTemplate).where(ReportTemplate.is_active == True)
        if user_id:
            query = query.where(
                (ReportTemplate.created_by == user_id) | (ReportTemplate.is_public == True)
            )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_template(self, template_id: int, **kwargs) -> Optional[ReportTemplate]:
        """更新模板"""
        template = await self.get_template(template_id)
        if not template:
            return None
        for key, value in kwargs.items():
            if hasattr(template, key):
                setattr(template, key, value)
        await self.db.commit()
        return template
    
    async def delete_template(self, template_id: int) -> bool:
        """删除模板"""
        template = await self.get_template(template_id)
        if not template:
            return False
        template.is_active = False
        await self.db.commit()
        return True
    
    async def add_widget(self, template_id: int, widget_type: str, title: str,
                        x: int = 0, y: int = 0, w: int = 6, h: int = 4,
                        data_source: str = None, query_config: Dict = None,
                        chart_config: Dict = None) -> ReportWidget:
        """添加报表组件"""
        widget = ReportWidget(
            template_id=template_id, widget_type=widget_type, title=title,
            position_x=x, position_y=y, width=w, height=h,
            data_source=data_source, query_config=query_config or {},
            chart_config=chart_config or {}
        )
        self.db.add(widget)
        await self.db.commit()
        await self.db.refresh(widget)
        return widget
    
    async def get_widgets(self, template_id: int) -> List[ReportWidget]:
        """获取模板的所有组件"""
        query = select(ReportWidget).where(ReportWidget.template_id == template_id)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def generate_report(self, template_id: int, user_id: str,
                             parameters: Dict = None) -> GeneratedReport:
        """生成报表"""
        template = await self.get_template(template_id)
        if not template:
            raise ValueError("模板不存在")
        
        # 获取数据
        data = await self._fetch_report_data(template, parameters or {})
        
        report = GeneratedReport(
            template_id=template_id,
            name=f"{template.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            generated_by=user_id,
            parameters=parameters or {},
            data=data
        )
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        logger.info(f"生成报表: {report.name}")
        return report
    
    async def _fetch_report_data(self, template: ReportTemplate, parameters: Dict) -> Dict:
        """获取报表数据 (模拟)"""
        # 模拟数据
        return {
            "summary": {
                "total_trades": random.randint(100, 500),
                "total_volume": round(random.uniform(10000, 50000), 2),
                "total_amount": round(random.uniform(1000000, 5000000), 2),
                "avg_price": round(random.uniform(300, 500), 2)
            },
            "trends": [
                {"date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                 "volume": round(random.uniform(100, 500), 2),
                 "price": round(random.uniform(300, 500), 2)}
                for i in range(30, 0, -1)
            ],
            "distribution": [
                {"category": "现货交易", "value": random.randint(30, 50)},
                {"category": "中长期交易", "value": random.randint(20, 40)},
                {"category": "合同交易", "value": random.randint(10, 30)}
            ]
        }
    
    def get_available_data_sources(self) -> List[Dict[str, str]]:
        """获取可用数据源"""
        return [
            {"id": "trading_orders", "name": "交易订单", "category": "trading"},
            {"id": "market_prices", "name": "市场价格", "category": "market"},
            {"id": "settlement_records", "name": "结算记录", "category": "settlement"},
            {"id": "contracts", "name": "合同数据", "category": "contract"},
            {"id": "risk_exposure", "name": "风险敞口", "category": "risk"},
            {"id": "position_summary", "name": "持仓汇总", "category": "trading"},
        ]
    
    def get_available_chart_types(self) -> List[Dict[str, str]]:
        """获取可用图表类型"""
        return [
            {"id": "line", "name": "折线图", "icon": "line-chart"},
            {"id": "bar", "name": "柱状图", "icon": "bar-chart"},
            {"id": "pie", "name": "饼图", "icon": "pie-chart"},
            {"id": "area", "name": "面积图", "icon": "area-chart"},
            {"id": "table", "name": "数据表格", "icon": "table"},
            {"id": "stat", "name": "统计卡片", "icon": "number"},
        ]


def get_report_builder_service(db: AsyncSession) -> ReportBuilderService:
    return ReportBuilderService(db)
