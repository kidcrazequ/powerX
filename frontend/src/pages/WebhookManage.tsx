/**
 * PowerX Webhook 管理页面
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 */
import React, { useState } from 'react';
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Switch,
  Tag,
  Space,
  Typography,
  message,
  Popconfirm,
} from 'antd';
import {
  ApiOutlined,
  PlusOutlined,
  DeleteOutlined,
  EditOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons';

const { Text, Paragraph } = Typography;
const { Option } = Select;

// 可用事件
const availableEvents = [
  { value: 'order.created', label: '订单创建' },
  { value: 'order.filled', label: '订单成交' },
  { value: 'order.cancelled', label: '订单取消' },
  { value: 'price.alert', label: '价格预警' },
  { value: 'risk.warning', label: '风险警告' },
  { value: 'system.notice', label: '系统通知' },
];

// 模拟数据
const mockWebhooks = [
  {
    webhook_id: 'WH-A1B2C3D4E5F6',
    name: '订单通知',
    url: 'https://api.example.com/webhooks/orders',
    events: ['order.created', 'order.filled', 'order.cancelled'],
    is_active: true,
    success_count: 156,
    failure_count: 3,
    last_status: 'success',
  },
  {
    webhook_id: 'WH-G7H8I9J0K1L2',
    name: '风险预警',
    url: 'https://api.example.com/webhooks/risk',
    events: ['risk.warning', 'price.alert'],
    is_active: true,
    success_count: 42,
    failure_count: 0,
    last_status: 'success',
  },
];

const WebhookManage: React.FC = () => {
  const [webhooks, setWebhooks] = useState(mockWebhooks);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [editingWebhook, setEditingWebhook] = useState<any>(null);
  const [form] = Form.useForm();

  const handleCreate = async (values: any) => {
    const newWebhook = {
      webhook_id: `WH-${Date.now()}`,
      ...values,
      is_active: true,
      success_count: 0,
      failure_count: 0,
      last_status: null,
    };
    setWebhooks([...webhooks, newWebhook]);
    setCreateModalVisible(false);
    form.resetFields();
    message.success('Webhook 创建成功');
  };

  const handleDelete = (webhookId: string) => {
    setWebhooks(webhooks.filter(w => w.webhook_id !== webhookId));
    message.success('Webhook 已删除');
  };

  const handleToggle = (webhookId: string, active: boolean) => {
    setWebhooks(webhooks.map(w => 
      w.webhook_id === webhookId ? { ...w, is_active: active } : w
    ));
    message.success(active ? 'Webhook 已启用' : 'Webhook 已禁用');
  };

  const columns = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: any) => (
        <Space>
          <ApiOutlined style={{ color: record.is_active ? '#52c41a' : '#999' }} />
          <Text strong>{text}</Text>
        </Space>
      ),
    },
    {
      title: 'URL',
      dataIndex: 'url',
      key: 'url',
      render: (url: string) => (
        <Text code copyable ellipsis style={{ maxWidth: 300 }}>
          {url}
        </Text>
      ),
    },
    {
      title: '订阅事件',
      dataIndex: 'events',
      key: 'events',
      render: (events: string[]) => (
        <Space wrap>
          {events.map(e => (
            <Tag key={e} color="blue">
              {availableEvents.find(ae => ae.value === e)?.label || e}
            </Tag>
          ))}
        </Space>
      ),
    },
    {
      title: '状态',
      key: 'status',
      render: (_: any, record: any) => (
        <Switch
          checked={record.is_active}
          onChange={(checked) => handleToggle(record.webhook_id, checked)}
          checkedChildren="启用"
          unCheckedChildren="禁用"
        />
      ),
    },
    {
      title: '统计',
      key: 'stats',
      render: (_: any, record: any) => (
        <Space>
          <Tag icon={<CheckCircleOutlined />} color="success">
            {record.success_count}
          </Tag>
          <Tag icon={<CloseCircleOutlined />} color="error">
            {record.failure_count}
          </Tag>
        </Space>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => {
              setEditingWebhook(record);
              form.setFieldsValue(record);
              setCreateModalVisible(true);
            }}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除此 Webhook？"
            onConfirm={() => handleDelete(record.webhook_id)}
          >
            <Button
              type="link"
              size="small"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card
        title={
          <Space>
            <ApiOutlined />
            <span>Webhook 管理</span>
          </Space>
        }
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              setEditingWebhook(null);
              form.resetFields();
              setCreateModalVisible(true);
            }}
          >
            添加 Webhook
          </Button>
        }
      >
        <Paragraph type="secondary" style={{ marginBottom: 16 }}>
          配置 Webhook 以接收系统事件的实时通知。当触发事件时，系统会向配置的 URL 发送 HTTP POST 请求。
        </Paragraph>

        <Table
          columns={columns}
          dataSource={webhooks}
          rowKey="webhook_id"
          pagination={false}
        />
      </Card>

      {/* 创建/编辑弹窗 */}
      <Modal
        title={editingWebhook ? '编辑 Webhook' : '创建 Webhook'}
        open={createModalVisible}
        onCancel={() => {
          setCreateModalVisible(false);
          setEditingWebhook(null);
          form.resetFields();
        }}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreate}
        >
          <Form.Item
            name="name"
            label="名称"
            rules={[{ required: true, message: '请输入名称' }]}
          >
            <Input placeholder="例如：订单通知" />
          </Form.Item>

          <Form.Item
            name="url"
            label="URL"
            rules={[
              { required: true, message: '请输入 URL' },
              { type: 'url', message: '请输入有效的 URL' },
            ]}
          >
            <Input placeholder="https://api.example.com/webhook" />
          </Form.Item>

          <Form.Item
            name="events"
            label="订阅事件"
            rules={[{ required: true, message: '请选择至少一个事件' }]}
          >
            <Select
              mode="multiple"
              placeholder="选择要订阅的事件"
              options={availableEvents}
            />
          </Form.Item>

          <Form.Item
            name="secret"
            label="密钥 (可选)"
            extra="用于验证请求签名"
          >
            <Input.Password placeholder="留空自动生成" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingWebhook ? '保存' : '创建'}
              </Button>
              <Button onClick={() => {
                setCreateModalVisible(false);
                setEditingWebhook(null);
                form.resetFields();
              }}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default WebhookManage;
