/**
 * PowerX 跨省交易页面
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
  DatePicker,
  Tag,
  Space,
  Statistic,
  Row,
  Col,
  message,
} from 'antd';
import {
  SwapOutlined,
  PlusOutlined,
  ThunderboltOutlined,
  DollarOutlined,
} from '@ant-design/icons';

const { Option } = Select;
const { RangePicker } = DatePicker;

// 省份列表
const provinces = [
  '广东', '广西', '云南', '贵州', '海南',
  '江苏', '浙江', '上海', '安徽', '福建',
  '山东', '河南', '湖北', '湖南', '江西',
  '四川', '重庆', '内蒙古', '甘肃', '新疆',
];

// 模拟订单数据
const mockOrders = [
  {
    order_id: 'CRO-20260107-A1B2C3',
    order_type: 'buy',
    source_province: '广东',
    target_province: '云南',
    quantity: 1000,
    price: 380,
    transmission_fee: 25,
    total_price: 405,
    status: 'pending',
    created_at: '2026-01-07 10:30:00',
  },
  {
    order_id: 'CRO-20260107-D4E5F6',
    order_type: 'sell',
    source_province: '云南',
    target_province: '广东',
    quantity: 800,
    price: 350,
    transmission_fee: 25,
    total_price: 375,
    status: 'matched',
    created_at: '2026-01-07 09:15:00',
  },
];

// 模拟通道数据
const mockChannels = [
  {
    channel_id: 'CH-001',
    name: '云广特高压直流',
    from_province: '云南',
    to_province: '广东',
    capacity: 5000,
    available_capacity: 3200,
    transmission_fee: 25,
    loss_rate: 0.03,
  },
  {
    channel_id: 'CH-002',
    name: '西电东送南通道',
    from_province: '贵州',
    to_province: '广东',
    capacity: 4000,
    available_capacity: 2800,
    transmission_fee: 22,
    loss_rate: 0.025,
  },
];

const statusColors: Record<string, string> = {
  pending: 'blue',
  matching: 'processing',
  matched: 'green',
  partial: 'orange',
  completed: 'success',
  cancelled: 'default',
  failed: 'error',
};

const statusLabels: Record<string, string> = {
  pending: '待撮合',
  matching: '撮合中',
  matched: '已撮合',
  partial: '部分成交',
  completed: '已完成',
  cancelled: '已取消',
  failed: '失败',
};

const CrossProvince: React.FC = () => {
  const [orders, setOrders] = useState(mockOrders);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [channelModalVisible, setChannelModalVisible] = useState(false);
  const [form] = Form.useForm();

  const handleCreateOrder = async (values: any) => {
    const newOrder = {
      order_id: `CRO-${Date.now()}`,
      ...values,
      transmission_fee: 25,
      total_price: values.price + 25,
      status: 'pending',
      created_at: new Date().toISOString(),
    };
    setOrders([newOrder, ...orders]);
    setCreateModalVisible(false);
    form.resetFields();
    message.success('跨省订单创建成功');
  };

  const orderColumns = [
    {
      title: '订单号',
      dataIndex: 'order_id',
      key: 'order_id',
      render: (text: string) => (
        <span style={{ fontFamily: 'monospace' }}>{text}</span>
      ),
    },
    {
      title: '类型',
      dataIndex: 'order_type',
      key: 'order_type',
      render: (type: string) => (
        <Tag color={type === 'buy' ? 'green' : 'red'}>
          {type === 'buy' ? '买入' : '卖出'}
        </Tag>
      ),
    },
    {
      title: '交易路径',
      key: 'path',
      render: (_: any, record: any) => (
        <Space>
          <Tag color="blue">{record.source_province}</Tag>
          <SwapOutlined />
          <Tag color="purple">{record.target_province}</Tag>
        </Space>
      ),
    },
    {
      title: '电量 (MWh)',
      dataIndex: 'quantity',
      key: 'quantity',
      render: (value: number) => value.toLocaleString(),
    },
    {
      title: '电价',
      dataIndex: 'price',
      key: 'price',
      render: (value: number) => `¥${value}/MWh`,
    },
    {
      title: '输电费',
      dataIndex: 'transmission_fee',
      key: 'transmission_fee',
      render: (value: number) => `¥${value}/MWh`,
    },
    {
      title: '总价',
      dataIndex: 'total_price',
      key: 'total_price',
      render: (value: number) => (
        <span style={{ color: '#52c41a', fontWeight: 'bold' }}>
          ¥{value}/MWh
        </span>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={statusColors[status]}>
          {statusLabels[status]}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Space>
          <Button size="small" type="link">详情</Button>
          {record.status === 'pending' && (
            <Button size="small" type="link" danger>取消</Button>
          )}
        </Space>
      ),
    },
  ];

  const channelColumns = [
    {
      title: '通道名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '输电路径',
      key: 'path',
      render: (_: any, record: any) => (
        <Space>
          <Tag>{record.from_province}</Tag>
          <span>→</span>
          <Tag>{record.to_province}</Tag>
        </Space>
      ),
    },
    {
      title: '最大容量',
      dataIndex: 'capacity',
      key: 'capacity',
      render: (value: number) => `${value.toLocaleString()} MW`,
    },
    {
      title: '可用容量',
      dataIndex: 'available_capacity',
      key: 'available_capacity',
      render: (value: number, record: any) => (
        <span style={{ color: value / record.capacity > 0.5 ? '#52c41a' : '#faad14' }}>
          {value.toLocaleString()} MW
        </span>
      ),
    },
    {
      title: '输电费',
      dataIndex: 'transmission_fee',
      key: 'transmission_fee',
      render: (value: number) => `¥${value}/MWh`,
    },
    {
      title: '线损率',
      dataIndex: 'loss_rate',
      key: 'loss_rate',
      render: (value: number) => `${(value * 100).toFixed(1)}%`,
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日跨省交易量"
              value={12500}
              suffix="MWh"
              prefix={<ThunderboltOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="平均输电价格"
              value={24.5}
              suffix="元/MWh"
              prefix={<DollarOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="待撮合订单"
              value={8}
              suffix="笔"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="撮合成功率"
              value={85.6}
              suffix="%"
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 订单列表 */}
      <Card
        title={
          <Space>
            <SwapOutlined />
            <span>跨省交易订单</span>
          </Space>
        }
        extra={
          <Space>
            <Button onClick={() => setChannelModalVisible(true)}>
              输电通道
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setCreateModalVisible(true)}
            >
              新建订单
            </Button>
          </Space>
        }
      >
        <Table
          columns={orderColumns}
          dataSource={orders}
          rowKey="order_id"
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* 创建订单弹窗 */}
      <Modal
        title="创建跨省交易订单"
        open={createModalVisible}
        onCancel={() => setCreateModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateOrder}
        >
          <Form.Item
            name="order_type"
            label="交易类型"
            rules={[{ required: true }]}
          >
            <Select placeholder="选择交易类型">
              <Option value="buy">买入</Option>
              <Option value="sell">卖出</Option>
            </Select>
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="source_province"
                label="来源省份"
                rules={[{ required: true }]}
              >
                <Select placeholder="选择省份" showSearch>
                  {provinces.map(p => (
                    <Option key={p} value={p}>{p}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="target_province"
                label="目标省份"
                rules={[{ required: true }]}
              >
                <Select placeholder="选择省份" showSearch>
                  {provinces.map(p => (
                    <Option key={p} value={p}>{p}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="quantity"
                label="交易电量 (MWh)"
                rules={[{ required: true }]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={1}
                  placeholder="输入电量"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="price"
                label="报价 (元/MWh)"
                rules={[{ required: true }]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={0}
                  placeholder="输入价格"
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="delivery_time"
            label="交割时间"
            rules={[{ required: true }]}
          >
            <RangePicker
              style={{ width: '100%' }}
              showTime
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                提交订单
              </Button>
              <Button onClick={() => setCreateModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 输电通道弹窗 */}
      <Modal
        title="输电通道信息"
        open={channelModalVisible}
        onCancel={() => setChannelModalVisible(false)}
        footer={null}
        width={900}
      >
        <Table
          columns={channelColumns}
          dataSource={mockChannels}
          rowKey="channel_id"
          pagination={false}
        />
      </Modal>
    </div>
  );
};

export default CrossProvince;
