/**
 * PowerX 系统健康监控页面
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 */
import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Progress, Statistic, Space, Typography, theme, Spin } from 'antd';
import { PageContainer } from '@ant-design/pro-components';
import { CheckCircleOutlined, CloudServerOutlined, DatabaseOutlined, ApiOutlined, ClockCircleOutlined } from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';

const { Text } = Typography;

const SystemHealth: React.FC = () => {
  const { token } = theme.useToken();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setTimeout(() => setLoading(false), 500);
  }, []);

  const healthData = {
    score: 92, uptime: '15 days',
    cpu: 35, memory: 62, disk: 45,
    db: { status: 'connected', latency: 12.5 },
    api: { calls: 15234, avgTime: 45.2, errorRate: 0.8 }
  };

  const chartOption = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: Array.from({length: 24}, (_, i) => `${i}:00`) },
    yAxis: { type: 'value' },
    series: [{ type: 'bar', data: Array.from({length: 24}, () => Math.floor(Math.random() * 100) + 20), itemStyle: { color: token.colorPrimary } }]
  };

  if (loading) return <PageContainer><div style={{ textAlign: 'center', padding: 100 }}><Spin size="large" /></div></PageContainer>;

  return (
    <PageContainer header={{ title: '系统健康监控', subTitle: '实时监控系统运行状态' }}>
      <Row gutter={[20, 20]}>
        <Col xs={24} lg={8}>
          <Card style={{ borderRadius: 12, textAlign: 'center' }}>
            <Progress type="dashboard" percent={healthData.score} strokeColor={token.colorSuccess} />
            <Space style={{ marginTop: 16 }}><CheckCircleOutlined style={{ color: token.colorSuccess }} /><Text strong>系统健康</Text></Space>
            <div style={{ marginTop: 8 }}><ClockCircleOutlined /> <Text type="secondary">运行: {healthData.uptime}</Text></div>
          </Card>
        </Col>
        <Col xs={24} lg={16}>
          <Card title={<Space><CloudServerOutlined />资源使用</Space>} style={{ borderRadius: 12 }}>
            <Row gutter={20}>
              {[['CPU', healthData.cpu], ['内存', healthData.memory], ['磁盘', healthData.disk]].map(([name, value]) => (
                <Col span={8} key={name as string}>
                  <div style={{ textAlign: 'center' }}>
                    <Progress type="circle" percent={value as number} size={80} />
                    <div><Text strong>{name}</Text></div>
                  </div>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>
        <Col xs={12} lg={6}><Card style={{ borderRadius: 12 }}><Statistic title={<Space><DatabaseOutlined />数据库</Space>} value="已连接" prefix={<CheckCircleOutlined style={{ color: token.colorSuccess }} />} /></Card></Col>
        <Col xs={12} lg={6}><Card style={{ borderRadius: 12 }}><Statistic title="API 调用" value={healthData.api.calls} prefix={<ApiOutlined />} /></Card></Col>
        <Col xs={12} lg={6}><Card style={{ borderRadius: 12 }}><Statistic title="平均响应" value={healthData.api.avgTime} suffix="ms" /></Card></Col>
        <Col xs={12} lg={6}><Card style={{ borderRadius: 12 }}><Statistic title="错误率" value={healthData.api.errorRate} suffix="%" valueStyle={{ color: token.colorSuccess }} /></Card></Col>
        <Col span={24}><Card title="API 调用趋势" style={{ borderRadius: 12 }}><ReactECharts option={chartOption} style={{ height: 250 }} /></Card></Col>
      </Row>
    </PageContainer>
  );
};

export default SystemHealth;
