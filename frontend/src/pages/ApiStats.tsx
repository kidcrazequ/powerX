/**
 * PowerX API 统计页面
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Card, Row, Col, Table, Statistic, Progress, Select, Spin, theme, Tag } from 'antd';
import { 
  ApiOutlined, 
  ClockCircleOutlined, 
  CheckCircleOutlined, 
  WarningOutlined,
  SyncOutlined
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';

interface ApiStatsData {
  total_calls: number;
  avg_response_time_ms: number;
  error_rate: number;
  error_count: number;
  top_endpoints: Array<{ path: string; count: number; avg_time: number }>;
  by_status: Record<string, number>;
}

interface TimelinePoint {
  time: string;
  count: number;
  avg_time: number;
  errors: number;
}

const ApiStats: React.FC = () => {
  const { token } = theme.useToken();
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState(24);
  const [stats, setStats] = useState<ApiStatsData | null>(null);
  const [timeline, setTimeline] = useState<TimelinePoint[]>([]);

  const fetchStats = useCallback(async () => {
    setLoading(true);
    // 模拟数据
    await new Promise(resolve => setTimeout(resolve, 500));
    setStats({
      total_calls: 15842,
      avg_response_time_ms: 45.6,
      error_rate: 0.35,
      error_count: 55,
      top_endpoints: [
        { path: '/api/v1/market/price', count: 5420, avg_time: 23.5 },
        { path: '/api/v1/trading/orders', count: 3210, avg_time: 78.2 },
        { path: '/api/v1/auth/login', count: 1856, avg_time: 156.8 },
        { path: '/api/v1/contracts', count: 1245, avg_time: 42.1 },
        { path: '/api/v1/ai/predict', count: 987, avg_time: 234.5 },
      ],
      by_status: { '200': 14890, '201': 543, '400': 32, '401': 15, '500': 8 }
    });
    setTimeline(Array.from({ length: 24 }, (_, i) => ({
      time: `${String(i).padStart(2, '0')}:00`,
      count: Math.floor(Math.random() * 1000) + 200,
      avg_time: Math.random() * 100 + 20,
      errors: Math.floor(Math.random() * 10)
    })));
    setLoading(false);
  }, [timeRange]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  const timelineOption = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['请求数', '响应时间'], textStyle: { color: token.colorTextSecondary } },
    grid: { left: 60, right: 60, bottom: 30, top: 40 },
    xAxis: { type: 'category', data: timeline.map(t => t.time), axisLine: { lineStyle: { color: token.colorBorder } } },
    yAxis: [
      { type: 'value', name: '请求数', axisLine: { lineStyle: { color: token.colorBorder } } },
      { type: 'value', name: '响应时间(ms)', axisLine: { lineStyle: { color: token.colorBorder } } }
    ],
    series: [
      { name: '请求数', type: 'bar', data: timeline.map(t => t.count), itemStyle: { color: token.colorPrimary } },
      { name: '响应时间', type: 'line', yAxisIndex: 1, data: timeline.map(t => t.avg_time.toFixed(1)), itemStyle: { color: token.colorWarning }, smooth: true }
    ]
  };

  const statusPieOption = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', right: 10, top: 'center', textStyle: { color: token.colorTextSecondary } },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: stats ? Object.entries(stats.by_status).map(([status, count]) => ({
        name: status,
        value: count,
        itemStyle: { color: status.startsWith('2') ? token.colorSuccess : status.startsWith('4') ? token.colorWarning : token.colorError }
      })) : []
    }]
  };

  const columns = [
    { title: '接口路径', dataIndex: 'path', key: 'path', render: (text: string) => <code>{text}</code> },
    { title: '调用次数', dataIndex: 'count', key: 'count', sorter: (a: any, b: any) => a.count - b.count },
    { title: '平均响应(ms)', dataIndex: 'avg_time', key: 'avg_time', render: (v: number) => v.toFixed(1) },
  ];

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0, color: token.colorTextHeading }}>
          <ApiOutlined style={{ marginRight: 8 }} />
          API 统计
        </h2>
        <Select value={timeRange} onChange={setTimeRange} style={{ width: 120 }}>
          <Select.Option value={1}>最近1小时</Select.Option>
          <Select.Option value={6}>最近6小时</Select.Option>
          <Select.Option value={24}>最近24小时</Select.Option>
          <Select.Option value={168}>最近7天</Select.Option>
        </Select>
      </div>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic 
              title="总调用次数" 
              value={stats?.total_calls} 
              prefix={<ApiOutlined />}
              valueStyle={{ color: token.colorPrimary }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="平均响应时间" 
              value={stats?.avg_response_time_ms} 
              suffix="ms" 
              prefix={<ClockCircleOutlined />}
              precision={1}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="成功率" 
              value={100 - (stats?.error_rate || 0)} 
              suffix="%" 
              prefix={<CheckCircleOutlined />}
              precision={2}
              valueStyle={{ color: token.colorSuccess }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="错误数" 
              value={stats?.error_count} 
              prefix={<WarningOutlined />}
              valueStyle={{ color: token.colorError }}
            />
          </Card>
        </Col>
      </Row>

      {/* 图表 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={16}>
          <Card title="请求趋势">
            <ReactECharts option={timelineOption} style={{ height: 300 }} />
          </Card>
        </Col>
        <Col span={8}>
          <Card title="状态码分布">
            <ReactECharts option={statusPieOption} style={{ height: 300 }} />
          </Card>
        </Col>
      </Row>

      {/* 热门接口 */}
      <Card title="热门接口 TOP 5">
        <Table 
          dataSource={stats?.top_endpoints} 
          columns={columns} 
          pagination={false}
          rowKey="path"
          size="small"
        />
      </Card>
    </div>
  );
};

export default ApiStats;
