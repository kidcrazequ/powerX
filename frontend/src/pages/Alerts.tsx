/**
 * PowerX 预警管理页面
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 预警规则管理和预警记录查看
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  Tabs,
  Table,
  Space,
  Button,
  Input,
  Select,
  Tag,
  Row,
  Col,
  Statistic,
  Typography,
  Modal,
  Form,
  InputNumber,
  Tooltip,
  Popconfirm,
  message,
  Badge,
  Switch,
  Timeline,
  Descriptions,
  theme
} from 'antd';
import {
  AlertOutlined,
  BellOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
  ReloadOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  CloseCircleOutlined,
  InfoCircleOutlined,
  WarningOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

// ============ 类型定义 ============

interface AlertRule {
  id: number;
  name: string;
  alert_type: string;
  level: string;
  condition_type: string;
  condition_value: number;
  condition_operator: string;
  province?: string;
  description?: string;
  is_active: boolean;
  trigger_count: number;
  last_triggered?: string;
  created_at?: string;
}

interface AlertRecord {
  id: number;
  title: string;
  message?: string;
  level: string;
  status: string;
  alert_type: string;
  province?: string;
  current_value?: number;
  threshold_value?: number;
  rule_name?: string;
  acknowledged_by?: string;
  acknowledged_at?: string;
  resolved_by?: string;
  resolved_at?: string;
  created_at?: string;
}

interface AlertStats {
  total: number;
  pending_count: number;
  resolved_count: number;
  by_level: Record<string, number>;
}

// ============ 常量 ============

const ALERT_TYPES = [
  { value: 'PRICE_HIGH', label: '价格过高' },
  { value: 'PRICE_LOW', label: '价格过低' },
  { value: 'PRICE_CHANGE', label: '价格波动' },
  { value: 'VOLUME_ABNORMAL', label: '成交量异常' },
  { value: 'POSITION_RISK', label: '持仓风险' },
  { value: 'CONTRACT_EXPIRE', label: '合同到期' },
  { value: 'SETTLEMENT_DUE', label: '结算到期' }
];

const ALERT_LEVELS = [
  { value: 'INFO', label: '信息', color: 'blue' },
  { value: 'WARNING', label: '警告', color: 'orange' },
  { value: 'DANGER', label: '危险', color: 'red' },
  { value: 'CRITICAL', label: '紧急', color: 'magenta' }
];

const ALERT_STATUS = [
  { value: 'PENDING', label: '待处理', color: 'orange' },
  { value: 'ACKNOWLEDGED', label: '已确认', color: 'blue' },
  { value: 'RESOLVED', label: '已解决', color: 'green' },
  { value: 'IGNORED', label: '已忽略', color: 'default' }
];

const PROVINCES = [
  { value: 'guangdong', label: '广东' },
  { value: 'zhejiang', label: '浙江' },
  { value: 'jiangsu', label: '江苏' },
  { value: 'shandong', label: '山东' },
  { value: 'sichuan', label: '四川' }
];

const OPERATORS = [
  { value: '>=', label: '>=' },
  { value: '>', label: '>' },
  { value: '<=', label: '<=' },
  { value: '<', label: '<' },
  { value: '==', label: '==' }
];

// ============ Mock 数据 ============

const mockRules: AlertRule[] = [
  { id: 1, name: '价格上限预警', alert_type: 'PRICE_HIGH', level: 'WARNING', condition_type: 'price', condition_value: 600, condition_operator: '>=', province: 'guangdong', is_active: true, trigger_count: 5, last_triggered: '2026-01-07T10:30:00' },
  { id: 2, name: '价格下限预警', alert_type: 'PRICE_LOW', level: 'INFO', condition_type: 'price', condition_value: 200, condition_operator: '<=', province: 'guangdong', is_active: true, trigger_count: 2 },
  { id: 3, name: '价格波动预警', alert_type: 'PRICE_CHANGE', level: 'DANGER', condition_type: 'change_percent', condition_value: 10, condition_operator: '>=', is_active: true, trigger_count: 8 },
  { id: 4, name: '持仓风险预警', alert_type: 'POSITION_RISK', level: 'CRITICAL', condition_type: 'risk_score', condition_value: 80, condition_operator: '>=', is_active: true, trigger_count: 1 }
];

const mockRecords: AlertRecord[] = [
  { id: 1, title: '广东电价触发上限预警', level: 'WARNING', status: 'PENDING', alert_type: 'PRICE_HIGH', province: 'guangdong', current_value: 620.5, threshold_value: 600, rule_name: '价格上限预警', created_at: '2026-01-07T10:30:00' },
  { id: 2, title: '浙江电价波动过大', level: 'DANGER', status: 'ACKNOWLEDGED', alert_type: 'PRICE_CHANGE', province: 'zhejiang', current_value: 15.5, threshold_value: 10, acknowledged_by: 'admin', acknowledged_at: '2026-01-07T09:00:00', created_at: '2026-01-07T08:30:00' },
  { id: 3, title: '山东电价偏低', level: 'INFO', status: 'RESOLVED', alert_type: 'PRICE_LOW', province: 'shandong', current_value: 180.0, threshold_value: 200, resolved_by: 'trader1', resolved_at: '2026-01-06T16:00:00', created_at: '2026-01-06T14:00:00' },
  { id: 4, title: '持仓风险超过阈值', level: 'CRITICAL', status: 'PENDING', alert_type: 'POSITION_RISK', current_value: 85.0, threshold_value: 80, rule_name: '持仓风险预警', created_at: '2026-01-07T11:00:00' }
];

const mockStats: AlertStats = {
  total: 125,
  pending_count: 15,
  resolved_count: 85,
  by_level: { INFO: 40, WARNING: 50, DANGER: 25, CRITICAL: 10 }
};

// ============ 组件 ============

const Alerts: React.FC = () => {
  const { token } = theme.useToken();
  const [form] = Form.useForm();
  
  const [activeTab, setActiveTab] = useState('records');
  const [loading, setLoading] = useState(false);
  
  // 规则管理
  const [rules, setRules] = useState<AlertRule[]>(mockRules);
  const [ruleModalVisible, setRuleModalVisible] = useState(false);
  const [editingRule, setEditingRule] = useState<AlertRule | null>(null);
  
  // 预警记录
  const [records, setRecords] = useState<AlertRecord[]>(mockRecords);
  const [stats, setStats] = useState<AlertStats>(mockStats);
  const [detailVisible, setDetailVisible] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState<AlertRecord | null>(null);

  const getLevelIcon = (level: string) => {
    switch (level) {
      case 'INFO': return <InfoCircleOutlined style={{ color: token.colorInfo }} />;
      case 'WARNING': return <WarningOutlined style={{ color: token.colorWarning }} />;
      case 'DANGER': return <ExclamationCircleOutlined style={{ color: token.colorError }} />;
      case 'CRITICAL': return <CloseCircleOutlined style={{ color: '#eb2f96' }} />;
      default: return <InfoCircleOutlined />;
    }
  };

  const handleCreateRule = () => {
    setEditingRule(null);
    form.resetFields();
    setRuleModalVisible(true);
  };

  const handleEditRule = (rule: AlertRule) => {
    setEditingRule(rule);
    form.setFieldsValue(rule);
    setRuleModalVisible(true);
  };

  const handleSaveRule = async () => {
    try {
      const values = await form.validateFields();
      if (editingRule) {
        setRules(prev => prev.map(r => 
          r.id === editingRule.id ? { ...r, ...values } : r
        ));
        message.success('规则更新成功');
      } else {
        const newRule: AlertRule = {
          id: Date.now(),
          ...values,
          is_active: true,
          trigger_count: 0
        };
        setRules(prev => [...prev, newRule]);
        message.success('规则创建成功');
      }
      setRuleModalVisible(false);
      form.resetFields();
    } catch (error) {
      // 验证失败
    }
  };

  const handleToggleRule = (rule: AlertRule) => {
    setRules(prev => 
      prev.map(r => r.id === rule.id ? { ...r, is_active: !r.is_active } : r)
    );
    message.success(`规则已${rule.is_active ? '禁用' : '启用'}`);
  };

  const handleDeleteRule = (ruleId: number) => {
    setRules(prev => prev.filter(r => r.id !== ruleId));
    message.success('规则已删除');
  };

  const handleAcknowledge = (record: AlertRecord) => {
    setRecords(prev =>
      prev.map(r => r.id === record.id 
        ? { ...r, status: 'ACKNOWLEDGED', acknowledged_by: 'current_user', acknowledged_at: new Date().toISOString() }
        : r
      )
    );
    message.success('预警已确认');
  };

  const handleResolve = (record: AlertRecord) => {
    setRecords(prev =>
      prev.map(r => r.id === record.id 
        ? { ...r, status: 'RESOLVED', resolved_by: 'current_user', resolved_at: new Date().toISOString() }
        : r
      )
    );
    message.success('预警已解决');
  };

  // 规则表格列
  const ruleColumns: ColumnsType<AlertRule> = [
    {
      title: '规则名称',
      dataIndex: 'name',
      key: 'name',
      render: (name, record) => (
        <Space>
          {getLevelIcon(record.level)}
          <Text strong>{name}</Text>
        </Space>
      )
    },
    {
      title: '预警类型',
      dataIndex: 'alert_type',
      key: 'alert_type',
      render: (type) => ALERT_TYPES.find(t => t.value === type)?.label || type
    },
    {
      title: '级别',
      dataIndex: 'level',
      key: 'level',
      render: (level) => {
        const config = ALERT_LEVELS.find(l => l.value === level);
        return <Tag color={config?.color}>{config?.label || level}</Tag>;
      }
    },
    {
      title: '条件',
      key: 'condition',
      render: (_, record) => (
        <Text code>
          {record.condition_type} {record.condition_operator} {record.condition_value}
        </Text>
      )
    },
    {
      title: '省份',
      dataIndex: 'province',
      key: 'province',
      render: (p) => PROVINCES.find(pr => pr.value === p)?.label || '全部'
    },
    {
      title: '触发次数',
      dataIndex: 'trigger_count',
      key: 'trigger_count',
      render: (count) => <Badge count={count} showZero style={{ backgroundColor: count > 0 ? '#ff4d4f' : '#d9d9d9' }} />
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active, record) => (
        <Switch 
          checked={active} 
          size="small"
          onChange={() => handleToggleRule(record)}
        />
      )
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEditRule(record)}>
            编辑
          </Button>
          <Popconfirm title="确定删除此规则？" onConfirm={() => handleDeleteRule(record.id)}>
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  // 预警记录表格列
  const recordColumns: ColumnsType<AlertRecord> = [
    {
      title: '时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (time) => dayjs(time).format('MM-DD HH:mm')
    },
    {
      title: '预警标题',
      dataIndex: 'title',
      key: 'title',
      render: (title, record) => (
        <Space>
          {getLevelIcon(record.level)}
          <Text>{title}</Text>
        </Space>
      )
    },
    {
      title: '级别',
      dataIndex: 'level',
      key: 'level',
      width: 80,
      render: (level) => {
        const config = ALERT_LEVELS.find(l => l.value === level);
        return <Tag color={config?.color}>{config?.label}</Tag>;
      }
    },
    {
      title: '当前值',
      dataIndex: 'current_value',
      key: 'current_value',
      width: 100,
      render: (v, record) => (
        <Tooltip title={`阈值: ${record.threshold_value}`}>
          <Text type={v > (record.threshold_value || 0) ? 'danger' : 'success'}>
            {v?.toFixed(2)}
          </Text>
        </Tooltip>
      )
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => {
        const config = ALERT_STATUS.find(s => s.value === status);
        return <Tag color={config?.color}>{config?.label}</Tag>;
      }
    },
    {
      title: '操作',
      key: 'actions',
      width: 180,
      render: (_, record) => (
        <Space>
          {record.status === 'PENDING' && (
            <>
              <Button type="link" size="small" onClick={() => handleAcknowledge(record)}>
                确认
              </Button>
              <Button type="link" size="small" onClick={() => handleResolve(record)}>
                解决
              </Button>
            </>
          )}
          {record.status === 'ACKNOWLEDGED' && (
            <Button type="link" size="small" onClick={() => handleResolve(record)}>
              解决
            </Button>
          )}
          <Button 
            type="link" 
            size="small" 
            onClick={() => {
              setSelectedRecord(record);
              setDetailVisible(true);
            }}
          >
            详情
          </Button>
        </Space>
      )
    }
  ];

  const tabItems = [
    {
      key: 'records',
      label: (
        <span>
          <AlertOutlined />
          预警记录
          <Badge count={stats.pending_count} size="small" style={{ marginLeft: 8 }} />
        </span>
      ),
      children: (
        <>
          {/* 统计卡片 */}
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col xs={12} sm={6}>
              <Card>
                <Statistic
                  title="待处理"
                  value={stats.pending_count}
                  prefix={<ExclamationCircleOutlined style={{ color: token.colorWarning }} />}
                  valueStyle={{ color: token.colorWarning }}
                />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card>
                <Statistic
                  title="已解决"
                  value={stats.resolved_count}
                  prefix={<CheckCircleOutlined style={{ color: token.colorSuccess }} />}
                  valueStyle={{ color: token.colorSuccess }}
                />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card>
                <Statistic
                  title="危险级别"
                  value={stats.by_level?.DANGER || 0}
                  prefix={<WarningOutlined style={{ color: token.colorError }} />}
                  valueStyle={{ color: token.colorError }}
                />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card>
                <Statistic title="总预警" value={stats.total} prefix={<BellOutlined />} />
              </Card>
            </Col>
          </Row>

          {/* 筛选和表格 */}
          <Card>
            <Row justify="space-between" style={{ marginBottom: 16 }}>
              <Col>
                <Space>
                  <Select
                    placeholder="状态"
                    style={{ width: 120 }}
                    allowClear
                    options={ALERT_STATUS}
                  />
                  <Select
                    placeholder="级别"
                    style={{ width: 100 }}
                    allowClear
                    options={ALERT_LEVELS}
                  />
                  <Select
                    placeholder="省份"
                    style={{ width: 100 }}
                    allowClear
                    options={PROVINCES}
                  />
                </Space>
              </Col>
              <Col>
                <Button icon={<ReloadOutlined />}>刷新</Button>
              </Col>
            </Row>
            <Table
              columns={recordColumns}
              dataSource={records}
              rowKey="id"
              loading={loading}
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </>
      )
    },
    {
      key: 'rules',
      label: (
        <span>
          <BellOutlined />
          预警规则
        </span>
      ),
      children: (
        <Card>
          <Row justify="space-between" style={{ marginBottom: 16 }}>
            <Col>
              <Text type="secondary">配置预警触发条件</Text>
            </Col>
            <Col>
              <Space>
                <Button icon={<ReloadOutlined />}>刷新</Button>
                <Button type="primary" icon={<PlusOutlined />} onClick={handleCreateRule}>
                  创建规则
                </Button>
              </Space>
            </Col>
          </Row>
          <Table
            columns={ruleColumns}
            dataSource={rules}
            rowKey="id"
            loading={loading}
          />
        </Card>
      )
    }
  ];

  return (
    <div style={{ padding: 24 }}>
      {/* 页面标题 */}
      <div style={{ marginBottom: 24 }}>
        <Title level={4} style={{ margin: 0 }}>
          <AlertOutlined style={{ marginRight: 8 }} />
          预警管理
        </Title>
        <Text type="secondary">管理预警规则和查看预警记录</Text>
      </div>

      {/* 标签页 */}
      <Tabs activeKey={activeTab} onChange={setActiveTab} items={tabItems} />

      {/* 规则编辑弹窗 */}
      <Modal
        title={editingRule ? '编辑规则' : '创建规则'}
        open={ruleModalVisible}
        onOk={handleSaveRule}
        onCancel={() => {
          setRuleModalVisible(false);
          form.resetFields();
        }}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="name" label="规则名称" rules={[{ required: true }]}>
                <Input placeholder="例如: 价格上限预警" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="alert_type" label="预警类型" rules={[{ required: true }]}>
                <Select options={ALERT_TYPES} />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="level" label="预警级别" initialValue="WARNING">
                <Select options={ALERT_LEVELS} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="province" label="适用省份">
                <Select options={PROVINCES} allowClear placeholder="全部省份" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="condition_type" label="条件类型" rules={[{ required: true }]}>
                <Select options={[
                  { value: 'price', label: '价格' },
                  { value: 'change_percent', label: '变化百分比' },
                  { value: 'volume', label: '成交量' },
                  { value: 'risk_score', label: '风险分数' }
                ]} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="condition_operator" label="运算符" initialValue=">=">
                <Select options={OPERATORS} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="condition_value" label="阈值" rules={[{ required: true }]}>
                <InputNumber style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={2} placeholder="规则描述（可选）" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 预警详情弹窗 */}
      <Modal
        title="预警详情"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={null}
        width={600}
      >
        {selectedRecord && (
          <>
            <Descriptions column={2} bordered size="small">
              <Descriptions.Item label="预警标题" span={2}>{selectedRecord.title}</Descriptions.Item>
              <Descriptions.Item label="级别">
                <Tag color={ALERT_LEVELS.find(l => l.value === selectedRecord.level)?.color}>
                  {ALERT_LEVELS.find(l => l.value === selectedRecord.level)?.label}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="状态">
                <Tag color={ALERT_STATUS.find(s => s.value === selectedRecord.status)?.color}>
                  {ALERT_STATUS.find(s => s.value === selectedRecord.status)?.label}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="当前值">{selectedRecord.current_value}</Descriptions.Item>
              <Descriptions.Item label="阈值">{selectedRecord.threshold_value}</Descriptions.Item>
              <Descriptions.Item label="省份">
                {PROVINCES.find(p => p.value === selectedRecord.province)?.label || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="触发规则">{selectedRecord.rule_name || '-'}</Descriptions.Item>
              <Descriptions.Item label="创建时间" span={2}>
                {dayjs(selectedRecord.created_at).format('YYYY-MM-DD HH:mm:ss')}
              </Descriptions.Item>
            </Descriptions>
            
            <Title level={5} style={{ marginTop: 16 }}>处理时间线</Title>
            <Timeline
              items={[
                {
                  color: 'blue',
                  children: `预警触发 - ${dayjs(selectedRecord.created_at).format('MM-DD HH:mm')}`
                },
                ...(selectedRecord.acknowledged_at ? [{
                  color: 'orange',
                  children: `${selectedRecord.acknowledged_by} 确认预警 - ${dayjs(selectedRecord.acknowledged_at).format('MM-DD HH:mm')}`
                }] : []),
                ...(selectedRecord.resolved_at ? [{
                  color: 'green',
                  children: `${selectedRecord.resolved_by} 解决预警 - ${dayjs(selectedRecord.resolved_at).format('MM-DD HH:mm')}`
                }] : [])
              ]}
            />
          </>
        )}
      </Modal>
    </div>
  );
};

export default Alerts;
