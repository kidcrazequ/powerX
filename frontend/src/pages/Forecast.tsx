/**
 * PowerX 电量预测页面
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 日/周/月电量预测和负荷曲线
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
  Segmented,
  Tag,
  Progress,
  Descriptions,
  List,
  Alert,
  theme
} from 'antd';
import {
  LineChartOutlined,
  ThunderboltOutlined,
  RiseOutlined,
  FallOutlined,
  ClockCircleOutlined,
  BulbOutlined,
  CalendarOutlined
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

// ============ 常量 ============

const PROVINCES = [
  { value: 'guangdong', label: '广东' },
  { value: 'zhejiang', label: '浙江' },
  { value: 'jiangsu', label: '江苏' },
  { value: 'shandong', label: '山东' },
  { value: 'sichuan', label: '四川' }
];

// ============ Mock 数据生成 ============

const generateHourlyLoads = () => {
  const pattern = [0.65, 0.60, 0.55, 0.52, 0.50, 0.55, 0.65, 0.80, 0.95, 1.00, 0.98, 0.95, 0.90, 0.92, 0.95, 0.98, 1.00, 1.05, 1.10, 1.08, 1.00, 0.90, 0.80, 0.70];
  const baseLoad = 120000;
  
  return pattern.map((factor, hour) => ({
    hour: `${hour}:00`,
    load: Math.round(baseLoad * factor * (1 + Math.random() * 0.03 - 0.015)),
    energy: Math.round(baseLoad * factor / 1000 * (1 + Math.random() * 0.03 - 0.015) * 10) / 10
  }));
};

const generateWeeklyLoads = () => {
  const weeklyPattern = [1.0, 1.02, 1.01, 1.0, 0.98, 0.75, 0.70];
  const baseEnergy = 2800;
  
  return Array.from({ length: 7 }, (_, i) => ({
    date: dayjs().add(i, 'day').format('MM-DD'),
    weekday: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][(dayjs().day() + i) % 7],
    energy: Math.round(baseEnergy * weeklyPattern[(dayjs().day() + i) % 7] * (1 + Math.random() * 0.05 - 0.025))
  }));
};

const generateMonthlyLoads = () => {
  const daysInMonth = dayjs().daysInMonth();
  const baseEnergy = 2800;
  
  return Array.from({ length: daysInMonth }, (_, i) => {
    const date = dayjs().startOf('month').add(i, 'day');
    const weekday = date.day();
    const weeklyFactor = [0.70, 1.0, 1.02, 1.01, 1.0, 0.98, 0.75][weekday];
    
    return {
      date: date.format('MM-DD'),
      energy: Math.round(baseEnergy * weeklyFactor * (1 + Math.random() * 0.05 - 0.025))
    };
  });
};

const mockPeakValley = {
  peak: { hours: [10, 11, 18, 19, 20], percentage: 35, avgLoad: 125000 },
  flat: { hours: [7, 8, 9, 12, 13, 14, 15, 16, 17, 21, 22], percentage: 45, avgLoad: 110000 },
  valley: { hours: [0, 1, 2, 3, 4, 5, 6, 23], percentage: 20, avgLoad: 70000 }
};

// ============ 组件 ============

const Forecast: React.FC = () => {
  const { token } = theme.useToken();
  
  const [province, setProvince] = useState('guangdong');
  const [forecastType, setForecastType] = useState<string>('daily');
  const [selectedDate, setSelectedDate] = useState(dayjs());
  
  const [hourlyData, setHourlyData] = useState(generateHourlyLoads());
  const [weeklyData, setWeeklyData] = useState(generateWeeklyLoads());
  const [monthlyData, setMonthlyData] = useState(generateMonthlyLoads());

  useEffect(() => {
    // 模拟数据更新
    setHourlyData(generateHourlyLoads());
    setWeeklyData(generateWeeklyLoads());
    setMonthlyData(generateMonthlyLoads());
  }, [province, selectedDate]);

  // 日负荷曲线图配置
  const dailyChartOption = {
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const data = params[0];
        return `${data.name}<br/>负荷: ${data.value.toLocaleString()} MW<br/>电量: ${hourlyData[data.dataIndex].energy} GWh`;
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: hourlyData.map(d => d.hour),
      axisLine: { lineStyle: { color: token.colorBorder } },
      axisLabel: { color: token.colorTextSecondary }
    },
    yAxis: {
      type: 'value',
      name: '负荷 (MW)',
      axisLine: { lineStyle: { color: token.colorBorder } },
      axisLabel: { color: token.colorTextSecondary },
      splitLine: { lineStyle: { color: token.colorBorderSecondary, type: 'dashed' } }
    },
    series: [{
      type: 'line',
      data: hourlyData.map(d => d.load),
      smooth: true,
      lineStyle: { color: '#1890ff', width: 3 },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(24, 144, 255, 0.4)' },
            { offset: 1, color: 'rgba(24, 144, 255, 0.05)' }
          ]
        }
      },
      markPoint: {
        data: [
          { type: 'max', name: '最大值' },
          { type: 'min', name: '最小值' }
        ]
      },
      markLine: {
        data: [{ type: 'average', name: '平均值' }]
      }
    }]
  };

  // 周电量图配置
  const weeklyChartOption = {
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: weeklyData.map(d => `${d.date}\n${d.weekday}`),
      axisLine: { lineStyle: { color: token.colorBorder } },
      axisLabel: { color: token.colorTextSecondary }
    },
    yAxis: {
      type: 'value',
      name: '电量 (GWh)',
      axisLine: { lineStyle: { color: token.colorBorder } },
      axisLabel: { color: token.colorTextSecondary },
      splitLine: { lineStyle: { color: token.colorBorderSecondary, type: 'dashed' } }
    },
    series: [{
      type: 'bar',
      data: weeklyData.map(d => d.energy),
      itemStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: '#52c41a' },
            { offset: 1, color: '#73d13d' }
          ]
        },
        borderRadius: [4, 4, 0, 0]
      }
    }]
  };

  // 月电量图配置
  const monthlyChartOption = {
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: monthlyData.map(d => d.date),
      axisLine: { lineStyle: { color: token.colorBorder } },
      axisLabel: { 
        color: token.colorTextSecondary,
        interval: 'auto'
      }
    },
    yAxis: {
      type: 'value',
      name: '电量 (GWh)',
      axisLine: { lineStyle: { color: token.colorBorder } },
      axisLabel: { color: token.colorTextSecondary },
      splitLine: { lineStyle: { color: token.colorBorderSecondary, type: 'dashed' } }
    },
    series: [{
      type: 'line',
      data: monthlyData.map(d => d.energy),
      smooth: true,
      lineStyle: { color: '#722ed1', width: 2 },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(114, 46, 209, 0.3)' },
            { offset: 1, color: 'rgba(114, 46, 209, 0.05)' }
          ]
        }
      }
    }]
  };

  // 计算统计数据
  const totalDailyEnergy = hourlyData.reduce((sum, d) => sum + d.energy, 0);
  const peakLoad = Math.max(...hourlyData.map(d => d.load));
  const valleyLoad = Math.min(...hourlyData.map(d => d.load));

  return (
    <div style={{ padding: 24 }}>
      {/* 页面标题 */}
      <div style={{ marginBottom: 24 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Title level={4} style={{ margin: 0 }}>
              <ThunderboltOutlined style={{ marginRight: 8 }} />
              电量预测
            </Title>
            <Text type="secondary">日/周/月电量和负荷曲线预测</Text>
          </Col>
          <Col>
            <Space>
              <Select
                value={province}
                onChange={setProvince}
                options={PROVINCES}
                style={{ width: 120 }}
              />
              <DatePicker
                value={selectedDate}
                onChange={(d) => d && setSelectedDate(d)}
              />
            </Space>
          </Col>
        </Row>
      </div>

      {/* 统计概览 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="预测日电量"
              value={totalDailyEnergy}
              precision={1}
              valueStyle={{ color: token.colorPrimary }}
              prefix={<BulbOutlined />}
              suffix="GWh"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="峰值负荷"
              value={peakLoad}
              valueStyle={{ color: token.colorError }}
              prefix={<RiseOutlined />}
              suffix="MW"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="谷值负荷"
              value={valleyLoad}
              valueStyle={{ color: token.colorSuccess }}
              prefix={<FallOutlined />}
              suffix="MW"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="峰谷比"
              value={(peakLoad / valleyLoad).toFixed(2)}
              prefix={<LineChartOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 预测类型切换 */}
      <Card style={{ marginBottom: 24 }}>
        <Segmented
          value={forecastType}
          onChange={(v) => setForecastType(v as string)}
          options={[
            { label: '日负荷曲线', value: 'daily', icon: <ClockCircleOutlined /> },
            { label: '周电量预测', value: 'weekly', icon: <CalendarOutlined /> },
            { label: '月电量预测', value: 'monthly', icon: <CalendarOutlined /> }
          ]}
          block
          style={{ marginBottom: 24 }}
        />

        {forecastType === 'daily' && (
          <ReactECharts option={dailyChartOption} style={{ height: 400 }} />
        )}

        {forecastType === 'weekly' && (
          <ReactECharts option={weeklyChartOption} style={{ height: 400 }} />
        )}

        {forecastType === 'monthly' && (
          <ReactECharts option={monthlyChartOption} style={{ height: 400 }} />
        )}
      </Card>

      {/* 峰谷时段分析 */}
      <Card title="峰谷时段分析">
        <Row gutter={24}>
          <Col span={8}>
            <Card 
              size="small" 
              style={{ background: 'rgba(255, 77, 79, 0.1)', border: 'none' }}
            >
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text strong style={{ color: token.colorError }}>
                  <RiseOutlined /> 高峰时段
                </Text>
                <Text>
                  {mockPeakValley.peak.hours.map(h => `${h}:00`).join(', ')}
                </Text>
                <Progress 
                  percent={mockPeakValley.peak.percentage} 
                  strokeColor={token.colorError}
                  format={p => `${p}% 电量占比`}
                />
                <Statistic
                  value={mockPeakValley.peak.avgLoad}
                  suffix="MW"
                  valueStyle={{ fontSize: 16 }}
                />
              </Space>
            </Card>
          </Col>
          <Col span={8}>
            <Card 
              size="small" 
              style={{ background: 'rgba(24, 144, 255, 0.1)', border: 'none' }}
            >
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text strong style={{ color: token.colorPrimary }}>
                  <LineChartOutlined /> 平段时段
                </Text>
                <Text>
                  {mockPeakValley.flat.hours.slice(0, 5).map(h => `${h}:00`).join(', ')}...
                </Text>
                <Progress 
                  percent={mockPeakValley.flat.percentage} 
                  strokeColor={token.colorPrimary}
                  format={p => `${p}% 电量占比`}
                />
                <Statistic
                  value={mockPeakValley.flat.avgLoad}
                  suffix="MW"
                  valueStyle={{ fontSize: 16 }}
                />
              </Space>
            </Card>
          </Col>
          <Col span={8}>
            <Card 
              size="small" 
              style={{ background: 'rgba(82, 196, 26, 0.1)', border: 'none' }}
            >
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text strong style={{ color: token.colorSuccess }}>
                  <FallOutlined /> 低谷时段
                </Text>
                <Text>
                  {mockPeakValley.valley.hours.map(h => `${h}:00`).join(', ')}
                </Text>
                <Progress 
                  percent={mockPeakValley.valley.percentage} 
                  strokeColor={token.colorSuccess}
                  format={p => `${p}% 电量占比`}
                />
                <Statistic
                  value={mockPeakValley.valley.avgLoad}
                  suffix="MW"
                  valueStyle={{ fontSize: 16 }}
                />
              </Space>
            </Card>
          </Col>
        </Row>

        <Alert
          style={{ marginTop: 16 }}
          type="info"
          showIcon
          message="交易建议"
          description={
            <List
              size="small"
              dataSource={[
                '建议在低谷时段 (0:00-6:00) 买入电量，价格较低',
                '建议在高峰时段 (18:00-20:00) 卖出电量，价格较高',
                `峰谷价差约 ${Math.round((peakLoad - valleyLoad) * 0.004)} 元/MWh，存在套利机会`
              ]}
              renderItem={item => <List.Item>{item}</List.Item>}
            />
          }
        />
      </Card>
    </div>
  );
};

export default Forecast;
