/**
 * PowerX 自然语言命令面板
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 支持通过自然语言进行交易操作
 */

import React, { useState, useRef, useEffect } from 'react'
import {
  Card,
  Input,
  Button,
  List,
  Tag,
  Space,
  Typography,
  Modal,
  Descriptions,
  message,
  Spin,
  Empty,
  Tooltip,
  theme
} from 'antd'
import {
  SendOutlined,
  ThunderboltOutlined,
  HistoryOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  RobotOutlined,
  ClearOutlined,
  BulbOutlined
} from '@ant-design/icons'
import dayjs from 'dayjs'

const { useToken } = theme
const { Text, Title } = Typography
const { TextArea } = Input

interface CommandResult {
  id: string
  command: string
  timestamp: string
  success: boolean
  action?: string
  result?: Record<string, any>
  error?: string
}

interface ParsedIntent {
  action: string
  province?: string
  quantity?: number
  price?: number
  direction?: string
  message: string
}

interface NLCommandPanelProps {
  onExecute?: (intent: ParsedIntent) => Promise<boolean>
}

const NLCommandPanel: React.FC<NLCommandPanelProps> = ({ onExecute }) => {
  const { token } = useToken()
  const [command, setCommand] = useState('')
  const [processing, setProcessing] = useState(false)
  const [commandHistory, setCommandHistory] = useState<CommandResult[]>([])
  const [confirmModalVisible, setConfirmModalVisible] = useState(false)
  const [pendingIntent, setPendingIntent] = useState<ParsedIntent | null>(null)
  const inputRef = useRef<any>(null)

  // 示例命令
  const exampleCommands = [
    '买入100MWh广东现货',
    '查询今日成交记录',
    '设置价格提醒，当广东电价超过500时通知我',
    '查看广东市场分析',
    '创建条件单：广东价格低于400时买入50MWh'
  ]

  // 解析自然语言命令
  const parseCommand = (text: string): ParsedIntent | null => {
    const normalized = text.trim().toLowerCase()
    
    // 买入/卖出命令
    const tradeMatch = normalized.match(/(买入|卖出)(\d+)?\s*(mwh|兆瓦时)?\s*(广东|浙江|江苏|山东|四川)?(现货|日前|实时)?/)
    if (tradeMatch) {
      return {
        action: 'TRADE',
        direction: tradeMatch[1] === '买入' ? 'BUY' : 'SELL',
        quantity: tradeMatch[2] ? parseInt(tradeMatch[2]) : 100,
        province: tradeMatch[4] || '广东',
        message: `${tradeMatch[1]} ${tradeMatch[2] || 100} MWh ${tradeMatch[4] || '广东'} ${tradeMatch[5] || '现货'}`
      }
    }
    
    // 查询命令
    if (normalized.includes('查询') || normalized.includes('查看')) {
      if (normalized.includes('成交') || normalized.includes('记录')) {
        return {
          action: 'QUERY_TRADES',
          message: '查询交易记录'
        }
      }
      if (normalized.includes('分析') || normalized.includes('市场')) {
        const provinceMatch = normalized.match(/(广东|浙江|江苏|山东|四川)/)
        return {
          action: 'MARKET_ANALYSIS',
          province: provinceMatch ? provinceMatch[1] : '广东',
          message: `查看${provinceMatch ? provinceMatch[1] : ''}市场分析`
        }
      }
    }
    
    // 设置提醒
    if (normalized.includes('提醒') || normalized.includes('通知') || normalized.includes('预警')) {
      const priceMatch = normalized.match(/(\d+)/)
      const provinceMatch = normalized.match(/(广东|浙江|江苏|山东|四川)/)
      return {
        action: 'SET_ALERT',
        province: provinceMatch ? provinceMatch[1] : '广东',
        price: priceMatch ? parseInt(priceMatch[1]) : 500,
        message: `设置${provinceMatch ? provinceMatch[1] : ''}价格提醒: ${priceMatch ? priceMatch[1] : 500} 元/MWh`
      }
    }
    
    // 条件单
    if (normalized.includes('条件单')) {
      return {
        action: 'CREATE_CONDITIONAL',
        message: '创建条件单'
      }
    }
    
    return null
  }

  // 处理命令
  const handleSubmit = async () => {
    if (!command.trim()) return
    
    setProcessing(true)
    
    try {
      const intent = parseCommand(command)
      
      if (!intent) {
        const result: CommandResult = {
          id: Date.now().toString(),
          command: command,
          timestamp: new Date().toISOString(),
          success: false,
          error: '无法识别命令，请尝试其他表达方式'
        }
        setCommandHistory(prev => [result, ...prev])
        message.warning('无法识别命令')
        setCommand('')
        setProcessing(false)
        return
      }
      
      // 如果是交易命令，需要确认
      if (intent.action === 'TRADE') {
        setPendingIntent(intent)
        setConfirmModalVisible(true)
        setProcessing(false)
        return
      }
      
      // 其他命令直接执行
      await executeCommand(intent)
      
    } catch (error) {
      message.error('命令执行失败')
    } finally {
      setCommand('')
      setProcessing(false)
    }
  }

  // 执行命令
  const executeCommand = async (intent: ParsedIntent) => {
    const result: CommandResult = {
      id: Date.now().toString(),
      command: command || intent.message,
      timestamp: new Date().toISOString(),
      success: true,
      action: intent.action,
      result: {
        ...intent,
        executed_at: new Date().toISOString()
      }
    }
    
    // 模拟执行
    if (onExecute) {
      const success = await onExecute(intent)
      result.success = success
      if (!success) {
        result.error = '执行失败'
      }
    }
    
    setCommandHistory(prev => [result, ...prev])
    message.success(`命令已执行: ${intent.message}`)
  }

  // 确认交易
  const handleConfirmTrade = async () => {
    if (!pendingIntent) return
    
    setConfirmModalVisible(false)
    setProcessing(true)
    
    try {
      await executeCommand(pendingIntent)
    } finally {
      setPendingIntent(null)
      setCommand('')
      setProcessing(false)
    }
  }

  // 使用示例命令
  const handleUseExample = (example: string) => {
    setCommand(example)
    inputRef.current?.focus()
  }

  // 清空历史
  const handleClearHistory = () => {
    setCommandHistory([])
  }

  return (
    <>
      <Card
        title={
          <Space>
            <RobotOutlined style={{ color: token.colorPrimary }} />
            <span>自然语言交易</span>
          </Space>
        }
        extra={
          commandHistory.length > 0 && (
            <Tooltip title="清空历史">
              <Button
                type="text"
                icon={<ClearOutlined />}
                onClick={handleClearHistory}
                size="small"
              />
            </Tooltip>
          )
        }
      >
        {/* 命令输入区 */}
        <div style={{ marginBottom: 16 }}>
          <Space.Compact style={{ width: '100%' }}>
            <TextArea
              ref={inputRef}
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              placeholder="输入自然语言命令，例如：买入100MWh广东现货"
              autoSize={{ minRows: 2, maxRows: 4 }}
              onPressEnter={(e) => {
                if (!e.shiftKey) {
                  e.preventDefault()
                  handleSubmit()
                }
              }}
              disabled={processing}
            />
          </Space.Compact>
          <div style={{ marginTop: 8, display: 'flex', justifyContent: 'space-between' }}>
            <Text type="secondary" style={{ fontSize: 12 }}>
              按 Enter 发送，Shift + Enter 换行
            </Text>
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={handleSubmit}
              loading={processing}
            >
              发送
            </Button>
          </div>
        </div>

        {/* 示例命令 */}
        <div style={{ 
          background: token.colorBgTextHover, 
          padding: 12, 
          borderRadius: 8,
          marginBottom: 16
        }}>
          <Space size={4} style={{ marginBottom: 8 }}>
            <BulbOutlined style={{ color: token.colorWarning }} />
            <Text strong>试试这些命令:</Text>
          </Space>
          <div>
            {exampleCommands.map((example, index) => (
              <Tag
                key={index}
                style={{ marginBottom: 4, cursor: 'pointer' }}
                onClick={() => handleUseExample(example)}
              >
                {example}
              </Tag>
            ))}
          </div>
        </div>

        {/* 命令历史 */}
        <div>
          <Space style={{ marginBottom: 8 }}>
            <HistoryOutlined />
            <Text strong>命令历史</Text>
          </Space>
          
          {commandHistory.length === 0 ? (
            <Empty 
              description="暂无命令记录" 
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            />
          ) : (
            <List
              dataSource={commandHistory.slice(0, 10)}
              renderItem={(item) => (
                <List.Item style={{ padding: '8px 0' }}>
                  <Space direction="vertical" style={{ width: '100%' }} size={4}>
                    <Space style={{ justifyContent: 'space-between', width: '100%' }}>
                      <Space>
                        {item.success ? (
                          <CheckCircleOutlined style={{ color: token.colorSuccess }} />
                        ) : (
                          <CloseCircleOutlined style={{ color: token.colorError }} />
                        )}
                        <Text>{item.command}</Text>
                      </Space>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {dayjs(item.timestamp).format('HH:mm:ss')}
                      </Text>
                    </Space>
                    {item.action && (
                      <Tag color="blue">{item.action}</Tag>
                    )}
                    {item.error && (
                      <Text type="danger" style={{ fontSize: 12 }}>
                        {item.error}
                      </Text>
                    )}
                  </Space>
                </List.Item>
              )}
            />
          )}
        </div>
      </Card>

      {/* 交易确认弹窗 */}
      <Modal
        title={
          <Space>
            <ThunderboltOutlined style={{ color: token.colorWarning }} />
            <span>确认交易</span>
          </Space>
        }
        open={confirmModalVisible}
        onCancel={() => {
          setConfirmModalVisible(false)
          setPendingIntent(null)
        }}
        onOk={handleConfirmTrade}
        okText="确认执行"
        cancelText="取消"
        okButtonProps={{ danger: pendingIntent?.direction === 'SELL' }}
      >
        {pendingIntent && (
          <Descriptions bordered column={1}>
            <Descriptions.Item label="操作类型">
              <Tag color={pendingIntent.direction === 'BUY' ? 'red' : 'green'}>
                {pendingIntent.direction === 'BUY' ? '买入' : '卖出'}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="省份">
              {pendingIntent.province}
            </Descriptions.Item>
            <Descriptions.Item label="数量">
              {pendingIntent.quantity} MWh
            </Descriptions.Item>
            <Descriptions.Item label="价格类型">
              市价单
            </Descriptions.Item>
          </Descriptions>
        )}
        <div style={{ 
          marginTop: 16, 
          padding: 12, 
          background: token.colorWarningBg,
          borderRadius: 8
        }}>
          <Text type="warning">
            请确认交易信息无误后再执行，交易执行后无法撤销。
          </Text>
        </div>
      </Modal>
    </>
  )
}

export default NLCommandPanel
