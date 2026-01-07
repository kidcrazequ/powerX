/**
 * PowerX 审批中心页面
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 */
import React, { useState } from 'react';
import { Card, Table, Button, Modal, Form, Input, Tag, Space, Tabs, message, theme } from 'antd';
import { PageContainer } from '@ant-design/pro-components';
import { CheckOutlined, CloseOutlined, ClockCircleOutlined, PlusOutlined } from '@ant-design/icons';

const { TextArea } = Input;

interface ApprovalRequest {
  id: number;
  title: string;
  requester: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  created_at: string;
  type: string;
}

const mockPending: ApprovalRequest[] = [
  { id: 1, title: '大额交易审批 - 500MWh', requester: '张三', status: 'PENDING', created_at: '2026-01-07 10:30', type: '大额交易' },
  { id: 2, title: '限额变更申请', requester: '李四', status: 'PENDING', created_at: '2026-01-07 09:15', type: '限额变更' }
];

const mockMy: ApprovalRequest[] = [
  { id: 3, title: '新增交易权限', requester: '我', status: 'APPROVED', created_at: '2026-01-06 14:00', type: '权限申请' },
  { id: 4, title: '系统配置变更', requester: '我', status: 'REJECTED', created_at: '2026-01-05 11:00', type: '系统配置' }
];

const ApprovalCenter: React.FC = () => {
  const { token } = theme.useToken();
  const [approvalModal, setApprovalModal] = useState<{visible: boolean; request?: ApprovalRequest; action?: string}>({ visible: false });
  const [comment, setComment] = useState('');

  const handleApprove = (request: ApprovalRequest, action: string) => {
    setApprovalModal({ visible: true, request, action });
  };

  const handleSubmit = () => {
    message.success(approvalModal.action === 'approve' ? '已批准' : '已拒绝');
    setApprovalModal({ visible: false });
    setComment('');
  };

  const getStatusTag = (status: string) => {
    const config: Record<string, { color: string; icon: React.ReactNode; text: string }> = {
      'PENDING': { color: 'processing', icon: <ClockCircleOutlined />, text: '待审批' },
      'APPROVED': { color: 'success', icon: <CheckOutlined />, text: '已通过' },
      'REJECTED': { color: 'error', icon: <CloseOutlined />, text: '已拒绝' }
    };
    const c = config[status];
    return <Tag color={c.color} icon={c.icon}>{c.text}</Tag>;
  };

  const pendingColumns = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    { title: '申请标题', dataIndex: 'title' },
    { title: '申请人', dataIndex: 'requester' },
    { title: '类型', dataIndex: 'type', render: (t: string) => <Tag>{t}</Tag> },
    { title: '申请时间', dataIndex: 'created_at' },
    {
      title: '操作', key: 'action',
      render: (_: any, record: ApprovalRequest) => (
        <Space>
          <Button type="primary" size="small" icon={<CheckOutlined />} onClick={() => handleApprove(record, 'approve')}>通过</Button>
          <Button danger size="small" icon={<CloseOutlined />} onClick={() => handleApprove(record, 'reject')}>拒绝</Button>
        </Space>
      )
    }
  ];

  const myColumns = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    { title: '申请标题', dataIndex: 'title' },
    { title: '类型', dataIndex: 'type', render: (t: string) => <Tag>{t}</Tag> },
    { title: '状态', dataIndex: 'status', render: (s: string) => getStatusTag(s) },
    { title: '申请时间', dataIndex: 'created_at' }
  ];

  return (
    <PageContainer
      header={{
        title: '审批中心',
        subTitle: '处理待审批请求，查看申请历史',
        extra: [<Button key="new" type="primary" icon={<PlusOutlined />}>发起申请</Button>]
      }}
    >
      <Card style={{ borderRadius: 12 }}>
        <Tabs items={[
          { key: 'pending', label: `待我审批 (${mockPending.length})`, children: <Table dataSource={mockPending} columns={pendingColumns} rowKey="id" pagination={false} /> },
          { key: 'my', label: '我的申请', children: <Table dataSource={mockMy} columns={myColumns} rowKey="id" pagination={false} /> }
        ]} />
      </Card>

      <Modal
        title={approvalModal.action === 'approve' ? '审批通过' : '审批拒绝'}
        open={approvalModal.visible}
        onOk={handleSubmit}
        onCancel={() => setApprovalModal({ visible: false })}
        okText={approvalModal.action === 'approve' ? '确认通过' : '确认拒绝'}
        okButtonProps={{ danger: approvalModal.action === 'reject' }}
      >
        <p><strong>申请:</strong> {approvalModal.request?.title}</p>
        <Form.Item label="审批意见"><TextArea rows={3} value={comment} onChange={e => setComment(e.target.value)} placeholder="输入审批意见" /></Form.Item>
      </Modal>
    </PageContainer>
  );
};

export default ApprovalCenter;
