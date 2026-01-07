/**
 * PowerX 现货交易页面 - 现代深色版
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 日前/日内现货交易功能
 */

import React, { useState } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Form, 
  Input, 
  Select, 
  Button, 
  Table, 
  Tag, 
  Space,
  Statistic,
  Typography,
  Radio,
  InputNumber,
  Modal,
  message,
  Tabs,
  Divider,
  Alert,
  theme,
  Tooltip
} from 'antd';
import { 
  ThunderboltOutlined,
  ShoppingCartOutlined,
  LineChartOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  HistoryOutlined,
  RobotOutlined,
  SafetyCertificateOutlined
} from '@ant-design/icons';
import { PageContainer, ProCard, StatisticCard } from '@ant-design/pro-components';
import ReactECharts from 'echarts-for-react';
import { useSettingsStore } from '../stores/settingsStore';

const { Text, Title } = Typography;
const { Option } = Select;

// 模拟订单数据
const mockOrders = [
  { 
    id: 'SPT20260107001', 
    time: '2026-01-07 10:00',
    marketType: 'DAY_AHEAD',
    direction: 'BUY',
    price: 485.00,
    quantity: 100,
    status: 'FILLED',
    filledPrice: 482.50,
    filledQty: 100
  },
  { 
    id: 'SPT20260107002', 
    time: '2026-01-07 10:15',
    marketType: 'DAY_AHEAD',
    direction: 'BUY',
    price: 490.00,
    quantity: 50,
    status: 'PARTIAL',
    filledPrice: 488.00,
    filledQty: 30
  },
  { 
    id: 'SPT20260107003', 
    time: '2026-01-07 10:30',
    marketType: 'INTRADAY',
    direction: 'SELL',
    price: 495.00,
    quantity: 80,
    status: 'PENDING',
    filledPrice: null,
    filledQty: 0
  }
];

// 模拟实时行情
const mockQuotes = [
  { hour: '00:00', dayAhead: 445, intraday: 448, volume: 1250 },
  { hour: '04:00', dayAhead: 428, intraday: 432, volume: 980 },
  { hour: '08:00', dayAhead: 498, intraday: 502, volume: 2100 },
  { hour: '12:00', dayAhead: 512, intraday: 515, volume: 2450 },
  { hour: '16:00', dayAhead: 525, intraday: 528, volume: 2680 },
  { hour: '20:00', dayAhead: 495, intraday: 498, volume: 2150 }
];

// 价格走势图配置
const getPriceChartOption = (token: any, themeMode: string) => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'cross' },
    backgroundColor: themeMode === 'dark' ? 'rgba(20, 20, 20, 0.9)' : 'rgba(255, 255, 255, 0.9)',
    borderColor: token.colorBorderSecondary,
    textStyle: { color: token.colorText }
  },
  legend: {
    data: ['日前价格', '实时价格'],
    top: 0,
    textStyle: { color: token.colorTextSecondary }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: '15%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: mockQuotes.map(q => q.hour),
    axisLabel: { color: token.colorTextDescription },
    axisLine: { lineStyle: { color: themeMode === 'dark' ? token.colorBorderSecondary : 'rgba(0,0,0,0.15)' } }
  },
  yAxis: [
    {
      type: 'value',
      name: '元/MWh',
      min: 400,
      max: 550,
      axisLabel: { color: token.colorTextDescription },
      nameTextStyle: { color: token.colorTextDescription },
      axisLine: { show: true, lineStyle: { color: themeMode === 'dark' ? token.colorBorderSecondary : 'rgba(0,0,0,0.15)' } },
      splitLine: { lineStyle: { color: themeMode === 'dark' ? token.colorBorderSecondary : 'rgba(0,0,0,0.06)', type: 'dashed' } }
    }
  ],
  series: [
    {
      name: '日前价格',
      type: 'line',
      smooth: true,
      data: mockQuotes.map(q => q.dayAhead),
      lineStyle: { color: token.colorPrimary, width: 2 },
      itemStyle: { color: token.colorPrimary },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: `${token.colorPrimary}20` },
            { offset: 1, color: `${token.colorPrimary}00` }
          ]
        }
      }
    },
    {
      name: '实时价格',
      type: 'line',
      smooth: true,
      data: mockQuotes.map(q => q.intraday),
      lineStyle: { color: token.colorSuccess, width: 2, type: 'dashed' },
      itemStyle: { color: token.colorSuccess }
    }
  ]
});

const SpotTrading: React.FC = () => {
  const [form] = Form.useForm();
  const [orderModalVisible, setOrderModalVisible] = useState(false);
  const [selectedProvince, setSelectedProvince] = useState('广东');
  const [marketType, setMarketType] = useState('DAY_AHEAD');
  const { token } = theme.useToken();
  const { themeMode } = useSettingsStore();

  // 订单表格列
  const orderColumns = [
    { 
      title: '订单编号', 
      dataIndex: 'id', 
      key: 'id',
      render: (text: string) => <Text copyable className="data-font" style={{ fontSize: 13 }}>{text}</Text>
    },
    { 
      title: '申报时间', 
      dataIndex: 'time', 
      key: 'time',
      render: (text: string) => <span className="data-font" style={{ fontSize: 13, color: token.colorTextSecondary }}>{text}</span>
    },
    { 
      title: '交易品种', 
      dataIndex: 'marketType', 
      key: 'marketType',
      render: (type: string) => (
        <Tag color={type === 'DAY_AHEAD' ? 'blue' : 'purple'} bordered={false}>
          {type === 'DAY_AHEAD' ? '日前现货' : '日内现货'}
        </Tag>
      )
    },
    { 
      title: '方向', 
      dataIndex: 'direction', 
      key: 'direction',
      render: (dir: string) => (
        <Tag color={dir === 'BUY' ? 'green' : 'red'} bordered={false}>
          {dir === 'BUY' ? '买入' : '卖出'}
        </Tag>
      )
    },
    { 
      title: '价格(元)', 
      dataIndex: 'price', 
      key: 'price',
      render: (val: number) => <span className="data-font">{val.toFixed(2)}</span>
    },
    { 
      title: '数量(MWh)', 
      dataIndex: 'quantity', 
      key: 'quantity',
      render: (val: number) => <span className="data-font">{val.toLocaleString()}</span>
    },
    { 
      title: '成交价', 
      dataIndex: 'filledPrice', 
      key: 'filledPrice',
      render: (val: number | null) => val ? <span className="data-font" style={{ color: token.colorSuccess }}>{val.toFixed(2)}</span> : <Text type="secondary">-</Text>
    },
    { 
      title: '成交量', 
      dataIndex: 'filledQty', 
      key: 'filledQty',
      render: (val: number) => <span className="data-font" style={{ fontWeight: 600 }}>{val.toLocaleString()}</span>
    },
    { 
      title: '状态', 
      dataIndex: 'status', 
      key: 'status',
      render: (status: string) => {
        const config: Record<string, { color: string; icon: React.ReactNode; text: string }> = {
          FILLED: { color: 'success', icon: <CheckCircleOutlined />, text: '全部成交' },
          PARTIAL: { color: 'warning', icon: <ClockCircleOutlined />, text: '部分成交' },
          PENDING: { color: 'processing', icon: <ClockCircleOutlined />, text: '待成交' }
        };
        const cfg = config[status];
        return <Tag icon={cfg.icon} color={cfg.color} bordered={false}>{cfg.text}</Tag>;
      }
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Space size="middle">
          {record.status === 'PENDING' && (
            <Button type="text" danger size="small">撤销</Button>
          )}
          <Button type="text" size="small" style={{ color: token.colorPrimary }}>详情</Button>
        </Space>
      )
    }
  ];

  // 提交订单
  const handleSubmitOrder = (values: any) => {
    message.loading('订单正提交至交易网关...', 1);
    setTimeout(() => {
      message.success('现货申报订单提交成功！');
      setOrderModalVisible(false);
      form.resetFields();
    }, 1200);
  };

  return (
    <PageContainer
      header={{
        title: '现货交易终端',
        subTitle: '日前/日内现货市场快速报单与订单执行监控',
        extra: [
          <Button key="history" icon={<HistoryOutlined />}>交易日志</Button>,
          <Button key="new" type="primary" icon={<ThunderboltOutlined />} onClick={() => setOrderModalVisible(true)}>
            新报单
          </Button>
        ]
      }}
    >
      {/* 市场概览 */}
      <Row gutter={[20, 20]}>
        <Col xs={24} sm={12} lg={6}>
          <StatisticCard
            className="hover-card"
            statistic={{
              title: <Text type="secondary" style={{ fontSize: 12 }}>日前成交均价 (DA)</Text>,
              value: 485.32,
              suffix: <span style={{ fontSize: 12, marginLeft: 4 }}>元/MWh</span>,
              description: <Tag color="green" bordered={false} style={{ borderRadius: 4 }}>+2.5%</Tag>
            }}
            style={{ borderRadius: 12, border: 'none' }}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatisticCard
            className="hover-card"
            statistic={{
              title: <Text type="secondary" style={{ fontSize: 12 }}>实时成交均价 (RT)</Text>,
              value: 488.15,
              suffix: <span style={{ fontSize: 12, marginLeft: 4 }}>元/MWh</span>,
              description: <Tag color="red" bordered={false} style={{ borderRadius: 4 }}>+0.6%</Tag>
            }}
            style={{ borderRadius: 12, border: 'none' }}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatisticCard
            className="hover-card"
            statistic={{
              title: <Text type="secondary" style={{ fontSize: 12 }}>今日累计执行</Text>,
              value: 12580,
              suffix: <span style={{ fontSize: 12, marginLeft: 4 }}>MWh</span>,
              icon: <div style={{ width: 32, height: 32, borderRadius: 8, background: 'rgba(22, 119, 255, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <CheckCircleOutlined style={{ color: token.colorPrimary }} />
              </div>
            }}
            style={{ borderRadius: 12, border: 'none' }}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatisticCard
            className="hover-card"
            statistic={{
              title: <Text type="secondary" style={{ fontSize: 12 }}>风险敞口占比</Text>,
              value: 15.8,
              suffix: <span style={{ fontSize: 12, marginLeft: 4 }}>%</span>,
              description: <Tag color="blue" bordered={false} style={{ borderRadius: 4 }}>安全范围内</Tag>
            }}
            style={{ borderRadius: 12, border: 'none' }}
          />
        </Col>
      </Row>

      <Row gutter={[20, 20]} style={{ marginTop: 20 }}>
        {/* 行情图表 */}
        <Col xs={24} lg={16}>
          <Card
            className="hover-card"
            title={
              <Space>
                <LineChartOutlined style={{ color: token.colorPrimary }} />
                <span>{selectedProvince}省现货市场价差监测 (DA vs RT)</span>
              </Space>
            }
            extra={
              <Select 
                value={selectedProvince} 
                onChange={setSelectedProvince} 
                style={{ width: 100 }}
                variant="borderless"
              >
                <Option value="广东">广东市场</Option>
                <Option value="浙江">浙江市场</Option>
                <Option value="山东">山东市场</Option>
              </Select>
            }
            style={{ borderRadius: 12, border: 'none' }}
          >
            <ReactECharts 
              key={themeMode}
              option={getPriceChartOption(token, themeMode)} 
              style={{ height: 420 }} 
              theme={themeMode} 
            />
          </Card>
        </Col>

        {/* 快速下单 */}
        <Col xs={24} lg={8}>
          <Card
            className="hover-card"
            title={
              <Space>
                <ShoppingCartOutlined style={{ color: '#722ed1' }} />
                <span>现货委单执行柜台</span>
              </Space>
            }
            style={{ borderRadius: 12, border: 'none' }}
          >
            <div style={{ 
              marginBottom: 20, padding: '12px 16px', background: `${token.colorPrimary}10`, 
              borderRadius: 8, border: `1px solid ${token.colorPrimary}20`, display: 'flex', alignItems: 'center'
            }}>
              <RobotOutlined style={{ color: token.colorPrimary, marginRight: 12, fontSize: 18 }} />
              <Text style={{ fontSize: 13 }}>
                AI 交易建议: 当前 RT 价格低于预期均值，建议在 <Text strong>485.00</Text> 以下适当补入现货头寸。
              </Text>
            </div>

            <Form layout="vertical" form={form} onFinish={handleSubmitOrder} requiredMark={false}>
              <Row gutter={12}>
                <Col span={12}>
                  <Form.Item label={<Text type="secondary" style={{ fontSize: 12 }}>申报品种</Text>} name="marketType" initialValue="DAY_AHEAD">
                    <Select variant="filled" style={{ borderRadius: 6 }}>
                      <Option value="DAY_AHEAD">日前现货</Option>
                      <Option value="INTRADAY">日内现货</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item label={<Text type="secondary" style={{ fontSize: 12 }}>交易方向</Text>} name="direction" initialValue="BUY">
                    <Radio.Group block variant="filled" style={{ width: '100%' }}>
                      <Radio.Button value="BUY" style={{ width: '50%', textAlign: 'center' }}>买入</Radio.Button>
                      <Radio.Button value="SELL" style={{ width: '50%', textAlign: 'center' }}>卖出</Radio.Button>
                    </Radio.Group>
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item 
                label={<Text type="secondary" style={{ fontSize: 12 }}>申报价格 (元/MWh)</Text>} 
                name="price" 
                rules={[{ required: true, message: '请输入报价' }]}
              >
                <InputNumber 
                  style={{ width: '100%', borderRadius: 6 }} 
                  min={0} 
                  max={1500} 
                  precision={2}
                  placeholder="请输入 0-1500 之间的价格"
                  variant="filled"
                />
              </Form.Item>

              <Form.Item 
                label={<Text type="secondary" style={{ fontSize: 12 }}>交易数量 (MWh)</Text>} 
                name="quantity"
                rules={[{ required: true, message: '请输入数量' }]}
              >
                <InputNumber 
                  style={{ width: '100%', borderRadius: 6 }} 
                  min={0.1} 
                  precision={1}
                  placeholder="最小单位: 0.1 MWh"
                  variant="filled"
                />
              </Form.Item>

              <div style={{ marginTop: 24, padding: 12, background: themeMode === 'dark' ? 'rgba(255,255,255,0.02)' : 'rgba(0,0,0,0.02)', borderRadius: 8, marginBottom: 24 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <Text type="secondary" style={{ fontSize: 12 }}>估算成交金额</Text>
                  <Text className="data-font" strong>0.00 CNY</Text>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Text type="secondary" style={{ fontSize: 12 }}>可用交易额度</Text>
                  <Text className="data-font">5,000,000.00</Text>
                </div>
              </div>

              <Form.Item style={{ marginBottom: 0 }}>
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  block 
                  icon={<ThunderboltOutlined />}
                  style={{ height: 44, borderRadius: 8, fontWeight: 600, boxShadow: `0 4px 12px ${token.colorPrimary}40` }}
                >
                  确认申报提交
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </Col>
      </Row>

      {/* 订单列表 */}
      <Card 
        className="hover-card"
        title={
          <Space>
            <ClockCircleOutlined style={{ color: token.colorWarning }} />
            <span>当日委单执行流水</span>
          </Space>
        }
        style={{ marginTop: 20, borderRadius: 12, border: 'none' }}
        extra={
          <Space>
            <Button size="small">全部撤单</Button>
            <Button type="primary" size="small" ghost onClick={() => setOrderModalVisible(true)}>导出报表</Button>
          </Space>
        }
      >
        <Table 
          columns={orderColumns}
          dataSource={mockOrders}
          rowKey="id"
          pagination={{ pageSize: 8, showSizeChanger: false }}
          size="middle"
        />
      </Card>

      {/* 订单确认弹窗 */}
      <Modal
        title={
          <Space>
            <SafetyCertificateOutlined style={{ color: token.colorSuccess }} />
            <span>现货交易申报确认</span>
          </Space>
        }
        open={orderModalVisible}
        onCancel={() => setOrderModalVisible(false)}
        footer={[
          <Button key="back" onClick={() => setOrderModalVisible(false)}>取消</Button>,
          <Button key="submit" type="primary" onClick={() => handleSubmitOrder({})}>确认提交</Button>
        ]}
        centered
        styles={{ body: { padding: '24px' } }}
      >
        <Text type="secondary">您正在向广东电力市场提交一笔日前买入申报，请核对信息：</Text>
        <div style={{ marginTop: 20, padding: 16, background: themeMode === 'dark' ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.02)', borderRadius: 8 }}>
          <Row gutter={[16, 12]}>
            <Col span={12}><Text type="secondary">品种：</Text><Text strong>日前现货</Text></Col>
            <Col span={12}><Text type="secondary">方向：</Text><Tag color="green">买入</Tag></Col>
            <Col span={12}><Text type="secondary">价格：</Text><Text strong className="data-font">485.00 元/MWh</Text></Col>
            <Col span={12}><Text type="secondary">数量：</Text><Text strong className="data-font">100.0 MWh</Text></Col>
          </Row>
        </div>
      </Modal>
    </PageContainer>
  );
};

export default SpotTrading;
