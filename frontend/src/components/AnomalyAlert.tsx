/**
 * PowerX 异常警报组件
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 展示市场异常检测结果和警报
 */

import React, { useState, useEffect } from 'react'
import {
  Card,
  List,
  Tag,
  Space,
  Button,
  Typography,
  Badge,
  Empty,
  Spin,
  Modal,
  Descriptions,
  Alert,
  Row,
  Col,
  Statistic,
  theme
} from 'antd'
import {
  WarningOutlined,
  ExclamationCircleOutlined,
  BellOutlined,
  ReloadOutlined,
  EyeOutlined,
  RiseOutlined,
  FallOutlined,
  StockOutlined
} from '@ant-design/icons'
import dayjs from 'dayjs'
import api from '../services/api'

const { useToken } = theme
const { Text, Title } = Typography

interface Anomaly {
  id: string
  type: string
  severity: string
  province: string
  market_type: string
  detected_at: string
  description: string
  current_value: number
  expected_value: number
  deviation_pct: number
  details: Record<string, any>
  recommendations: string[]
}

interface AnomalyStats {
  total_count: number
  time_range_hours: number
  by_type: Record<string, number>
  by_severity: Record<string, number>
  by_province: Record<string, number>
  latest_anomaly: Anomaly | null
}

interface AnomalyAlertProps {
  compact?: boolean
  onViewAll?: () => void
}

// Mock 数据
const mockAnomalies: Anomaly[] = [
  {
    id: 'ano-001',
    type: 'PRICE_SPIKE',
    severity: 'HIGH',
    province: '广东',
    market_type: 'DAY_AHEAD',
    detected_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
    description: '广东日前市场价格在过去1小时内上涨超过15%，偏离历史均值',
    current_value: 512.45,
    expected_value: 445.60,
    deviation_pct: 15.0,
    details: { trigger: '负荷激增', duration: '45分钟' },
    recommendations: [
      '密切关注市场动态，考虑适时卖出持仓',
      '检查风险敞口，确保不超过限额',
      '关注调度通知，确认是否有特殊情况'
    ]
  },
  {
    id: 'ano-002',
    type: 'VOLUME_SURGE',
    severity: 'MEDIUM',
    province: '浙江',
    market_type: 'REAL_TIME',
    detected_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    description: '浙江实时市场成交量异常放大，较前一交易日同期增长200%',
    current_value: 45800,
    expected_value: 15200,
    deviation_pct: 201.3,
    details: { trigger: '新能源消纳', duration: '2小时' },
    recommendations: [
      '注意市场流动性变化',
      '评估大宗交易对价格的影响',
      '考虑分批建仓策略'
    ]
  },
  {
    id: 'ano-003',
    type: 'SPREAD_ABNORMAL',
    severity: 'LOW',
    province: '山东',
    market_type: 'DAY_AHEAD',
    detected_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
    description: '山东与周边省份电价价差扩大至异常区间',
    current_value: 35.50,
    expected_value: 12.00,
    deviation_pct: 195.8,
    details: { trigger: '跨省输电受限', duration: '3小时' },
    recommendations: [
      '关注跨省交易机会',
      '评估套利空间和风险'
    ]
  }
]

const mockStats: AnomalyStats = {
  total_count: 3,
  time_range_hours: 24,
  by_type: { PRICE_SPIKE: 1, VOLUME_SURGE: 1, SPREAD_ABNORMAL: 1 },
  by_severity: { HIGH: 1, MEDIUM: 1, LOW: 1 },
  by_province: { '广东': 1, '浙江': 1, '山东': 1 },
  latest_anomaly: mockAnomalies[0]
}

const AnomalyAlert: React.FC<AnomalyAlertProps> = ({
  compact = false,
  onViewAll
}) => {
  const { token } = useToken()
  const [anomalies, setAnomalies] = useState<Anomaly[]>(mockAnomalies)
  const [stats, setStats] = useState<AnomalyStats | null>(mockStats)
  const [loading, setLoading] = useState(false)
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [selectedAnomaly, setSelectedAnomaly] = useState<Anomaly | null>(null)

  const loadAnomalies = async () => {
    setLoading(true)
    try {
      const [anomalyResponse, statsResponse] = await Promise.all([
        api.get('/ai-advisor/anomalies', { params: { hours: 24 } }),
        api.get('/ai-advisor/anomaly-stats', { params: { hours: 24 } })
      ])
      
      if (anomalyResponse.data.success && anomalyResponse.data.data.length > 0) {
        setAnomalies(anomalyResponse.data.data)
      } else {
        setAnomalies(mockAnomalies)
      }
      if (statsResponse.data.success && statsResponse.data.data) {
        setStats(statsResponse.data.data)
      } else {
        setStats(mockStats)
      }
    } catch (error) {
      console.error('加载异常数据失败，使用 Mock 数据:', error)
      setAnomalies(mockAnomalies)
      setStats(mockStats)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAnomalies()
    // 每分钟刷新
    const interval = setInterval(loadAnomalies, 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  const getTypeIcon = (type: string) => {
    const icons: Record<string, React.ReactNode> = {
      PRICE_SPIKE: <RiseOutlined style={{ color: token.colorError }} />,
      PRICE_CRASH: <FallOutlined style={{ color: token.colorSuccess }} />,
      VOLUME_SURGE: <StockOutlined style={{ color: token.colorWarning }} />,
      VOLUME_DROP: <StockOutlined style={{ color: token.colorTextSecondary }} />,
      PATTERN_UNUSUAL: <ExclamationCircleOutlined style={{ color: token.colorPrimary }} />,
      SPREAD_ABNORMAL: <WarningOutlined style={{ color: token.colorWarning }} />
    }
    return icons[type] || <ExclamationCircleOutlined />
  }

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      PRICE_SPIKE: '价格飙升',
      PRICE_CRASH: '价格暴跌',
      VOLUME_SURGE: '成交量激增',
      VOLUME_DROP: '成交量骤降',
      PATTERN_UNUSUAL: '异常模式',
      SPREAD_ABNORMAL: '价差异常'
    }
    return labels[type] || type
  }

  const getSeverityTag = (severity: string) => {
    const config: Record<string, { color: string; text: string }> = {
      LOW: { color: 'default', text: '低' },
      MEDIUM: { color: 'warning', text: '中' },
      HIGH: { color: 'error', text: '高' },
      CRITICAL: { color: '#ff0000', text: '严重' }
    }
    const c = config[severity] || { color: 'default', text: severity }
    return <Tag color={c.color}>{c.text}</Tag>
  }

  const handleViewDetail = (anomaly: Anomaly) => {
    setSelectedAnomaly(anomaly)
    setDetailModalVisible(true)
  }

  if (compact) {
    // 紧凑模式 - 显示最新几条异常
    const recentAnomalies = anomalies.slice(0, 3)
    const criticalCount = anomalies.filter(
      a => a.severity === 'HIGH' || a.severity === 'CRITICAL'
    ).length

    return (
      <Card
        title={
          <Space>
            <WarningOutlined style={{ color: criticalCount > 0 ? token.colorError : token.colorWarning }} />
            <span>市场异常监测</span>
            {criticalCount > 0 && (
              <Badge count={criticalCount} style={{ backgroundColor: token.colorError }} />
            )}
          </Space>
        }
        extra={
          <Space>
            <Button
              type="text"
              icon={<ReloadOutlined spin={loading} />}
              onClick={loadAnomalies}
              size="small"
            />
            {onViewAll && (
              <Button type="link" size="small" onClick={onViewAll}>
                查看全部
              </Button>
            )}
          </Space>
        }
        bodyStyle={{ padding: '12px 16px' }}
      >
        {recentAnomalies.length === 0 && loading ? (
          <div style={{ textAlign: 'center', padding: 20 }}>
            <Spin />
          </div>
        ) : recentAnomalies.length === 0 ? (
          <Alert
            message="暂无异常"
            description="过去24小时内未检测到市场异常"
            type="success"
            showIcon
          />
        ) : (
          <List
            dataSource={recentAnomalies}
            renderItem={(item) => (
              <List.Item 
                style={{ padding: '8px 0', cursor: 'pointer' }}
                onClick={() => handleViewDetail(item)}
              >
                <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                  <Space>
                    {getTypeIcon(item.type)}
                    <Text>{item.province}</Text>
                    <Text type="secondary">{getTypeLabel(item.type)}</Text>
                  </Space>
                  <Space>
                    {getSeverityTag(item.severity)}
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {dayjs(item.detected_at).format('HH:mm')}
                    </Text>
                  </Space>
                </Space>
              </List.Item>
            )}
          />
        )}
      </Card>
    )
  }

  // 完整模式
  return (
    <>
      <Card
        title={
          <Space>
            <WarningOutlined style={{ color: token.colorWarning }} />
            <span>市场异常监测</span>
            <Badge count={anomalies.length} showZero />
          </Space>
        }
        extra={
          <Button
            icon={<ReloadOutlined />}
            onClick={loadAnomalies}
            loading={loading}
          >
            刷新
          </Button>
        }
      >
        {/* 统计概览 */}
        {stats && (
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col span={6}>
              <Statistic 
                title="24小时异常数" 
                value={stats.total_count}
                prefix={<ExclamationCircleOutlined />}
              />
            </Col>
            <Col span={6}>
              <Statistic 
                title="高危异常" 
                value={(stats.by_severity?.HIGH || 0) + (stats.by_severity?.CRITICAL || 0)}
                prefix={<WarningOutlined />}
                valueStyle={{ color: token.colorError }}
              />
            </Col>
            <Col span={6}>
              <Statistic 
                title="价格异常" 
                value={(stats.by_type?.PRICE_SPIKE || 0) + (stats.by_type?.PRICE_CRASH || 0)}
                prefix={<StockOutlined />}
              />
            </Col>
            <Col span={6}>
              <Statistic 
                title="成交量异常" 
                value={(stats.by_type?.VOLUME_SURGE || 0) + (stats.by_type?.VOLUME_DROP || 0)}
                prefix={<StockOutlined />}
              />
            </Col>
          </Row>
        )}

        {/* 异常列表 */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <Spin size="large" />
          </div>
        ) : anomalies.length === 0 ? (
          <Empty description="过去24小时未检测到异常" />
        ) : (
          <List
            dataSource={anomalies}
            renderItem={(item) => (
              <List.Item
                actions={[
                  <Button 
                    type="link" 
                    icon={<EyeOutlined />}
                    onClick={() => handleViewDetail(item)}
                  >
                    详情
                  </Button>
                ]}
              >
                <List.Item.Meta
                  avatar={
                    <div style={{ 
                      width: 40, 
                      height: 40, 
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      background: token.colorBgTextHover,
                      fontSize: 18
                    }}>
                      {getTypeIcon(item.type)}
                    </div>
                  }
                  title={
                    <Space>
                      <Text strong>{item.province}</Text>
                      <Tag>{getTypeLabel(item.type)}</Tag>
                      {getSeverityTag(item.severity)}
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {dayjs(item.detected_at).format('YYYY-MM-DD HH:mm:ss')}
                      </Text>
                    </Space>
                  }
                  description={
                    <Space direction="vertical" size={4}>
                      <Text>{item.description}</Text>
                      <Text type="secondary">
                        偏离程度: {item.deviation_pct > 0 ? '+' : ''}{item.deviation_pct}%
                      </Text>
                    </Space>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </Card>

      {/* 详情弹窗 */}
      <Modal
        title={
          <Space>
            {selectedAnomaly && getTypeIcon(selectedAnomaly.type)}
            <span>异常详情</span>
          </Space>
        }
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={600}
      >
        {selectedAnomaly && (
          <>
            <Descriptions bordered column={2}>
              <Descriptions.Item label="异常类型">
                {getTypeLabel(selectedAnomaly.type)}
              </Descriptions.Item>
              <Descriptions.Item label="严重程度">
                {getSeverityTag(selectedAnomaly.severity)}
              </Descriptions.Item>
              <Descriptions.Item label="省份">
                {selectedAnomaly.province}
              </Descriptions.Item>
              <Descriptions.Item label="市场类型">
                {selectedAnomaly.market_type === 'DAY_AHEAD' ? '日前市场' : '实时市场'}
              </Descriptions.Item>
              <Descriptions.Item label="当前值">
                {selectedAnomaly.current_value.toFixed(2)}
              </Descriptions.Item>
              <Descriptions.Item label="预期值">
                {selectedAnomaly.expected_value.toFixed(2)}
              </Descriptions.Item>
              <Descriptions.Item label="偏离程度" span={2}>
                <Text 
                  strong 
                  style={{ 
                    color: Math.abs(selectedAnomaly.deviation_pct) > 10 
                      ? token.colorError 
                      : token.colorWarning 
                  }}
                >
                  {selectedAnomaly.deviation_pct > 0 ? '+' : ''}{selectedAnomaly.deviation_pct}%
                </Text>
              </Descriptions.Item>
              <Descriptions.Item label="检测时间" span={2}>
                {dayjs(selectedAnomaly.detected_at).format('YYYY-MM-DD HH:mm:ss')}
              </Descriptions.Item>
              <Descriptions.Item label="描述" span={2}>
                {selectedAnomaly.description}
              </Descriptions.Item>
            </Descriptions>

            <div style={{ marginTop: 16 }}>
              <Title level={5}>建议操作</Title>
              <List
                dataSource={selectedAnomaly.recommendations}
                renderItem={(item, index) => (
                  <List.Item>
                    <Space>
                      <Badge count={index + 1} style={{ backgroundColor: token.colorPrimary }} />
                      <Text>{item}</Text>
                    </Space>
                  </List.Item>
                )}
              />
            </div>
          </>
        )}
      </Modal>
    </>
  )
}

export default AnomalyAlert
