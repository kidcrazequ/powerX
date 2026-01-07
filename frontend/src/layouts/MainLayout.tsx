/**
 * PowerX 主布局组件
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 */

import React, { useState } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { 
  Layout, 
  Menu, 
  Avatar, 
  Dropdown, 
  Space, 
  Typography, 
  Select, 
  Badge, 
  theme,
  Drawer,
  List,
  Button,
  Tag,
  Empty,
  Tooltip
} from 'antd'
import {
  DashboardOutlined,
  ThunderboltOutlined,
  LineChartOutlined,
  BarChartOutlined,
  FileTextOutlined,
  SettingOutlined,
  RobotOutlined,
  LogoutOutlined,
  UserOutlined,
  BellOutlined,
  SwapOutlined,
  BankOutlined,
  CheckOutlined,
  DeleteOutlined,
  CloseOutlined,
  InfoCircleOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  CloseCircleOutlined,
  ExperimentOutlined,
  FundOutlined,
  AlertOutlined,
  AuditOutlined,
  TeamOutlined,
} from '@ant-design/icons'
import type { MenuProps } from 'antd'

import { useAuthStore } from '../stores/authStore'
import { useNotificationStore, NotificationItem, NotificationType, NotificationCategory } from '../stores/notificationStore'
import { useSettingsStore } from '../stores/settingsStore'

const { Header, Sider, Content } = Layout
const { Text } = Typography

// 省份选项
const PROVINCES = [
  { value: '广东', label: '广东' },
  { value: '浙江', label: '浙江' },
  { value: '山东', label: '山东' },
  { value: '山西', label: '山西' },
  { value: '甘肃', label: '甘肃' },
]

// 菜单项
const menuItems: MenuProps['items'] = [
  {
    key: '/',
    icon: <DashboardOutlined />,
    label: '交易仪表盘',
  },
  {
    key: 'trading',
    icon: <ThunderboltOutlined />,
    label: '电力交易',
    children: [
      {
        key: '/spot-trading',
        icon: <SwapOutlined />,
        label: '现货交易',
      },
      {
        key: '/mid-long-trading',
        icon: <BankOutlined />,
        label: '中长期交易',
      },
      {
        key: '/conditional-order',
        icon: <ThunderboltOutlined />,
        label: '条件单',
      },
      {
        key: '/trading-rules',
        icon: <SettingOutlined />,
        label: '交易规则',
      },
      {
        key: '/combo-order',
        icon: <SwapOutlined />,
        label: '组合订单',
      },
      {
        key: '/algo-trading',
        icon: <LineChartOutlined />,
        label: '算法交易',
      },
      {
        key: '/cross-province',
        icon: <SwapOutlined />,
        label: '跨省交易',
      },
      {
        key: '/option-trading',
        icon: <FundOutlined />,
        label: '期权交易',
      },
    ],
  },
  {
    key: '/market',
    icon: <LineChartOutlined />,
    label: '市场数据',
  },
  {
    key: '/contract',
    icon: <FileTextOutlined />,
    label: '合同管理',
  },
  {
    key: '/settlement',
    icon: <BarChartOutlined />,
    label: '结算中心',
  },
  {
    key: '/ai',
    icon: <RobotOutlined />,
    label: 'AI 助手',
  },
  {
    key: '/report',
    icon: <FileTextOutlined />,
    label: '报告中心',
  },
  {
    key: 'data',
    icon: <FundOutlined />,
    label: '数据服务',
    children: [
      {
        key: '/analytics',
        icon: <BarChartOutlined />,
        label: '数据分析',
      },
      {
        key: '/forecast',
        icon: <LineChartOutlined />,
        label: '电量预测',
      },
      {
        key: '/simulation',
        icon: <ExperimentOutlined />,
        label: '交易模拟',
      },
      {
        key: '/report-builder',
        icon: <FileTextOutlined />,
        label: '报表生成器',
      },
      {
        key: '/history-replay',
        icon: <LineChartOutlined />,
        label: '历史回放',
      },
      {
        key: '/prediction-reconciliation',
        icon: <BarChartOutlined />,
        label: '预测对账',
      },
      {
        key: '/data-screen',
        icon: <FundOutlined />,
        label: '数据大屏',
      },
    ],
  },
  {
    key: 'risk',
    icon: <AlertOutlined />,
    label: '风控合规',
    children: [
      {
        key: '/alerts',
        icon: <AlertOutlined />,
        label: '预警管理',
      },
      {
        key: '/trading-limits',
        icon: <BarChartOutlined />,
        label: '交易限额',
      },
      {
        key: '/approval',
        icon: <CheckOutlined />,
        label: '审批中心',
      },
    ],
  },
  {
    key: 'system',
    icon: <SettingOutlined />,
    label: '系统管理',
    children: [
      {
        key: '/system-health',
        icon: <DashboardOutlined />,
        label: '系统健康',
      },
      {
        key: '/audit-log',
        icon: <AuditOutlined />,
        label: '审计日志',
      },
      {
        key: '/admin',
        icon: <TeamOutlined />,
        label: '权限管理',
      },
      {
        key: '/notification-settings',
        icon: <BellOutlined />,
        label: '通知设置',
      },
      {
        key: '/backup',
        icon: <FileTextOutlined />,
        label: '备份管理',
      },
      {
        key: '/api-stats',
        icon: <BarChartOutlined />,
        label: 'API 统计',
      },
      {
        key: '/webhook',
        icon: <SwapOutlined />,
        label: 'Webhook',
      },
      {
        key: '/open-api',
        icon: <SettingOutlined />,
        label: '开放 API',
      },
      {
        key: '/digital-signature',
        icon: <FileTextOutlined />,
        label: '电子签章',
      },
      {
        key: '/two-factor',
        icon: <SettingOutlined />,
        label: '双因素认证',
      },
    ],
  },
]

/**
 * 获取通知类型图标
 * @param type 通知类型
 */
const getNotificationIcon = (type: NotificationType) => {
  const iconMap = {
    info: <InfoCircleOutlined style={{ color: '#1677ff' }} />,
    success: <CheckCircleOutlined style={{ color: '#52c41a' }} />,
    warning: <WarningOutlined style={{ color: '#faad14' }} />,
    error: <CloseCircleOutlined style={{ color: '#ff4d4f' }} />,
  }
  return iconMap[type]
}

/**
 * 获取通知分类标签
 * @param category 分类
 */
const getCategoryTag = (category: NotificationCategory) => {
  const tagMap = {
    trade: { color: 'blue', text: '交易' },
    price: { color: 'orange', text: '价格' },
    system: { color: 'purple', text: '系统' },
    report: { color: 'cyan', text: '报告' },
  }
  const tag = tagMap[category]
  return <Tag color={tag.color} style={{ marginRight: 0 }}>{tag.text}</Tag>
}

/**
 * 格式化时间显示
 * @param date 时间
 */
const formatTime = (date: Date): string => {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}

const MainLayout: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()
  const { themeMode } = useSettingsStore()
  const { 
    notifications, 
    visible: notificationVisible, 
    setVisible: setNotificationVisible,
    markAsRead,
    markAllAsRead,
    removeNotification,
    clearAll,
    getUnreadCount 
  } = useNotificationStore()
  const [collapsed, setCollapsed] = useState(false)
  const [currentProvince, setCurrentProvince] = useState('广东')

  const { token } = theme.useToken();

  // 未读通知数量
  const unreadCount = getUnreadCount()

  // 用户下拉菜单
  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人信息',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '系统设置',
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      danger: true,
    },
  ]

  // 处理菜单点击
  const handleMenuClick: MenuProps['onClick'] = ({ key }) => {
    navigate(key)
  }

  // 处理用户菜单点击
  const handleUserMenuClick: MenuProps['onClick'] = ({ key }) => {
    switch (key) {
      case 'profile':
        navigate('/profile')
        break
      case 'settings':
        navigate('/settings')
        break
      case 'logout':
        logout()
        navigate('/login')
        break
    }
  }

  /**
   * 处理通知点击
   * @param notification 通知项
   */
  const handleNotificationClick = (notification: NotificationItem) => {
    // 标记为已读
    if (!notification.read) {
      markAsRead(notification.id)
    }
    
    // 根据分类跳转到对应页面
    switch (notification.category) {
      case 'trade':
        navigate('/spot-trading')
        break
      case 'price':
        navigate('/market')
        break
      case 'report':
        navigate('/report')
        break
      default:
        break
    }
    
    setNotificationVisible(false)
  }

  return (
    <Layout style={{ minHeight: '100vh', background: token.colorBgLayout }}>
      {/* 侧边栏 */}
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        theme={themeMode}
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
          borderRight: `1px solid ${token.colorBorderSecondary}`,
          zIndex: 101,
          backgroundColor: themeMode === 'dark' ? '#001529' : '#ffffff',
        }}
      >
            {/* Logo */}
            <div 
              key={`logo-${themeMode}`}
              className={themeMode === 'dark' ? 'logo-glow' : ''}
              style={{
                height: 64,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderBottom: `1px solid ${themeMode === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.06)'}`,
                background: 'transparent',
                transition: 'all 0.3s',
              }}
            >
              <ThunderboltOutlined style={{ 
                fontSize: 24, 
                color: token.colorPrimary,
                filter: themeMode === 'dark' 
                  ? `drop-shadow(0 0 8px ${token.colorPrimary}60)`
                  : 'none'
              }} />
              {!collapsed && (
                <span 
                  key={`logo-text-${themeMode}`}
                  style={{ 
                    fontWeight: 700,
                    marginLeft: 10, 
                    fontSize: 20, 
                    letterSpacing: -0.5,
                    color: themeMode === 'dark' ? '#ffffff' : '#1a1a2e',
                    display: 'inline-block',
                  }}
                >
                  Power
                  <span style={{ color: token.colorPrimary }}>X</span>
                </span>
              )}
            </div>

        {/* 菜单 */}
        <Menu
          theme={themeMode}
          mode="inline"
          selectedKeys={[location.pathname]}
          defaultOpenKeys={['trading']}
          items={menuItems}
          onClick={handleMenuClick}
          style={{ background: 'transparent', marginTop: 16 }}
        />
      </Sider>

      <Layout style={{ 
        marginLeft: collapsed ? 80 : 200, 
        transition: 'margin-left 0.2s',
        background: token.colorBgLayout 
      }}>
        {/* 头部 */}
        <Header style={{
          padding: '0 24px',
          background: themeMode === 'dark' ? 'rgba(20, 20, 20, 0.8)' : 'rgba(255, 255, 255, 0.8)',
          backdropFilter: 'blur(10px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: `1px solid ${token.colorBorderSecondary}`,
          position: 'sticky',
          top: 0,
          zIndex: 100,
        }}>
          {/* 左侧：省份选择 */}
          <Space>
            <Text type="secondary">当前市场：</Text>
            <Select
              value={currentProvince}
              onChange={setCurrentProvince}
              options={PROVINCES}
              style={{ width: 100 }}
              variant="borderless"
            />
          </Space>

          {/* 右侧：通知和用户 */}
          <Space size="large">
            <Tooltip title="消息通知">
              <Badge count={unreadCount} size="small">
                <BellOutlined 
                  style={{ fontSize: 18, cursor: 'pointer', color: token.colorTextSecondary }} 
                  onClick={() => setNotificationVisible(true)}
                />
              </Badge>
            </Tooltip>
            
            <Dropdown
              menu={{ items: userMenuItems, onClick: handleUserMenuClick }}
              placement="bottomRight"
            >
              <Space style={{ cursor: 'pointer' }}>
                <Avatar 
                  size="small"
                  icon={<UserOutlined />} 
                  style={{ backgroundColor: token.colorPrimary }}
                />
                <Text strong>{user?.name || '用户'}</Text>
              </Space>
            </Dropdown>
          </Space>
        </Header>

        {/* 内容区 */}
        <Content style={{
          margin: 0,
          minHeight: 'calc(100vh - 64px)',
          background: token.colorBgLayout,
          position: 'relative',
        }}>
          {/* 装饰性背景 */}
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: 300,
            background: `linear-gradient(to bottom, ${token.colorPrimary}10, transparent)`,
            pointerEvents: 'none',
          }} />
          
              <div 
                className="animate-in"
                style={{
                  padding: '24px 32px',
                  position: 'relative',
                  zIndex: 1,
                }}
              >
                <Outlet />
              </div>
        </Content>
      </Layout>

      {/* 通知抽屉 */}
      <Drawer
        title={
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Space>
              <BellOutlined />
              <span>消息通知</span>
              {unreadCount > 0 && (
                <Badge count={unreadCount} style={{ marginLeft: 8 }} />
              )}
            </Space>
          </div>
        }
        placement="right"
        width={400}
        open={notificationVisible}
        onClose={() => setNotificationVisible(false)}
        closeIcon={<CloseOutlined />}
        extra={
          <Space>
            <Button 
              type="text" 
              size="small" 
              icon={<CheckOutlined />}
              onClick={markAllAsRead}
              disabled={unreadCount === 0}
            >
              全部已读
            </Button>
            <Button 
              type="text" 
              size="small" 
              danger
              icon={<DeleteOutlined />}
              onClick={clearAll}
              disabled={notifications.length === 0}
            >
              清空
            </Button>
          </Space>
        }
        styles={{
          body: { padding: 0 },
          header: { borderBottom: `1px solid ${token.colorBorderSecondary}` }
        }}
      >
        {notifications.length === 0 ? (
          <Empty 
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="暂无消息"
            style={{ marginTop: 100 }}
          />
        ) : (
          <List
            dataSource={notifications}
            renderItem={(item) => (
              <List.Item
                style={{
                  padding: '16px 20px',
                  cursor: 'pointer',
                  background: item.read ? 'transparent' : 'rgba(22, 119, 255, 0.05)',
                  borderBottom: `1px solid ${token.colorBorderSecondary}`,
                  transition: 'background 0.2s',
                }}
                onClick={() => handleNotificationClick(item)}
                actions={[
                  <Tooltip title="删除" key="delete">
                    <Button 
                      type="text" 
                      size="small"
                      danger
                      icon={<DeleteOutlined />}
                      onClick={(e) => {
                        e.stopPropagation()
                        removeNotification(item.id)
                      }}
                    />
                  </Tooltip>
                ]}
              >
                <List.Item.Meta
                  avatar={getNotificationIcon(item.type)}
                  title={
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <Text strong style={{ flex: 1 }}>
                        {!item.read && (
                          <Badge status="processing" style={{ marginRight: 8 }} />
                        )}
                        {item.title}
                      </Text>
                      {getCategoryTag(item.category)}
                    </div>
                  }
                  description={
                    <div>
                      <Text 
                        type="secondary" 
                        style={{ 
                          fontSize: 13, 
                          display: 'block',
                          marginBottom: 8,
                          lineHeight: 1.5
                        }}
                      >
                        {item.content}
                      </Text>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {formatTime(item.createdAt)}
                      </Text>
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </Drawer>
    </Layout>
  )
}

export default MainLayout
