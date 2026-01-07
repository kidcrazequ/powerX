/**
 * PowerX 历史数据回放页面
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 */
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  Card, Row, Col, DatePicker, Button, Space, Slider, Select, 
  Table, Tag, Statistic, Timeline, message, theme 
} from 'antd';
import { 
  PlayCircleOutlined, PauseCircleOutlined, StepBackwardOutlined,
  StepForwardOutlined, FastBackwardOutlined, FastForwardOutlined,
  HistoryOutlined, ClockCircleOutlined
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import dayjs from 'dayjs';

interface DataPoint {
  timestamp: string;
  time: string;
  price: number;
  volume: number;
  high: number;
  low: number;
}

interface TradingEvent {
  id: number;
  timestamp: string;
  type: string;
  description: string;
}

const HistoryReplay: React.FC = () => {
  const { token } = theme.useToken();
  const [selectedDate, setSelectedDate] = useState<dayjs.Dayjs>(dayjs().subtract(1, 'day'));
  const [data, setData] = useState<DataPoint[]>([]);
  const [events, setEvents] = useState<TradingEvent[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // 加载数据
  useEffect(() => {
    loadData();
  }, [selectedDate]);

  const loadData = useCallback(() => {
    // 模拟加载数据
    const mockData: DataPoint[] = [];
    let basePrice = 400;
    for (let hour = 9; hour <= 16; hour++) {
      for (let minute = 0; minute < 60; minute += 5) {
        if (hour === 16 && minute > 0) break;
        basePrice += (Math.random() - 0.5) * 10;
        mockData.push({
          timestamp: `${selectedDate.format('YYYY-MM-DD')} ${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}:00`,
          time: `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`,
          price: Math.round(basePrice * 100) / 100,
          volume: Math.round((Math.random() * 500 + 200) * 100) / 100,
          high: Math.round((basePrice + Math.random() * 5) * 100) / 100,
          low: Math.round((basePrice - Math.random() * 5) * 100) / 100
        });
      }
    }
    setData(mockData);
    setCurrentIndex(0);

    // 模拟事件
    setEvents([
      { id: 1, timestamp: '09:30:00', type: 'order_submit', description: '提交买入订单 500MWh' },
      { id: 2, timestamp: '10:15:00', type: 'order_filled', description: '订单成交 500MWh @ 405.2' },
      { id: 3, timestamp: '11:00:00', type: 'price_alert', description: '价格触及预警线 420' },
      { id: 4, timestamp: '14:30:00', type: 'order_submit', description: '提交卖出订单 300MWh' },
      { id: 5, timestamp: '15:00:00', type: 'order_filled', description: '订单成交 300MWh @ 418.5' },
    ]);
  }, [selectedDate]);

  // 播放控制
  useEffect(() => {
    if (isPlaying && currentIndex < data.length - 1) {
      timerRef.current = setTimeout(() => {
        setCurrentIndex(prev => prev + 1);
      }, 1000 / speed);
    } else if (currentIndex >= data.length - 1) {
      setIsPlaying(false);
    }
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [isPlaying, currentIndex, data.length, speed]);

  const handlePlay = () => setIsPlaying(true);
  const handlePause = () => setIsPlaying(false);
  const handleReset = () => { setCurrentIndex(0); setIsPlaying(false); };
  const handleStepForward = () => setCurrentIndex(prev => Math.min(prev + 1, data.length - 1));
  const handleStepBackward = () => setCurrentIndex(prev => Math.max(prev - 1, 0));

  const currentData = data.slice(0, currentIndex + 1);
  const currentPoint = data[currentIndex];

  const chartOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: currentData.map(d => d.time) },
    yAxis: { type: 'value', min: 'dataMin', max: 'dataMax' },
    series: [
      { name: '价格', type: 'line', data: currentData.map(d => d.price), smooth: true,
        itemStyle: { color: token.colorPrimary }, areaStyle: { color: `${token.colorPrimary}20` } }
    ],
    grid: { left: 60, right: 20, bottom: 30, top: 20 }
  };

  const volumeOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: currentData.map(d => d.time) },
    yAxis: { type: 'value' },
    series: [
      { name: '成交量', type: 'bar', data: currentData.map(d => d.volume),
        itemStyle: { color: token.colorSuccess } }
    ],
    grid: { left: 60, right: 20, bottom: 30, top: 20 }
  };

  const eventTypeColors: Record<string, string> = {
    order_submit: 'blue', order_filled: 'green', price_alert: 'orange', volume_spike: 'red'
  };

  return (
    <div style={{ padding: 24 }}>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0, color: token.colorTextHeading }}>
          <HistoryOutlined style={{ marginRight: 8 }} />
          历史数据回放
        </h2>
        <Space>
          <DatePicker value={selectedDate} onChange={(date) => date && setSelectedDate(date)} 
            disabledDate={(current) => current && current > dayjs().subtract(1, 'day')} />
          <Select value={speed} onChange={setSpeed} style={{ width: 100 }}>
            <Select.Option value={0.5}>0.5x</Select.Option>
            <Select.Option value={1}>1x</Select.Option>
            <Select.Option value={2}>2x</Select.Option>
            <Select.Option value={5}>5x</Select.Option>
          </Select>
        </Space>
      </div>

      {/* 控制栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Row align="middle" gutter={16}>
          <Col flex="none">
            <Space>
              <Button icon={<FastBackwardOutlined />} onClick={handleReset} />
              <Button icon={<StepBackwardOutlined />} onClick={handleStepBackward} disabled={currentIndex === 0} />
              {isPlaying ? (
                <Button type="primary" icon={<PauseCircleOutlined />} onClick={handlePause}>暂停</Button>
              ) : (
                <Button type="primary" icon={<PlayCircleOutlined />} onClick={handlePlay} disabled={currentIndex >= data.length - 1}>播放</Button>
              )}
              <Button icon={<StepForwardOutlined />} onClick={handleStepForward} disabled={currentIndex >= data.length - 1} />
            </Space>
          </Col>
          <Col flex="auto">
            <Slider 
              value={currentIndex} 
              max={data.length - 1} 
              onChange={setCurrentIndex}
              tooltip={{ formatter: (val) => data[val || 0]?.time || '' }}
            />
          </Col>
          <Col flex="none">
            <Space>
              <ClockCircleOutlined />
              <span style={{ fontFamily: 'monospace', fontSize: 18 }}>{currentPoint?.time || '--:--'}</span>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 实时数据 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card><Statistic title="当前价格" value={currentPoint?.price || 0} precision={2} suffix="元/MWh" valueStyle={{ color: token.colorPrimary }} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="最高价" value={currentPoint?.high || 0} precision={2} suffix="元/MWh" valueStyle={{ color: token.colorError }} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="最低价" value={currentPoint?.low || 0} precision={2} suffix="元/MWh" valueStyle={{ color: token.colorSuccess }} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="成交量" value={currentPoint?.volume || 0} precision={2} suffix="MWh" /></Card>
        </Col>
      </Row>

      {/* 图表和事件 */}
      <Row gutter={16}>
        <Col span={16}>
          <Card title="价格走势" style={{ marginBottom: 16 }}>
            <ReactECharts option={chartOption} style={{ height: 250 }} />
          </Card>
          <Card title="成交量">
            <ReactECharts option={volumeOption} style={{ height: 200 }} />
          </Card>
        </Col>
        <Col span={8}>
          <Card title="交易事件" style={{ height: '100%' }}>
            <Timeline items={events.map(event => ({
              color: eventTypeColors[event.type] || 'gray',
              children: (
                <div>
                  <Tag color={eventTypeColors[event.type]}>{event.timestamp}</Tag>
                  <div style={{ marginTop: 4 }}>{event.description}</div>
                </div>
              )
            }))} />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default HistoryReplay;
