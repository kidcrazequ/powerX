/**
 * PowerX 仪表盘小部件容器
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 */
import React from 'react';
import { Card, Spin, Empty, theme } from 'antd';
import { 
  LineChartOutlined, 
  OrderedListOutlined, 
  PieChartOutlined, 
  DashboardOutlined,
  RobotOutlined,
  AlertOutlined,
  MonitorOutlined,
  ThunderboltOutlined
} from '@ant-design/icons';

interface WidgetContainerProps {
  type: string;
  title: string;
  loading?: boolean;
  error?: string;
  children?: React.ReactNode;
  onRefresh?: () => void;
  config?: Record<string, any>;
}

const widgetIcons: Record<string, React.ReactNode> = {
  price_chart: <LineChartOutlined />,
  order_list: <OrderedListOutlined />,
  position_summary: <PieChartOutlined />,
  market_overview: <DashboardOutlined />,
  ai_recommendation: <RobotOutlined />,
  alert_panel: <AlertOutlined />,
  exposure_monitor: <MonitorOutlined />,
  quick_trade: <ThunderboltOutlined />
};

const WidgetContainer: React.FC<WidgetContainerProps> = ({
  type,
  title,
  loading = false,
  error,
  children,
  onRefresh,
  config
}) => {
  const { token } = theme.useToken();
  const icon = widgetIcons[type] || <DashboardOutlined />;

  const renderContent = () => {
    if (loading) {
      return (
        <div style={{ 
          height: '100%', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center' 
        }}>
          <Spin />
        </div>
      );
    }

    if (error) {
      return (
        <Empty 
          description={error} 
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          style={{ margin: 20 }}
        />
      );
    }

    return children || (
      <div style={{ 
        height: 150, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        color: token.colorTextSecondary,
        flexDirection: 'column',
        gap: 8
      }}>
        <span style={{ fontSize: 32 }}>{icon}</span>
        <span>{title}</span>
      </div>
    );
  };

  return (
    <Card
      size="small"
      title={
        <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {icon}
          {title}
        </span>
      }
      style={{ height: '100%', borderRadius: 8 }}
      styles={{ body: { padding: 12, height: 'calc(100% - 46px)' } }}
    >
      {renderContent()}
    </Card>
  );
};

export default WidgetContainer;
