/**
 * PowerX 组合订单管理页面
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 提供组合订单的创建、查看和管理功能
 */

import React, { useState, useEffect } from 'react';
import { 
  Card, Table, Button, Modal, Form, Input, Select, InputNumber, 
  Space, Tag, message, Popconfirm, Steps, Radio, List, Empty,
  Row, Col, Statistic, Tooltip, theme
} from 'antd';
import { 
  PlusOutlined, DeleteOutlined, SendOutlined, 
  ShoppingCartOutlined, ReloadOutlined, CheckCircleOutlined,
  ClockCircleOutlined, ExclamationCircleOutlined, EyeOutlined
} from '@ant-design/icons';
import api from '../services/api';

const { useToken } = theme;

interface OrderItem {
  order_id?: string;
  province: string;
  market_type: string;
  order_type: string;
  quantity: number;
  price?: number;
  priority: number;
  status?: string;
  filled_quantity?: number;
}

interface ComboOrder {
  combo_id: string;
  name: string;
  description?: string;
  execution_strategy: string;
  status: string;
  total_orders: number;
  filled_orders: number;
  total_quantity: number;
  total_amount: number;
  items: OrderItem[];
}

// Mock 数据
const mockCombos: ComboOrder[] = [
  {
    combo_id: 'COMBO-20260107-001',
    name: '日前批量采购',
    description: '多省份同时买入',
    execution_strategy: 'all_or_none',
    status: 'filled',
    total_orders: 3,
    filled_orders: 3,
    total_quantity: 500,
    total_amount: 225000,
    items: [
      { order_id: 'ORD-001', province: '广东', market_type: 'spot', order_type: 'buy', quantity: 200, price: 450, priority: 0, status: 'filled', filled_quantity: 200 },
      { order_id: 'ORD-002', province: '浙江', market_type: 'spot', order_type: 'buy', quantity: 150, price: 445, priority: 1, status: 'filled', filled_quantity: 150 },
      { order_id: 'ORD-003', province: '江苏', market_type: 'spot', order_type: 'buy', quantity: 150, price: 455, priority: 2, status: 'filled', filled_quantity: 150 }
    ]
  },
  {
    combo_id: 'COMBO-20260107-002',
    name: '套利组合',
    description: '广东买入浙江卖出',
    execution_strategy: 'partial_ok',
    status: 'partial',
    total_orders: 2,
    filled_orders: 1,
    total_quantity: 300,
    total_amount: 135000,
    items: [
      { order_id: 'ORD-004', province: '广东', market_type: 'spot', order_type: 'buy', quantity: 150, price: 440, priority: 0, status: 'filled', filled_quantity: 150 },
      { order_id: 'ORD-005', province: '浙江', market_type: 'spot', order_type: 'sell', quantity: 150, price: 460, priority: 1, status: 'pending', filled_quantity: 0 }
    ]
  },
  {
    combo_id: 'COMBO-20260107-003',
    name: '中长期组合',
    description: '多月份分批买入',
    execution_strategy: 'best_effort',
    status: 'submitted',
    total_orders: 4,
    filled_orders: 0,
    total_quantity: 800,
    total_amount: 360000,
    items: [
      { order_id: 'ORD-006', province: '广东', market_type: 'mid_long', order_type: 'buy', quantity: 200, price: 448, priority: 0, status: 'pending', filled_quantity: 0 },
      { order_id: 'ORD-007', province: '广东', market_type: 'mid_long', order_type: 'buy', quantity: 200, price: 452, priority: 1, status: 'pending', filled_quantity: 0 },
      { order_id: 'ORD-008', province: '广东', market_type: 'mid_long', order_type: 'buy', quantity: 200, price: 455, priority: 2, status: 'pending', filled_quantity: 0 },
      { order_id: 'ORD-009', province: '广东', market_type: 'mid_long', order_type: 'buy', quantity: 200, price: 458, priority: 3, status: 'pending', filled_quantity: 0 }
    ]
  }
];

const ComboOrder: React.FC = () => {
  const { token } = useToken();
  const [combos, setCombos] = useState<ComboOrder[]>(mockCombos);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [selectedCombo, setSelectedCombo] = useState<ComboOrder | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [form] = Form.useForm();
  const [items, setItems] = useState<OrderItem[]>([]);

  useEffect(() => {
    loadCombos();
  }, []);

  const loadCombos = async () => {
    try {
      const res = await api.get('/combo-orders');
      if (res.data && res.data.length > 0) {
        setCombos(res.data);
      }
    } catch (error) {
      console.error('加载失败，使用 Mock 数据:', error);
      setCombos(mockCombos);
    }
  };

  const handleCreate = async () => {
    try {
      const values = await form.validateFields();
      await api.post('/combo-orders', {
        ...values,
        items: items.map((item, idx) => ({ ...item, priority: idx }))
      });
      message.success('创建成功');
      setModalVisible(false);
      form.resetFields();
      setItems([]);
      setCurrentStep(0);
      loadCombos();
    } catch (error) {
      message.error('创建失败');
    }
  };

  const handleSubmit = async (comboId: string) => {
    try {
      await api.post(`/combo-orders/${comboId}/submit`);
      message.success('提交成功');
      loadCombos();
    } catch (error) {
      message.error('提交失败');
    }
  };

  const handleCancel = async (comboId: string) => {
    try {
      await api.post(`/combo-orders/${comboId}/cancel`);
      message.success('已取消');
      loadCombos();
    } catch (error) {
      message.error('取消失败');
    }
  };

  const handleViewDetail = (combo: ComboOrder) => {
    setSelectedCombo(combo);
    setDetailModalVisible(true);
  };

  const addItem = () => {
    setItems([
      ...items,
      {
        province: '广东',
        market_type: 'spot',
        order_type: 'buy',
        quantity: 100,
        price: 450,
        priority: items.length
      }
    ]);
  };

  const removeItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const updateItem = (index: number, field: string, value: any) => {
    const newItems = [...items];
    newItems[index] = { ...newItems[index], [field]: value };
    setItems(newItems);
  };

  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; text: string; icon: React.ReactNode }> = {
      draft: { color: 'default', text: '草稿', icon: <ClockCircleOutlined /> },
      pending: { color: 'processing', text: '待提交', icon: <ClockCircleOutlined /> },
      submitted: { color: 'blue', text: '已提交', icon: <ClockCircleOutlined /> },
      partial: { color: 'warning', text: '部分成交', icon: <ExclamationCircleOutlined /> },
      filled: { color: 'success', text: '全部成交', icon: <CheckCircleOutlined /> },
      cancelled: { color: 'default', text: '已取消', icon: null },
      failed: { color: 'error', text: '失败', icon: null }
    };
    const s = statusMap[status] || { color: 'default', text: status, icon: null };
    return <Tag color={s.color} icon={s.icon}>{s.text}</Tag>;
  };

  const getStrategyLabel = (strategy: string) => {
    const labels: Record<string, string> = {
      all_or_none: '全部成交或取消',
      partial_ok: '允许部分成交',
      best_effort: '尽力成交'
    };
    return labels[strategy] || strategy;
  };

  const columns = [
    {
      title: '组合名称',
      key: 'name',
      render: (_: any, record: ComboOrder) => (
        <Space>
          <ShoppingCartOutlined style={{ color: token.colorPrimary }} />
          <span>{record.name}</span>
        </Space>
      )
    },
    {
      title: '组合ID',
      dataIndex: 'combo_id',
      key: 'combo_id',
      render: (text: string) => <Tag color="blue">{text}</Tag>
    },
    {
      title: '执行策略',
      dataIndex: 'execution_strategy',
      key: 'execution_strategy',
      render: (text: string) => <Tag>{getStrategyLabel(text)}</Tag>
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => getStatusTag(status)
    },
    {
      title: '进度',
      key: 'progress',
      render: (_: any, record: ComboOrder) => (
        <span>{record.filled_orders} / {record.total_orders} 单</span>
      )
    },
    {
      title: '总电量',
      dataIndex: 'total_quantity',
      key: 'total_quantity',
      render: (val: number) => `${val.toLocaleString()} MWh`
    },
    {
      title: '总金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      render: (val: number) => `¥${val.toLocaleString()}`
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: any, record: ComboOrder) => (
        <Space>
          <Tooltip title="查看详情">
            <Button 
              type="text" 
              icon={<EyeOutlined />}
              onClick={() => handleViewDetail(record)}
            />
          </Tooltip>
          {record.status === 'draft' && (
            <Tooltip title="提交">
              <Button 
                type="text"
                icon={<SendOutlined />}
                onClick={() => handleSubmit(record.combo_id)}
              />
            </Tooltip>
          )}
          {['draft', 'submitted', 'partial'].includes(record.status) && (
            <Popconfirm
              title="确认取消?"
              onConfirm={() => handleCancel(record.combo_id)}
            >
              <Tooltip title="取消">
                <Button type="text" danger icon={<DeleteOutlined />} />
              </Tooltip>
            </Popconfirm>
          )}
        </Space>
      )
    }
  ];

  // 统计数据
  const stats = {
    total: combos.length,
    submitted: combos.filter(c => c.status === 'submitted').length,
    partial: combos.filter(c => c.status === 'partial').length,
    filled: combos.filter(c => c.status === 'filled').length,
    totalQuantity: combos.reduce((sum, c) => sum + c.total_quantity, 0),
    totalAmount: combos.reduce((sum, c) => sum + c.total_amount, 0)
  };

  return (
    <div style={{ padding: 24 }}>
      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic 
              title="全部组合" 
              value={stats.total} 
              prefix={<ShoppingCartOutlined />}
              valueStyle={{ color: token.colorPrimary }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="已提交" 
              value={stats.submitted} 
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: token.colorInfo }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="部分成交" 
              value={stats.partial}
              prefix={<ExclamationCircleOutlined />}
              valueStyle={{ color: token.colorWarning }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="全部成交" 
              value={stats.filled}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: token.colorSuccess }}
            />
          </Card>
        </Col>
      </Row>

      {/* 组合列表 */}
      <Card
        title={
          <Space>
            <ShoppingCartOutlined />
            <span>组合订单管理</span>
          </Space>
        }
        extra={
          <Space>
            <Button icon={<ReloadOutlined />} onClick={loadCombos}>
              刷新
            </Button>
            <Button 
              type="primary" 
              icon={<PlusOutlined />} 
              onClick={() => setModalVisible(true)}
            >
              创建组合
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={combos}
          rowKey="combo_id"
          loading={loading}
          pagination={{ pageSize: 10 }}
          expandable={{ 
            expandedRowRender: (record: ComboOrder) => (
              <Table
                dataSource={record.items}
                rowKey="order_id"
                size="small"
                pagination={false}
                columns={[
                  { title: '订单ID', dataIndex: 'order_id', key: 'order_id' },
                  { title: '省份', dataIndex: 'province', key: 'province' },
                  { 
                    title: '市场', 
                    dataIndex: 'market_type', 
                    key: 'market_type',
                    render: (t: string) => t === 'spot' ? '现货' : '中长期'
                  },
                  { 
                    title: '方向', 
                    dataIndex: 'order_type', 
                    key: 'order_type',
                    render: (t: string) => (
                      <Tag color={t === 'buy' ? 'red' : 'green'}>{t === 'buy' ? '买入' : '卖出'}</Tag>
                    )
                  },
                  { title: '电量', dataIndex: 'quantity', key: 'quantity', render: (v: number) => `${v} MWh` },
                  { title: '价格', dataIndex: 'price', key: 'price', render: (v: number) => v ? `¥${v}` : '-' },
                  { 
                    title: '状态', 
                    dataIndex: 'status', 
                    key: 'status',
                    render: (s: string) => getStatusTag(s)
                  }
                ]}
              />
            )
          }}
          locale={{
            emptyText: <Empty description="暂无组合订单" />
          }}
        />
      </Card>

      {/* 创建组合弹窗 */}
      <Modal
        title="创建组合订单"
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
          setItems([]);
          setCurrentStep(0);
        }}
        width={800}
        footer={
          <Space>
            {currentStep > 0 && (
              <Button onClick={() => setCurrentStep(currentStep - 1)}>上一步</Button>
            )}
            {currentStep < 1 ? (
              <Button type="primary" onClick={() => setCurrentStep(1)}>
                下一步
              </Button>
            ) : (
              <Button type="primary" onClick={handleCreate} disabled={items.length === 0}>
                创建组合
              </Button>
            )}
          </Space>
        }
      >
        <Steps
          current={currentStep}
          items={[
            { title: '基本信息' },
            { title: '添加订单' }
          ]}
          style={{ marginBottom: 24 }}
        />

        {currentStep === 0 && (
          <Form form={form} layout="vertical">
            <Form.Item name="name" label="组合名称" rules={[{ required: true }]}>
              <Input placeholder="例如: 日前批量采购" />
            </Form.Item>
            <Form.Item name="description" label="描述">
              <Input.TextArea placeholder="可选描述" />
            </Form.Item>
            <Form.Item name="execution_strategy" label="执行策略" initialValue="all_or_none">
              <Radio.Group>
                <Radio.Button value="all_or_none">全部成交或取消</Radio.Button>
                <Radio.Button value="partial_ok">允许部分成交</Radio.Button>
                <Radio.Button value="best_effort">尽力成交</Radio.Button>
              </Radio.Group>
            </Form.Item>
          </Form>
        )}

        {currentStep === 1 && (
          <div>
            <Button 
              type="dashed" 
              onClick={addItem} 
              icon={<PlusOutlined />}
              style={{ marginBottom: 16, width: '100%' }}
            >
              添加订单
            </Button>
            
            {items.length === 0 ? (
              <Empty description="暂无订单，请添加" />
            ) : (
              <List
                dataSource={items}
                renderItem={(item, index) => (
                  <List.Item
                    actions={[
                      <Button 
                        danger 
                        size="small" 
                        icon={<DeleteOutlined />}
                        onClick={() => removeItem(index)}
                      />
                    ]}
                  >
                    <Space wrap>
                      <Select
                        value={item.province}
                        onChange={v => updateItem(index, 'province', v)}
                        style={{ width: 100 }}
                        options={[
                          { value: '广东', label: '广东' },
                          { value: '浙江', label: '浙江' },
                          { value: '江苏', label: '江苏' }
                        ]}
                      />
                      <Select
                        value={item.market_type}
                        onChange={v => updateItem(index, 'market_type', v)}
                        style={{ width: 100 }}
                        options={[
                          { value: 'spot', label: '现货' },
                          { value: 'mid_long', label: '中长期' }
                        ]}
                      />
                      <Select
                        value={item.order_type}
                        onChange={v => updateItem(index, 'order_type', v)}
                        style={{ width: 80 }}
                        options={[
                          { value: 'buy', label: '买入' },
                          { value: 'sell', label: '卖出' }
                        ]}
                      />
                      <InputNumber
                        value={item.quantity}
                        onChange={v => updateItem(index, 'quantity', v)}
                        addonAfter="MWh"
                        min={1}
                        style={{ width: 130 }}
                      />
                      <InputNumber
                        value={item.price}
                        onChange={v => updateItem(index, 'price', v)}
                        addonBefore="¥"
                        min={0}
                        style={{ width: 130 }}
                      />
                    </Space>
                  </List.Item>
                )}
              />
            )}
          </div>
        )}
      </Modal>

      {/* 详情弹窗 */}
      <Modal
        title="组合订单详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
        {selectedCombo && (
          <>
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={8}>
                <Statistic title="组合名称" value={selectedCombo.name} />
              </Col>
              <Col span={8}>
                <Statistic title="总电量" value={selectedCombo.total_quantity} suffix="MWh" />
              </Col>
              <Col span={8}>
                <Statistic title="总金额" value={selectedCombo.total_amount} prefix="¥" />
              </Col>
            </Row>
            <Table
              dataSource={selectedCombo.items}
              rowKey="order_id"
              size="small"
              pagination={false}
              columns={[
                { title: '订单ID', dataIndex: 'order_id', key: 'order_id' },
                { title: '省份', dataIndex: 'province', key: 'province' },
                { 
                  title: '方向', 
                  dataIndex: 'order_type', 
                  key: 'order_type',
                  render: (t: string) => (
                    <Tag color={t === 'buy' ? 'red' : 'green'}>{t === 'buy' ? '买入' : '卖出'}</Tag>
                  )
                },
                { title: '电量', dataIndex: 'quantity', key: 'quantity', render: (v: number) => `${v} MWh` },
                { title: '价格', dataIndex: 'price', key: 'price', render: (v: number) => v ? `¥${v}` : '-' },
                { 
                  title: '状态', 
                  dataIndex: 'status', 
                  key: 'status',
                  render: (s: string) => getStatusTag(s)
                }
              ]}
            />
          </>
        )}
      </Modal>
    </div>
  );
};

export default ComboOrder;
