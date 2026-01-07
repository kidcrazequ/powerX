/**
 * PowerX 电力交易仪表盘
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 展示交易概览、市场数据、持仓信息和 AI 助手入口
 */

import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Statistic, 
  Table, 
  Tag, 
  Progress,
  Typography,
  Space,
  Button,
  Tooltip,
  Alert,
  theme
} from 'antd';
import { 
  ArrowUpOutlined, 
  ArrowDownOutlined,
  ThunderboltOutlined,
  LineChartOutlined,
  BarChartOutlined,
  AlertOutlined,
  RobotOutlined,
  SyncOutlined,
  FileTextOutlined
} from '@ant-design/icons';
import { PageContainer, StatisticCard } from '@ant-design/pro-components';
import { useNavigate } from 'react-router-dom';
import ReactECharts from 'echarts-for-react';
import { useSettingsStore } from '../stores/settingsStore';
import { AIRecommendation, AnomalyAlert } from '../components';

const { Title, Text } = Typography;

// 模拟市场数据
const mockMarketData = {
  currentPrice: 485.32,
  priceChange: 12.58,
  priceChangePercent: 2.66,
  highPrice: 512.45,
  lowPrice: 468.20,
  avgPrice: 492.18,
  volume: 125840,
  timestamp: new Date().toLocaleString('zh-CN')
};

// 模拟持仓数据
const mockPositions = [
  { 
    id: 1, 
    contract: '广东现货2026Q1', 
    direction: '买入', 
    quantity: 500, 
    avgPrice: 478.50,
    currentPrice: 485.32,
    pnl: 3410,
    pnlPercent: 1.42
  },
  { 
    id: 2, 
    contract: '浙江中长期月度', 
    direction: '卖出', 
    quantity: 300, 
    avgPrice: 495.00,
    currentPrice: 488.15,
    pnl: 2055,
    pnlPercent: 1.38
  },
  { 
    id: 3, 
    contract: '山东日前现货', 
    direction: '买入', 
    quantity: 200, 
    avgPrice: 452.30,
    currentPrice: 448.90,
    pnl: -680,
    pnlPercent: -0.75
  }
];

// 模拟风险告警
const mockAlerts = [
  { level: 'warning', message: '广东现货价格波动较大，建议关注风险敞口' },
  { level: 'info', message: '山东省明日预计新能源出力增加，电价可能下降' }
];

// 价格走势图配置
const getPriceChartOption = (token: any, themeMode: string) => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'cross' },
    backgroundColor: themeMode === 'dark' ? 'rgba(20, 20, 20, 0.9)' : 'rgba(255, 255, 255, 0.9)',
    borderColor: token.colorBorderSecondary,
    textStyle: { color: token.colorText }
  },
  legend: {
    data: ['广东', '浙江', '山东'],
    top: 0,
    textStyle: { color: token.colorTextSecondary }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: '15%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
    axisLabel: { color: token.colorTextDescription },
    axisLine: { lineStyle: { color: themeMode === 'dark' ? token.colorBorderSecondary : 'rgba(0,0,0,0.15)' } }
  },
  yAxis: {
    type: 'value',
    name: '元/MWh',
    min: 400,
    max: 600,
    axisLabel: { color: token.colorTextDescription },
    nameTextStyle: { color: token.colorTextDescription },
    axisLine: { show: true, lineStyle: { color: themeMode === 'dark' ? token.colorBorderSecondary : 'rgba(0,0,0,0.15)' } },
    splitLine: { lineStyle: { color: themeMode === 'dark' ? token.colorBorderSecondary : 'rgba(0,0,0,0.06)', type: 'dashed' } }
  },
  series: [
    {
      name: '广东',
      type: 'line',
      smooth: true,
      data: [468, 445, 512, 498, 485, 520, 485],
      lineStyle: { color: token.colorPrimary, width: 2 },
      itemStyle: { color: token.colorPrimary },
      areaStyle: { 
        color: { 
          type: 'linear', 
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: `${token.colorPrimary}40` },
            { offset: 1, color: `${token.colorPrimary}00` }
          ]
        }
      }
    },
    {
      name: '浙江',
      type: 'line',
      smooth: true,
      data: [478, 455, 502, 488, 495, 510, 492],
      lineStyle: { color: token.colorSuccess, width: 2 },
      itemStyle: { color: token.colorSuccess }
    },
    {
      name: '山东',
      type: 'line',
      smooth: true,
      data: [452, 438, 485, 475, 468, 490, 449],
      lineStyle: { color: token.colorWarning, width: 2 },
      itemStyle: { color: token.colorWarning }
    }
  ]
});

// 成交量图配置
const getVolumeChartOption = (token: any, themeMode: string) => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: themeMode === 'dark' ? 'rgba(20, 20, 20, 0.9)' : 'rgba(255, 255, 255, 0.9)',
    borderColor: token.colorBorderSecondary,
    textStyle: { color: token.colorText }
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
    data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    axisLabel: { color: token.colorTextDescription },
    axisLine: { lineStyle: { color: themeMode === 'dark' ? token.colorBorderSecondary : 'rgba(0,0,0,0.15)' } }
  },
  yAxis: {
    type: 'value',
    name: 'MWh',
    axisLabel: { color: token.colorTextDescription },
    nameTextStyle: { color: token.colorTextDescription },
    axisLine: { show: true, lineStyle: { color: themeMode === 'dark' ? token.colorBorderSecondary : 'rgba(0,0,0,0.15)' } },
    splitLine: { lineStyle: { color: themeMode === 'dark' ? token.colorBorderSecondary : 'rgba(0,0,0,0.06)', type: 'dashed' } }
  },
  series: [
    {
      name: '成交量',
      type: 'bar',
      data: [12580, 15420, 14230, 16890, 15840, 8920, 7650],
      itemStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ]
        },
        borderRadius: [4, 4, 0, 0]
      }
    }
  ]
});

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const { token } = theme.useToken();
  const { themeMode } = useSettingsStore();

  // 持仓表格列定义
  const positionColumns = [
    { 
      title: '合约', 
      dataIndex: 'contract', 
      key: 'contract',
      render: (text: string) => <Text strong>{text}</Text>
    },
    { 
      title: '方向', 
      dataIndex: 'direction', 
      key: 'direction',
      render: (direction: string) => (
        <Tag color={direction === '买入' ? 'green' : 'red'} bordered={false}>{direction}</Tag>
      )
    },
    { 
      title: '持仓量(MWh)', 
      dataIndex: 'quantity', 
      key: 'quantity',
      render: (val: number) => <span className="data-font">{val.toLocaleString()}</span>
    },
    { 
      title: '均价(元)', 
      dataIndex: 'avgPrice', 
      key: 'avgPrice',
      render: (val: number) => <span className="data-font">{val.toFixed(2)}</span>
    },
    { 
      title: '现价(元)', 
      dataIndex: 'currentPrice', 
      key: 'currentPrice',
      render: (val: number) => <span className="data-font">{val.toFixed(2)}</span>
    },
    { 
      title: '盈亏(元)', 
      dataIndex: 'pnl', 
      key: 'pnl',
      render: (pnl: number, record: any) => (
        <Space>
          <Text strong type={pnl >= 0 ? 'success' : 'danger'} className="data-font">
            {pnl >= 0 ? '+' : ''}{pnl.toLocaleString()}
          </Text>
          <Text type={pnl >= 0 ? 'success' : 'danger'} style={{ fontSize: 12 }}>
            ({record.pnlPercent >= 0 ? '+' : ''}{record.pnlPercent.toFixed(2)}%)
          </Text>
        </Space>
      )
    }
  ];

  // 刷新数据
  const handleRefresh = () => {
    setLoading(true);
    setTimeout(() => setLoading(false), 1000);
  };

  return (
    <PageContainer
      header={{
        title: '交易控制台',
        subTitle: '实时能源市场分析与自动交易监控',
        extra: [
          <Button key="refresh" icon={<SyncOutlined spin={loading} />} onClick={handleRefresh}>
            刷新数据
          </Button>,
          <Button 
            key="ai" 
            type="primary" 
            icon={<RobotOutlined />}
            onClick={() => navigate('/ai')}
            style={{ boxShadow: `0 4px 12px ${token.colorPrimary}40` }}
          >
            AI 智能建议
          </Button>
        ]
      }}
    >
      {/* 风险告警 */}
      <div style={{ marginBottom: 24 }}>
        {mockAlerts.map((alert, index) => (
          <Alert
            key={index}
            message={<Text strong>{alert.message}</Text>}
            type={alert.level as 'warning' | 'info'}
            showIcon
            closable
            style={{ 
              marginBottom: 12, 
              borderRadius: 8,
              border: 'none',
              background: alert.level === 'warning' 
                ? (themeMode === 'dark' ? 'rgba(250, 173, 20, 0.15)' : 'rgba(250, 173, 20, 0.05)')
                : (themeMode === 'dark' ? 'rgba(22, 119, 255, 0.15)' : 'rgba(22, 119, 255, 0.05)'),
              backdropFilter: 'blur(4px)'
            }}
          />
        ))}
      </div>

          <Row gutter={[20, 20]}>
            <Col xs={24} sm={12} lg={6} className="animate-in" style={{ animationDelay: '0.1s' }}>
              <StatisticCard
                className="hover-card"
                statistic={{
                  title: <Text type="secondary">广东现货价格</Text>,
                  value: mockMarketData.currentPrice,
                  suffix: <Text style={{ fontSize: 14, marginLeft: 4 }}>元/MWh</Text>,
                  description: (
                    <Space>
                      {mockMarketData.priceChange >= 0 ? 
                        <ArrowUpOutlined className="price-up" /> : 
                        <ArrowDownOutlined className="price-down" />
                      }
                      <Text className={`data-font ${mockMarketData.priceChange >= 0 ? 'price-up' : 'price-down'}`}>
                        {mockMarketData.priceChange >= 0 ? '+' : ''}{mockMarketData.priceChange} 
                        ({mockMarketData.priceChangePercent}%)
                      </Text>
                    </Space>
                  )
                }}
                chart={
                  <Progress 
                    percent={(mockMarketData.currentPrice - 400) / 2} 
                    showInfo={false}
                    strokeColor={{ '0%': token.colorPrimary, '100%': token.colorInfoActive }}
                    trailColor={themeMode === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)'}
                    size="small"
                  />
                }
                style={{ borderRadius: 12 }}
              />
            </Col>
            <Col xs={24} sm={12} lg={6} className="animate-in" style={{ animationDelay: '0.2s' }}>
              <StatisticCard
                className="hover-card"
                statistic={{
                  title: <Text type="secondary">今日成交总量</Text>,
                  value: mockMarketData.volume,
                  suffix: <Text style={{ fontSize: 14, marginLeft: 4 }}>MWh</Text>,
                  icon: <div style={{ 
                    width: 32, height: 32, borderRadius: 8, background: 'rgba(114, 46, 209, 0.1)', 
                    display: 'flex', alignItems: 'center', justifyContent: 'center' 
                  }}>
                    <ThunderboltOutlined style={{ color: '#722ed1' }} />
                  </div>
                }}
                style={{ borderRadius: 12 }}
              />
            </Col>
            <Col xs={24} sm={12} lg={6} className="animate-in" style={{ animationDelay: '0.3s' }}>
              <StatisticCard
                className="hover-card"
                statistic={{
                  title: <Text type="secondary">实时盈亏估计</Text>,
                  value: 4785,
                  prefix: <Text className="price-up" style={{ marginRight: 4 }}>+</Text>,
                  suffix: <Text style={{ fontSize: 14, marginLeft: 4 }}>CNY</Text>,
                  valueStyle: { color: token.colorSuccess }
                }}
                style={{ borderRadius: 12 }}
              />
            </Col>
            <Col xs={24} sm={12} lg={6} className="animate-in" style={{ animationDelay: '0.4s' }}>
              <StatisticCard
                className="hover-card"
                statistic={{
                  title: <Text type="secondary">风险敞口评估</Text>,
                  value: 23.5,
                  suffix: <Text style={{ fontSize: 14, marginLeft: 4 }}>%</Text>,
                  description: <Tag color="orange" bordered={false} style={{ borderRadius: 4 }}>中等风险</Tag>
                }}
                style={{ borderRadius: 12 }}
              />
            </Col>
          </Row>

      {/* 图表区域 */}
      <Row gutter={[20, 20]} style={{ marginTop: 20 }}>
        <Col xs={24} lg={16}>
          <Card 
            className="hover-card"
            title={
              <Space>
                <LineChartOutlined style={{ color: token.colorPrimary }} />
                <span>全省电力市场实时报价 (Real-time MCP)</span>
              </Space>
            }
            extra={<Text type="secondary" style={{ fontSize: 12 }}>数据源: 交易中心 • {mockMarketData.timestamp}</Text>}
            style={{ borderRadius: 12, border: 'none' }}
          >
            <ReactECharts 
              key={themeMode}
              option={getPriceChartOption(token, themeMode)} 
              style={{ height: 350 }} 
              theme={themeMode} 
            />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card 
            className="hover-card"
            title={
              <Space>
                <BarChartOutlined style={{ color: '#722ed1' }} />
                <span>成交分布</span>
              </Space>
            }
            style={{ borderRadius: 12, border: 'none' }}
          >
            <ReactECharts 
              key={themeMode}
              option={getVolumeChartOption(token, themeMode)} 
              style={{ height: 350 }} 
              theme={themeMode} 
            />
          </Card>
        </Col>
      </Row>

      {/* AI 建议和异常监测 */}
      <Row gutter={[20, 20]} style={{ marginTop: 20 }}>
        <Col xs={24} lg={12}>
          <AIRecommendation compact onTrade={(rec) => {
            navigate('/spot-trading', { state: { recommendation: rec } });
          }} />
        </Col>
        <Col xs={24} lg={12}>
          <AnomalyAlert compact onViewAll={() => navigate('/alerts')} />
        </Col>
      </Row>

      {/* 持仓列表 */}
      <Card 
        className="hover-card"
        title={
          <Space>
            <FileTextOutlined style={{ color: token.colorSuccess }} />
            <span>核心持仓摘要</span>
          </Space>
        }
        style={{ marginTop: 20, borderRadius: 12, border: 'none' }}
        extra={
          <Button type="link" onClick={() => navigate('/spot-trading')} icon={<ArrowUpOutlined rotate={45} />}>
            进入交易终端
          </Button>
        }
      >
        <Table 
          columns={positionColumns}
          dataSource={mockPositions}
          rowKey="id"
          pagination={false}
          size="middle"
        />
      </Card>
    </PageContainer>
  );
};

export default Dashboard;
