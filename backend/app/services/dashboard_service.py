"""
PowerX 仪表盘服务
创建日期: 2026-01-07
作者: zhi.qu
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any, Optional
from loguru import logger

from app.models.dashboard_config import DashboardLayout, WidgetConfig


class DashboardService:
    """仪表盘服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_layout(self, user_id: str) -> Optional[DashboardLayout]:
        """获取用户的仪表盘布局"""
        query = select(DashboardLayout).where(
            DashboardLayout.user_id == user_id,
            DashboardLayout.is_active == True
        ).order_by(DashboardLayout.is_default.desc())
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def save_layout(self, user_id: str, layout: List[Dict]) -> DashboardLayout:
        """保存用户布局"""
        existing = await self.get_user_layout(user_id)
        if existing:
            existing.layout = layout
            await self.db.commit()
            return existing
        
        new_layout = DashboardLayout(user_id=user_id, layout=layout, is_default=True)
        self.db.add(new_layout)
        await self.db.commit()
        await self.db.refresh(new_layout)
        logger.info(f"保存仪表盘布局: 用户={user_id}")
        return new_layout
    
    async def get_user_widgets(self, user_id: str) -> List[WidgetConfig]:
        """获取用户的组件配置"""
        query = select(WidgetConfig).where(
            WidgetConfig.user_id == user_id,
            WidgetConfig.is_visible == True
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def add_widget(self, user_id: str, widget_type: str, widget_name: str,
                        config: Dict = None, x: int = 0, y: int = 0) -> WidgetConfig:
        """添加组件"""
        widget = WidgetConfig(
            user_id=user_id, widget_type=widget_type, widget_name=widget_name,
            config=config or {}, position_x=x, position_y=y
        )
        self.db.add(widget)
        await self.db.commit()
        await self.db.refresh(widget)
        return widget
    
    async def update_widget(self, widget_id: int, **kwargs) -> Optional[WidgetConfig]:
        """更新组件配置"""
        widget = await self.db.get(WidgetConfig, widget_id)
        if not widget:
            return None
        for key, value in kwargs.items():
            if hasattr(widget, key):
                setattr(widget, key, value)
        await self.db.commit()
        return widget
    
    async def remove_widget(self, widget_id: int) -> bool:
        """删除组件"""
        widget = await self.db.get(WidgetConfig, widget_id)
        if not widget:
            return False
        widget.is_visible = False
        await self.db.commit()
        return True
    
    def get_available_widgets(self) -> List[Dict[str, str]]:
        """获取可用组件列表"""
        return [
            {"type": "price_chart", "name": "价格走势图", "icon": "line-chart"},
            {"type": "order_list", "name": "订单列表", "icon": "ordered-list"},
            {"type": "position_summary", "name": "持仓汇总", "icon": "pie-chart"},
            {"type": "market_overview", "name": "市场概览", "icon": "dashboard"},
            {"type": "ai_recommendation", "name": "AI推荐", "icon": "robot"},
            {"type": "alert_panel", "name": "预警面板", "icon": "alert"},
            {"type": "exposure_monitor", "name": "敞口监控", "icon": "monitor"},
            {"type": "quick_trade", "name": "快捷交易", "icon": "thunderbolt"},
        ]


def get_dashboard_service(db: AsyncSession) -> DashboardService:
    return DashboardService(db)
