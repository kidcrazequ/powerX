/**
 * PowerX AI 交易建议组件
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 展示 AI 生成的交易建议
 */

import React, { useState, useEffect } from 'react'
import {
  Card,
  List,
  Tag,
  Space,
  Button,
  Progress,
  Typography,
  Tooltip,
  Badge,
  Empty,
  Spin,
  Row,
  Col,
  Divider,
  theme
} from 'antd'
import {
  RocketOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  MinusOutlined,
  ReloadOutlined,
  InfoCircleOutlined,
  ThunderboltOutlined,
  FireOutlined
} from '@ant-design/icons'
import api from '../services/api'

const { useToken } = theme
const { Text, Title } = Typography

interface Recommendation {
  id: string
  province: string
  market_type: string
  direction: string
  confidence: number
  current_price: number
  target_price: number
  potential_profit_pct: number
  reason: string
  factors: Array<{
    name: string
    value: string
    contribution: number
  }>
  risk_level: string
  created_at: string
  valid_until: string
}

interface AIRecommendationProps {
  onTrade?: (recommendation: Recommendation) => void
  compact?: boolean
}

// Mock 数据
const mockRecommendations: Recommendation[] = [
  {
    id: 'rec-001',
    province: '广东',
    market_type: 'DAY_AHEAD',
    direction: 'BUY',
    confidence: 0.85,
    current_price: 452.30,
    target_price: 478.50,
    potential_profit_pct: 5.8,
    reason: '预计明日用电负荷增加，电价有望上涨',
    factors: [
      { name: '负荷预测', value: '+8.2%', contribution: 0.4 },
      { name: '新能源出力', value: '偏低', contribution: 0.3 },
      { name: '历史规律', value: '周中高峰', contribution: 0.3 }
    ],
    risk_level: 'MEDIUM',
    created_at: new Date().toISOString(),
    valid_until: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
  },
  {
    id: 'rec-002',
    province: '浙江',
    market_type: 'REAL_TIME',
    direction: 'SELL',
    confidence: 0.72,
    current_price: 488.15,
    target_price: 465.00,
    potential_profit_pct: 4.7,
    reason: '下午光伏出力高峰，实时电价预计下跌',
    factors: [
      { name: '光伏预测', value: '+15%', contribution: 0.5 },
      { name: '需求侧响应', value: '启动', contribution: 0.3 },
      { name: '市场情绪', value: '偏空', contribution: 0.2 }
    ],
    risk_level: 'LOW',
    created_at: new Date().toISOString(),
    valid_until: new Date(Date.now() + 4 * 60 * 60 * 1000).toISOString()
  },
  {
    id: 'rec-003',
    province: '山东',
    market_type: 'DAY_AHEAD',
    direction: 'HOLD',
    confidence: 0.58,
    current_price: 448.90,
    target_price: 450.00,
    potential_profit_pct: 0.2,
    reason: '市场波动较小，建议观望等待更好时机',
    factors: [
      { name: '供需平衡', value: '稳定', contribution: 0.4 },
      { name: '政策影响', value: '中性', contribution: 0.3 },
      { name: '季节因素', value: '平稳', contribution: 0.3 }
    ],
    risk_level: 'LOW',
    created_at: new Date().toISOString(),
    valid_until: new Date(Date.now() + 12 * 60 * 60 * 1000).toISOString()
  }
]

const AIRecommendation: React.FC<AIRecommendationProps> = ({
  onTrade,
  compact = false
}) => {
  const { token } = useToken()
  const [recommendations, setRecommendations] = useState<Recommendation[]>(mockRecommendations)
  const [loading, setLoading] = useState(false)

  const loadRecommendations = async () => {
    setLoading(true)
    try {
      const response = await api.get('/ai-advisor/recommendations', {
        params: { limit: compact ? 3 : 5 }
      })
      if (response.data.success && response.data.data.length > 0) {
        setRecommendations(response.data.data)
      } else {
        setRecommendations(mockRecommendations)
      }
    } catch (error) {
      console.error('加载交易建议失败，使用 Mock 数据:', error)
      setRecommendations(mockRecommendations)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadRecommendations()
    // 每5分钟刷新一次
    const interval = setInterval(loadRecommendations, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  const getDirectionIcon = (direction: string) => {
    switch (direction) {
      case 'BUY':
        return <ArrowUpOutlined style={{ color: token.colorError }} />
      case 'SELL':
        return <ArrowDownOutlined style={{ color: token.colorSuccess }} />
      default:
        return <MinusOutlined style={{ color: token.colorTextSecondary }} />
    }
  }

  const getDirectionTag = (direction: string) => {
    const config: Record<string, { color: string; text: string; icon: React.ReactNode }> = {
      BUY: { color: 'red', text: '买入', icon: <ArrowUpOutlined /> },
      SELL: { color: 'green', text: '卖出', icon: <ArrowDownOutlined /> },
      HOLD: { color: 'default', text: '观望', icon: <MinusOutlined /> }
    }
    const c = config[direction] || config.HOLD
    return <Tag color={c.color} icon={c.icon}>{c.text}</Tag>
  }

  const getRiskTag = (risk: string) => {
    const config: Record<string, { color: string; text: string }> = {
      LOW: { color: 'success', text: '低风险' },
      MEDIUM: { color: 'warning', text: '中风险' },
      HIGH: { color: 'error', text: '高风险' }
    }
    const c = config[risk] || { color: 'default', text: risk }
    return <Tag color={c.color}>{c.text}</Tag>
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.7) return token.colorSuccess
    if (confidence >= 0.5) return token.colorWarning
    return token.colorError
  }

  if (compact) {
    // 紧凑模式 - 用于仪表盘
    return (
      <Card
        title={
          <Space>
            <RocketOutlined style={{ color: token.colorPrimary }} />
            <span>AI 交易建议</span>
          </Space>
        }
        extra={
          <Button
            type="text"
            icon={<ReloadOutlined spin={loading} />}
            onClick={loadRecommendations}
            size="small"
          />
        }
        bodyStyle={{ padding: '12px 16px' }}
      >
        {recommendations.length === 0 && loading ? (
          <div style={{ textAlign: 'center', padding: 20 }}>
            <Spin />
          </div>
        ) : recommendations.length === 0 ? (
          <Empty description="暂无建议" image={Empty.PRESENTED_IMAGE_SIMPLE} />
        ) : (
          <List
            dataSource={recommendations}
            renderItem={(item) => (
              <List.Item style={{ padding: '8px 0' }}>
                <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                  <Space>
                    {getDirectionIcon(item.direction)}
                    <Text strong>{item.province}</Text>
                    {getDirectionTag(item.direction)}
                  </Space>
                  <Space>
                    <Text type="secondary">
                      置信度: {(item.confidence * 100).toFixed(0)}%
                    </Text>
                    {item.direction !== 'HOLD' && (
                      <Tag color={item.potential_profit_pct > 0 ? 'success' : 'error'}>
                        {item.potential_profit_pct > 0 ? '+' : ''}{item.potential_profit_pct}%
                      </Tag>
                    )}
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
    <Card
      title={
        <Space>
          <RocketOutlined style={{ color: token.colorPrimary }} />
          <span>AI 智能交易建议</span>
          <Badge count={recommendations.length} showZero color={token.colorPrimary} />
        </Space>
      }
      extra={
        <Button
          icon={<ReloadOutlined />}
          onClick={loadRecommendations}
          loading={loading}
        >
          刷新建议
        </Button>
      }
    >
      {loading ? (
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Spin size="large" tip="AI 正在分析市场..." />
        </div>
      ) : recommendations.length === 0 ? (
        <Empty description="暂无交易建议" />
      ) : (
        <List
          grid={{ gutter: 16, column: 2 }}
          dataSource={recommendations}
          renderItem={(item) => (
            <List.Item>
              <Card
                size="small"
                style={{
                  borderLeft: `4px solid ${
                    item.direction === 'BUY' 
                      ? token.colorError 
                      : item.direction === 'SELL' 
                        ? token.colorSuccess 
                        : token.colorBorder
                  }`
                }}
              >
                {/* 头部 */}
                <Row justify="space-between" align="middle">
                  <Col>
                    <Space>
                      <ThunderboltOutlined style={{ color: token.colorPrimary }} />
                      <Title level={5} style={{ margin: 0 }}>{item.province}</Title>
                      {getDirectionTag(item.direction)}
                    </Space>
                  </Col>
                  <Col>
                    {getRiskTag(item.risk_level)}
                  </Col>
                </Row>

                <Divider style={{ margin: '12px 0' }} />

                {/* 价格信息 */}
                <Row gutter={16}>
                  <Col span={8}>
                    <Text type="secondary">当前价格</Text>
                    <div>
                      <Text strong style={{ fontSize: 16 }}>
                        ¥{item.current_price.toFixed(2)}
                      </Text>
                    </div>
                  </Col>
                  <Col span={8}>
                    <Text type="secondary">目标价格</Text>
                    <div>
                      <Text strong style={{ fontSize: 16, color: token.colorPrimary }}>
                        ¥{item.target_price.toFixed(2)}
                      </Text>
                    </div>
                  </Col>
                  <Col span={8}>
                    <Text type="secondary">预期收益</Text>
                    <div>
                      <Text 
                        strong 
                        style={{ 
                          fontSize: 16, 
                          color: item.potential_profit_pct > 0 
                            ? token.colorSuccess 
                            : token.colorError 
                        }}
                      >
                        {item.potential_profit_pct > 0 ? '+' : ''}{item.potential_profit_pct}%
                      </Text>
                    </div>
                  </Col>
                </Row>

                <Divider style={{ margin: '12px 0' }} />

                {/* 置信度 */}
                <div style={{ marginBottom: 12 }}>
                  <Row justify="space-between" style={{ marginBottom: 4 }}>
                    <Text type="secondary">AI 置信度</Text>
                    <Text strong style={{ color: getConfidenceColor(item.confidence) }}>
                      {(item.confidence * 100).toFixed(0)}%
                    </Text>
                  </Row>
                  <Progress
                    percent={item.confidence * 100}
                    showInfo={false}
                    strokeColor={getConfidenceColor(item.confidence)}
                    size="small"
                  />
                </div>

                {/* 分析理由 */}
                <div style={{ 
                  background: token.colorBgTextHover, 
                  padding: '8px 12px', 
                  borderRadius: 6,
                  marginBottom: 12
                }}>
                  <Space size={4}>
                    <InfoCircleOutlined style={{ color: token.colorPrimary }} />
                    <Text type="secondary">{item.reason}</Text>
                  </Space>
                </div>

                {/* 影响因素 */}
                <div style={{ marginBottom: 12 }}>
                  <Text type="secondary" style={{ fontSize: 12, marginBottom: 4, display: 'block' }}>
                    影响因素
                  </Text>
                  <Space wrap>
                    {item.factors.map((factor, idx) => (
                      <Tooltip key={idx} title={`贡献度: ${(factor.contribution * 100).toFixed(0)}%`}>
                        <Tag>
                          {factor.name}: {factor.value}
                        </Tag>
                      </Tooltip>
                    ))}
                  </Space>
                </div>

                {/* 操作按钮 */}
                {onTrade && item.direction !== 'HOLD' && (
                  <Button 
                    type="primary" 
                    block
                    icon={<FireOutlined />}
                    onClick={() => onTrade(item)}
                  >
                    立即{item.direction === 'BUY' ? '买入' : '卖出'}
                  </Button>
                )}
              </Card>
            </List.Item>
          )}
        />
      )}
    </Card>
  )
}

export default AIRecommendation
