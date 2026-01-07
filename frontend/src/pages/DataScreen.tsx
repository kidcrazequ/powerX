/**
 * PowerX 数据大屏页面
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 全屏展示的数据可视化看板
 */

import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Space, Tag, Button, theme } from 'antd';
import { 
  FullscreenOutlined, FullscreenExitOutlined,
  ThunderboltOutlined, DollarOutlined
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { useSettingsStore } from '../stores/settingsStore';

const { useToken } = theme;

const DataScreen: React.FC = () => {
  const { token } = useToken();
  const { themeMode } = useSettingsStore();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());

  const isDark = themeMode === 'dark';

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const priceChartOption = {
    backgroundColor: 'transparent',
    title: { 
      text: '实时电价趋势', 
      textStyle: { color: token.colorText, fontSize: 16 } 
    },
    tooltip: { 
      trigger: 'axis',
      backgroundColor: isDark ? 'rgba(20, 20, 20, 0.9)' : 'rgba(255, 255, 255, 0.95)',
      borderColor: token.colorBorderSecondary,
      textStyle: { color: token.colorText }
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
      data: ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00'],
      axisLine: { lineStyle: { color: token.colorBorderSecondary } },
      axisLabel: { color: token.colorTextSecondary }
    },
    yAxis: { 
      type: 'value',
      axisLine: { lineStyle: { color: token.colorBorderSecondary } },
      axisLabel: { color: token.colorTextSecondary },
      splitLine: { lineStyle: { color: token.colorBorderSecondary, type: 'dashed' } }
    },
    series: [{
      data: [420, 435, 450, 448, 455, 460, 458],
      type: 'line',
      smooth: true,
      areaStyle: { 
        color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: `${token.colorPrimary}88` }, 
            { offset: 1, color: `${token.colorPrimary}11` }
          ]
        }
      },
      lineStyle: { color: token.colorPrimary, width: 3 },
      itemStyle: { color: token.colorPrimary }
    }]
  };

  const volumeChartOption = {
    backgroundColor: 'transparent',
    title: { 
      text: '各省成交量', 
      textStyle: { color: token.colorText, fontSize: 16 } 
    },
    tooltip: { 
      trigger: 'axis',
      backgroundColor: isDark ? 'rgba(20, 20, 20, 0.9)' : 'rgba(255, 255, 255, 0.95)',
      borderColor: token.colorBorderSecondary,
      textStyle: { color: token.colorText }
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
      data: ['广东', '浙江', '江苏', '山东', '四川'],
      axisLine: { lineStyle: { color: token.colorBorderSecondary } },
      axisLabel: { color: token.colorTextSecondary }
    },
    yAxis: { 
      type: 'value',
      axisLine: { lineStyle: { color: token.colorBorderSecondary } },
      axisLabel: { color: token.colorTextSecondary },
      splitLine: { lineStyle: { color: token.colorBorderSecondary, type: 'dashed' } }
    },
    series: [{
      data: [25600, 18400, 22100, 15800, 12300],
      type: 'bar',
      itemStyle: { 
        color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: token.colorSuccess }, 
            { offset: 1, color: `${token.colorSuccess}44` }
          ]
        },
        borderRadius: [4, 4, 0, 0]
      }
    }]
  };

  const pieChartOption = {
    backgroundColor: 'transparent',
    title: { 
      text: '交易类型分布', 
      textStyle: { color: token.colorText, fontSize: 16 } 
    },
    tooltip: { 
      trigger: 'item',
      backgroundColor: isDark ? 'rgba(20, 20, 20, 0.9)' : 'rgba(255, 255, 255, 0.95)',
      borderColor: token.colorBorderSecondary,
      textStyle: { color: token.colorText }
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: [
        { value: 45, name: '日前市场', itemStyle: { color: token.colorPrimary } },
        { value: 30, name: '实时市场', itemStyle: { color: token.colorSuccess } },
        { value: 25, name: '中长期', itemStyle: { color: '#722ed1' } }
      ],
      label: { color: token.colorText }
    }]
  };

  const gaugeOption = {
    backgroundColor: 'transparent',
    series: [{
      type: 'gauge',
      startAngle: 180,
      endAngle: 0,
      min: 0,
      max: 100,
      splitNumber: 5,
      itemStyle: { color: token.colorPrimary },
      progress: { show: true, width: 18 },
      pointer: { show: false },
      axisLine: { lineStyle: { width: 18, color: [[1, token.colorBorderSecondary]] } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      title: { offsetCenter: [0, '30%'], fontSize: 14, color: token.colorTextSecondary },
      detail: { 
        valueAnimation: true, offsetCenter: [0, '-10%'], 
        fontSize: 36, color: token.colorText, formatter: '{value}%' 
      },
      data: [{ value: 78, name: '系统负载' }]
    }]
  };

  const trades = [
    { time: '12:35:22', type: 'buy', qty: 150, price: 458 },
    { time: '12:34:55', type: 'sell', qty: 200, price: 457 },
    { time: '12:34:18', type: 'buy', qty: 100, price: 459 },
    { time: '12:33:42', type: 'sell', qty: 180, price: 456 }
  ];

  return (
    <div style={{ 
      minHeight: '100vh',
      background: isDark 
        ? 'linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #16213e 100%)'
        : 'linear-gradient(135deg, #f5f7fa 0%, #e8ecf0 50%, #f0f2f5 100%)',
      padding: 24,
      color: token.colorText
    }}>
      {/* 顶部信息栏 */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: 24,
        padding: '16px 24px',
        background: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.02)',
        borderRadius: 8,
        backdropFilter: 'blur(10px)',
        border: `1px solid ${token.colorBorderSecondary}`
      }}>
        <Space size="large">
          <ThunderboltOutlined style={{ fontSize: 32, color: token.colorWarning }} />
          <div>
            <h1 style={{ margin: 0, fontSize: 24, fontWeight: 600, color: token.colorText }}>
              PowerX 电力交易数据大屏
            </h1>
            <span style={{ color: token.colorTextSecondary }}>实时监控与分析</span>
          </div>
        </Space>
        
        <Space size="large">
          <Tag color="green" style={{ fontSize: 14, padding: '4px 12px' }}>
            系统正常运行
          </Tag>
          <span style={{ fontSize: 24, fontFamily: 'monospace', color: token.colorPrimary }}>
            {currentTime.toLocaleTimeString()}
          </span>
          <Button 
            icon={isFullscreen ? <FullscreenExitOutlined /> : <FullscreenOutlined />}
            onClick={toggleFullscreen}
          >
            {isFullscreen ? '退出全屏' : '全屏'}
          </Button>
        </Space>
      </div>

      {/* 核心指标 */}
      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card>
            <Statistic
              title="实时电价"
              value={458.5}
              suffix="元/MWh"
              valueStyle={{ color: token.colorPrimary, fontSize: 32, fontFamily: 'monospace' }}
              prefix={<DollarOutlined />}
            />
            <div style={{ marginTop: 8 }}>
              <Tag color="green">↑ 2.3%</Tag>
              <span style={{ color: token.colorTextSecondary, fontSize: 12 }}>较昨日</span>
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日成交量"
              value={125680}
              suffix="MWh"
              valueStyle={{ color: token.colorSuccess, fontSize: 32, fontFamily: 'monospace' }}
            />
            <div style={{ marginTop: 8 }}>
              <Tag color="blue">↑ 5.8%</Tag>
              <span style={{ color: token.colorTextSecondary, fontSize: 12 }}>较昨日</span>
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="成交金额"
              value={5756}
              suffix="万元"
              valueStyle={{ color: '#722ed1', fontSize: 32, fontFamily: 'monospace' }}
            />
            <div style={{ marginTop: 8 }}>
              <Tag color="orange">↑ 8.2%</Tag>
              <span style={{ color: token.colorTextSecondary, fontSize: 12 }}>较昨日</span>
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="活跃交易方"
              value={268}
              suffix="家"
              valueStyle={{ color: token.colorWarning, fontSize: 32, fontFamily: 'monospace' }}
            />
            <div style={{ marginTop: 8 }}>
              <Tag color="cyan">在线率 95%</Tag>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 图表区域 */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={12}>
          <Card>
            <ReactECharts 
              key={`price-${themeMode}`}
              option={priceChartOption} 
              style={{ height: 300 }} 
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card>
            <ReactECharts 
              key={`volume-${themeMode}`}
              option={volumeChartOption} 
              style={{ height: 300 }} 
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={8}>
          <Card>
            <ReactECharts 
              key={`pie-${themeMode}`}
              option={pieChartOption} 
              style={{ height: 250 }} 
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <ReactECharts 
              key={`gauge-${themeMode}`}
              option={gaugeOption} 
              style={{ height: 250 }} 
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card 
            title={
              <Space>
                <ThunderboltOutlined style={{ color: token.colorWarning }} />
                <span>最新成交</span>
              </Space>
            }
            style={{ height: 290 }}
          >
            {trades.map((trade, i) => (
              <div key={i} style={{ 
                display: 'flex', 
                justifyContent: 'space-between',
                padding: '8px 0',
                borderBottom: `1px solid ${token.colorBorderSecondary}`
              }}>
                <span style={{ color: token.colorTextSecondary }}>{trade.time}</span>
                <Tag color={trade.type === 'buy' ? 'red' : 'green'}>
                  {trade.type === 'buy' ? '买入' : '卖出'}
                </Tag>
                <span>{trade.qty} MWh</span>
                <span style={{ color: token.colorPrimary }}>¥{trade.price}</span>
              </div>
            ))}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DataScreen;
