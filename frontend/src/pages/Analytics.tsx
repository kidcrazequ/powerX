/**
 * PowerX 数据分析页面
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 交易绩效、收益归因和趋势分析
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Select,
  DatePicker,
  Typography,
  Space,
  Table,
  Progress,
  Tooltip,
  Tag,
  Segmented,
  theme
} from 'antd';
import {
  LineChartOutlined,
  PieChartOutlined,
  BarChartOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  TrophyOutlined,
  RiseOutlined,
  FallOutlined,
  ThunderboltOutlined
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

// ============ 类型定义 ============

interface PerformanceSummary {
  total_trades: number;
  win_trades: number;
  win_rate: number;
  total_profit: number;
  total_volume_mwh: number;
}

interface Attribution {
  price_difference: { amount: number; percentage: number };
  timing: { amount: number; percentage: number };
  volume: { amount: number; percentage: number };
  strategy: { amount: number; percentage: number };
}

// ============ 常量 ============

const PROVINCES = [
  { value: 'guangdong', label: '广东' },
  { value: 'zhejiang', label: '浙江' },
  { value: 'jiangsu', label: '江苏' },
  { value: 'shandong', label: '山东' },
  { value: 'sichuan', label: '四川' }
];

// ============ Mock 数据 ============

const mockPerformance: PerformanceSummary = {
  total_trades: 128,
  win_trades: 89,
  win_rate: 69.5,
  total_profit: 156800,
  total_volume_mwh: 12500
};

const mockAttribution: Attribution = {
  price_difference: { amount: 78400, percentage: 50 },
  timing: { amount: 39200, percentage: 25 },
  volume: { amount: 23520, percentage: 15 },
  strategy: { amount: 15680, percentage: 10 }
};

const mockDailyProfit = Array.from({ length: 30 }, (_, i) => ({
  date: dayjs().subtract(29 - i, 'day').format('MM-DD'),
  profit: Math.random() * 10000 - 3000,
  cumulative: 0
})).map((item, index, arr) => {
  item.cumulative = arr.slice(0, index + 1).reduce((sum, d) => sum + d.profit, 0);
  return item;
});

const mockHourlyPattern = Array.from({ length: 24 }, (_, hour) => {
  const basePattern = [0.7, 0.65, 0.6, 0.58, 0.6, 0.7, 0.85, 1.0, 1.1, 1.15, 1.12, 1.1, 1.05, 1.0, 0.95, 0.9, 0.92, 1.0, 1.15, 1.2, 1.1, 0.95, 0.85, 0.75];
  return {
    hour: `${hour}:00`,
    price: Math.round(450 * basePattern[hour]),
    volume: Math.round(Math.random() * 5000 + 2000)
  };
});

// ============ 组件 ============

const Analytics: React.FC = () => {
  const { token } = theme.useToken();
  
  const [dateRange, setDateRange] = useState<any>(null);
  const [province, setProvince] = useState('guangdong');
  const [analysisType, setAnalysisType] = useState<string>('performance');

  // 绩效趋势图配置
  const performanceChartOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['日收益', '累计收益'],
      textStyle: { color: token.colorTextSecondary }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: mockDailyProfit.map(d => d.date),
      axisLine: { lineStyle: { color: token.colorBorder } },
      axisLabel: { color: token.colorTextSecondary }
    },
    yAxis: [
      {
        type: 'value',
        name: '日收益',
        axisLine: { lineStyle: { color: token.colorBorder } },
        axisLabel: { color: token.colorTextSecondary },
        splitLine: { lineStyle: { color: token.colorBorderSecondary, type: 'dashed' } }
      },
      {
        type: 'value',
        name: '累计收益',
        axisLine: { lineStyle: { color: token.colorBorder } },
        axisLabel: { color: token.colorTextSecondary }
      }
    ],
    series: [
      {
        name: '日收益',
        type: 'bar',
        data: mockDailyProfit.map(d => d.profit),
        itemStyle: {
          color: (params: any) => params.value >= 0 ? token.colorSuccess : token.colorError
        }
      },
      {
        name: '累计收益',
        type: 'line',
        yAxisIndex: 1,
        data: mockDailyProfit.map(d => d.cumulative),
        smooth: true,
        lineStyle: { color: token.colorPrimary, width: 2 },
        itemStyle: { color: token.colorPrimary }
      }
    ]
  };

  // 收益归因图配置
  const attributionChartOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 元 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      textStyle: { color: token.colorTextSecondary }
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: token.colorBgContainer,
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold'
          }
        },
        labelLine: { show: false },
        data: [
          { value: mockAttribution.price_difference.amount, name: '价差收益', itemStyle: { color: '#1890ff' } },
          { value: mockAttribution.timing.amount, name: '时机收益', itemStyle: { color: '#52c41a' } },
          { value: mockAttribution.volume.amount, name: '交易量贡献', itemStyle: { color: '#faad14' } },
          { value: mockAttribution.strategy.amount, name: '策略贡献', itemStyle: { color: '#722ed1' } }
        ]
      }
    ]
  };

  // 小时价格模式图配置
  const hourlyPatternChartOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: {
      data: ['价格', '成交量'],
      textStyle: { color: token.colorTextSecondary }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: mockHourlyPattern.map(d => d.hour),
      axisLine: { lineStyle: { color: token.colorBorder } },
      axisLabel: { color: token.colorTextSecondary }
    },
    yAxis: [
      {
        type: 'value',
        name: '价格(元/MWh)',
        axisLine: { lineStyle: { color: token.colorBorder } },
        axisLabel: { color: token.colorTextSecondary },
        splitLine: { lineStyle: { color: token.colorBorderSecondary, type: 'dashed' } }
      },
      {
        type: 'value',
        name: '成交量',
        axisLine: { lineStyle: { color: token.colorBorder } },
        axisLabel: { color: token.colorTextSecondary }
      }
    ],
    series: [
      {
        name: '价格',
        type: 'line',
        data: mockHourlyPattern.map(d => d.price),
        smooth: true,
        lineStyle: { color: '#1890ff', width: 3 },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(24, 144, 255, 0.3)' },
              { offset: 1, color: 'rgba(24, 144, 255, 0.05)' }
            ]
          }
        }
      },
      {
        name: '成交量',
        type: 'bar',
        yAxisIndex: 1,
        data: mockHourlyPattern.map(d => d.volume),
        itemStyle: { color: 'rgba(82, 196, 26, 0.6)' }
      }
    ]
  };

  return (
    <div style={{ padding: 24 }}>
      {/* 页面标题 */}
      <div style={{ marginBottom: 24 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Title level={4} style={{ margin: 0 }}>
              <LineChartOutlined style={{ marginRight: 8 }} />
              数据分析
            </Title>
            <Text type="secondary">交易绩效、收益归因和趋势分析</Text>
          </Col>
          <Col>
            <Space>
              <Select
                value={province}
                onChange={setProvince}
                options={PROVINCES}
                style={{ width: 120 }}
              />
              <RangePicker
                value={dateRange}
                onChange={setDateRange}
              />
            </Space>
          </Col>
        </Row>
      </div>

      {/* 绩效概览 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="总收益"
              value={mockPerformance.total_profit}
              precision={0}
              valueStyle={{ color: token.colorSuccess }}
              prefix={<RiseOutlined />}
              suffix="元"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="交易胜率"
              value={mockPerformance.win_rate}
              precision={1}
              valueStyle={{ color: token.colorPrimary }}
              prefix={<TrophyOutlined />}
              suffix="%"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="交易次数"
              value={mockPerformance.total_trades}
              prefix={<ThunderboltOutlined />}
              suffix={
                <Text type="secondary" style={{ fontSize: 14 }}>
                  (赢 {mockPerformance.win_trades})
                </Text>
              }
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="交易量"
              value={mockPerformance.total_volume_mwh}
              precision={0}
              prefix={<BarChartOutlined />}
              suffix="MWh"
            />
          </Card>
        </Col>
      </Row>

      {/* 分析类型切换 */}
      <Card style={{ marginBottom: 24 }}>
        <Segmented
          value={analysisType}
          onChange={(v) => setAnalysisType(v as string)}
          options={[
            { label: '绩效趋势', value: 'performance', icon: <LineChartOutlined /> },
            { label: '收益归因', value: 'attribution', icon: <PieChartOutlined /> },
            { label: '时段模式', value: 'hourly', icon: <BarChartOutlined /> }
          ]}
          block
          style={{ marginBottom: 24 }}
        />
        
        {analysisType === 'performance' && (
          <ReactECharts option={performanceChartOption} style={{ height: 400 }} />
        )}
        
        {analysisType === 'attribution' && (
          <Row gutter={24}>
            <Col span={12}>
              <ReactECharts option={attributionChartOption} style={{ height: 400 }} />
            </Col>
            <Col span={12}>
              <Title level={5}>收益归因明细</Title>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Card size="small">
                  <Row justify="space-between">
                    <Col>
                      <Text strong>价差收益</Text>
                      <br />
                      <Text type="secondary">买卖价格差异带来的收益</Text>
                    </Col>
                    <Col>
                      <Text style={{ fontSize: 20, color: token.colorPrimary }}>
                        {mockAttribution.price_difference.amount.toLocaleString()} 元
                      </Text>
                    </Col>
                  </Row>
                  <Progress percent={mockAttribution.price_difference.percentage} strokeColor="#1890ff" />
                </Card>
                
                <Card size="small">
                  <Row justify="space-between">
                    <Col>
                      <Text strong>时机收益</Text>
                      <br />
                      <Text type="secondary">择时交易带来的收益</Text>
                    </Col>
                    <Col>
                      <Text style={{ fontSize: 20, color: token.colorSuccess }}>
                        {mockAttribution.timing.amount.toLocaleString()} 元
                      </Text>
                    </Col>
                  </Row>
                  <Progress percent={mockAttribution.timing.percentage} strokeColor="#52c41a" />
                </Card>
                
                <Card size="small">
                  <Row justify="space-between">
                    <Col>
                      <Text strong>交易量贡献</Text>
                      <br />
                      <Text type="secondary">规模效应带来的收益</Text>
                    </Col>
                    <Col>
                      <Text style={{ fontSize: 20, color: token.colorWarning }}>
                        {mockAttribution.volume.amount.toLocaleString()} 元
                      </Text>
                    </Col>
                  </Row>
                  <Progress percent={mockAttribution.volume.percentage} strokeColor="#faad14" />
                </Card>
                
                <Card size="small">
                  <Row justify="space-between">
                    <Col>
                      <Text strong>策略贡献</Text>
                      <br />
                      <Text type="secondary">AI策略带来的收益</Text>
                    </Col>
                    <Col>
                      <Text style={{ fontSize: 20, color: '#722ed1' }}>
                        {mockAttribution.strategy.amount.toLocaleString()} 元
                      </Text>
                    </Col>
                  </Row>
                  <Progress percent={mockAttribution.strategy.percentage} strokeColor="#722ed1" />
                </Card>
              </Space>
            </Col>
          </Row>
        )}
        
        {analysisType === 'hourly' && (
          <>
            <ReactECharts option={hourlyPatternChartOption} style={{ height: 400 }} />
            <Row gutter={16} style={{ marginTop: 16 }}>
              <Col span={8}>
                <Card size="small" style={{ background: 'rgba(255, 77, 79, 0.1)' }}>
                  <Statistic
                    title="高峰时段"
                    value="18:00 - 20:00"
                    valueStyle={{ color: token.colorError, fontSize: 18 }}
                  />
                  <Text type="secondary">建议卖出</Text>
                </Card>
              </Col>
              <Col span={8}>
                <Card size="small" style={{ background: 'rgba(82, 196, 26, 0.1)' }}>
                  <Statistic
                    title="低谷时段"
                    value="02:00 - 06:00"
                    valueStyle={{ color: token.colorSuccess, fontSize: 18 }}
                  />
                  <Text type="secondary">建议买入</Text>
                </Card>
              </Col>
              <Col span={8}>
                <Card size="small" style={{ background: 'rgba(24, 144, 255, 0.1)' }}>
                  <Statistic
                    title="峰谷价差"
                    value={180}
                    suffix="元/MWh"
                    valueStyle={{ color: token.colorPrimary, fontSize: 18 }}
                  />
                  <Text type="secondary">套利空间</Text>
                </Card>
              </Col>
            </Row>
          </>
        )}
      </Card>
    </div>
  );
};

export default Analytics;
