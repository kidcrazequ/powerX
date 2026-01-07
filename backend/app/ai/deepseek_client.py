"""
PowerX DeepSeek API 客户端

创建日期: 2026-01-07
作者: zhi.qu

封装 DeepSeek API 调用
"""

import httpx
from typing import List, Dict, Optional, AsyncGenerator
import json

from app.core.config import settings


class DeepSeekClient:
    """DeepSeek API 客户端"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化客户端
        
        Args:
            api_key: API密钥，默认从配置读取
            base_url: API基础URL，默认从配置读取
        """
        self.api_key = api_key or settings.DEEPSEEK_API_KEY
        self.base_url = (base_url or settings.DEEPSEEK_BASE_URL).rstrip("/") + "/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> Dict:
        """
        聊天补全
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            stream: 是否流式输出
            
        Returns:
            API响应
        """
        # 如果没有 API key，返回模拟响应
        if not self.api_key or self.api_key == "your-deepseek-api-key":
            return self._mock_response(messages)
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"API 调用失败: {response.status_code} - {response.text}")
            
            return response.json()
    
    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncGenerator[str, None]:
        """
        流式聊天补全
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            
        Yields:
            响应内容片段
        """
        if not self.api_key or self.api_key == "your-deepseek-api-key":
            yield self._mock_response(messages)["choices"][0]["message"]["content"]
            return
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            content = chunk["choices"][0].get("delta", {}).get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
    
    def _mock_response(self, messages: List[Dict[str, str]]) -> Dict:
        """
        生成模拟响应（用于演示）
        
        Args:
            messages: 消息列表
            
        Returns:
            模拟的 API 响应
        """
        last_message = messages[-1]["content"] if messages else ""
        
        # 根据问题类型生成不同的模拟回复
        if "电价" in last_message or "价格" in last_message:
            content = """根据最新市场数据分析，广东省现货电价呈现以下特点：

1. **当前价格**：485.32 元/MWh，较昨日上涨 2.66%
2. **价格区间**：今日波动区间 468-512 元/MWh
3. **主要影响因素**：
   - 气温升高导致用电负荷增加
   - 部分火电机组检修
   - 新能源出力波动

**预测**: 预计明日电价将维持在 480-510 元/MWh 区间。建议在低谷时段（0:00-6:00）适量买入。"""

        elif "策略" in last_message or "建议" in last_message:
            content = """基于当前市场情况，我为您推荐以下交易策略：

📊 **短期策略（现货）**
- 在低谷时段（0:00-6:00）适量买入
- 预计价格区间：420-450 元/MWh
- 建议买入量：100-200 MWh

📈 **中期策略（月度）**
- 锁定部分基础负荷，签订月度双边
- 建议比例：总用电量的 60-70%
- 预期节省：约 3-5%

⚠️ **风险提示**
- 注意控制现货敞口
- 关注极端天气预警"""

        elif "政策" in last_message or "规则" in last_message:
            content = """根据《电力中长期交易基本规则》（发改能源规〔2020〕889号），当前主要政策要点如下：

1. **交易主体**：发电企业、售电公司、电力大用户均可参与
2. **交易品种**：年度长协、月度竞价、月度双边
3. **交易方式**：集中竞价与双边协商相结合
4. **结算规则**：按月结算，偏差电量按规则考核

广东省特别规定：
- 实行节点电价机制
- 15分钟结算周期
- 限价范围：0-1500 元/MWh

如需了解更多详情，请告诉我您具体关注哪方面的政策。"""

        else:
            content = """感谢您的提问！作为 PowerX AI 助手，我可以帮助您：

1. 🔮 **电价预测** - 分析各省电价走势
2. 💡 **策略推荐** - 提供个性化交易策略
3. 📚 **政策解读** - 解答电力市场政策问题
4. 📊 **风险评估** - 分析交易风险敞口

请问您想了解哪方面的内容？"""

        return {
            "id": "mock-response",
            "object": "chat.completion",
            "created": 1704614400,
            "model": "deepseek-chat",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": content
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 200,
                "total_tokens": 300
            }
        }
