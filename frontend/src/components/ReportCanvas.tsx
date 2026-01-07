/**
 * PowerX 报表画布组件
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 */
import React, { useState } from 'react';
import { Card, Empty, Button, Dropdown, theme } from 'antd';
import { PlusOutlined, DeleteOutlined, SettingOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';

interface ReportWidget {
  id: string;
  type: string;
  title: string;
  x: number;
  y: number;
  w: number;
  h: number;
  config?: Record<string, any>;
}

interface ReportCanvasProps {
  widgets: ReportWidget[];
  onAddWidget?: (type: string) => void;
  onRemoveWidget?: (id: string) => void;
  onWidgetConfigChange?: (id: string, config: Record<string, any>) => void;
  renderWidget?: (widget: ReportWidget) => React.ReactNode;
  editable?: boolean;
}

const widgetTypes: MenuProps['items'] = [
  { key: 'line', label: '折线图' },
  { key: 'bar', label: '柱状图' },
  { key: 'pie', label: '饼图' },
  { key: 'table', label: '数据表格' },
  { key: 'stat', label: '统计卡片' },
  { key: 'text', label: '文本块' }
];

const ReportCanvas: React.FC<ReportCanvasProps> = ({
  widgets,
  onAddWidget,
  onRemoveWidget,
  onWidgetConfigChange,
  renderWidget,
  editable = true
}) => {
  const { token } = theme.useToken();
  const [selectedWidget, setSelectedWidget] = useState<string | null>(null);

  const handleAddWidget = (type: string) => {
    onAddWidget?.(type);
  };

  if (widgets.length === 0) {
    return (
      <Card 
        style={{ 
          minHeight: 400, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center' 
        }}
      >
        <Empty description="报表画布为空">
          {editable && (
            <Dropdown
              menu={{
                items: widgetTypes,
                onClick: ({ key }) => handleAddWidget(key)
              }}
            >
              <Button type="primary" icon={<PlusOutlined />}>
                添加组件
              </Button>
            </Dropdown>
          )}
        </Empty>
      </Card>
    );
  }

  return (
    <div style={{ position: 'relative', minHeight: 500 }}>
      {/* 工具栏 */}
      {editable && (
        <div style={{ marginBottom: 12, display: 'flex', justifyContent: 'flex-end' }}>
          <Dropdown
            menu={{
              items: widgetTypes,
              onClick: ({ key }) => handleAddWidget(key)
            }}
          >
            <Button icon={<PlusOutlined />}>添加组件</Button>
          </Dropdown>
        </div>
      )}

      {/* 画布网格 */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(12, 1fr)',
          gap: 12,
          padding: 12,
          backgroundColor: token.colorBgLayout,
          borderRadius: 8,
          minHeight: 400
        }}
      >
        {widgets.map(widget => (
          <div
            key={widget.id}
            style={{
              gridColumn: `span ${widget.w}`,
              gridRow: `span ${widget.h}`,
              minHeight: 150
            }}
            onClick={() => setSelectedWidget(widget.id)}
          >
            <Card
              size="small"
              title={widget.title}
              style={{
                height: '100%',
                border: selectedWidget === widget.id 
                  ? `2px solid ${token.colorPrimary}` 
                  : undefined,
                cursor: editable ? 'pointer' : 'default'
              }}
              extra={
                editable && selectedWidget === widget.id ? (
                  <>
                    <Button
                      type="text"
                      size="small"
                      icon={<SettingOutlined />}
                      onClick={(e) => {
                        e.stopPropagation();
                        // 打开配置面板
                      }}
                    />
                    <Button
                      type="text"
                      size="small"
                      danger
                      icon={<DeleteOutlined />}
                      onClick={(e) => {
                        e.stopPropagation();
                        onRemoveWidget?.(widget.id);
                      }}
                    />
                  </>
                ) : null
              }
            >
              {renderWidget ? (
                renderWidget(widget)
              ) : (
                <div
                  style={{
                    height: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: token.colorTextSecondary
                  }}
                >
                  {widget.type} 组件
                </div>
              )}
            </Card>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ReportCanvas;
