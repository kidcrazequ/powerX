/**
 * PowerX 主应用组件
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 */

import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ConfigProvider, theme } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import enUS from 'antd/locale/en_US'

import MainLayout from './layouts/MainLayout'
import Dashboard from './pages/Dashboard'
import SpotTrading from './pages/SpotTrading'
import MidLongTrading from './pages/MidLongTrading'
import Market from './pages/Market'
import Contract from './pages/Contract'
import Settlement from './pages/Settlement'
import AIAssistant from './pages/AI'
import Report from './pages/Report'
import Login from './pages/Login'
import Profile from './pages/Profile'
import Settings from './pages/Settings'
import AuditLog from './pages/AuditLog'
import Admin from './pages/Admin'
import Alerts from './pages/Alerts'
import Analytics from './pages/Analytics'
import Forecast from './pages/Forecast'
import Simulation from './pages/Simulation'
import ConditionalOrder from './pages/ConditionalOrder'
import TradingRules from './pages/TradingRules'
import SystemHealth from './pages/SystemHealth'
import TradingLimits from './pages/TradingLimits'
import ApprovalCenter from './pages/ApprovalCenter'
import NotificationSettings from './pages/NotificationSettings'
import BackupManage from './pages/BackupManage'
import ApiStats from './pages/ApiStats'
import ReportBuilder from './pages/ReportBuilder'
import HistoryReplay from './pages/HistoryReplay'
import TwoFactorSetup from './pages/TwoFactorSetup'
import ComboOrder from './pages/ComboOrder'
import AlgoTrading from './pages/AlgoTrading'
import PredictionReconciliation from './pages/PredictionReconciliation'
import DataScreen from './pages/DataScreen'
import CrossProvince from './pages/CrossProvince'
import OptionTrading from './pages/OptionTrading'
import WebhookManage from './pages/WebhookManage'
import OpenAPI from './pages/OpenAPI'
import DigitalSignature from './pages/DigitalSignature'
import { useAuthStore } from './stores/authStore'
import { useSettingsStore } from './stores/settingsStore'

/**
 * 受保护的路由组件
 */
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuthStore()
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

/**
 * 深色主题配置
 */
const darkThemeConfig = {
  algorithm: theme.darkAlgorithm,
  token: {
    colorPrimary: '#1677ff',
    borderRadius: 6,
    colorBgContainer: '#141414',
    colorBgLayout: '#000000',
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
  },
  components: {
    Card: {
      colorBgContainer: '#1f1f1f',
    },
    Table: {
      colorBgContainer: '#1f1f1f',
      colorHeaderBg: '#1a1a1a',
    },
    Menu: {
      colorItemBg: 'transparent',
      colorSubItemBg: 'transparent',
    }
  },
}

/**
 * 浅色主题配置
 */
const lightThemeConfig = {
  algorithm: theme.defaultAlgorithm,
  token: {
    colorPrimary: '#1677ff',
    borderRadius: 6,
    colorBgContainer: '#ffffff',
    colorBgLayout: '#f5f5f5',
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
  },
  components: {
    Card: {
      colorBgContainer: '#ffffff',
    },
    Table: {
      colorBgContainer: '#ffffff',
      colorHeaderBg: '#fafafa',
    },
    Menu: {
      colorItemBg: 'transparent',
      colorSubItemBg: 'transparent',
    }
  },
}

/**
 * 主应用组件
 */
const App: React.FC = () => {
  // 获取用户设置
  const { themeMode, language } = useSettingsStore()
  
  // 根据设置选择主题和语言
  const themeConfig = themeMode === 'dark' ? darkThemeConfig : lightThemeConfig
  const locale = language === 'zh-CN' ? zhCN : enUS

  // 同步主题到 HTML 标签，方便 CSS 使用
  React.useEffect(() => {
    document.documentElement.setAttribute('data-theme', themeMode)
  }, [themeMode])

  return (
    <ConfigProvider
      locale={locale}
      theme={themeConfig}
    >
      <BrowserRouter>
        <Routes>
          {/* 登录页 */}
          <Route path="/login" element={<Login />} />
          
          {/* 主布局 */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <MainLayout />
              </ProtectedRoute>
            }
          >
            {/* 仪表盘 */}
            <Route index element={<Dashboard />} />
            
            {/* 现货交易 */}
            <Route path="spot-trading" element={<SpotTrading />} />
            
            {/* 中长期交易 */}
            <Route path="mid-long-trading" element={<MidLongTrading />} />
            
            {/* 市场数据 */}
            <Route path="market" element={<Market />} />
            
            {/* 合同管理 */}
            <Route path="contract" element={<Contract />} />
            
            {/* 结算中心 */}
            <Route path="settlement" element={<Settlement />} />
            
            {/* AI 助手 */}
            <Route path="ai" element={<AIAssistant />} />
            
            {/* 报告中心 */}
            <Route path="report" element={<Report />} />
            
            {/* 个人信息 */}
            <Route path="profile" element={<Profile />} />
            
            {/* 系统设置 */}
            <Route path="settings" element={<Settings />} />
            
            {/* 数据分析 */}
            <Route path="analytics" element={<Analytics />} />
            
            {/* 电量预测 */}
            <Route path="forecast" element={<Forecast />} />
            
            {/* 交易模拟 */}
            <Route path="simulation" element={<Simulation />} />
            
            {/* 预警管理 */}
            <Route path="alerts" element={<Alerts />} />
            
            {/* 审计日志 */}
            <Route path="audit-log" element={<AuditLog />} />
            
            {/* 系统管理 */}
            <Route path="admin" element={<Admin />} />
            
            {/* 条件单管理 */}
            <Route path="conditional-order" element={<ConditionalOrder />} />
            
            {/* 交易规则 */}
            <Route path="trading-rules" element={<TradingRules />} />
            
            {/* 系统健康 */}
            <Route path="system-health" element={<SystemHealth />} />
            
            {/* 交易限额 */}
            <Route path="trading-limits" element={<TradingLimits />} />
            
            {/* 审批中心 */}
            <Route path="approval" element={<ApprovalCenter />} />
            
            {/* 通知设置 */}
            <Route path="notification-settings" element={<NotificationSettings />} />
            
            {/* 备份管理 */}
            <Route path="backup" element={<BackupManage />} />
            
            {/* API 统计 */}
            <Route path="api-stats" element={<ApiStats />} />
            
            {/* 报表生成器 */}
            <Route path="report-builder" element={<ReportBuilder />} />
            
            {/* 历史回放 */}
            <Route path="history-replay" element={<HistoryReplay />} />
            
            {/* 双因素认证 */}
            <Route path="two-factor" element={<TwoFactorSetup />} />
            
            {/* 组合订单 */}
            <Route path="combo-order" element={<ComboOrder />} />
            
            {/* 算法交易 */}
            <Route path="algo-trading" element={<AlgoTrading />} />
            
            {/* 预测对账 */}
            <Route path="prediction-reconciliation" element={<PredictionReconciliation />} />
            
            {/* 数据大屏 */}
            <Route path="data-screen" element={<DataScreen />} />
            
            {/* 跨省交易 */}
            <Route path="cross-province" element={<CrossProvince />} />
            
            {/* 期权交易 */}
            <Route path="option-trading" element={<OptionTrading />} />
            
            {/* Webhook管理 */}
            <Route path="webhook" element={<WebhookManage />} />
            
            {/* 开放API */}
            <Route path="open-api" element={<OpenAPI />} />
            
            {/* 电子签章 */}
            <Route path="digital-signature" element={<DigitalSignature />} />
          </Route>
          
          {/* 404 重定向 */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  )
}

export default App
