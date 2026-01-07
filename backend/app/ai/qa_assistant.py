"""
PowerX 智能问答助手

创建日期: 2026-01-07
作者: zhi.qu

基于 DeepSeek 和知识库的智能问答服务
"""

from typing import Dict, List, Optional

from app.ai.deepseek_client import DeepSeekClient


class QAAssistant:
    """智能问答助手"""
    
    # 知识库索引（模拟）
    KNOWLEDGE_BASE = {
        "电力中长期交易": """
《电力中长期交易基本规则》（发改能源规〔2020〕889号）要点：
1. 交易主体：发电企业、售电公司、电力大用户
2. 交易品种：年度长协、月度竞价、月度双边
3. 交易方式：集中竞价与双边协商相结合
4. 结算规则：按月结算，偏差电量按规则考核
""",
        "现货市场": """
《电力现货市场基本规则》（试行）要点：
1. 市场类型：日前市场、日内市场、实时平衡市场
2. 出清方式：集中优化出清
3. 价格形成：边际成本定价
4. 结算周期：按时段结算（15分钟或1小时）
""",
        "广东": """
广东省电力市场特点：
1. 实行节点电价机制
2. 15分钟结算周期
3. 限价范围：0-1500 元/MWh
4. 不允许负电价
5. 交易中心：广东电力交易中心
""",
        "山东": """
山东省电力市场特点：
1. 统一出清价格机制
2. 允许负电价（最低 -100 元/MWh）
3. 新能源占比高（约 35%）
4. 容量补偿机制
5. 交易中心：山东电力交易中心
""",
        "售电公司": """
《售电公司管理办法》要点：
1. 注册资本要求：不低于 2000 万元
2. 信用保证金：根据代理电量确定
3. 业务范围：代理购电、增值服务
4. 考核机制：偏差电量考核
"""
    }
    
    def __init__(self):
        self.client = DeepSeekClient()
    
    async def answer_question(
        self,
        question: str,
        context: Optional[List[Dict]] = None
    ) -> str:
        """
        回答问题
        
        Args:
            question: 用户问题
            context: 对话上下文
            
        Returns:
            回答内容
        """
        # 检索相关知识
        relevant_knowledge = self._retrieve_knowledge(question)
        
        # 构建提示词
        system_prompt = """你是 PowerX 智能电力交易助手，专注于中国电力市场交易。
你可以帮助用户：
1. 解答电力市场政策和规则问题
2. 分析各省电价走势
3. 提供交易策略建议
4. 解读市场数据

请基于以下知识库信息回答用户问题，如果问题超出知识范围，请诚实告知。

知识库信息：
""" + relevant_knowledge
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加对话上下文
        if context:
            for msg in context[-5:]:  # 只保留最近5轮对话
                messages.append(msg)
        
        messages.append({"role": "user", "content": question})
        
        # 调用 AI
        response = await self.client.chat_completion(messages)
        
        return response["choices"][0]["message"]["content"]
    
    def _retrieve_knowledge(self, question: str) -> str:
        """
        检索相关知识
        
        Args:
            question: 用户问题
            
        Returns:
            相关知识文本
        """
        relevant = []
        
        # 简单关键词匹配
        keywords = {
            "中长期": "电力中长期交易",
            "长协": "电力中长期交易",
            "月度": "电力中长期交易",
            "现货": "现货市场",
            "日前": "现货市场",
            "日内": "现货市场",
            "广东": "广东",
            "山东": "山东",
            "售电": "售电公司",
            "售电公司": "售电公司"
        }
        
        for keyword, topic in keywords.items():
            if keyword in question and topic in self.KNOWLEDGE_BASE:
                if self.KNOWLEDGE_BASE[topic] not in relevant:
                    relevant.append(self.KNOWLEDGE_BASE[topic])
        
        if not relevant:
            # 返回通用知识
            relevant.append(self.KNOWLEDGE_BASE["电力中长期交易"])
            relevant.append(self.KNOWLEDGE_BASE["现货市场"])
        
        return "\n\n".join(relevant)
    
    async def get_policy_interpretation(
        self,
        policy_name: str
    ) -> str:
        """
        获取政策解读
        
        Args:
            policy_name: 政策名称
            
        Returns:
            政策解读内容
        """
        prompt = f"请详细解读《{policy_name}》的主要内容和对电力交易的影响。"
        
        messages = [
            {"role": "system", "content": "你是电力市场政策专家，擅长解读各类电力市场政策法规。"},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.client.chat_completion(messages)
        return response["choices"][0]["message"]["content"]
    
    async def get_market_explanation(
        self,
        province: str,
        topic: str
    ) -> str:
        """
        获取市场解释
        
        Args:
            province: 省份
            topic: 主题
            
        Returns:
            解释内容
        """
        knowledge = self.KNOWLEDGE_BASE.get(province, "")
        
        prompt = f"""请基于以下{province}省电力市场信息，解释{topic}相关内容：

{knowledge}

请给出详细的解释和实际交易建议。"""

        messages = [
            {"role": "system", "content": "你是电力市场分析师，熟悉各省电力交易规则。"},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.client.chat_completion(messages)
        return response["choices"][0]["message"]["content"]
