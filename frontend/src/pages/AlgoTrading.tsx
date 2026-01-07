/**
 * PowerX 算法交易管理页面
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 提供算法交易订单的创建、监控和管理功能
 */

import React, { useState, useEffect } from 'react';
import { 
  Card, Table, Button, Modal, Form, Select, InputNumber, 
  Space, Tag, message, Tabs, Progress, Slider, Tooltip,
  Row, Col, Statistic, Empty, theme
} from 'antd';
import { 
  RobotOutlined, PlayCircleOutlined, PauseCircleOutlined, 
  StopOutlined, LineChartOutlined, BarChartOutlined,
  ReloadOutlined, CheckCircleOutlined, ClockCircleOutlined,
  ExclamationCircleOutlined, PlusOutlined
} from '@ant-design/icons';
import api from '../services/api';

const { useToken } = theme;

interface AlgoOrder {
  algo_id: string;
  algo_type: string;
  algo_params: any;
  province: string;
  market_type: string;
  order_type: string;
  target_quantity: number;
  target_price?: number;
  status: string;
  filled_quantity: number;
  avg_price?: number;
  slices_total: number;
  slices_filled: number;
}

// Mock 数据
const mockAlgoOrders: AlgoOrder[] = [
  {
    algo_id: 'ALGO-20260107-001',
    algo_type: 'twap',
    algo_params: { duration_minutes: 120, slice_count: 12 },
    province: '广东',
    market_type: 'spot',
    order_type: 'buy',
    target_quantity: 500,
    target_price: 460,
    status: 'running',
    filled_quantity: 250,
    avg_price: 452.5,
    slices_total: 12,
    slices_filled: 6
  },
  {
    algo_id: 'ALGO-20260107-002',
    algo_type: 'vwap',
    algo_params: { duration_minutes: 180 },
    province: '浙江',
    market_type: 'spot',
    order_type: 'sell',
    target_quantity: 300,
    target_price: 480,
    status: 'completed',
    filled_quantity: 300,
    avg_price: 478.2,
    slices_total: 15,
    slices_filled: 15
  },
  {
    algo_id: 'ALGO-20260107-003',
    algo_type: 'iceberg',
    algo_params: { visible_quantity: 50, price: 455 },
    province: '江苏',
    market_type: 'spot',
    order_type: 'buy',
    target_quantity: 400,
    target_price: 455,
    status: 'paused',
    filled_quantity: 150,
    avg_price: 454.8,
    slices_total: 8,
    slices_filled: 3
  },
  {
    algo_id: 'ALGO-20260107-004',
    algo_type: 'twap',
    algo_params: { duration_minutes: 60, slice_count: 6 },
    province: '广东',
    market_type: 'mid_long',
    order_type: 'buy',
    target_quantity: 200,
    status: 'created',
    filled_quantity: 0,
    slices_total: 6,
    slices_filled: 0
  }
];

const AlgoTrading: React.FC = () => {
  const { token } = useToken();
  const [orders, setOrders] = useState<AlgoOrder[]>(mockAlgoOrders);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [algoType, setAlgoType] = useState<'twap' | 'vwap' | 'iceberg'>('twap');
  const [form] = Form.useForm();

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    try {
      const res = await api.get('/algo-trading');
      if (res.data && res.data.length > 0) {
        setOrders(res.data);
      }
    } catch (error) {
      console.error('加载失败，使用 Mock 数据:', error);
      setOrders(mockAlgoOrders);
    }
  };

  const handleCreate = async () => {
    try {
      const values = await form.validateFields();
      await api.post(`/algo-trading/${algoType}`, values);
      message.success('创建成功');
      setModalVisible(false);
      form.resetFields();
      loadOrders();
    } catch (error) {
      message.error('创建失败');
    }
  };

  const handleStart = async (algoId: string) => {
    try {
      await api.post(`/algo-trading/${algoId}/start`);
      message.success('已启动');
      loadOrders();
    } catch (error) {
      message.error('启动失败');
    }
  };

  const handlePause = async (algoId: string) => {
    try {
      await api.post(`/algo-trading/${algoId}/pause`);
      message.success('已暂停');
      loadOrders();
    } catch (error) {
      message.error('暂停失败');
    }
  };

  const handleCancel = async (algoId: string) => {
    try {
      await api.post(`/algo-trading/${algoId}/cancel`);
      message.success('已取消');
      loadOrders();
    } catch (error) {
      message.error('取消失败');
    }
  };

  const getAlgoTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      twap: 'TWAP',
      vwap: 'VWAP',
      iceberg: '冰山'
    };
    return labels[type] || type;
  };

  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; text: string; icon: React.ReactNode }> = {
      created: { color: 'default', text: '待启动', icon: <ClockCircleOutlined /> },
      running: { color: 'processing', text: '运行中', icon: <PlayCircleOutlined /> },
      paused: { color: 'warning', text: '已暂停', icon: <PauseCircleOutlined /> },
      completed: { color: 'success', text: '已完成', icon: <CheckCircleOutlined /> },
      cancelled: { color: 'default', text: '已取消', icon: null },
      failed: { color: 'error', text: '失败', icon: <ExclamationCircleOutlined /> }
    };
    const s = statusMap[status] || { color: 'default', text: status, icon: null };
    return <Tag color={s.color} icon={s.icon}>{s.text}</Tag>;
  };

  const getDirectionTag = (direction: string) => {
    if (direction === 'buy') {
      return <Tag color="red">买入</Tag>;
    }
    return <Tag color="green">卖出</Tag>;
  };

  const columns = [
    {
      title: '算法名称',
      key: 'name',
      render: (_: any, record: AlgoOrder) => (
        <Space>
          <RobotOutlined style={{ color: token.colorPrimary }} />
          <span>{getAlgoTypeLabel(record.algo_type)} #{record.algo_id.slice(-3)}</span>
        </Space>
      )
    },
    {
      title: '订单ID',
      dataIndex: 'algo_id',
      key: 'algo_id',
      render: (text: string) => <Tag color="blue">{text}</Tag>
    },
    {
      title: '算法类型',
      dataIndex: 'algo_type',
      key: 'algo_type',
      render: (type: string) => (
        <Tag color={type === 'iceberg' ? 'cyan' : 'purple'}>
          {getAlgoTypeLabel(type)}
        </Tag>
      )
    },
    {
      title: '方向',
      dataIndex: 'order_type',
      key: 'order_type',
      render: (type: string) => getDirectionTag(type)
    },
    {
      title: '目标电量',
      dataIndex: 'target_quantity',
      key: 'target_quantity',
      render: (val: number) => `${val.toLocaleString()} MWh`
    },
    {
      title: '执行进度',
      key: 'progress',
      width: 150,
      render: (_: any, record: AlgoOrder) => (
        <Space direction="vertical" size={0} style={{ width: '100%' }}>
          <Progress 
            percent={Math.round((record.slices_filled / record.slices_total) * 100)}
            size="small"
            status={record.status === 'running' ? 'active' : undefined}
          />
          <span style={{ fontSize: 12, color: token.colorTextSecondary }}>
            {record.slices_filled} / {record.slices_total} 切片
          </span>
        </Space>
      )
    },
    {
      title: '已成交',
      key: 'filled',
      render: (_: any, record: AlgoOrder) => (
        <Space direction="vertical" size={0}>
          <span>{record.filled_quantity.toLocaleString()} MWh</span>
          {record.avg_price && (
            <span style={{ fontSize: 12, color: token.colorTextSecondary }}>
              均价 ¥{record.avg_price.toFixed(2)}
            </span>
          )}
        </Space>
      )
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => getStatusTag(status)
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: any, record: AlgoOrder) => (
        <Space>
          {record.status === 'created' && (
            <Tooltip title="启动">
              <Button 
                type="text"
                icon={<PlayCircleOutlined />}
                onClick={() => handleStart(record.algo_id)}
              />
            </Tooltip>
          )}
          {record.status === 'running' && (
            <Tooltip title="暂停">
              <Button 
                type="text"
                icon={<PauseCircleOutlined />}
                onClick={() => handlePause(record.algo_id)}
              />
            </Tooltip>
          )}
          {record.status === 'paused' && (
            <Tooltip title="继续">
              <Button 
                type="text"
                icon={<PlayCircleOutlined />}
                onClick={() => handleStart(record.algo_id)}
              />
            </Tooltip>
          )}
          {['created', 'running', 'paused'].includes(record.status) && (
            <Tooltip title="取消">
              <Button 
                type="text"
                danger
                icon={<StopOutlined />}
                onClick={() => handleCancel(record.algo_id)}
              />
            </Tooltip>
          )}
        </Space>
      )
    }
  ];

  // 统计数据
  const stats = {
    total: orders.length,
    running: orders.filter(o => o.status === 'running').length,
    paused: orders.filter(o => o.status === 'paused').length,
    completed: orders.filter(o => o.status === 'completed').length,
    totalFilled: orders.reduce((sum, o) => sum + o.filled_quantity, 0)
  };

  const renderAlgoForm = () => {
    switch (algoType) {
      case 'twap':
        return (
          <>
            <Form.Item name="duration_minutes" label="执行时长(分钟)" rules={[{ required: true }]}>
              <InputNumber min={5} max={480} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item name="slice_count" label="切片数">
              <InputNumber min={2} max={50} style={{ width: '100%' }} />
            </Form.Item>
          </>
        );
      case 'vwap':
        return (
          <>
            <Form.Item name="duration_minutes" label="执行时长(分钟)" rules={[{ required: true }]}>
              <InputNumber min={5} max={480} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item label="成交量分布" extra="留空使用默认分布">
              <Slider 
                range 
                marks={{ 0: '开始', 100: '结束' }}
                disabled
              />
            </Form.Item>
          </>
        );
      case 'iceberg':
        return (
          <>
            <Form.Item name="visible_quantity" label="显示数量(MWh)" rules={[{ required: true }]}>
              <InputNumber min={1} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item name="price" label="价格" rules={[{ required: true }]}>
              <InputNumber min={0} addonBefore="¥" style={{ width: '100%' }} />
            </Form.Item>
          </>
        );
    }
  };

  return (
    <div style={{ padding: 24 }}>
      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic 
              title="全部算法单" 
              value={stats.total} 
              prefix={<RobotOutlined />}
              valueStyle={{ color: token.colorPrimary }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="运行中" 
              value={stats.running} 
              prefix={<PlayCircleOutlined />}
              valueStyle={{ color: token.colorInfo }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="已暂停" 
              value={stats.paused}
              prefix={<PauseCircleOutlined />}
              valueStyle={{ color: token.colorWarning }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="已完成" 
              value={stats.completed}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: token.colorSuccess }}
            />
          </Card>
        </Col>
      </Row>

      {/* 算法订单列表 */}
      <Card
        title={
          <Space>
            <RobotOutlined />
            <span>算法交易管理</span>
          </Space>
        }
        extra={
          <Space>
            <Button icon={<ReloadOutlined />} onClick={loadOrders}>
              刷新
            </Button>
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={() => setModalVisible(true)}
            >
              新建算法单
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={orders}
          rowKey="algo_id"
          loading={loading}
          pagination={{ pageSize: 10 }}
          locale={{
            emptyText: <Empty description="暂无算法订单" />
          }}
        />
      </Card>

      {/* 创建算法订单弹窗 */}
      <Modal
        title="新建算法订单"
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
        }}
        onOk={handleCreate}
        width={600}
      >
        <Tabs
          activeKey={algoType}
          onChange={(key) => {
            setAlgoType(key as 'twap' | 'vwap' | 'iceberg');
            form.resetFields();
          }}
          items={[
            {
              key: 'twap',
              label: (
                <Space>
                  <LineChartOutlined />
                  TWAP
                </Space>
              )
            },
            {
              key: 'vwap',
              label: (
                <Space>
                  <BarChartOutlined />
                  VWAP
                </Space>
              )
            },
            {
              key: 'iceberg',
              label: (
                <Space>
                  ❄️ 冰山订单
                </Space>
              )
            }
          ]}
        />

        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="order_type" label="交易方向" rules={[{ required: true }]}>
            <Select
              options={[
                { value: 'buy', label: '买入' },
                { value: 'sell', label: '卖出' }
              ]}
            />
          </Form.Item>
          
          <Form.Item name="target_quantity" label="目标电量(MWh)" rules={[{ required: true }]}>
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>
          
          <Form.Item name="province" label="省份" initialValue="广东">
            <Select
              options={[
                { value: '广东', label: '广东' },
                { value: '浙江', label: '浙江' },
                { value: '江苏', label: '江苏' }
              ]}
            />
          </Form.Item>
          
          {renderAlgoForm()}
          
          {algoType !== 'iceberg' && (
            <>
              <Form.Item name="price_limit_upper" label="价格上限">
                <InputNumber min={0} addonBefore="¥" style={{ width: '100%' }} />
              </Form.Item>
              <Form.Item name="price_limit_lower" label="价格下限">
                <InputNumber min={0} addonBefore="¥" style={{ width: '100%' }} />
              </Form.Item>
            </>
          )}
        </Form>
      </Modal>
    </div>
  );
};

export default AlgoTrading;
