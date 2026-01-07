/**
 * PowerX 系统管理页面
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 用户管理、角色管理和权限配置
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
  Typography,
  Modal,
  Form,
  Checkbox,
  Tooltip,
  Popconfirm,
  message,
  Badge,
  Avatar,
  Switch,
  Descriptions,
  Tree,
  theme
} from 'antd';
import {
  UserOutlined,
  TeamOutlined,
  SafetyOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
  ReloadOutlined,
  KeyOutlined,
  SettingOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { DataNode } from 'antd/es/tree';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

// ============ 类型定义 ============

interface User {
  id: string;
  username: string;
  email?: string;
  roles: string[];
  is_active: boolean;
  created_at?: string;
  last_login?: string;
}

interface Role {
  id: number;
  code: string;
  name: string;
  description?: string;
  is_system: boolean;
  is_active: boolean;
  permissions?: Permission[];
}

interface Permission {
  code: string;
  name: string;
  module: string;
  description?: string;
}

// ============ 常量 ============

const ROLE_COLORS: Record<string, string> = {
  super_admin: 'red',
  admin: 'orange',
  trader: 'green',
  analyst: 'blue',
  risk_manager: 'purple',
  viewer: 'default'
};

const ROLE_LABELS: Record<string, string> = {
  super_admin: '超级管理员',
  admin: '管理员',
  trader: '交易员',
  analyst: '分析师',
  risk_manager: '风控',
  viewer: '只读用户'
};

const PERMISSION_MODULES = [
  { code: 'trading', name: '交易管理' },
  { code: 'contract', name: '合同管理' },
  { code: 'settlement', name: '结算管理' },
  { code: 'market', name: '市场数据' },
  { code: 'ai', name: 'AI服务' },
  { code: 'report', name: '报告管理' },
  { code: 'admin', name: '系统管理' }
];

// ============ Mock 数据 ============

const mockUsers: User[] = [
  { id: 'USER-001', username: 'admin', email: 'admin@powerx.com', roles: ['super_admin'], is_active: true, created_at: '2026-01-01T00:00:00', last_login: '2026-01-07T10:30:00' },
  { id: 'USER-002', username: 'trader1', email: 'trader1@powerx.com', roles: ['trader'], is_active: true, created_at: '2026-01-02T00:00:00', last_login: '2026-01-07T09:15:00' },
  { id: 'USER-003', username: 'analyst', email: 'analyst@powerx.com', roles: ['analyst'], is_active: true, created_at: '2026-01-03T00:00:00', last_login: '2026-01-06T16:45:00' },
  { id: 'USER-004', username: 'risk_mgr', email: 'risk@powerx.com', roles: ['risk_manager'], is_active: true, created_at: '2026-01-04T00:00:00', last_login: '2026-01-07T08:00:00' },
  { id: 'USER-005', username: 'viewer1', email: 'viewer@powerx.com', roles: ['viewer'], is_active: false, created_at: '2026-01-05T00:00:00' }
];

const mockRoles: Role[] = [
  { id: 1, code: 'super_admin', name: '超级管理员', description: '拥有系统所有权限', is_system: true, is_active: true },
  { id: 2, code: 'admin', name: '管理员', description: '管理用户和系统配置', is_system: true, is_active: true },
  { id: 3, code: 'trader', name: '交易员', description: '执行交易操作', is_system: true, is_active: true },
  { id: 4, code: 'analyst', name: '分析师', description: '数据分析和报告生成', is_system: true, is_active: true },
  { id: 5, code: 'risk_manager', name: '风控', description: '风险监控和预警', is_system: true, is_active: true },
  { id: 6, code: 'viewer', name: '只读用户', description: '仅能查看数据', is_system: true, is_active: true }
];

const mockPermissions: Permission[] = [
  { code: 'trading.view', name: '查看交易', module: 'trading' },
  { code: 'trading.create', name: '创建交易', module: 'trading' },
  { code: 'trading.cancel', name: '取消交易', module: 'trading' },
  { code: 'contract.view', name: '查看合同', module: 'contract' },
  { code: 'contract.create', name: '创建合同', module: 'contract' },
  { code: 'contract.edit', name: '编辑合同', module: 'contract' },
  { code: 'settlement.view', name: '查看结算', module: 'settlement' },
  { code: 'settlement.export', name: '导出结算', module: 'settlement' },
  { code: 'market.view', name: '查看市场数据', module: 'market' },
  { code: 'market.realtime', name: '实时数据', module: 'market' },
  { code: 'ai.chat', name: 'AI对话', module: 'ai' },
  { code: 'ai.predict', name: '价格预测', module: 'ai' },
  { code: 'ai.strategy', name: '策略生成', module: 'ai' },
  { code: 'report.view', name: '查看报告', module: 'report' },
  { code: 'report.create', name: '创建报告', module: 'report' },
  { code: 'admin.user', name: '用户管理', module: 'admin' },
  { code: 'admin.role', name: '角色管理', module: 'admin' },
  { code: 'admin.audit', name: '审计日志', module: 'admin' }
];

// ============ 组件 ============

const Admin: React.FC = () => {
  const { token } = theme.useToken();
  const [form] = Form.useForm();
  
  const [activeTab, setActiveTab] = useState('users');
  const [loading, setLoading] = useState(false);
  
  // 用户管理
  const [users, setUsers] = useState<User[]>(mockUsers);
  const [userModalVisible, setUserModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  
  // 角色管理
  const [roles, setRoles] = useState<Role[]>(mockRoles);
  const [roleModalVisible, setRoleModalVisible] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [selectedPermissions, setSelectedPermissions] = useState<string[]>([]);

  // 构建权限树
  const buildPermissionTree = (): DataNode[] => {
    const moduleMap: Record<string, DataNode> = {};
    
    PERMISSION_MODULES.forEach(m => {
      moduleMap[m.code] = {
        title: m.name,
        key: m.code,
        children: []
      };
    });
    
    mockPermissions.forEach(p => {
      if (moduleMap[p.module]) {
        moduleMap[p.module].children?.push({
          title: p.name,
          key: p.code
        });
      }
    });
    
    return Object.values(moduleMap);
  };

  const handleEditRole = (role: Role) => {
    setEditingRole(role);
    setSelectedPermissions(role.permissions?.map(p => p.code) || []);
    setRoleModalVisible(true);
    form.setFieldsValue({
      code: role.code,
      name: role.name,
      description: role.description
    });
  };

  const handleSaveRole = async () => {
    try {
      const values = await form.validateFields();
      message.success('角色保存成功');
      setRoleModalVisible(false);
      form.resetFields();
      setEditingRole(null);
    } catch (error) {
      // 验证失败
    }
  };

  const handleToggleUserStatus = (user: User) => {
    setUsers(prev => 
      prev.map(u => 
        u.id === user.id ? { ...u, is_active: !u.is_active } : u
      )
    );
    message.success(`用户已${user.is_active ? '禁用' : '启用'}`);
  };

  // 用户表格列
  const userColumns: ColumnsType<User> = [
    {
      title: '用户',
      key: 'user',
      render: (_, record) => (
        <Space>
          <Avatar icon={<UserOutlined />} style={{ backgroundColor: token.colorPrimary }} />
          <div>
            <div>{record.username}</div>
            <Text type="secondary" style={{ fontSize: 12 }}>{record.email}</Text>
          </div>
        </Space>
      )
    },
    {
      title: '角色',
      dataIndex: 'roles',
      key: 'roles',
      render: (roles: string[]) => (
        <Space>
          {roles.map(role => (
            <Tag key={role} color={ROLE_COLORS[role] || 'default'}>
              {ROLE_LABELS[role] || role}
            </Tag>
          ))}
        </Space>
      )
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active) => (
        <Badge status={active ? 'success' : 'default'} text={active ? '正常' : '禁用'} />
      )
    },
    {
      title: '最后登录',
      dataIndex: 'last_login',
      key: 'last_login',
      render: (time) => time ? dayjs(time).format('MM-DD HH:mm') : '-'
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time) => dayjs(time).format('YYYY-MM-DD')
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Tooltip title="编辑角色">
            <Button type="link" size="small" icon={<KeyOutlined />} />
          </Tooltip>
          <Tooltip title={record.is_active ? '禁用' : '启用'}>
            <Switch 
              size="small" 
              checked={record.is_active}
              onChange={() => handleToggleUserStatus(record)}
            />
          </Tooltip>
        </Space>
      )
    }
  ];

  // 角色表格列
  const roleColumns: ColumnsType<Role> = [
    {
      title: '角色代码',
      dataIndex: 'code',
      key: 'code',
      render: (code) => <Tag color={ROLE_COLORS[code]}>{code}</Tag>
    },
    {
      title: '角色名称',
      dataIndex: 'name',
      key: 'name'
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      render: (desc) => <Text type="secondary">{desc || '-'}</Text>
    },
    {
      title: '类型',
      dataIndex: 'is_system',
      key: 'is_system',
      render: (isSystem) => (
        <Tag color={isSystem ? 'blue' : 'default'}>
          {isSystem ? '系统内置' : '自定义'}
        </Tag>
      )
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active) => (
        <Badge status={active ? 'success' : 'default'} text={active ? '启用' : '禁用'} />
      )
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button 
            type="link" 
            size="small" 
            icon={<EditOutlined />}
            onClick={() => handleEditRole(record)}
          >
            编辑
          </Button>
          {!record.is_system && (
            <Popconfirm title="确定删除此角色？" okText="确定" cancelText="取消">
              <Button type="link" size="small" danger icon={<DeleteOutlined />}>
                删除
              </Button>
            </Popconfirm>
          )}
        </Space>
      )
    }
  ];

  const tabItems = [
    {
      key: 'users',
      label: (
        <span>
          <UserOutlined />
          用户管理
        </span>
      ),
      children: (
        <Card>
          <Row justify="space-between" style={{ marginBottom: 16 }}>
            <Col>
              <Space>
                <Input
                  placeholder="搜索用户"
                  prefix={<SearchOutlined />}
                  style={{ width: 200 }}
                />
                <Select
                  placeholder="角色筛选"
                  style={{ width: 120 }}
                  allowClear
                  options={Object.entries(ROLE_LABELS).map(([k, v]) => ({ value: k, label: v }))}
                />
              </Space>
            </Col>
            <Col>
              <Space>
                <Button icon={<ReloadOutlined />}>刷新</Button>
                <Button type="primary" icon={<PlusOutlined />}>添加用户</Button>
              </Space>
            </Col>
          </Row>
          <Table
            columns={userColumns}
            dataSource={users}
            rowKey="id"
            loading={loading}
          />
        </Card>
      )
    },
    {
      key: 'roles',
      label: (
        <span>
          <TeamOutlined />
          角色管理
        </span>
      ),
      children: (
        <Card>
          <Row justify="space-between" style={{ marginBottom: 16 }}>
            <Col>
              <Text type="secondary">
                管理系统角色和权限分配
              </Text>
            </Col>
            <Col>
              <Space>
                <Button icon={<ReloadOutlined />}>刷新</Button>
                <Button type="primary" icon={<PlusOutlined />}>创建角色</Button>
              </Space>
            </Col>
          </Row>
          <Table
            columns={roleColumns}
            dataSource={roles}
            rowKey="id"
            loading={loading}
          />
        </Card>
      )
    },
    {
      key: 'permissions',
      label: (
        <span>
          <SafetyOutlined />
          权限配置
        </span>
      ),
      children: (
        <Card>
          <Row gutter={24}>
            <Col span={12}>
              <Card title="权限列表" size="small">
                <Tree
                  checkable
                  treeData={buildPermissionTree()}
                  defaultExpandAll
                />
              </Card>
            </Col>
            <Col span={12}>
              <Card title="权限说明" size="small">
                <Descriptions column={1} size="small">
                  {PERMISSION_MODULES.map(m => (
                    <Descriptions.Item key={m.code} label={m.name}>
                      {mockPermissions.filter(p => p.module === m.code).length} 项权限
                    </Descriptions.Item>
                  ))}
                </Descriptions>
              </Card>
            </Col>
          </Row>
        </Card>
      )
    }
  ];

  return (
    <div style={{ padding: 24 }}>
      {/* 页面标题 */}
      <div style={{ marginBottom: 24 }}>
        <Title level={4} style={{ margin: 0 }}>
          <SettingOutlined style={{ marginRight: 8 }} />
          系统管理
        </Title>
        <Text type="secondary">管理用户、角色和权限配置</Text>
      </div>

      {/* 标签页 */}
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={tabItems}
      />

      {/* 角色编辑弹窗 */}
      <Modal
        title={editingRole ? '编辑角色' : '创建角色'}
        open={roleModalVisible}
        onOk={handleSaveRole}
        onCancel={() => {
          setRoleModalVisible(false);
          setEditingRole(null);
          form.resetFields();
        }}
        width={700}
      >
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="code"
                label="角色代码"
                rules={[{ required: true, message: '请输入角色代码' }]}
              >
                <Input placeholder="例如: custom_role" disabled={editingRole?.is_system} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="name"
                label="角色名称"
                rules={[{ required: true, message: '请输入角色名称' }]}
              >
                <Input placeholder="例如: 自定义角色" />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="description" label="角色描述">
            <Input.TextArea rows={2} placeholder="描述角色的职责和权限范围" />
          </Form.Item>
          <Form.Item label="权限配置">
            <Tree
              checkable
              treeData={buildPermissionTree()}
              checkedKeys={selectedPermissions}
              onCheck={(checked) => setSelectedPermissions(checked as string[])}
              defaultExpandAll
              style={{ 
                maxHeight: 300, 
                overflow: 'auto',
                border: `1px solid ${token.colorBorder}`,
                borderRadius: 8,
                padding: 8
              }}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Admin;
