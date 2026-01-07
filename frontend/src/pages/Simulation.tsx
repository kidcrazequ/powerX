/**
 * PowerX 交易模拟/回测页面
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 策略回测和模拟交易功能
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Select,
  DatePicker,
  Typography,
  Space,
  Table,
  Tag,
  Button,
  Modal,
  Form,
  Input,
  InputNumber,
  Descriptions,
  Progress,
  Empty,
  message,
  Tabs,
  theme,
  Tooltip,
  Spin,
  Popconfirm
} from 'antd';
import {
  ExperimentOutlined,
  PlayCircleOutlined,
  LineChartOutlined,
  HistoryOutlined,
  RiseOutlined,
  FallOutlined,
  DeleteOutlined,
  EyeOutlined,
  ReloadOutlined,
  PlusOutlined,
  TrophyOutlined
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import dayjs from 'dayjs';

const { Title, Text, Paragraph } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;

// ============ 类型定义 ============

interface Strategy {
  name: string;
  description: string;
  params: Record<string, {
    type: string;
    default: any;
    description: string;
  }>;
}

interface BacktestSession {
  id: number;
  name: string;
  strategy_name: string;
  status: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  total_return: number | null;
  win_rate: number | null;
  created_at: string;
}

interface SessionDetail {
  id: number;
  name: string;
  description: string | null;
  strategy_name: string;
  strategy_params: Record<string, any> | null;
  start_date: string;
  end_date: string;
  initial_capital: number;
  status: string;
  progress: number;
  final_capital: number | null;
  total_return: number | null;
  annual_return: number | null;
  max_drawdown: number | null;
  sharpe_ratio: number | null;
  win_rate: number | null;
  total_trades: number | null;
  result_data: {
    equity_curve?: Array<{
      date: string;
      equity: number;
    }>;
    statistics?: Record<string, any>;
  } | null;
}

interface TradeRecord {
  id: number;
  trade_time: string;
  direction: string;
  price: number;
  quantity: number;
  amount: number;
  commission: number;
  profit: number | null;
  profit_rate: number | null;
  signal: string | null;
}

// ============ Mock 数据 ============

const MOCK_STRATEGIES: Record<string, Strategy> = {
  mean_reversion: {
    name: "均值回归",
    description: "当价格偏离均值一定幅度时进行反向交易",
    params: {
      window: { type: "int", default: 20, description: "均值计算窗口" },
      threshold: { type: "float", default: 2.0, description: "标准差倍数阈值" }
    }
  },
  momentum: {
    name: "动量策略",
    description: "跟随价格趋势进行交易",
    params: {
      fast_period: { type: "int", default: 5, description: "快速均线周期" },
      slow_period: { type: "int", default: 20, description: "慢速均线周期" }
    }
  },
  breakout: {
    name: "突破策略",
    description: "当价格突破区间时进行交易",
    params: {
      lookback: { type: "int", default: 20, description: "回顾周期" },
      multiplier: { type: "float", default: 1.5, description: "突破幅度倍数" }
    }
  },
  arbitrage: {
    name: "跨省套利",
    description: "利用省间价差进行套利交易",
    params: {
      spread_threshold: { type: "float", default: 30.0, description: "价差阈值 (元/MWh)" },
      max_position: { type: "float", default: 1000.0, description: "最大持仓 (MWh)" }
    }
  },
  peak_valley: {
    name: "峰谷套利",
    description: "低谷买入、高峰卖出",
    params: {
      buy_hours: { type: "list", default: [0, 1, 2, 3, 4, 5], description: "买入时段" },
      sell_hours: { type: "list", default: [18, 19, 20, 21], description: "卖出时段" }
    }
  }
};

const generateMockSessions = (): BacktestSession[] => {
  const strategies = Object.keys(MOCK_STRATEGIES);
  const statuses = ['COMPLETED', 'COMPLETED', 'COMPLETED', 'RUNNING', 'FAILED'];
  
  return Array.from({ length: 8 }, (_, i) => ({
    id: i + 1,
    name: `回测任务 ${i + 1}`,
    strategy_name: strategies[i % strategies.length],
    status: statuses[i % statuses.length],
    start_date: dayjs().subtract(30 + i * 10, 'day').format('YYYY-MM-DD'),
    end_date: dayjs().subtract(i * 5, 'day').format('YYYY-MM-DD'),
    initial_capital: 1000000,
    total_return: Math.random() * 0.3 - 0.05,
    win_rate: 0.4 + Math.random() * 0.3,
    created_at: dayjs().subtract(i, 'day').format('YYYY-MM-DD HH:mm:ss')
  }));
};

const generateMockEquityCurve = () => {
  const curve = [];
  let equity = 1000000;
  
  for (let i = 0; i < 60; i++) {
    const change = (Math.random() - 0.48) * 20000;
    equity = Math.max(equity + change, 800000);
    curve.push({
      date: dayjs().subtract(60 - i, 'day').format('YYYY-MM-DD'),
      equity: Math.round(equity)
    });
  }
  
  return curve;
};

const generateMockTrades = (): TradeRecord[] => {
  return Array.from({ length: 20 }, (_, i) => ({
    id: i + 1,
    trade_time: dayjs().subtract(30 - i, 'day').format('YYYY-MM-DD HH:mm:ss'),
    direction: i % 2 === 0 ? 'BUY' : 'SELL',
    price: 450 + Math.random() * 50,
    quantity: 100 + Math.random() * 200,
    amount: 50000 + Math.random() * 30000,
    commission: 50 + Math.random() * 30,
    profit: i % 2 === 1 ? (Math.random() - 0.3) * 5000 : null,
    profit_rate: i % 2 === 1 ? (Math.random() - 0.3) * 0.1 : null,
    signal: ['momentum_BUY', 'momentum_SELL', 'mean_reversion_BUY'][i % 3]
  }));
};

// ============ 组件 ============

const Simulation: React.FC = () => {
  const { token } = theme.useToken();
  
  const [sessions, setSessions] = useState<BacktestSession[]>([]);
  const [selectedSession, setSelectedSession] = useState<SessionDetail | null>(null);
  const [trades, setTrades] = useState<TradeRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  
  const [form] = Form.useForm();

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    setLoading(true);
    // 模拟 API 调用
    await new Promise(resolve => setTimeout(resolve, 500));
    setSessions(generateMockSessions());
    setLoading(false);
  };

  const handleCreateBacktest = async (values: any) => {
    setLoading(true);
    // 模拟 API 调用
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    message.success('回测任务已创建，正在后台执行');
    setCreateModalVisible(false);
    form.resetFields();
    loadSessions();
  };

  const handleViewDetail = async (session: BacktestSession) => {
    setLoading(true);
    // 模拟 API 调用
    await new Promise(resolve => setTimeout(resolve, 500));
    
    setSelectedSession({
      ...session,
      description: '测试回测任务',
      strategy_params: { window: 20, threshold: 2.0 },
      progress: session.status === 'COMPLETED' ? 100 : 65,
      final_capital: session.initial_capital * (1 + (session.total_return || 0)),
      annual_return: (session.total_return || 0) * 4,
      max_drawdown: Math.random() * 0.15,
      sharpe_ratio: 0.8 + Math.random() * 1.2,
      total_trades: 20 + Math.floor(Math.random() * 30),
      result_data: {
        equity_curve: generateMockEquityCurve()
      }
    });
    
    setTrades(generateMockTrades());
    setDetailModalVisible(true);
    setLoading(false);
  };

  const handleDeleteSession = async (id: number) => {
    setLoading(true);
    await new Promise(resolve => setTimeout(resolve, 500));
    setSessions(sessions.filter(s => s.id !== id));
    message.success('回测会话已删除');
    setLoading(false);
  };

  // 状态标签
  const StatusTag: React.FC<{ status: string }> = ({ status }) => {
    const configs: Record<string, { color: string; text: string }> = {
      PENDING: { color: 'default', text: '等待中' },
      RUNNING: { color: 'processing', text: '执行中' },
      COMPLETED: { color: 'success', text: '已完成' },
      FAILED: { color: 'error', text: '失败' },
      CANCELLED: { color: 'warning', text: '已取消' }
    };
    const config = configs[status] || configs.PENDING;
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  // 权益曲线图配置
  const getEquityChartOption = () => {
    if (!selectedSession?.result_data?.equity_curve) return {};
    
    const curve = selectedSession.result_data.equity_curve;
    
    return {
      tooltip: {
        trigger: 'axis',
        formatter: (params: any) => {
          const data = params[0];
          return `${data.name}<br/>权益: ¥${data.value.toLocaleString()}`;
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: curve.map(d => d.date),
        axisLine: { lineStyle: { color: token.colorBorder } },
        axisLabel: { color: token.colorTextSecondary }
      },
      yAxis: {
        type: 'value',
        name: '账户权益',
        axisLine: { lineStyle: { color: token.colorBorder } },
        axisLabel: {
          color: token.colorTextSecondary,
          formatter: (value: number) => `¥${(value / 10000).toFixed(0)}万`
        },
        splitLine: { lineStyle: { color: token.colorBorderSecondary, type: 'dashed' } }
      },
      series: [{
        type: 'line',
        data: curve.map(d => d.equity),
        smooth: true,
        lineStyle: {
          color: curve[curve.length - 1].equity >= selectedSession.initial_capital
            ? token.colorSuccess
            : token.colorError,
          width: 2
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(82, 196, 26, 0.3)' },
              { offset: 1, color: 'rgba(82, 196, 26, 0.05)' }
            ]
          }
        }
      }]
    };
  };

  // 会话列表列定义
  const columns = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: BacktestSession) => (
        <Space direction="vertical" size={0}>
          <Text strong>{text}</Text>
          <Text type="secondary" style={{ fontSize: 12 }}>
            {MOCK_STRATEGIES[record.strategy_name]?.name || record.strategy_name}
          </Text>
        </Space>
      )
    },
    {
      title: '时间范围',
      key: 'dateRange',
      render: (_: any, record: BacktestSession) => (
        <Text style={{ fontSize: 12 }}>
          {record.start_date} ~ {record.end_date}
        </Text>
      )
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => <StatusTag status={status} />
    },
    {
      title: '收益率',
      dataIndex: 'total_return',
      key: 'total_return',
      render: (value: number | null, record: BacktestSession) => {
        if (record.status !== 'COMPLETED' || value === null) return '-';
        return (
          <Text style={{ color: value >= 0 ? token.colorSuccess : token.colorError }}>
            {value >= 0 ? <RiseOutlined /> : <FallOutlined />}
            {' '}{(value * 100).toFixed(2)}%
          </Text>
        );
      }
    },
    {
      title: '胜率',
      dataIndex: 'win_rate',
      key: 'win_rate',
      render: (value: number | null, record: BacktestSession) => {
        if (record.status !== 'COMPLETED' || value === null) return '-';
        return <Text>{(value * 100).toFixed(1)}%</Text>;
      }
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text: string) => <Text style={{ fontSize: 12 }}>{text}</Text>
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: BacktestSession) => (
        <Space>
          <Tooltip title="查看详情">
            <Button
              type="link"
              icon={<EyeOutlined />}
              onClick={() => handleViewDetail(record)}
            />
          </Tooltip>
          <Popconfirm
            title="确定要删除这个回测会话吗？"
            onConfirm={() => handleDeleteSession(record.id)}
          >
            <Tooltip title="删除">
              <Button type="link" danger icon={<DeleteOutlined />} />
            </Tooltip>
          </Popconfirm>
        </Space>
      )
    }
  ];

  // 交易记录列定义
  const tradeColumns = [
    {
      title: '时间',
      dataIndex: 'trade_time',
      key: 'trade_time',
      render: (text: string) => dayjs(text).format('MM-DD HH:mm')
    },
    {
      title: '方向',
      dataIndex: 'direction',
      key: 'direction',
      render: (text: string) => (
        <Tag color={text === 'BUY' ? 'green' : 'red'}>
          {text === 'BUY' ? '买入' : '卖出'}
        </Tag>
      )
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      render: (value: number) => `¥${value.toFixed(2)}`
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      render: (value: number) => `${value.toFixed(0)} MWh`
    },
    {
      title: '金额',
      dataIndex: 'amount',
      key: 'amount',
      render: (value: number) => `¥${value.toLocaleString()}`
    },
    {
      title: '盈亏',
      dataIndex: 'profit',
      key: 'profit',
      render: (value: number | null) => {
        if (value === null) return '-';
        return (
          <Text style={{ color: value >= 0 ? token.colorSuccess : token.colorError }}>
            {value >= 0 ? '+' : ''}{value.toFixed(2)}
          </Text>
        );
      }
    }
  ];

  return (
    <div style={{ padding: 24 }}>
      {/* 页面标题 */}
      <div style={{ marginBottom: 24 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Title level={4} style={{ margin: 0 }}>
              <ExperimentOutlined style={{ marginRight: 8 }} />
              交易模拟与回测
            </Title>
            <Text type="secondary">策略回测验证和模拟交易</Text>
          </Col>
          <Col>
            <Space>
              <Button icon={<ReloadOutlined />} onClick={loadSessions}>
                刷新
              </Button>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setCreateModalVisible(true)}
              >
                新建回测
              </Button>
            </Space>
          </Col>
        </Row>
      </div>

      {/* 策略卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        {Object.entries(MOCK_STRATEGIES).map(([key, strategy]) => (
          <Col xs={24} sm={12} md={8} lg={4} key={key}>
            <Card
              hoverable
              size="small"
              onClick={() => {
                form.setFieldsValue({ strategy_name: key });
                setCreateModalVisible(true);
              }}
            >
              <Space direction="vertical" size={4} style={{ width: '100%' }}>
                <Text strong>{strategy.name}</Text>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {strategy.description.slice(0, 20)}...
                </Text>
              </Space>
            </Card>
          </Col>
        ))}
      </Row>

      {/* 回测历史列表 */}
      <Card title="回测历史" extra={<HistoryOutlined />}>
        <Table
          columns={columns}
          dataSource={sessions}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* 创建回测 Modal */}
      <Modal
        title="新建回测任务"
        open={createModalVisible}
        onCancel={() => setCreateModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateBacktest}
          initialValues={{
            initial_capital: 1000000,
            dateRange: [dayjs().subtract(30, 'day'), dayjs()]
          }}
        >
          <Form.Item
            name="name"
            label="回测名称"
            rules={[{ required: true, message: '请输入回测名称' }]}
          >
            <Input placeholder="例如：动量策略30日回测" />
          </Form.Item>
          
          <Form.Item
            name="strategy_name"
            label="选择策略"
            rules={[{ required: true, message: '请选择策略' }]}
          >
            <Select placeholder="选择交易策略">
              {Object.entries(MOCK_STRATEGIES).map(([key, strategy]) => (
                <Option key={key} value={key}>
                  <Space>
                    <Text strong>{strategy.name}</Text>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {strategy.description}
                    </Text>
                  </Space>
                </Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item
            name="dateRange"
            label="回测时间范围"
            rules={[{ required: true, message: '请选择时间范围' }]}
          >
            <RangePicker style={{ width: '100%' }} />
          </Form.Item>
          
          <Form.Item
            name="initial_capital"
            label="初始资金"
            rules={[{ required: true, message: '请输入初始资金' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              min={10000}
              max={100000000}
              step={100000}
              formatter={value => `¥ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
              parser={value => value!.replace(/¥\s?|(,*)/g, '')}
            />
          </Form.Item>
          
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={3} placeholder="可选：回测任务描述" />
          </Form.Item>
          
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={loading} icon={<PlayCircleOutlined />}>
                开始回测
              </Button>
              <Button onClick={() => setCreateModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 回测详情 Modal */}
      <Modal
        title={
          <Space>
            <TrophyOutlined />
            回测结果详情
          </Space>
        }
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
        width={1000}
      >
        {selectedSession && (
          <Spin spinning={loading}>
            {/* 统计指标 */}
            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col span={6}>
                <Statistic
                  title="最终权益"
                  value={selectedSession.final_capital}
                  precision={0}
                  prefix="¥"
                  valueStyle={{ color: token.colorPrimary }}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="总收益率"
                  value={(selectedSession.total_return || 0) * 100}
                  precision={2}
                  suffix="%"
                  valueStyle={{
                    color: (selectedSession.total_return || 0) >= 0
                      ? token.colorSuccess
                      : token.colorError
                  }}
                  prefix={(selectedSession.total_return || 0) >= 0 ? <RiseOutlined /> : <FallOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="最大回撤"
                  value={(selectedSession.max_drawdown || 0) * 100}
                  precision={2}
                  suffix="%"
                  valueStyle={{ color: token.colorWarning }}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="夏普比率"
                  value={selectedSession.sharpe_ratio}
                  precision={2}
                />
              </Col>
            </Row>
            
            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col span={6}>
                <Statistic title="胜率" value={(selectedSession.win_rate || 0) * 100} precision={1} suffix="%" />
              </Col>
              <Col span={6}>
                <Statistic title="总交易次数" value={selectedSession.total_trades || 0} />
              </Col>
              <Col span={6}>
                <Statistic title="年化收益率" value={(selectedSession.annual_return || 0) * 100} precision={2} suffix="%" />
              </Col>
              <Col span={6}>
                <Statistic title="初始资金" value={selectedSession.initial_capital} precision={0} prefix="¥" />
              </Col>
            </Row>

            <Tabs
              items={[
                {
                  key: 'equity',
                  label: '权益曲线',
                  children: (
                    <ReactECharts option={getEquityChartOption()} style={{ height: 300 }} />
                  )
                },
                {
                  key: 'trades',
                  label: '交易记录',
                  children: (
                    <Table
                      columns={tradeColumns}
                      dataSource={trades}
                      rowKey="id"
                      size="small"
                      pagination={{ pageSize: 10 }}
                    />
                  )
                },
                {
                  key: 'info',
                  label: '基本信息',
                  children: (
                    <Descriptions bordered column={2}>
                      <Descriptions.Item label="回测名称">{selectedSession.name}</Descriptions.Item>
                      <Descriptions.Item label="策略">
                        {MOCK_STRATEGIES[selectedSession.strategy_name]?.name || selectedSession.strategy_name}
                      </Descriptions.Item>
                      <Descriptions.Item label="开始日期">{selectedSession.start_date}</Descriptions.Item>
                      <Descriptions.Item label="结束日期">{selectedSession.end_date}</Descriptions.Item>
                      <Descriptions.Item label="描述" span={2}>
                        {selectedSession.description || '无'}
                      </Descriptions.Item>
                    </Descriptions>
                  )
                }
              ]}
            />
          </Spin>
        )}
      </Modal>
    </div>
  );
};

export default Simulation;
