/**
 * PowerX 期权交易页面
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
  Tabs,
  message,
} from 'antd';
import {
  RiseOutlined,
  FallOutlined,
  PlusOutlined,
  DollarOutlined,
} from '@ant-design/icons';

const { Option } = Select;

// 模拟期权合约数据
const mockContracts = [
  {
    contract_id: 'OPT-20260107-A1B2C3',
    name: '广东电力看涨期权 202603',
    underlying: '广东电力',
    option_type: 'call',
    strike_price: 450,
    premium: 15.5,
    expiration_date: '2026-03-31',
    is_active: true,
  },
  {
    contract_id: 'OPT-20260107-D4E5F6',
    name: '广东电力看跌期权 202603',
    underlying: '广东电力',
    option_type: 'put',
    strike_price: 400,
    premium: 12.3,
    expiration_date: '2026-03-31',
    is_active: true,
  },
  {
    contract_id: 'OPT-20260107-G7H8I9',
    name: '江苏电力看涨期权 202606',
    underlying: '江苏电力',
    option_type: 'call',
    strike_price: 420,
    premium: 18.0,
    expiration_date: '2026-06-30',
    is_active: true,
  },
];

// 模拟持仓数据
const mockPositions = [
  {
    contract_id: 'OPT-20260107-A1B2C3',
    contract_name: '广东电力看涨期权 202603',
    side: 'long',
    quantity: 100,
    avg_price: 15.5,
    current_price: 18.2,
    unrealized_pnl: 270,
  },
  {
    contract_id: 'OPT-20260107-D4E5F6',
    contract_name: '广东电力看跌期权 202603',
    side: 'short',
    quantity: 50,
    avg_price: 12.3,
    current_price: 10.8,
    unrealized_pnl: 75,
  },
];

const OptionTrading: React.FC = () => {
  const [contracts, setContracts] = useState(mockContracts);
  const [positions, setPositions] = useState(mockPositions);
  const [orderModalVisible, setOrderModalVisible] = useState(false);
  const [selectedContract, setSelectedContract] = useState<any>(null);
  const [form] = Form.useForm();

  const handlePlaceOrder = async (values: any) => {
    message.success('订单提交成功');
    setOrderModalVisible(false);
    form.resetFields();
  };

  const openOrderModal = (contract: any) => {
    setSelectedContract(contract);
    form.setFieldsValue({ contract_id: contract.contract_id });
    setOrderModalVisible(true);
  };

  const contractColumns = [
    {
      title: '合约代码',
      dataIndex: 'contract_id',
      key: 'contract_id',
      render: (text: string) => (
        <span style={{ fontFamily: 'monospace' }}>{text}</span>
      ),
    },
    {
      title: '合约名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '类型',
      dataIndex: 'option_type',
      key: 'option_type',
      render: (type: string) => (
        <Tag
          color={type === 'call' ? 'green' : 'red'}
          icon={type === 'call' ? <RiseOutlined /> : <FallOutlined />}
        >
          {type === 'call' ? '看涨' : '看跌'}
        </Tag>
      ),
    },
    {
      title: '标的',
      dataIndex: 'underlying',
      key: 'underlying',
    },
    {
      title: '执行价格',
      dataIndex: 'strike_price',
      key: 'strike_price',
      render: (value: number) => `¥${value}/MWh`,
    },
    {
      title: '权利金',
      dataIndex: 'premium',
      key: 'premium',
      render: (value: number) => (
        <span style={{ color: '#1890ff', fontWeight: 'bold' }}>
          ¥{value}/MWh
        </span>
      ),
    },
    {
      title: '到期日',
      dataIndex: 'expiration_date',
      key: 'expiration_date',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Space>
          <Button
            type="primary"
            size="small"
            onClick={() => openOrderModal(record)}
          >
            交易
          </Button>
          <Button size="small">详情</Button>
        </Space>
      ),
    },
  ];

  const positionColumns = [
    {
      title: '合约',
      dataIndex: 'contract_name',
      key: 'contract_name',
    },
    {
      title: '方向',
      dataIndex: 'side',
      key: 'side',
      render: (side: string) => (
        <Tag color={side === 'long' ? 'green' : 'red'}>
          {side === 'long' ? '多头' : '空头'}
        </Tag>
      ),
    },
    {
      title: '持仓量',
      dataIndex: 'quantity',
      key: 'quantity',
      render: (value: number) => value.toLocaleString(),
    },
    {
      title: '均价',
      dataIndex: 'avg_price',
      key: 'avg_price',
      render: (value: number) => `¥${value}`,
    },
    {
      title: '现价',
      dataIndex: 'current_price',
      key: 'current_price',
      render: (value: number) => `¥${value}`,
    },
    {
      title: '未实现盈亏',
      dataIndex: 'unrealized_pnl',
      key: 'unrealized_pnl',
      render: (value: number) => (
        <span style={{ color: value >= 0 ? '#52c41a' : '#f5222d', fontWeight: 'bold' }}>
          {value >= 0 ? '+' : ''}{value.toLocaleString()}
        </span>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: () => (
        <Space>
          <Button size="small" type="primary">平仓</Button>
          <Button size="small">行权</Button>
        </Space>
      ),
    },
  ];

  const tabItems = [
    {
      key: 'contracts',
      label: '期权合约',
      children: (
        <Table
          columns={contractColumns}
          dataSource={contracts}
          rowKey="contract_id"
          pagination={{ pageSize: 10 }}
        />
      ),
    },
    {
      key: 'positions',
      label: '我的持仓',
      children: (
        <Table
          columns={positionColumns}
          dataSource={positions}
          rowKey="contract_id"
          pagination={false}
        />
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
              title="持仓市值"
              value={25800}
              prefix={<DollarOutlined />}
              suffix="元"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="未实现盈亏"
              value={345}
              valueStyle={{ color: '#52c41a' }}
              prefix="+"
              suffix="元"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已实现盈亏"
              value={1280}
              valueStyle={{ color: '#52c41a' }}
              prefix="+"
              suffix="元"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="活跃合约"
              value={12}
              suffix="个"
            />
          </Card>
        </Col>
      </Row>

      {/* 主内容 */}
      <Card
        title="期权交易"
        extra={
          <Button type="primary" icon={<PlusOutlined />}>
            自定义合约
          </Button>
        }
      >
        <Tabs items={tabItems} />
      </Card>

      {/* 下单弹窗 */}
      <Modal
        title={`交易 - ${selectedContract?.name || ''}`}
        open={orderModalVisible}
        onCancel={() => setOrderModalVisible(false)}
        footer={null}
        width={500}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handlePlaceOrder}
        >
          <Form.Item name="contract_id" hidden>
            <Input />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="side"
                label="买卖方向"
                rules={[{ required: true }]}
              >
                <Select placeholder="选择方向">
                  <Option value="buy">买入</Option>
                  <Option value="sell">卖出</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="position_effect"
                label="开平仓"
                rules={[{ required: true }]}
              >
                <Select placeholder="选择开平仓">
                  <Option value="open">开仓</Option>
                  <Option value="close">平仓</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="quantity"
                label="数量"
                rules={[{ required: true }]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={1}
                  placeholder="输入数量"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="price"
                label="价格 (留空为市价)"
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={0}
                  placeholder="权利金"
                />
              </Form.Item>
            </Col>
          </Row>

          {selectedContract && (
            <Card size="small" style={{ marginBottom: 16, background: '#fafafa' }}>
              <Row>
                <Col span={12}>
                  <div>执行价格: ¥{selectedContract.strike_price}/MWh</div>
                </Col>
                <Col span={12}>
                  <div>当前权利金: ¥{selectedContract.premium}/MWh</div>
                </Col>
              </Row>
            </Card>
          )}

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                提交订单
              </Button>
              <Button onClick={() => setOrderModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default OptionTrading;
