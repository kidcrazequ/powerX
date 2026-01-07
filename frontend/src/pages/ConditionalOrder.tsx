/**
 * PowerX 条件单管理页面
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 提供条件单的创建、查看和管理功能
 */

import React, { useState, useEffect } from 'react'
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
  message,
  Tooltip,
  Popconfirm,
  Tabs,
  Statistic,
  Row,
  Col,
  Empty,
  Descriptions,
  Badge,
  theme
} from 'antd'
import {
  PlusOutlined,
  DeleteOutlined,
  EyeOutlined,
  ThunderboltOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ExclamationCircleOutlined,
  ReloadOutlined
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'
import api from '../services/api'

const { useToken } = theme
const { Option } = Select

interface ConditionalOrder {
  id: number
  user_id: string
  name: string | null
  condition_type: string
  province: string
  market_type: string
  trigger_price: number | null
  trigger_change_pct: number | null
  trigger_time: string | null
  trigger_volume: number | null
  order_direction: string
  order_quantity: number
  order_price_type: string
  order_limit_price: number | null
  status: string
  is_enabled: boolean
  valid_from: string
  valid_until: string | null
  triggered_at: string | null
  triggered_price: number | null
  executed_at: string | null
  executed_order_id: string | null
  created_at: string
}

interface ConditionType {
  value: string
  label: string
  description: string
}

// Mock 数据
const mockOrders: ConditionalOrder[] = [
  {
    id: 1,
    user_id: 'user-001',
    name: '广东价格突破买入',
    condition_type: 'PRICE_ABOVE',
    province: '广东',
    market_type: 'DAY_AHEAD',
    trigger_price: 500,
    trigger_change_pct: null,
    trigger_time: null,
    trigger_volume: null,
    order_direction: 'BUY',
    order_quantity: 100,
    order_price_type: 'MARKET',
    order_limit_price: null,
    status: 'PENDING',
    is_enabled: true,
    valid_from: '2026-01-07T00:00:00Z',
    valid_until: '2026-01-14T00:00:00Z',
    triggered_at: null,
    triggered_price: null,
    executed_at: null,
    executed_order_id: null,
    created_at: '2026-01-07T08:30:00Z'
  },
  {
    id: 2,
    user_id: 'user-001',
    name: '浙江低价买入',
    condition_type: 'PRICE_BELOW',
    province: '浙江',
    market_type: 'DAY_AHEAD',
    trigger_price: 380,
    trigger_change_pct: null,
    trigger_time: null,
    trigger_volume: null,
    order_direction: 'BUY',
    order_quantity: 200,
    order_price_type: 'LIMIT',
    order_limit_price: 375,
    status: 'TRIGGERED',
    is_enabled: true,
    valid_from: '2026-01-06T00:00:00Z',
    valid_until: null,
    triggered_at: '2026-01-07T10:15:00Z',
    triggered_price: 378.5,
    executed_at: null,
    executed_order_id: null,
    created_at: '2026-01-06T14:20:00Z'
  },
  {
    id: 3,
    user_id: 'user-001',
    name: '定时卖出',
    condition_type: 'TIME_TRIGGER',
    province: '山东',
    market_type: 'REAL_TIME',
    trigger_price: null,
    trigger_change_pct: null,
    trigger_time: '2026-01-07T14:00:00Z',
    trigger_volume: null,
    order_direction: 'SELL',
    order_quantity: 150,
    order_price_type: 'MARKET',
    order_limit_price: null,
    status: 'EXECUTED',
    is_enabled: true,
    valid_from: '2026-01-07T00:00:00Z',
    valid_until: null,
    triggered_at: '2026-01-07T14:00:00Z',
    triggered_price: 445.2,
    executed_at: '2026-01-07T14:00:05Z',
    executed_order_id: 'ORD-2026010714-001',
    created_at: '2026-01-07T09:00:00Z'
  },
  {
    id: 4,
    user_id: 'user-001',
    name: '成交量突破买入',
    condition_type: 'VOLUME_ABOVE',
    province: '江苏',
    market_type: 'DAY_AHEAD',
    trigger_price: null,
    trigger_change_pct: null,
    trigger_time: null,
    trigger_volume: 50000,
    order_direction: 'BUY',
    order_quantity: 80,
    order_price_type: 'MARKET',
    order_limit_price: null,
    status: 'PENDING',
    is_enabled: true,
    valid_from: '2026-01-07T00:00:00Z',
    valid_until: '2026-01-10T00:00:00Z',
    triggered_at: null,
    triggered_price: null,
    executed_at: null,
    executed_order_id: null,
    created_at: '2026-01-07T11:30:00Z'
  }
]

const mockConditionTypes: ConditionType[] = [
  { value: 'PRICE_ABOVE', label: '价格上穿', description: '当价格高于设定值时触发' },
  { value: 'PRICE_BELOW', label: '价格下穿', description: '当价格低于设定值时触发' },
  { value: 'TIME_TRIGGER', label: '定时触发', description: '在指定时间触发' },
  { value: 'VOLUME_ABOVE', label: '成交量突破', description: '当成交量超过设定值时触发' }
]

const ConditionalOrder: React.FC = () => {
  const { token } = useToken()
  const [form] = Form.useForm()
  const [orders, setOrders] = useState<ConditionalOrder[]>(mockOrders)
  const [conditionTypes, setConditionTypes] = useState<ConditionType[]>(mockConditionTypes)
  // 因为已有 mock 数据，初始不显示 loading
  const [loading, setLoading] = useState(false)
  const [dataLoaded, setDataLoaded] = useState(true)
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [selectedOrder, setSelectedOrder] = useState<ConditionalOrder | null>(null)
  const [selectedConditionType, setSelectedConditionType] = useState<string>('')
  const [statusFilter, setStatusFilter] = useState<string>('')

  const provinces = ['广东', '浙江', '江苏', '山东', '四川']

  // 加载条件单列表
  const loadOrders = async () => {
    try {
      const params: Record<string, any> = {}
      if (statusFilter) params.status = statusFilter
      
      const response = await api.get('/conditional-orders', { params })
      if (response.data.success) {
        setOrders(response.data.data)
      }
    } catch (error) {
      console.error('加载条件单失败，使用 Mock 数据:', error)
      // 使用 mock 数据
      let filtered = mockOrders
      if (statusFilter) {
        filtered = mockOrders.filter(o => o.status === statusFilter)
      }
      setOrders(filtered)
    }
  }

  // 加载条件类型
  const loadConditionTypes = async () => {
    try {
      const response = await api.get('/conditional-orders/types')
      if (response.data.success) {
        setConditionTypes(response.data.data)
      }
    } catch (error) {
      console.error('加载条件类型失败，使用 Mock 数据:', error)
      setConditionTypes(mockConditionTypes)
    }
  }

  useEffect(() => {
    loadOrders()
    loadConditionTypes()
  }, [statusFilter])

  // 创建条件单
  const handleCreate = async (values: any) => {
    try {
      const payload = {
        ...values,
        trigger_time: values.trigger_time?.toISOString(),
        valid_until: values.valid_until?.toISOString()
      }
      
      const response = await api.post('/conditional-orders', payload)
      if (response.data.success) {
        message.success('条件单创建成功')
        setCreateModalVisible(false)
        form.resetFields()
        loadOrders()
      }
    } catch (error) {
      message.error('创建失败')
    }
  }

  // 取消条件单
  const handleCancel = async (orderId: number) => {
    try {
      const response = await api.delete(`/conditional-orders/${orderId}`)
      if (response.data.success) {
        message.success('条件单已取消')
        loadOrders()
      }
    } catch (error) {
      message.error('取消失败')
    }
  }

  // 查看详情
  const handleViewDetail = (order: ConditionalOrder) => {
    setSelectedOrder(order)
    setDetailModalVisible(true)
  }

  // 状态标签
  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; text: string; icon: React.ReactNode }> = {
      PENDING: { color: 'processing', text: '等待触发', icon: <ClockCircleOutlined /> },
      TRIGGERED: { color: 'warning', text: '已触发', icon: <ExclamationCircleOutlined /> },
      EXECUTED: { color: 'success', text: '已执行', icon: <CheckCircleOutlined /> },
      CANCELLED: { color: 'default', text: '已取消', icon: <CloseCircleOutlined /> },
      EXPIRED: { color: 'default', text: '已过期', icon: <CloseCircleOutlined /> },
      FAILED: { color: 'error', text: '执行失败', icon: <CloseCircleOutlined /> }
    }
    const s = statusMap[status] || { color: 'default', text: status, icon: null }
    return <Tag color={s.color} icon={s.icon}>{s.text}</Tag>
  }

  // 方向标签
  const getDirectionTag = (direction: string) => {
    if (direction === 'BUY') {
      return <Tag color="red">买入</Tag>
    }
    return <Tag color="green">卖出</Tag>
  }

  // 条件类型标签
  const getConditionTypeLabel = (type: string) => {
    const t = conditionTypes.find(ct => ct.value === type)
    return t?.label || type
  }

  const columns: ColumnsType<ConditionalOrder> = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
      render: (name, record) => (
        <Space>
          <ThunderboltOutlined style={{ color: token.colorPrimary }} />
          <span>{name || `条件单#${record.id}`}</span>
        </Space>
      )
    },
    {
      title: '条件类型',
      dataIndex: 'condition_type',
      key: 'condition_type',
      render: (type) => <Tag>{getConditionTypeLabel(type)}</Tag>
    },
    {
      title: '省份',
      dataIndex: 'province',
      key: 'province'
    },
    {
      title: '触发条件',
      key: 'trigger',
      render: (_, record) => {
        if (record.trigger_price) {
          return `价格 ${record.condition_type === 'PRICE_ABOVE' ? '>' : '<'} ${record.trigger_price} 元`
        }
        if (record.trigger_time) {
          return `时间: ${dayjs(record.trigger_time).format('MM-DD HH:mm')}`
        }
        if (record.trigger_volume) {
          return `成交量 > ${record.trigger_volume} MWh`
        }
        return '-'
      }
    },
    {
      title: '方向',
      dataIndex: 'order_direction',
      key: 'order_direction',
      render: (dir) => getDirectionTag(dir)
    },
    {
      title: '数量',
      dataIndex: 'order_quantity',
      key: 'order_quantity',
      render: (qty) => `${qty} MWh`
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => getStatusTag(status)
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time) => dayjs(time).format('MM-DD HH:mm')
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Tooltip title="查看详情">
            <Button 
              type="text" 
              icon={<EyeOutlined />} 
              onClick={() => handleViewDetail(record)}
            />
          </Tooltip>
          {record.status === 'PENDING' && (
            <Popconfirm
              title="确定取消该条件单？"
              onConfirm={() => handleCancel(record.id)}
            >
              <Tooltip title="取消">
                <Button type="text" danger icon={<DeleteOutlined />} />
              </Tooltip>
            </Popconfirm>
          )}
        </Space>
      )
    }
  ]

  // 统计数据
  const stats = {
    total: orders.length,
    pending: orders.filter(o => o.status === 'PENDING').length,
    triggered: orders.filter(o => o.status === 'TRIGGERED').length,
    executed: orders.filter(o => o.status === 'EXECUTED').length
  }

  return (
    <div style={{ padding: 24 }}>
      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic 
              title="全部条件单" 
              value={stats.total} 
              prefix={<ThunderboltOutlined />}
              valueStyle={{ color: token.colorPrimary }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="等待触发" 
              value={stats.pending} 
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: token.colorWarning }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="已触发" 
              value={stats.triggered}
              prefix={<ExclamationCircleOutlined />}
              valueStyle={{ color: token.colorInfo }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="已执行" 
              value={stats.executed}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: token.colorSuccess }}
            />
          </Card>
        </Col>
      </Row>

      {/* 条件单列表 */}
      <Card
        title={
          <Space>
            <ThunderboltOutlined />
            <span>条件单管理</span>
          </Space>
        }
        extra={
          <Space>
            <Select
              placeholder="状态筛选"
              allowClear
              style={{ width: 120 }}
              onChange={setStatusFilter}
              value={statusFilter || undefined}
            >
              <Option value="PENDING">等待触发</Option>
              <Option value="TRIGGERED">已触发</Option>
              <Option value="EXECUTED">已执行</Option>
              <Option value="CANCELLED">已取消</Option>
            </Select>
            <Button icon={<ReloadOutlined />} onClick={loadOrders}>
              刷新
            </Button>
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={() => setCreateModalVisible(true)}
            >
              新建条件单
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={orders}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
          locale={{
            emptyText: <Empty description="暂无条件单" />
          }}
        />
      </Card>

      {/* 创建条件单弹窗 */}
      <Modal
        title="新建条件单"
        open={createModalVisible}
        onCancel={() => {
          setCreateModalVisible(false)
          form.resetFields()
          setSelectedConditionType('')
        }}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreate}
          initialValues={{
            market_type: 'DAY_AHEAD',
            order_direction: 'BUY',
            order_price_type: 'MARKET'
          }}
        >
          <Form.Item name="name" label="条件单名称">
            <Input placeholder="可选，默认自动生成" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="province" label="省份" rules={[{ required: true }]}>
                <Select placeholder="选择省份">
                  {provinces.map(p => (
                    <Option key={p} value={p}>{p}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="market_type" label="市场类型" rules={[{ required: true }]}>
                <Select>
                  <Option value="DAY_AHEAD">日前市场</Option>
                  <Option value="REAL_TIME">实时市场</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item 
            name="condition_type" 
            label="条件类型" 
            rules={[{ required: true }]}
          >
            <Select 
              placeholder="选择触发条件类型"
              onChange={(v) => setSelectedConditionType(v)}
            >
              {conditionTypes.map(ct => (
                <Option key={ct.value} value={ct.value}>
                  {ct.label} - {ct.description}
                </Option>
              ))}
            </Select>
          </Form.Item>

          {/* 根据条件类型显示不同的输入 */}
          {(selectedConditionType === 'PRICE_ABOVE' || selectedConditionType === 'PRICE_BELOW') && (
            <Form.Item 
              name="trigger_price" 
              label="触发价格 (元/MWh)"
              rules={[{ required: true }]}
            >
              <InputNumber 
                style={{ width: '100%' }} 
                min={0} 
                precision={2}
                placeholder={`当价格${selectedConditionType === 'PRICE_ABOVE' ? '高于' : '低于'}此值时触发`}
              />
            </Form.Item>
          )}

          {selectedConditionType === 'TIME_TRIGGER' && (
            <Form.Item 
              name="trigger_time" 
              label="触发时间"
              rules={[{ required: true }]}
            >
              <DatePicker 
                showTime 
                style={{ width: '100%' }}
                placeholder="选择触发时间"
              />
            </Form.Item>
          )}

          {selectedConditionType === 'VOLUME_ABOVE' && (
            <Form.Item 
              name="trigger_volume" 
              label="触发成交量 (MWh)"
              rules={[{ required: true }]}
            >
              <InputNumber 
                style={{ width: '100%' }} 
                min={0}
                placeholder="当成交量高于此值时触发"
              />
            </Form.Item>
          )}

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item 
                name="order_direction" 
                label="交易方向"
                rules={[{ required: true }]}
              >
                <Select>
                  <Option value="BUY">买入</Option>
                  <Option value="SELL">卖出</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item 
                name="order_quantity" 
                label="交易数量 (MWh)"
                rules={[{ required: true }]}
              >
                <InputNumber style={{ width: '100%' }} min={1} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="order_price_type" label="价格类型">
                <Select>
                  <Option value="MARKET">市价单</Option>
                  <Option value="LIMIT">限价单</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="valid_until" label="有效期至">
            <DatePicker 
              showTime 
              style={{ width: '100%' }}
              placeholder="可选，默认7天后过期"
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setCreateModalVisible(false)}>取消</Button>
              <Button type="primary" htmlType="submit">创建</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 详情弹窗 */}
      <Modal
        title="条件单详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={700}
      >
        {selectedOrder && (
          <Descriptions bordered column={2}>
            <Descriptions.Item label="ID">{selectedOrder.id}</Descriptions.Item>
            <Descriptions.Item label="名称">{selectedOrder.name || '-'}</Descriptions.Item>
            <Descriptions.Item label="状态">{getStatusTag(selectedOrder.status)}</Descriptions.Item>
            <Descriptions.Item label="省份">{selectedOrder.province}</Descriptions.Item>
            <Descriptions.Item label="条件类型">
              {getConditionTypeLabel(selectedOrder.condition_type)}
            </Descriptions.Item>
            <Descriptions.Item label="市场类型">
              {selectedOrder.market_type === 'DAY_AHEAD' ? '日前市场' : '实时市场'}
            </Descriptions.Item>
            <Descriptions.Item label="触发价格">
              {selectedOrder.trigger_price ? `${selectedOrder.trigger_price} 元/MWh` : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="触发时间">
              {selectedOrder.trigger_time 
                ? dayjs(selectedOrder.trigger_time).format('YYYY-MM-DD HH:mm:ss')
                : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="交易方向">
              {getDirectionTag(selectedOrder.order_direction)}
            </Descriptions.Item>
            <Descriptions.Item label="交易数量">
              {selectedOrder.order_quantity} MWh
            </Descriptions.Item>
            <Descriptions.Item label="创建时间">
              {dayjs(selectedOrder.created_at).format('YYYY-MM-DD HH:mm:ss')}
            </Descriptions.Item>
            <Descriptions.Item label="有效期至">
              {selectedOrder.valid_until 
                ? dayjs(selectedOrder.valid_until).format('YYYY-MM-DD HH:mm:ss')
                : '永久有效'}
            </Descriptions.Item>
            {selectedOrder.triggered_at && (
              <>
                <Descriptions.Item label="触发时间">
                  {dayjs(selectedOrder.triggered_at).format('YYYY-MM-DD HH:mm:ss')}
                </Descriptions.Item>
                <Descriptions.Item label="触发价格">
                  {selectedOrder.triggered_price} 元/MWh
                </Descriptions.Item>
              </>
            )}
            {selectedOrder.executed_at && (
              <>
                <Descriptions.Item label="执行时间">
                  {dayjs(selectedOrder.executed_at).format('YYYY-MM-DD HH:mm:ss')}
                </Descriptions.Item>
                <Descriptions.Item label="订单号">
                  {selectedOrder.executed_order_id}
                </Descriptions.Item>
              </>
            )}
          </Descriptions>
        )}
      </Modal>
    </div>
  )
}

export default ConditionalOrder
