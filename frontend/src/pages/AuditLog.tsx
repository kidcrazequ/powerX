/**
 * PowerX 审计日志页面
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 查询和展示系统操作日志
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Space,
  Button,
  Input,
  Select,
  DatePicker,
  Tag,
  Row,
  Col,
  Statistic,
  Typography,
  Tooltip,
  Modal,
  Descriptions,
  Badge,
  message,
  theme
} from 'antd';
import {
  SearchOutlined,
  ReloadOutlined,
  EyeOutlined,
  DownloadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  UserOutlined,
  ClockCircleOutlined,
  FileTextOutlined,
  SafetyOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

// ============ 类型定义 ============

interface AuditLogItem {
  id: number;
  action: string;
  module: string;
  resource?: string;
  resource_id?: string;
  user_id?: string;
  username?: string;
  user_ip?: string;
  method?: string;
  path?: string;
  status_code?: number;
  response_time?: number;
  description?: string;
  success: boolean;
  error_message?: string;
  created_at?: string;
}

interface AuditStatistics {
  total: number;
  success_count: number;
  failure_count: number;
  success_rate: number;
  by_module: Record<string, number>;
  by_action: Record<string, number>;
}

// ============ 常量 ============

const MODULE_OPTIONS = [
  { value: 'AUTH', label: '认证' },
  { value: 'TRADING', label: '交易' },
  { value: 'CONTRACT', label: '合同' },
  { value: 'SETTLEMENT', label: '结算' },
  { value: 'MARKET', label: '市场' },
  { value: 'AI', label: 'AI服务' },
  { value: 'REPORT', label: '报告' },
  { value: 'ADMIN', label: '管理' },
  { value: 'SYSTEM', label: '系统' }
];

const ACTION_OPTIONS = [
  { value: 'CREATE', label: '创建' },
  { value: 'READ', label: '查询' },
  { value: 'UPDATE', label: '更新' },
  { value: 'DELETE', label: '删除' },
  { value: 'LOGIN', label: '登录' },
  { value: 'LOGOUT', label: '登出' },
  { value: 'EXPORT', label: '导出' },
  { value: 'IMPORT', label: '导入' },
  { value: 'EXECUTE', label: '执行' }
];

const ACTION_COLORS: Record<string, string> = {
  CREATE: 'green',
  READ: 'blue',
  UPDATE: 'orange',
  DELETE: 'red',
  LOGIN: 'cyan',
  LOGOUT: 'default',
  EXPORT: 'purple',
  IMPORT: 'geekblue',
  EXECUTE: 'magenta'
};

const MODULE_COLORS: Record<string, string> = {
  AUTH: 'blue',
  TRADING: 'green',
  CONTRACT: 'orange',
  SETTLEMENT: 'purple',
  MARKET: 'cyan',
  AI: 'magenta',
  REPORT: 'geekblue',
  ADMIN: 'red',
  SYSTEM: 'default'
};

// ============ 模拟数据 ============

const generateMockData = (): AuditLogItem[] => {
  const modules = ['AUTH', 'TRADING', 'CONTRACT', 'MARKET', 'AI'];
  const actions = ['CREATE', 'READ', 'UPDATE', 'DELETE', 'LOGIN', 'EXECUTE'];
  const users = ['admin', 'trader1', 'trader2', 'analyst'];
  
  return Array.from({ length: 50 }, (_, i) => ({
    id: 50 - i,
    action: actions[Math.floor(Math.random() * actions.length)],
    module: modules[Math.floor(Math.random() * modules.length)],
    resource: ['order', 'contract', 'report', 'user'][Math.floor(Math.random() * 4)],
    resource_id: `RES-${1000 + i}`,
    user_id: `USER-${i % 4 + 1}`,
    username: users[i % 4],
    user_ip: `192.168.1.${100 + (i % 50)}`,
    method: ['GET', 'POST', 'PUT', 'DELETE'][Math.floor(Math.random() * 4)],
    path: `/api/v1/${['trading', 'contracts', 'market', 'ai'][Math.floor(Math.random() * 4)]}`,
    status_code: Math.random() > 0.1 ? 200 : 500,
    response_time: Math.floor(Math.random() * 500) + 50,
    description: `执行${actions[Math.floor(Math.random() * actions.length)]}操作`,
    success: Math.random() > 0.1,
    error_message: Math.random() > 0.9 ? '操作失败：权限不足' : undefined,
    created_at: dayjs().subtract(i * 10, 'minute').toISOString()
  }));
};

const mockStatistics: AuditStatistics = {
  total: 1250,
  success_count: 1180,
  failure_count: 70,
  success_rate: 94.4,
  by_module: {
    AUTH: 320,
    TRADING: 450,
    CONTRACT: 180,
    MARKET: 200,
    AI: 100
  },
  by_action: {
    CREATE: 280,
    READ: 520,
    UPDATE: 180,
    DELETE: 50,
    LOGIN: 150,
    EXECUTE: 70
  }
};

// ============ 组件 ============

const AuditLog: React.FC = () => {
  const { token } = theme.useToken();
  
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<AuditLogItem[]>([]);
  const [statistics, setStatistics] = useState<AuditStatistics>(mockStatistics);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  
  // 筛选条件
  const [filters, setFilters] = useState({
    keyword: '',
    module: undefined as string | undefined,
    action: undefined as string | undefined,
    success: undefined as boolean | undefined,
    dateRange: null as any
  });
  
  // 详情弹窗
  const [detailVisible, setDetailVisible] = useState(false);
  const [selectedLog, setSelectedLog] = useState<AuditLogItem | null>(null);

  useEffect(() => {
    loadData();
  }, [currentPage, pageSize]);

  const loadData = async () => {
    setLoading(true);
    try {
      // 模拟 API 调用
      await new Promise(resolve => setTimeout(resolve, 500));
      const mockData = generateMockData();
      setData(mockData);
      setTotal(mockData.length);
    } catch (error) {
      message.error('加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setCurrentPage(1);
    loadData();
  };

  const handleReset = () => {
    setFilters({
      keyword: '',
      module: undefined,
      action: undefined,
      success: undefined,
      dateRange: null
    });
    setCurrentPage(1);
    loadData();
  };

  const handleViewDetail = (record: AuditLogItem) => {
    setSelectedLog(record);
    setDetailVisible(true);
  };

  const columns: ColumnsType<AuditLogItem> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
      render: (id) => <Text type="secondary">#{id}</Text>
    },
    {
      title: '时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 160,
      render: (time) => (
        <Tooltip title={time}>
          <Space>
            <ClockCircleOutlined style={{ color: token.colorTextSecondary }} />
            {dayjs(time).format('MM-DD HH:mm:ss')}
          </Space>
        </Tooltip>
      )
    },
    {
      title: '用户',
      dataIndex: 'username',
      key: 'username',
      width: 120,
      render: (username, record) => (
        <Tooltip title={`IP: ${record.user_ip}`}>
          <Space>
            <UserOutlined />
            {username || '-'}
          </Space>
        </Tooltip>
      )
    },
    {
      title: '模块',
      dataIndex: 'module',
      key: 'module',
      width: 100,
      render: (module) => (
        <Tag color={MODULE_COLORS[module] || 'default'}>
          {MODULE_OPTIONS.find(m => m.value === module)?.label || module}
        </Tag>
      )
    },
    {
      title: '操作',
      dataIndex: 'action',
      key: 'action',
      width: 80,
      render: (action) => (
        <Tag color={ACTION_COLORS[action] || 'default'}>
          {ACTION_OPTIONS.find(a => a.value === action)?.label || action}
        </Tag>
      )
    },
    {
      title: '资源',
      key: 'resource',
      width: 150,
      render: (_, record) => (
        <Text>
          {record.resource}
          {record.resource_id && (
            <Text type="secondary" style={{ marginLeft: 4 }}>
              ({record.resource_id})
            </Text>
          )}
        </Text>
      )
    },
    {
      title: '请求',
      key: 'request',
      width: 200,
      ellipsis: true,
      render: (_, record) => (
        <Tooltip title={record.path}>
          <Text>
            <Tag color="default" style={{ marginRight: 4 }}>
              {record.method}
            </Tag>
            {record.path}
          </Text>
        </Tooltip>
      )
    },
    {
      title: '耗时',
      dataIndex: 'response_time',
      key: 'response_time',
      width: 80,
      render: (time) => (
        <Text type={time > 300 ? 'warning' : 'secondary'}>
          {time}ms
        </Text>
      )
    },
    {
      title: '状态',
      dataIndex: 'success',
      key: 'success',
      width: 80,
      render: (success) => (
        success ? (
          <Badge status="success" text="成功" />
        ) : (
          <Badge status="error" text="失败" />
        )
      )
    },
    {
      title: '操作',
      key: 'actions',
      width: 80,
      fixed: 'right',
      render: (_, record) => (
        <Button
          type="link"
          size="small"
          icon={<EyeOutlined />}
          onClick={() => handleViewDetail(record)}
        >
          详情
        </Button>
      )
    }
  ];

  return (
    <div style={{ padding: 24 }}>
      {/* 页面标题 */}
      <div style={{ marginBottom: 24 }}>
        <Title level={4} style={{ margin: 0 }}>
          <SafetyOutlined style={{ marginRight: 8 }} />
          审计日志
        </Title>
        <Text type="secondary">查看系统操作日志，追踪用户行为</Text>
      </div>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="总操作数"
              value={statistics.total}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="成功操作"
              value={statistics.success_count}
              prefix={<CheckCircleOutlined style={{ color: token.colorSuccess }} />}
              valueStyle={{ color: token.colorSuccess }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="失败操作"
              value={statistics.failure_count}
              prefix={<CloseCircleOutlined style={{ color: token.colorError }} />}
              valueStyle={{ color: token.colorError }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="成功率"
              value={statistics.success_rate}
              suffix="%"
              precision={1}
              valueStyle={{ color: statistics.success_rate > 90 ? token.colorSuccess : token.colorWarning }}
            />
          </Card>
        </Col>
      </Row>

      {/* 筛选区域 */}
      <Card style={{ marginBottom: 16 }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={6}>
            <Input
              placeholder="搜索关键词"
              prefix={<SearchOutlined />}
              value={filters.keyword}
              onChange={(e) => setFilters({ ...filters, keyword: e.target.value })}
              allowClear
            />
          </Col>
          <Col xs={24} sm={12} md={4}>
            <Select
              placeholder="模块"
              style={{ width: '100%' }}
              value={filters.module}
              onChange={(value) => setFilters({ ...filters, module: value })}
              allowClear
              options={MODULE_OPTIONS}
            />
          </Col>
          <Col xs={24} sm={12} md={4}>
            <Select
              placeholder="操作类型"
              style={{ width: '100%' }}
              value={filters.action}
              onChange={(value) => setFilters({ ...filters, action: value })}
              allowClear
              options={ACTION_OPTIONS}
            />
          </Col>
          <Col xs={24} sm={12} md={4}>
            <Select
              placeholder="状态"
              style={{ width: '100%' }}
              value={filters.success}
              onChange={(value) => setFilters({ ...filters, success: value })}
              allowClear
              options={[
                { value: true, label: '成功' },
                { value: false, label: '失败' }
              ]}
            />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <RangePicker
              style={{ width: '100%' }}
              value={filters.dateRange}
              onChange={(dates) => setFilters({ ...filters, dateRange: dates })}
            />
          </Col>
        </Row>
        <Row style={{ marginTop: 16 }}>
          <Col>
            <Space>
              <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
                搜索
              </Button>
              <Button icon={<ReloadOutlined />} onClick={handleReset}>
                重置
              </Button>
              <Button icon={<DownloadOutlined />}>
                导出
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 数据表格 */}
      <Card>
        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1200 }}
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (page, size) => {
              setCurrentPage(page);
              setPageSize(size);
            }
          }}
        />
      </Card>

      {/* 详情弹窗 */}
      <Modal
        title="日志详情"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={null}
        width={700}
      >
        {selectedLog && (
          <Descriptions column={2} bordered size="small">
            <Descriptions.Item label="ID">{selectedLog.id}</Descriptions.Item>
            <Descriptions.Item label="时间">
              {dayjs(selectedLog.created_at).format('YYYY-MM-DD HH:mm:ss')}
            </Descriptions.Item>
            <Descriptions.Item label="用户">{selectedLog.username}</Descriptions.Item>
            <Descriptions.Item label="IP">{selectedLog.user_ip}</Descriptions.Item>
            <Descriptions.Item label="模块">
              <Tag color={MODULE_COLORS[selectedLog.module]}>
                {MODULE_OPTIONS.find(m => m.value === selectedLog.module)?.label}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="操作">
              <Tag color={ACTION_COLORS[selectedLog.action]}>
                {ACTION_OPTIONS.find(a => a.value === selectedLog.action)?.label}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="资源">{selectedLog.resource}</Descriptions.Item>
            <Descriptions.Item label="资源ID">{selectedLog.resource_id}</Descriptions.Item>
            <Descriptions.Item label="请求方法">
              <Tag>{selectedLog.method}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="响应时间">{selectedLog.response_time}ms</Descriptions.Item>
            <Descriptions.Item label="请求路径" span={2}>
              {selectedLog.path}
            </Descriptions.Item>
            <Descriptions.Item label="状态" span={2}>
              {selectedLog.success ? (
                <Badge status="success" text="成功" />
              ) : (
                <Badge status="error" text="失败" />
              )}
            </Descriptions.Item>
            {selectedLog.error_message && (
              <Descriptions.Item label="错误信息" span={2}>
                <Text type="danger">{selectedLog.error_message}</Text>
              </Descriptions.Item>
            )}
            {selectedLog.description && (
              <Descriptions.Item label="描述" span={2}>
                {selectedLog.description}
              </Descriptions.Item>
            )}
          </Descriptions>
        )}
      </Modal>
    </div>
  );
};

export default AuditLog;
