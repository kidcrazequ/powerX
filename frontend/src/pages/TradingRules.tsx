/**
 * PowerX 交易规则配置页面
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 提供交易规则的创建、管理和执行历史查看功能
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
  Switch,
  Tag,
  Space,
  message,
  Tooltip,
  Popconfirm,
  Tabs,
  Row,
  Col,
  Statistic,
  Empty,
  Descriptions,
  Typography,
  Divider,
  Alert,
  theme
} from 'antd'
import {
  PlusOutlined,
  DeleteOutlined,
  EditOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  HistoryOutlined,
  SettingOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ReloadOutlined,
  CodeOutlined
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'
import api from '../services/api'

const { useToken } = theme
const { Option } = Select
const { TextArea } = Input
const { Text, Paragraph } = Typography

interface TradingRule {
  id: number
  user_id: string
  name: string
  description: string | null
  status: string
  priority: number
  condition_expression: Record<string, any>
  action_type: string
  action_params: Record<string, any> | null
  provinces: string[] | null
  market_types: string[] | null
  max_executions_per_day: number
  min_interval_seconds: number
  execution_count: number
  today_execution_count: number
  last_executed_at: string | null
  created_at: string
  updated_at: string | null
}

interface RuleExecution {
  id: number
  rule_id: number
  executed_at: string
  action_executed: string | null
  success: boolean
  action_result: Record<string, any> | null
  error_message: string | null
}

interface ActionType {
  value: string
  label: string
  description: string
}

// Mock 数据
const mockRules: TradingRule[] = [
  {
    id: 1,
    user_id: 'user-001',
    name: '广东价格高于500自动卖出',
    description: '当广东现货价格超过500元时自动卖出持仓',
    status: 'ACTIVE',
    priority: 10,
    condition_expression: {
      operator: 'AND',
      conditions: [
        { field: 'price', op: '>', value: 500 },
        { field: 'province', op: '==', value: '广东' }
      ]
    },
    action_type: 'PLACE_ORDER',
    action_params: { direction: 'SELL', quantity: 50 },
    provinces: ['广东'],
    market_types: ['DAY_AHEAD'],
    max_executions_per_day: 5,
    min_interval_seconds: 300,
    execution_count: 12,
    today_execution_count: 2,
    last_executed_at: '2026-01-07T10:30:00Z',
    created_at: '2026-01-01T08:00:00Z',
    updated_at: '2026-01-07T10:30:00Z'
  },
  {
    id: 2,
    user_id: 'user-001',
    name: '低价买入策略',
    description: '当任意省份价格低于350元时发送通知',
    status: 'ACTIVE',
    priority: 5,
    condition_expression: {
      operator: 'OR',
      conditions: [
        { field: 'price', op: '<', value: 350 }
      ]
    },
    action_type: 'SEND_NOTIFICATION',
    action_params: { channel: 'wechat', template: 'price_alert' },
    provinces: null,
    market_types: ['DAY_AHEAD', 'REAL_TIME'],
    max_executions_per_day: 10,
    min_interval_seconds: 600,
    execution_count: 28,
    today_execution_count: 0,
    last_executed_at: '2026-01-06T15:20:00Z',
    created_at: '2025-12-20T09:00:00Z',
    updated_at: '2026-01-06T15:20:00Z'
  },
  {
    id: 3,
    user_id: 'user-001',
    name: '波动率预警',
    description: '当价格波动超过5%时触发预警',
    status: 'PAUSED',
    priority: 8,
    condition_expression: {
      operator: 'AND',
      conditions: [
        { field: 'volatility', op: '>', value: 5 }
      ]
    },
    action_type: 'TRIGGER_ALERT',
    action_params: { level: 'warning' },
    provinces: ['广东', '浙江'],
    market_types: ['REAL_TIME'],
    max_executions_per_day: 20,
    min_interval_seconds: 120,
    execution_count: 56,
    today_execution_count: 0,
    last_executed_at: '2026-01-05T18:45:00Z',
    created_at: '2025-12-15T10:00:00Z',
    updated_at: '2026-01-05T18:45:00Z'
  }
]

const mockActionTypes: ActionType[] = [
  { value: 'PLACE_ORDER', label: '下单', description: '自动提交交易订单' },
  { value: 'CANCEL_ORDER', label: '撤单', description: '取消挂单' },
  { value: 'SEND_NOTIFICATION', label: '发送通知', description: '发送微信/邮件通知' },
  { value: 'TRIGGER_ALERT', label: '触发预警', description: '在系统中生成预警' },
  { value: 'EXECUTE_SCRIPT', label: '执行脚本', description: '运行自定义脚本' }
]

const TradingRules: React.FC = () => {
  const { token } = useToken()
  const [form] = Form.useForm()
  const [rules, setRules] = useState<TradingRule[]>(mockRules)
  const [actionTypes, setActionTypes] = useState<ActionType[]>(mockActionTypes)
  // 因为已有 mock 数据，初始不显示 loading
  const [loading, setLoading] = useState(false)
  const [dataLoaded, setDataLoaded] = useState(true)
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [historyModalVisible, setHistoryModalVisible] = useState(false)
  const [selectedRule, setSelectedRule] = useState<TradingRule | null>(null)
  const [executions, setExecutions] = useState<RuleExecution[]>([])
  const [statusFilter, setStatusFilter] = useState<string>('')

  const provinces = ['广东', '浙江', '江苏', '山东', '四川']

  // 加载规则列表
  const loadRules = async () => {
    try {
      const params: Record<string, any> = {}
      if (statusFilter) params.status = statusFilter
      
      const response = await api.get('/trading-rules', { params })
      if (response.data.success) {
        setRules(response.data.data)
      }
    } catch (error) {
      console.error('加载规则失败，使用 Mock 数据:', error)
      let filtered = mockRules
      if (statusFilter) {
        filtered = mockRules.filter(r => r.status === statusFilter)
      }
      setRules(filtered)
    }
  }

  // 加载动作类型
  const loadActionTypes = async () => {
    try {
      const response = await api.get('/trading-rules/action-types')
      if (response.data.success) {
        setActionTypes(response.data.data)
      }
    } catch (error) {
      console.error('加载动作类型失败，使用 Mock 数据:', error)
      setActionTypes(mockActionTypes)
    }
  }

  useEffect(() => {
    loadRules()
    loadActionTypes()
  }, [statusFilter])

  // 创建规则
  const handleCreate = async (values: any) => {
    try {
      // 解析条件表达式
      let conditionExpression
      try {
        conditionExpression = JSON.parse(values.condition_expression)
      } catch {
        message.error('条件表达式格式错误，请输入有效的 JSON')
        return
      }

      const payload = {
        ...values,
        condition_expression: conditionExpression,
        action_params: values.action_params ? JSON.parse(values.action_params) : null
      }
      
      const response = await api.post('/trading-rules', payload)
      if (response.data.success) {
        message.success('规则创建成功')
        setCreateModalVisible(false)
        form.resetFields()
        loadRules()
      }
    } catch (error) {
      message.error('创建失败')
    }
  }

  // 更新规则状态
  const handleStatusChange = async (ruleId: number, newStatus: string) => {
    try {
      const response = await api.put(`/trading-rules/${ruleId}/status?new_status=${newStatus}`)
      if (response.data.success) {
        message.success(newStatus === 'ACTIVE' ? '规则已启用' : '规则已暂停')
        loadRules()
      }
    } catch (error) {
      message.error('状态更新失败')
    }
  }

  // 删除规则
  const handleDelete = async (ruleId: number) => {
    try {
      const response = await api.delete(`/trading-rules/${ruleId}`)
      if (response.data.success) {
        message.success('规则已删除')
        loadRules()
      }
    } catch (error) {
      message.error('删除失败')
    }
  }

  // 查看执行历史
  const handleViewHistory = async (rule: TradingRule) => {
    setSelectedRule(rule)
    try {
      const response = await api.get(`/trading-rules/${rule.id}/executions`)
      if (response.data.success) {
        setExecutions(response.data.data)
        setHistoryModalVisible(true)
      }
    } catch (error) {
      message.error('加载执行历史失败')
    }
  }

  // 状态标签
  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; text: string }> = {
      ACTIVE: { color: 'success', text: '运行中' },
      INACTIVE: { color: 'default', text: '未激活' },
      PAUSED: { color: 'warning', text: '已暂停' },
      DELETED: { color: 'error', text: '已删除' }
    }
    const s = statusMap[status] || { color: 'default', text: status }
    return <Tag color={s.color}>{s.text}</Tag>
  }

  // 动作类型标签
  const getActionTypeLabel = (type: string) => {
    const t = actionTypes.find(at => at.value === type)
    return t?.label || type
  }

  const columns: ColumnsType<TradingRule> = [
    {
      title: '规则名称',
      dataIndex: 'name',
      key: 'name',
      render: (name, record) => (
        <Space direction="vertical" size={0}>
          <Space>
            <SettingOutlined style={{ color: token.colorPrimary }} />
            <Text strong>{name}</Text>
            {record.priority > 0 && (
              <Tag color="blue">优先级: {record.priority}</Tag>
            )}
          </Space>
          {record.description && (
            <Text type="secondary" style={{ fontSize: 12 }}>
              {record.description}
            </Text>
          )}
        </Space>
      )
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => getStatusTag(status)
    },
    {
      title: '动作',
      dataIndex: 'action_type',
      key: 'action_type',
      render: (type) => <Tag>{getActionTypeLabel(type)}</Tag>
    },
    {
      title: '执行统计',
      key: 'stats',
      render: (_, record) => (
        <Space direction="vertical" size={0}>
          <Text>总计: {record.execution_count} 次</Text>
          <Text type="secondary">今日: {record.today_execution_count} 次</Text>
        </Space>
      )
    },
    {
      title: '最后执行',
      dataIndex: 'last_executed_at',
      key: 'last_executed_at',
      render: (time) => time ? dayjs(time).format('MM-DD HH:mm') : '-'
    },
    {
      title: '开关',
      key: 'toggle',
      width: 80,
      render: (_, record) => (
        <Switch
          checked={record.status === 'ACTIVE'}
          onChange={(checked) => handleStatusChange(
            record.id, 
            checked ? 'ACTIVE' : 'PAUSED'
          )}
          disabled={record.status === 'DELETED'}
        />
      )
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_, record) => (
        <Space>
          <Tooltip title="执行历史">
            <Button 
              type="text" 
              icon={<HistoryOutlined />}
              onClick={() => handleViewHistory(record)}
            />
          </Tooltip>
          <Popconfirm
            title="确定删除该规则？"
            onConfirm={() => handleDelete(record.id)}
          >
            <Tooltip title="删除">
              <Button type="text" danger icon={<DeleteOutlined />} />
            </Tooltip>
          </Popconfirm>
        </Space>
      )
    }
  ]

  // 执行历史表格列
  const executionColumns: ColumnsType<RuleExecution> = [
    {
      title: '执行时间',
      dataIndex: 'executed_at',
      key: 'executed_at',
      render: (time) => dayjs(time).format('YYYY-MM-DD HH:mm:ss')
    },
    {
      title: '动作',
      dataIndex: 'action_executed',
      key: 'action_executed',
      render: (action) => action ? getActionTypeLabel(action) : '-'
    },
    {
      title: '结果',
      dataIndex: 'success',
      key: 'success',
      render: (success) => success 
        ? <Tag color="success" icon={<CheckCircleOutlined />}>成功</Tag>
        : <Tag color="error" icon={<CloseCircleOutlined />}>失败</Tag>
    },
    {
      title: '详情',
      key: 'detail',
      render: (_, record) => (
        record.success 
          ? <Text type="secondary">{JSON.stringify(record.action_result)}</Text>
          : <Text type="danger">{record.error_message}</Text>
      )
    }
  ]

  // 统计数据
  const stats = {
    total: rules.length,
    active: rules.filter(r => r.status === 'ACTIVE').length,
    totalExecutions: rules.reduce((sum, r) => sum + r.execution_count, 0),
    todayExecutions: rules.reduce((sum, r) => sum + r.today_execution_count, 0)
  }

  // 示例条件表达式
  const exampleExpression = `{
  "operator": "AND",
  "conditions": [
    {"field": "price", "op": ">", "value": 500},
    {"field": "province", "op": "==", "value": "广东"}
  ]
}`

  return (
    <div style={{ padding: 24 }}>
      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic 
              title="规则总数" 
              value={stats.total} 
              prefix={<SettingOutlined />}
              valueStyle={{ color: token.colorPrimary }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="运行中" 
              value={stats.active} 
              prefix={<PlayCircleOutlined />}
              valueStyle={{ color: token.colorSuccess }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="总执行次数" 
              value={stats.totalExecutions}
              prefix={<HistoryOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="今日执行" 
              value={stats.todayExecutions}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: token.colorInfo }}
            />
          </Card>
        </Col>
      </Row>

      {/* 规则列表 */}
      <Card
        title={
          <Space>
            <SettingOutlined />
            <span>交易规则引擎</span>
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
              <Option value="ACTIVE">运行中</Option>
              <Option value="INACTIVE">未激活</Option>
              <Option value="PAUSED">已暂停</Option>
            </Select>
            <Button icon={<ReloadOutlined />} onClick={loadRules}>
              刷新
            </Button>
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={() => setCreateModalVisible(true)}
            >
              新建规则
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={rules}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
          locale={{
            emptyText: <Empty description="暂无交易规则" />
          }}
        />
      </Card>

      {/* 创建规则弹窗 */}
      <Modal
        title="新建交易规则"
        open={createModalVisible}
        onCancel={() => {
          setCreateModalVisible(false)
          form.resetFields()
        }}
        footer={null}
        width={700}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreate}
          initialValues={{
            priority: 0,
            max_executions_per_day: 10,
            min_interval_seconds: 60
          }}
        >
          <Form.Item 
            name="name" 
            label="规则名称" 
            rules={[{ required: true, message: '请输入规则名称' }]}
          >
            <Input placeholder="例如：广东价格突破500自动买入" />
          </Form.Item>

          <Form.Item name="description" label="规则描述">
            <TextArea rows={2} placeholder="描述规则的用途和触发条件" />
          </Form.Item>

          <Form.Item 
            name="condition_expression" 
            label={
              <Space>
                <span>条件表达式 (JSON)</span>
                <Tooltip title="点击查看示例">
                  <CodeOutlined style={{ color: token.colorPrimary }} />
                </Tooltip>
              </Space>
            }
            rules={[{ required: true, message: '请输入条件表达式' }]}
          >
            <TextArea 
              rows={6} 
              placeholder={exampleExpression}
              style={{ fontFamily: 'monospace' }}
            />
          </Form.Item>

          <Alert
            message="条件表达式说明"
            description={
              <ul style={{ margin: 0, paddingLeft: 20 }}>
                <li>operator: 逻辑运算符，支持 AND、OR</li>
                <li>conditions: 条件数组</li>
                <li>field: 字段名，如 price、volume、province</li>
                <li>op: 比较运算符，支持 &gt;、&lt;、&gt;=、&lt;=、==、!=</li>
                <li>value: 比较值</li>
              </ul>
            }
            type="info"
            style={{ marginBottom: 16 }}
          />

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item 
                name="action_type" 
                label="触发动作"
                rules={[{ required: true }]}
              >
                <Select placeholder="选择动作类型">
                  {actionTypes.map(at => (
                    <Option key={at.value} value={at.value}>
                      {at.label} - {at.description}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="priority" label="优先级">
                <InputNumber style={{ width: '100%' }} min={0} max={100} />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="action_params" label="动作参数 (JSON，可选)">
            <TextArea 
              rows={3} 
              placeholder='{"direction": "BUY", "quantity": 100}'
              style={{ fontFamily: 'monospace' }}
            />
          </Form.Item>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="provinces" label="适用省份">
                <Select mode="multiple" placeholder="全部省份" allowClear>
                  {provinces.map(p => (
                    <Option key={p} value={p}>{p}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="max_executions_per_day" label="每日最大执行次数">
                <InputNumber style={{ width: '100%' }} min={1} max={1000} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="min_interval_seconds" label="最小间隔 (秒)">
                <InputNumber style={{ width: '100%' }} min={0} />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setCreateModalVisible(false)}>取消</Button>
              <Button type="primary" htmlType="submit">创建规则</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 执行历史弹窗 */}
      <Modal
        title={`执行历史 - ${selectedRule?.name}`}
        open={historyModalVisible}
        onCancel={() => setHistoryModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setHistoryModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
        {selectedRule && (
          <>
            <Descriptions bordered size="small" style={{ marginBottom: 16 }}>
              <Descriptions.Item label="总执行次数">
                {selectedRule.execution_count}
              </Descriptions.Item>
              <Descriptions.Item label="今日执行">
                {selectedRule.today_execution_count}
              </Descriptions.Item>
              <Descriptions.Item label="最后执行">
                {selectedRule.last_executed_at 
                  ? dayjs(selectedRule.last_executed_at).format('YYYY-MM-DD HH:mm:ss')
                  : '-'}
              </Descriptions.Item>
            </Descriptions>
            
            <Table
              columns={executionColumns}
              dataSource={executions}
              rowKey="id"
              pagination={{ pageSize: 10 }}
              locale={{
                emptyText: <Empty description="暂无执行记录" />
              }}
            />
          </>
        )}
      </Modal>
    </div>
  )
}

export default TradingRules
