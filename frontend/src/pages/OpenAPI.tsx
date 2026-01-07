/**
 * PowerX 开放 API 管理页面
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
  InputNumber,
  Tag,
  Space,
  Typography,
  Statistic,
  Row,
  Col,
  message,
  Popconfirm,
  Alert,
} from 'antd';
import {
  KeyOutlined,
  PlusOutlined,
  DeleteOutlined,
  CopyOutlined,
  ApiOutlined,
  SafetyCertificateOutlined,
} from '@ant-design/icons';

const { Text, Paragraph } = Typography;
const { Option } = Select;

// 可用权限
const availablePermissions = [
  { value: 'market.read', label: '读取市场数据' },
  { value: 'market.subscribe', label: '订阅实时数据' },
  { value: 'order.read', label: '读取订单' },
  { value: 'order.create', label: '创建订单' },
  { value: 'order.cancel', label: '取消订单' },
  { value: 'position.read', label: '读取持仓' },
  { value: 'account.read', label: '读取账户' },
  { value: 'report.read', label: '读取报表' },
];

// 模拟数据
const mockKeys = [
  {
    key_id: 'KEY-A1B2C3D4E5F6',
    name: '生产环境',
    api_key: 'pk_live_xxxxxxxxxxxxx',
    permissions: ['market.read', 'order.read', 'position.read'],
    status: 'active',
    request_count: 12580,
    last_used_at: '2026-01-07 10:30:00',
    expires_at: '2027-01-07',
    created_at: '2026-01-07',
  },
  {
    key_id: 'KEY-G7H8I9J0K1L2',
    name: '测试环境',
    api_key: 'pk_test_xxxxxxxxxxxxx',
    permissions: ['market.read'],
    status: 'active',
    request_count: 458,
    last_used_at: '2026-01-06 15:20:00',
    expires_at: '2027-01-07',
    created_at: '2026-01-06',
  },
];

const OpenAPI: React.FC = () => {
  const [keys, setKeys] = useState(mockKeys);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [newKeyInfo, setNewKeyInfo] = useState<any>(null);
  const [form] = Form.useForm();

  const handleCreate = async (values: any) => {
    // 模拟创建新密钥
    const newKey = {
      key_id: `KEY-${Date.now()}`,
      name: values.name,
      api_key: `pk_${Math.random().toString(36).substring(2, 15)}`,
      api_secret: `sk_${Math.random().toString(36).substring(2, 30)}`,
      permissions: values.permissions,
      status: 'active',
      request_count: 0,
      last_used_at: null,
      expires_at: new Date(Date.now() + values.expires_days * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      created_at: new Date().toISOString().split('T')[0],
    };

    setNewKeyInfo(newKey);
    setKeys([...keys, newKey]);
    form.resetFields();
  };

  const handleRevoke = (keyId: string) => {
    setKeys(keys.map(k => 
      k.key_id === keyId ? { ...k, status: 'revoked' } : k
    ));
    message.success('密钥已吊销');
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    message.success('已复制到剪贴板');
  };

  const columns = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => (
        <Space>
          <KeyOutlined />
          <Text strong>{text}</Text>
        </Space>
      ),
    },
    {
      title: 'API Key',
      dataIndex: 'api_key',
      key: 'api_key',
      render: (key: string) => (
        <Space>
          <Text code>{key.substring(0, 12)}...</Text>
          <Button
            type="link"
            size="small"
            icon={<CopyOutlined />}
            onClick={() => copyToClipboard(key)}
          />
        </Space>
      ),
    },
    {
      title: '权限',
      dataIndex: 'permissions',
      key: 'permissions',
      render: (perms: string[]) => (
        <Space wrap>
          {perms.slice(0, 3).map(p => (
            <Tag key={p} color="blue">
              {availablePermissions.find(ap => ap.value === p)?.label || p}
            </Tag>
          ))}
          {perms.length > 3 && <Tag>+{perms.length - 3}</Tag>}
        </Space>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'active' ? 'success' : 'error'}>
          {status === 'active' ? '活跃' : '已吊销'}
        </Tag>
      ),
    },
    {
      title: '请求次数',
      dataIndex: 'request_count',
      key: 'request_count',
      render: (count: number) => count.toLocaleString(),
    },
    {
      title: '到期时间',
      dataIndex: 'expires_at',
      key: 'expires_at',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Space>
          {record.status === 'active' && (
            <Popconfirm
              title="确定吊销此密钥？此操作不可撤销。"
              onConfirm={() => handleRevoke(record.key_id)}
            >
              <Button type="link" size="small" danger icon={<DeleteOutlined />}>
                吊销
              </Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="活跃密钥"
              value={keys.filter(k => k.status === 'active').length}
              prefix={<KeyOutlined />}
              suffix="个"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总请求数"
              value={keys.reduce((sum, k) => sum + k.request_count, 0)}
              prefix={<ApiOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日请求"
              value={1256}
              prefix={<ApiOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="成功率"
              value={99.8}
              prefix={<SafetyCertificateOutlined />}
              suffix="%"
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* API 密钥列表 */}
      <Card
        title={
          <Space>
            <KeyOutlined />
            <span>API 密钥管理</span>
          </Space>
        }
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              setNewKeyInfo(null);
              setCreateModalVisible(true);
            }}
          >
            创建密钥
          </Button>
        }
      >
        <Paragraph type="secondary" style={{ marginBottom: 16 }}>
          使用 API 密钥可以通过 REST API 访问 PowerX 系统。请妥善保管您的密钥，不要在客户端代码中暴露。
        </Paragraph>

        <Table
          columns={columns}
          dataSource={keys}
          rowKey="key_id"
          pagination={false}
        />
      </Card>

      {/* 创建密钥弹窗 */}
      <Modal
        title="创建 API 密钥"
        open={createModalVisible}
        onCancel={() => {
          setCreateModalVisible(false);
          setNewKeyInfo(null);
          form.resetFields();
        }}
        footer={null}
        width={600}
      >
        {newKeyInfo ? (
          <div>
            <Alert
              message="密钥创建成功"
              description="请立即保存以下信息，API Secret 仅显示一次！"
              type="warning"
              showIcon
              style={{ marginBottom: 16 }}
            />

            <Card size="small" style={{ marginBottom: 16 }}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <Text type="secondary">API Key:</Text>
                  <br />
                  <Text code copyable>{newKeyInfo.api_key}</Text>
                </div>
                <div>
                  <Text type="secondary">API Secret (仅显示一次):</Text>
                  <br />
                  <Text code copyable style={{ color: '#f5222d' }}>
                    {newKeyInfo.api_secret}
                  </Text>
                </div>
              </Space>
            </Card>

            <Button
              type="primary"
              block
              onClick={() => {
                setCreateModalVisible(false);
                setNewKeyInfo(null);
              }}
            >
              我已保存，关闭
            </Button>
          </div>
        ) : (
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
              <Input placeholder="例如：生产环境、测试环境" />
            </Form.Item>

            <Form.Item
              name="permissions"
              label="权限"
              rules={[{ required: true, message: '请选择权限' }]}
            >
              <Select
                mode="multiple"
                placeholder="选择 API 权限"
                options={availablePermissions}
              />
            </Form.Item>

            <Form.Item
              name="allowed_ips"
              label="IP 白名单 (可选)"
              extra="多个 IP 用逗号分隔，留空则不限制"
            >
              <Input placeholder="例如：192.168.1.1, 10.0.0.1" />
            </Form.Item>

            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="rate_limit"
                  label="速率限制"
                  initialValue={1000}
                >
                  <InputNumber
                    style={{ width: '100%' }}
                    min={100}
                    max={10000}
                    addonAfter="次/小时"
                  />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="expires_days"
                  label="有效期"
                  initialValue={365}
                >
                  <InputNumber
                    style={{ width: '100%' }}
                    min={30}
                    max={730}
                    addonAfter="天"
                  />
                </Form.Item>
              </Col>
            </Row>

            <Form.Item>
              <Space>
                <Button type="primary" htmlType="submit">
                  创建密钥
                </Button>
                <Button onClick={() => {
                  setCreateModalVisible(false);
                  form.resetFields();
                }}>
                  取消
                </Button>
              </Space>
            </Form.Item>
          </Form>
        )}
      </Modal>
    </div>
  );
};

export default OpenAPI;
