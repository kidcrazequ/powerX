"""
PowerX 报告生成模块

创建日期: 2026-01-07
作者: zhi.qu

自动生成交易分析报告
"""

import uuid
from datetime import date, datetime
from typing import Dict, List, Optional

from app.ai.deepseek_client import DeepSeekClient


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        self.client = DeepSeekClient()
    
    async def generate(
        self,
        report_type: str,
        target_date: Optional[date] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        sections: Optional[List[str]] = None,
        user_id: Optional[int] = None
    ) -> Dict:
        """
        生成报告
        
        Args:
            report_type: 报告类型 (DAILY, WEEKLY, MONTHLY)
            target_date: 目标日期
            start_date: 开始日期
            end_date: 结束日期
            sections: 包含的章节
            user_id: 用户ID
            
        Returns:
            报告信息
        """
        report_id = f"RPT{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
        
        # 确定报告标题和日期范围
        title, date_range = self._get_report_title(report_type, target_date)
        
        # 生成报告内容
        content = await self._generate_content(
            report_type=report_type,
            date_range=date_range,
            sections=sections or ["trading", "market", "risk", "suggestion"]
        )
        
        return {
            "id": report_id,
            "report_id": report_id,
            "title": title,
            "report_type": report_type,
            "content": content,
            "status": "COMPLETED",
            "summary": self._generate_summary(report_type),
            "created_at": datetime.now().isoformat(),
            "generated_at": datetime.now().isoformat()
        }
    
    def _get_report_title(
        self,
        report_type: str,
        target_date: Optional[date]
    ) -> tuple:
        """
        获取报告标题
        """
        today = target_date or date.today()
        
        if report_type == "DAILY":
            title = f"{today.year}年{today.month}月{today.day}日交易日报"
            date_range = f"{today}"
        elif report_type == "WEEKLY":
            week_num = today.isocalendar()[1]
            title = f"{today.year}年{today.month}月第{week_num % 5 or 1}周交易周报"
            date_range = f"第{week_num}周"
        elif report_type == "MONTHLY":
            title = f"{today.year}年{today.month}月交易月报"
            date_range = f"{today.year}年{today.month}月"
        else:
            title = f"{today}专题分析报告"
            date_range = f"{today}"
        
        return title, date_range
    
    async def _generate_content(
        self,
        report_type: str,
        date_range: str,
        sections: List[str]
    ) -> str:
        """
        生成报告内容
        """
        content_parts = []
        
        # 报告头部
        content_parts.append(f"""# {date_range}交易分析报告

**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**生成方式**: AI 自动生成

---
""")
        
        # 交易汇总
        if "trading" in sections:
            content_parts.append("""## 一、交易概况

| 交易类型 | 交易电量(MWh) | 交易金额(万元) | 均价(元/MWh) |
|---------|-------------|--------------|-------------|
| 中长期 | 100,000 | 4,650 | 465.00 |
| 日前现货 | 20,000 | 976 | 488.00 |
| 日内现货 | 5,000 | 246 | 492.00 |
| **合计** | **125,000** | **5,872** | **469.76** |

""")
        
        # 市场分析
        if "market" in sections:
            content_parts.append("""## 二、市场行情分析

### 2.1 价格走势

- **均价**: 488.32 元/MWh，环比上涨 2.1%
- **最高价**: 612.45 元/MWh
- **最低价**: 398.20 元/MWh

### 2.2 影响因素

1. **负荷因素**: 用电负荷同比增长 8.5%
2. **供给因素**: 3台火电机组临时检修
3. **新能源**: 风电出力偏弱，较上周下降 12%

""")
        
        # 持仓分析
        if "position" in sections or "trading" in sections:
            content_parts.append("""## 三、持仓分析

| 合同类型 | 剩余电量(MWh) | 合同价格(元) | 执行进度 |
|---------|-------------|-------------|---------|
| 年度长协 | 41,500 | 465.00 | 17% |
| 月度双边 | 3,800 | 478.50 | 24% |

""")
        
        # 风险评估
        if "risk" in sections:
            content_parts.append("""## 四、风险提示

1. ⚠️ 预计持续低温，电价可能进一步上涨
2. ⚠️ 现货敞口占比达 20%，建议控制在 15% 以内
3. ⚠️ 关注月度竞价，合理安排报价策略

""")
        
        # AI 建议
        if "suggestion" in sections:
            content_parts.append("""## 五、AI 建议

基于当前市场情况，建议：

1. **增加中长期锁定比例**：将月度合同占比提高至 75%
2. **优化现货交易时段**：重点在凌晨低谷时段采购
3. **关注跨省交易机会**：浙江-广东价差有套利空间

""")
        
        # 报告尾部
        content_parts.append("""---

*本报告由 PowerX AI 系统自动生成，仅供参考。*
""")
        
        return "\n".join(content_parts)
    
    def _generate_summary(self, report_type: str) -> str:
        """
        生成报告摘要
        """
        if report_type == "DAILY":
            return "今日交易电量 18,500 MWh，均价 488.32 元/MWh，较昨日上涨 1.2%。"
        elif report_type == "WEEKLY":
            return "本周累计交易电量 125,000 MWh，交易金额 5,812.5 万元，现货占比 20%。"
        elif report_type == "MONTHLY":
            return "本月累计交易电量 520,000 MWh，交易金额 2.42 亿元，完成年度目标进度 8.3%。"
        else:
            return "专题分析报告已生成。"
    
    async def generate_with_ai(
        self,
        report_type: str,
        trading_data: Dict,
        market_data: Dict
    ) -> str:
        """
        使用 AI 生成报告内容
        """
        prompt = f"""请根据以下交易数据生成一份专业的{report_type}交易分析报告：

交易数据：
{trading_data}

市场数据：
{market_data}

请按照以下结构生成报告：
1. 交易概况
2. 市场行情分析
3. 持仓分析
4. 风险提示
5. 交易建议"""

        messages = [
            {"role": "system", "content": "你是专业的电力交易分析师，擅长撰写交易分析报告。"},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.client.chat_completion(messages, max_tokens=3000)
        return response["choices"][0]["message"]["content"]
