/**
 * PowerX 风险敞口监控组件
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 */
import React from 'react';
import { Card, Progress, Space, Typography, Tag, Row, Col, Statistic, theme } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined, WarningOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface ExposureData {
  long_position_mwh: number;
  short_position_mwh: number;
  net_exposure_mwh: number;
  gross_exposure_mwh: number;
  exposure_ratio: number;
  risk_level: 'low' | 'medium' | 'high';
}

interface ExposureMonitorProps {
  data?: ExposureData;
}

const ExposureMonitor: React.FC<ExposureMonitorProps> = ({ data }) => {
  const { token } = theme.useToken();

  // 默认模拟数据
  const exposureData: ExposureData = data || {
    long_position_mwh: 1500,
    short_position_mwh: 1200,
    net_exposure_mwh: 300,
    gross_exposure_mwh: 2700,
    exposure_ratio: 11.1,
    risk_level: 'low'
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return token.colorSuccess;
      case 'medium': return token.colorWarning;
      case 'high': return token.colorError;
      default: return token.colorPrimary;
    }
  };

  const getRiskTag = (level: string) => {
    const config = {
      low: { color: 'success', text: '低风险' },
      medium: { color: 'warning', text: '中风险' },
      high: { color: 'error', text: '高风险' }
    };
    const c = config[level as keyof typeof config] || config.low;
    return <Tag color={c.color} icon={level === 'high' ? <WarningOutlined /> : null}>{c.text}</Tag>;
  };

  return (
    <Card
      title={<Space>📊 风险敞口监控 {getRiskTag(exposureData.risk_level)}</Space>}
      style={{ borderRadius: 12 }}
    >
      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Statistic
            title="多头持仓"
            value={exposureData.long_position_mwh}
            suffix="MWh"
            valueStyle={{ color: token.colorSuccess }}
            prefix={<ArrowUpOutlined />}
          />
        </Col>
        <Col span={12}>
          <Statistic
            title="空头持仓"
            value={exposureData.short_position_mwh}
            suffix="MWh"
            valueStyle={{ color: token.colorError }}
            prefix={<ArrowDownOutlined />}
          />
        </Col>
        <Col span={12}>
          <Statistic
            title="净敞口"
            value={exposureData.net_exposure_mwh}
            suffix="MWh"
            valueStyle={{ color: exposureData.net_exposure_mwh >= 0 ? token.colorSuccess : token.colorError }}
          />
        </Col>
        <Col span={12}>
          <Statistic
            title="总敞口"
            value={exposureData.gross_exposure_mwh}
            suffix="MWh"
          />
        </Col>
        <Col span={24}>
          <div style={{ marginTop: 8 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
              <Text type="secondary">敞口比例</Text>
              <Text strong>{exposureData.exposure_ratio}%</Text>
            </div>
            <Progress
              percent={exposureData.exposure_ratio}
              strokeColor={getRiskColor(exposureData.risk_level)}
              showInfo={false}
            />
          </div>
        </Col>
      </Row>
    </Card>
  );
};

export default ExposureMonitor;
