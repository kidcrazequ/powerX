/**
 * PowerX 可拖拽仪表盘网格组件
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 */
import React, { useState, useCallback } from 'react';
import { Card, Button, Space, Dropdown, message, theme } from 'antd';
import { PlusOutlined, SaveOutlined, ReloadOutlined, AppstoreOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';

interface WidgetItem {
  id: string;
  type: string;
  name: string;
  x: number;
  y: number;
  w: number;
  h: number;
  config?: Record<string, any>;
}

interface DashboardGridProps {
  widgets: WidgetItem[];
  onLayoutChange?: (layout: WidgetItem[]) => void;
  onAddWidget?: (type: string) => void;
  onRemoveWidget?: (id: string) => void;
  renderWidget?: (widget: WidgetItem) => React.ReactNode;
}

const availableWidgets = [
  { key: 'price_chart', label: '价格走势图' },
  { key: 'order_list', label: '订单列表' },
  { key: 'position_summary', label: '持仓汇总' },
  { key: 'market_overview', label: '市场概览' },
  { key: 'ai_recommendation', label: 'AI推荐' },
  { key: 'exposure_monitor', label: '敞口监控' },
];

const DashboardGrid: React.FC<DashboardGridProps> = ({
  widgets,
  onLayoutChange,
  onAddWidget,
  onRemoveWidget,
  renderWidget
}) => {
  const { token } = theme.useToken();
  const [isEditing, setIsEditing] = useState(false);

  const handleSave = useCallback(() => {
    if (onLayoutChange) {
      onLayoutChange(widgets);
      message.success('布局已保存');
    }
    setIsEditing(false);
  }, [widgets, onLayoutChange]);

  const addWidgetItems: MenuProps['items'] = availableWidgets.map(w => ({
    key: w.key,
    label: w.label,
    onClick: () => onAddWidget?.(w.key)
  }));

  return (
    <div>
      {/* 工具栏 */}
      <div style={{ 
        marginBottom: 16, 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center' 
      }}>
        <Space>
          <Button 
            icon={<AppstoreOutlined />} 
            onClick={() => setIsEditing(!isEditing)}
            type={isEditing ? 'primary' : 'default'}
          >
            {isEditing ? '编辑中' : '编辑布局'}
          </Button>
          {isEditing && (
            <>
              <Dropdown menu={{ items: addWidgetItems }} placement="bottomLeft">
                <Button icon={<PlusOutlined />}>添加组件</Button>
              </Dropdown>
              <Button icon={<SaveOutlined />} type="primary" onClick={handleSave}>
                保存布局
              </Button>
            </>
          )}
        </Space>
        <Button icon={<ReloadOutlined />} onClick={() => message.info('刷新数据')}>
          刷新
        </Button>
      </div>

      {/* 网格布局 */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(12, 1fr)',
        gap: 16,
        minHeight: 400
      }}>
        {widgets.map(widget => (
          <div
            key={widget.id}
            style={{
              gridColumn: `span ${widget.w}`,
              gridRow: `span ${widget.h}`,
              minHeight: 200
            }}
          >
            <Card
              size="small"
              title={widget.name}
              style={{ 
                height: '100%', 
                borderRadius: 8,
                border: isEditing ? `2px dashed ${token.colorPrimary}` : undefined
              }}
              extra={isEditing && (
                <Button 
                  type="text" 
                  size="small" 
                  danger 
                  onClick={() => onRemoveWidget?.(widget.id)}
                >
                  移除
                </Button>
              )}
            >
              {renderWidget ? renderWidget(widget) : (
                <div style={{ 
                  height: '100%', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  color: token.colorTextSecondary 
                }}>
                  {widget.type} 组件
                </div>
              )}
            </Card>
          </div>
        ))}
      </div>

      {widgets.length === 0 && (
        <Card style={{ textAlign: 'center', padding: 40 }}>
          <p style={{ color: token.colorTextSecondary }}>暂无组件</p>
          <Dropdown menu={{ items: addWidgetItems }}>
            <Button type="primary" icon={<PlusOutlined />}>添加第一个组件</Button>
          </Dropdown>
        </Card>
      )}
    </div>
  );
};

export default DashboardGrid;
