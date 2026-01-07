/**
 * PowerX AI 助手界面 - 现代深色版
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 提供智能问答、策略推荐、价格预测等 AI 功能
 */

import React, { useState, useRef, useEffect } from 'react';
import { 
  Card, 
  Input, 
  Button, 
  List, 
  Avatar, 
  Typography,
  Space,
  Tabs,
  Spin,
  Tag,
  Row,
  Col,
  Select,
  Statistic,
  Divider,
  message,
  theme,
  Tooltip
} from 'antd';
import { 
  SendOutlined,
  RobotOutlined,
  UserOutlined,
  BulbOutlined,
  LineChartOutlined,
  QuestionCircleOutlined,
  ThunderboltOutlined,
  HistoryOutlined,
  ClearOutlined,
  EllipsisOutlined,
  LikeOutlined,
  DislikeOutlined
} from '@ant-design/icons';
import { PageContainer, ProCard } from '@ant-design/pro-components';
import ReactECharts from 'echarts-for-react';
import { useSettingsStore } from '../stores/settingsStore';
import { NLCommandPanel } from '../components';

const { TextArea } = Input;
const { Text, Paragraph, Title } = Typography;

// 消息类型
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  type?: 'text' | 'prediction' | 'strategy';
}

// 预测结果类型
interface PredictionResult {
  province: string;
  timeRange: string;
  predictions: { time: string; price: number; confidence: number }[];
  summary: string;
}

// 策略推荐类型
interface StrategyRecommendation {
  title: string;
  description: string;
  action: string;
  confidence: number;
  riskLevel: 'low' | 'medium' | 'high';
}

// 模拟 AI 响应
const mockAIResponses: Record<string, string> = {
  '广东电价': '根据最新市场数据分析，广东省现货电价目前呈现以下特点：\n\n1. **当前价格**：485.32 元/MWh，较昨日上涨 2.66%\n2. **价格区间**：今日波动区间 468-512 元/MWh\n3. **主要影响因素**：\n   - 气温升高导致用电负荷增加\n   - 部分火电机组检修\n   - 新能源出力波动\n\n建议关注明日负荷预测，预计峰值电价可能突破 500 元/MWh。',
  '交易策略': '基于当前市场情况，我为您推荐以下交易策略：\n\n📊 **短期策略（现货）**\n- 在低谷时段（0:00-6:00）适量买入\n- 预计价格区间：420-450 元/MWh\n- 建议买入量：100-200 MWh\n\n📈 **中期策略（月度）**\n- 锁定部分基础负荷，签订月度双边\n- 建议比例：总用电量的 60-70%\n- 预期节省：约 3-5%\n\n⚠️ **风险提示**\n- 注意控制现货敞口\n- 关注极端天气预警',
  'default': '感谢您的提问！作为 PowerX AI 助手，我可以帮助您：\n\n1. 🔮 **电价预测** - 分析各省电价走势\n2. 💡 **策略推荐** - 提供个性化交易策略\n3. 📚 **政策解读** - 解答电力市场政策问题\n4. 📊 **风险评估** - 分析交易风险敞口\n\n请问您想了解哪方面的内容？'
};

// 模拟价格预测数据
const mockPrediction: PredictionResult = {
  province: '广东',
  timeRange: '未来24小时',
  predictions: [
    { time: '00:00', price: 445, confidence: 0.85 },
    { time: '04:00', price: 428, confidence: 0.82 },
    { time: '08:00', price: 498, confidence: 0.78 },
    { time: '12:00', price: 512, confidence: 0.75 },
    { time: '16:00', price: 525, confidence: 0.72 },
    { time: '20:00', price: 495, confidence: 0.76 },
  ],
  summary: '预计明日电价将呈现"早晚低、午高"的典型曲线，峰值出现在16:00左右，建议在低谷时段增加采购。'
};

// 模拟策略推荐
const mockStrategies: StrategyRecommendation[] = [
  {
    title: '低谷时段套利策略',
    description: '利用凌晨低价时段买入电力，在早峰售出',
    action: '建议在 0:00-5:00 买入 200 MWh',
    confidence: 0.82,
    riskLevel: 'low'
  },
  {
    title: '日前-实时价差策略',
    description: '日前市场锁定基础量，实时市场灵活调整',
    action: '日前锁定 70%，实时补充 30%',
    confidence: 0.75,
    riskLevel: 'medium'
  },
  {
    title: '跨省价差套利',
    description: '利用广东-浙江价差进行套利交易',
    action: '当价差超过 15 元时执行',
    confidence: 0.68,
    riskLevel: 'high'
  }
];

// 预测图表配置
const getPredictionChartOption = (token: any, themeMode: string) => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: themeMode === 'dark' ? '#1f1f1f' : '#fff',
    borderColor: token.colorBorderSecondary,
    textStyle: { color: token.colorText },
    formatter: (params: any) => {
      const data = params[0];
      return `${data.name}<br/>预测价格: <span style="color:${token.colorPrimary};font-weight:bold">${data.value}</span> 元/MWh<br/>置信度: ${(mockPrediction.predictions.find(p => p.time === data.name)?.confidence || 0) * 100}%`;
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: '10%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: mockPrediction.predictions.map(p => p.time),
    axisLabel: { color: token.colorTextDescription },
    axisLine: { lineStyle: { color: themeMode === 'dark' ? token.colorBorderSecondary : 'rgba(0,0,0,0.15)' } }
  },
  yAxis: {
    type: 'value',
    name: '元/MWh',
    min: 400,
    max: 550,
    axisLine: { show: true, lineStyle: { color: themeMode === 'dark' ? token.colorBorderSecondary : 'rgba(0,0,0,0.15)' } },
    splitLine: { lineStyle: { color: themeMode === 'dark' ? token.colorBorderSecondary : 'rgba(0,0,0,0.06)', type: 'dashed' } },
    axisLabel: { color: token.colorTextDescription }
  },
  series: [
    {
      name: '预测价格',
      type: 'line',
      smooth: true,
      data: mockPrediction.predictions.map(p => p.price),
      lineStyle: { color: token.colorPrimary, width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      itemStyle: { color: token.colorPrimary },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: `${token.colorPrimary}40` },
            { offset: 1, color: `${token.colorPrimary}05` }
          ]
        }
      },
      markPoint: {
        data: [
          { type: 'max', name: '最高', itemStyle: { color: token.colorError } },
          { type: 'min', name: '最低', itemStyle: { color: token.colorSuccess } }
        ]
      }
    }
  ]
});

const AIAssistant: React.FC = () => {
  const { token } = theme.useToken();
  const { themeMode } = useSettingsStore();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: '您好！我是 PowerX AI 助手，基于 DeepSeek 大模型，可以帮助您进行电价预测、策略分析和政策解读。请问有什么可以帮助您的？',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedProvince, setSelectedProvince] = useState('广东');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 发送消息
  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);

    // 模拟 AI 响应延迟
    setTimeout(() => {
      let response = mockAIResponses.default;
      
      // 简单关键词匹配
      if (inputValue.includes('广东') || inputValue.includes('电价')) {
        response = mockAIResponses['广东电价'];
      } else if (inputValue.includes('策略') || inputValue.includes('建议')) {
        response = mockAIResponses['交易策略'];
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
      setLoading(false);
    }, 1500);
  };

  // 快捷问题
  const quickQuestions = [
    '广东明日电价预测',
    '推荐现货交易策略',
    '解读最新电力政策',
    '分析我的持仓风险'
  ];

  // 清空对话
  const handleClear = () => {
    setMessages([{
      id: '1',
      role: 'assistant',
      content: '对话已清空。请问有什么可以帮助您的？',
      timestamp: new Date()
    }]);
    message.success('历史会话已重置');
  };

  return (
    <PageContainer
      header={{
        title: 'AI 交易助手',
        subTitle: '深度学习驱动的电力市场分析终端'
      }}
    >
      <Row gutter={[24, 24]}>
        {/* 左侧：对话区域 */}
        <Col xs={24} lg={14}>
          <Card
            className="hover-card"
            title={
              <Space>
                <div style={{ 
                  width: 28, height: 28, borderRadius: 8, background: `${token.colorPrimary}20`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}>
                  <RobotOutlined style={{ color: token.colorPrimary, fontSize: 16 }} />
                </div>
                <span>智能交互终端</span>
              </Space>
            }
            extra={
              <Space>
                <Tooltip title="导出历史记录">
                  <Button type="text" icon={<HistoryOutlined />} />
                </Tooltip>
                <Tooltip title="重置会话">
                  <Button type="text" icon={<ClearOutlined />} onClick={handleClear} />
                </Tooltip>
              </Space>
            }
            bodyStyle={{ height: 600, display: 'flex', flexDirection: 'column', padding: 0 }}
            style={{ borderRadius: 12, border: 'none' }}
          >
            {/* 消息列表 */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '24px 24px 0' }}>
              <List
                itemLayout="horizontal"
                dataSource={messages}
                renderItem={(msg) => (
                  <div style={{ 
                    display: 'flex', 
                    flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
                    marginBottom: 24,
                    alignItems: 'flex-start'
                  }}>
                    <Avatar 
                      size={36}
                      icon={msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                      style={{ 
                        backgroundColor: msg.role === 'user' ? token.colorPrimary : '#722ed1',
                        flexShrink: 0,
                        boxShadow: '0 4px 8px rgba(0,0,0,0.2)'
                      }}
                    />
                    <div style={{ 
                      maxWidth: '80%', 
                      marginLeft: msg.role === 'user' ? 0 : 12,
                      marginRight: msg.role === 'user' ? 12 : 0,
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start'
                    }}>
                      <div style={{ marginBottom: 4, display: 'flex', alignItems: 'center', gap: 8 }}>
                        {msg.role !== 'user' && <Text strong style={{ fontSize: 13 }}>AI 助手</Text>}
                        <Text type="secondary" style={{ fontSize: 11, fontVariantNumeric: 'tabular-nums' }}>
                          {msg.timestamp.toLocaleTimeString()}
                        </Text>
                        {msg.role === 'user' && <Text strong style={{ fontSize: 13 }}>您</Text>}
                      </div>
                      <div 
                        style={{ 
                          whiteSpace: 'pre-wrap',
                          backgroundColor: msg.role === 'user' ? token.colorPrimary : (themeMode === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.03)'),
                          color: msg.role === 'user' ? '#fff' : token.colorText,
                          padding: '12px 16px',
                          borderRadius: msg.role === 'user' ? '12px 2px 12px 12px' : '2px 12px 12px 12px',
                          fontSize: 14,
                          lineHeight: 1.6,
                          boxShadow: '0 2px 12px rgba(0,0,0,0.05)',
                          border: msg.role === 'user' ? 'none' : `1px solid ${token.colorBorderSecondary}`
                        }}
                      >
                        {msg.content}
                      </div>
                      {msg.role === 'assistant' && msg.id !== '1' && (
                        <div style={{ marginTop: 4, display: 'flex', gap: 12 }}>
                          <Button type="text" size="small" icon={<LikeOutlined />} style={{ fontSize: 11, padding: 0, height: 'auto', color: token.colorTextDescription }}>有用</Button>
                          <Button type="text" size="small" icon={<DislikeOutlined />} style={{ fontSize: 11, padding: 0, height: 'auto', color: token.colorTextDescription }}>无用</Button>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              />
              {loading && (
                <div style={{ display: 'flex', gap: 12, marginBottom: 24 }}>
                  <Avatar icon={<RobotOutlined />} style={{ backgroundColor: '#722ed1' }} />
                  <div style={{ 
                    backgroundColor: themeMode === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.03)', 
                    padding: '12px 20px', 
                    borderRadius: '2px 12px 12px 12px',
                    border: `1px solid ${token.colorBorderSecondary}`
                  }}>
                    <Spin size="small" />
                    <Text style={{ marginLeft: 12, color: token.colorTextDescription }}>AI 正在深度检索实时行情...</Text>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* 底部输入区 */}
            <div style={{ 
              padding: 24, 
              borderTop: `1px solid ${token.colorBorderSecondary}`,
              background: themeMode === 'dark' ? 'rgba(255,255,255,0.01)' : 'rgba(0,0,0,0.01)'
            }}>
              {/* 快捷推荐 */}
              <div style={{ marginBottom: 16 }}>
                <Space wrap size={8}>
                  {quickQuestions.map((q, index) => (
                    <Button 
                      key={index}
                      size="small"
                      style={{ 
                        borderRadius: 16, 
                        fontSize: 12,
                        background: `${token.colorPrimary}10`,
                        borderColor: `${token.colorPrimary}30`,
                        color: token.colorPrimary
                      }}
                      onClick={() => setInputValue(q)}
                    >
                      {q}
                    </Button>
                  ))}
                </Space>
              </div>

              <Space.Compact style={{ width: '100%' }}>
                <TextArea
                  value={inputValue}
                  onChange={e => setInputValue(e.target.value)}
                  placeholder="询问电价预测、交易策略或政策解读..."
                  autoSize={{ minRows: 1, maxRows: 6 }}
                  style={{ 
                    background: themeMode === 'dark' ? 'rgba(255,255,255,0.03)' : '#fff', 
                    borderColor: token.colorBorder,
                    borderRadius: '8px 0 0 8px',
                    padding: '12px 16px'
                  }}
                  onPressEnter={(e) => {
                    if (!e.shiftKey) {
                      e.preventDefault();
                      handleSend();
                    }
                  }}
                />
                <Button 
                  type="primary" 
                  icon={<SendOutlined />} 
                  onClick={handleSend}
                  loading={loading}
                  style={{ 
                    height: 'auto', 
                    padding: '0 24px',
                    borderRadius: '0 8px 8px 0'
                  }}
                >
                  分析
                </Button>
              </Space.Compact>
              <div style={{ marginTop: 12, textAlign: 'center' }}>
                <Text type="secondary" style={{ fontSize: 11 }}>
                  基于 PowerX DeepEnergy 模型 • 实时接入 GD-ISO 交易数据
                </Text>
              </div>
            </div>
          </Card>
        </Col>

        {/* 右侧：功能面板 */}
        <Col xs={24} lg={10}>
          <div style={{ background: themeMode === 'dark' ? 'rgba(255,255,255,0.02)' : 'rgba(0,0,0,0.02)', borderRadius: 12, padding: 4 }}>
            <Tabs 
              defaultActiveKey="prediction" 
              centered
              styles={{ tabPane: { padding: '16px 4px' } }}
            >
              {/* 价格预测 Tab */}
              <Tabs.TabPane
                tab={
                  <Space>
                    <LineChartOutlined />
                    <Text strong>价格预测模型</Text>
                  </Space>
                }
                key="prediction"
              >
                <Card bordered={false} bodyStyle={{ padding: 0 }} style={{ background: 'transparent' }}>
                  <div style={{ padding: '0 16px 20px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                      <Select 
                        value={selectedProvince} 
                        onChange={setSelectedProvince}
                        style={{ width: 100 }}
                        variant="borderless"
                        options={[
                          { value: '广东', label: '广东市场' },
                          { value: '浙江', label: '浙江市场' },
                          { value: '山东', label: '山东市场' }
                        ]}
                      />
                      <Tag color="blue" bordered={false} style={{ margin: 0 }}>{mockPrediction.timeRange}</Tag>
                    </div>

                    <ReactECharts 
                      key={themeMode}
                      option={getPredictionChartOption(token, themeMode)} 
                      style={{ height: 260 }} 
                      theme={themeMode} 
                    />
                    
                    <Row gutter={12} style={{ marginTop: 24 }}>
                      <Col span={8}>
                        <div style={{ background: themeMode === 'dark' ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.02)', padding: 12, borderRadius: 8, textAlign: 'center' }}>
                          <Text type="secondary" style={{ fontSize: 11, display: 'block' }}>预测均价</Text>
                          <Text strong className="data-font" style={{ fontSize: 16 }}>483.50</Text>
                        </div>
                      </Col>
                      <Col span={8}>
                        <div style={{ background: themeMode === 'dark' ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.02)', padding: 12, borderRadius: 8, textAlign: 'center' }}>
                          <Text type="secondary" style={{ fontSize: 11, display: 'block' }}>预测峰值</Text>
                          <Text strong className="data-font" style={{ fontSize: 16, color: token.colorError }}>525.00</Text>
                        </div>
                      </Col>
                      <Col span={8}>
                        <div style={{ background: themeMode === 'dark' ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.02)', padding: 12, borderRadius: 8, textAlign: 'center' }}>
                          <Text type="secondary" style={{ fontSize: 11, display: 'block' }}>置信度</Text>
                          <Text strong className="data-font" style={{ fontSize: 16, color: token.colorSuccess }}>78%</Text>
                        </div>
                      </Col>
                    </Row>

                    <div style={{ 
                      marginTop: 20, padding: 16, borderRadius: 8, 
                      background: themeMode === 'dark' ? 'rgba(250, 173, 20, 0.05)' : 'rgba(250, 173, 20, 0.03)', 
                      border: `1px solid ${token.colorWarning}30`
                    }}>
                      <Space align="start">
                        <BulbOutlined style={{ color: '#faad14', marginTop: 4 }} />
                        <Text style={{ fontSize: 13, color: token.colorTextSecondary }}>{mockPrediction.summary}</Text>
                      </Space>
                    </div>
                  </div>
                </Card>
              </Tabs.TabPane>

              {/* 自然语言交易 Tab */}
              <Tabs.TabPane
                tab={
                  <Space>
                    <ThunderboltOutlined />
                    <Text strong>语音交易</Text>
                  </Space>
                }
                key="nl-trading"
              >
                <div style={{ padding: '0 8px' }}>
                  <NLCommandPanel 
                    onExecute={async (intent) => {
                      // 模拟执行
                      message.success(`命令已接收: ${intent.message}`);
                      return true;
                    }}
                  />
                </div>
              </Tabs.TabPane>

              {/* 策略推荐 Tab */}
              <Tabs.TabPane
                tab={
                  <Space>
                    <BulbOutlined />
                    <Text strong>智能策略库</Text>
                  </Space>
                }
                key="strategy"
              >
                <div style={{ padding: '0 8px' }}>
                  <List
                    dataSource={mockStrategies}
                    renderItem={(strategy) => (
                      <Card 
                        className="hover-card"
                        size="small" 
                        style={{ marginBottom: 16, borderRadius: 10, border: 'none', background: themeMode === 'dark' ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.02)' }}
                        title={
                          <Space>
                            <ThunderboltOutlined style={{ color: token.colorPrimary }} />
                            <Text strong style={{ fontSize: 14 }}>{strategy.title}</Text>
                          </Space>
                        }
                        extra={
                          <Tag bordered={false} color={
                            strategy.riskLevel === 'low' ? 'success' :
                            strategy.riskLevel === 'medium' ? 'warning' : 'error'
                          }>
                            {strategy.riskLevel === 'low' ? '低风险' :
                             strategy.riskLevel === 'medium' ? '中风险' : '高风险'}
                          </Tag>
                        }
                      >
                        <Paragraph style={{ color: token.colorTextDescription, fontSize: 13, marginBottom: 12 }}>
                          {strategy.description}
                        </Paragraph>
                        <div style={{ 
                          padding: '8px 12px', background: `${token.colorPrimary}10`, 
                          borderRadius: 6, border: `1px dashed ${token.colorPrimary}40`
                        }}>
                          <Text strong style={{ color: token.colorPrimary, fontSize: 13 }}>
                            💡 执行：{strategy.action}
                          </Text>
                        </div>
                        <div style={{ marginTop: 8, textAlign: 'right' }}>
                          <Text type="secondary" style={{ fontSize: 11 }}>模型置信度：{(strategy.confidence * 100).toFixed(0)}%</Text>
                        </div>
                      </Card>
                    )}
                  />
                </div>
              </Tabs.TabPane>
            </Tabs>
          </div>
        </Col>
      </Row>
    </PageContainer>
  );
};

export default AIAssistant;
