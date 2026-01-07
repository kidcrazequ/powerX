/**
 * PowerX 快捷键指南组件
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 */
import React from 'react';
import { Modal, Table, Tag, Space, Typography, theme } from 'antd';

const { Text } = Typography;

interface HotkeyGuideProps {
  visible: boolean;
  onClose: () => void;
}

const hotkeys = [
  { keys: ['Ctrl', 'T'], description: '新建交易' },
  { keys: ['Ctrl', 'S'], description: '保存当前内容' },
  { keys: ['Ctrl', '/'], description: '显示快捷键帮助' },
  { keys: ['Ctrl', 'R'], description: '刷新数据' },
  { keys: ['Ctrl', 'D'], description: '跳转到仪表盘' },
  { keys: ['Esc'], description: '关闭弹窗/取消操作' },
  { keys: ['↑', '↓'], description: '表格行导航' },
  { keys: ['Enter'], description: '确认/提交' },
];

const HotkeyGuide: React.FC<HotkeyGuideProps> = ({ visible, onClose }) => {
  const { token } = theme.useToken();

  const columns = [
    {
      title: '快捷键',
      dataIndex: 'keys',
      key: 'keys',
      render: (keys: string[]) => (
        <Space size={4}>
          {keys.map((key, index) => (
            <React.Fragment key={key}>
              <Tag style={{
                background: token.colorBgContainer,
                border: `1px solid ${token.colorBorder}`,
                borderRadius: 4,
                fontFamily: 'monospace',
                fontWeight: 600,
                padding: '2px 8px'
              }}>
                {key}
              </Tag>
              {index < keys.length - 1 && <Text type="secondary">+</Text>}
            </React.Fragment>
          ))}
        </Space>
      ),
    },
    {
      title: '功能',
      dataIndex: 'description',
      key: 'description',
    },
  ];

  return (
    <Modal
      title="⌨️ 快捷键指南"
      open={visible}
      onCancel={onClose}
      footer={null}
      width={500}
    >
      <Table
        dataSource={hotkeys}
        columns={columns}
        pagination={false}
        rowKey="description"
        size="small"
      />
      <div style={{ marginTop: 16, textAlign: 'center' }}>
        <Text type="secondary">按 Esc 关闭此窗口</Text>
      </div>
    </Modal>
  );
};

export default HotkeyGuide;
