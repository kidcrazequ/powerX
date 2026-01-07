/**
 * PowerX 结算中心页面 - 现代深色版
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 结算管理、费用明细、对账功能
 */

import React, { useState } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Table, 
  Tag, 
  Space,
  Typography,
  Button,
  Tabs,
  Statistic,
  DatePicker,
  Select,
  Descriptions,
  Divider,
  Progress,
  theme,
  Tooltip
} from 'antd';
import { 
  AccountBookOutlined,
  FileSearchOutlined,
  DownloadOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  WalletOutlined,
  BarChartOutlined,
  PieChartOutlined,
  CalendarOutlined,
  PrinterOutlined
} from '@ant-design/icons';
import { PageContainer, StatisticCard } from '@ant-design/pro-components';
import ReactECharts from 'echarts-for-react';
import dayjs from 'dayjs';
import { useSettingsStore } from '../stores/settingsStore';

const { Text, Title, Paragraph } = Typography;
const { Option } = Select;

// 模拟结算记录
const mockSettlementRecords = [
  { 
    id: 'STL20260107001',
    date: '2026-01-07',
    type: 'DAY_AHEAD',
    quantity: 500,
    avgPrice: 485.32,
    amount: 242660,
    fee: 4853.2,
    netAmount: 237806.8,
    status: 'SETTLED'
  },
  { 
    id: 'STL20260106001',
    date: '2026-01-06',
    type: 'MID_LONG',
    quantity: 4200,
    avgPrice: 465.00,
    amount: 1953000,
    fee: 19530,
    netAmount: 1933470,
    status: 'SETTLED'
  },
  { 
    id: 'STL20260105001',
    date: '2026-01-05',
    type: 'DAY_AHEAD',
    quantity: 480,
    avgPrice: 492.15,
    amount: 236232,
    fee: 4724.64,
    netAmount: 231507.36,
    status: 'PENDING'
  }
];

// 模拟月度统计
const mockMonthlySummary = {
  totalQuantity: 125000,
  totalAmount: 58125000,
  totalFee: 581250,
  netAmount: 57543750,
  spotQuantity: 25000,
  midLongQuantity: 100000,
  avgSpotPrice: 488.50,
  avgMidLongPrice: 468.00
};

// 费用构成图
const getFeeBreakdownOption = (token: any, themeMode: string) => ({
  tooltip: {
    trigger: 'item',
    backgroundColor: themeMode === 'dark' ? 'rgba(20, 20, 20, 0.9)' : 'rgba(255, 255, 255, 0.9)',
    borderColor: token.colorBorderSecondary,
    textStyle: { color: token.colorText },
    formatter: '{b}: <span style="font-weight:bold">{c}</span> 元 ({d}%)'
  },
  legend: {
    orient: 'vertical',
    right: '5%',
    top: 'center',
    textStyle: { color: token.colorTextSecondary }
  },
  series: [
    {
      name: '费用构成',
      type: 'pie',
      radius: ['50%', '80%'],
      center: ['40%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 8,
        borderColor: themeMode === 'dark' ? '#141414' : '#fff',
        borderWidth: 2
      },
      label: {
        show: false
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold',
          color: token.colorText
        }
      },
      data: [
        { value: 48000000, name: '中长期购电', itemStyle: { color: token.colorPrimary } },
        { value: 9500000, name: '现货购电', itemStyle: { color: token.colorSuccess } },
        { value: 450000, name: '输配电费', itemStyle: { color: token.colorWarning } },
        { value: 125000, name: '交易服务费', itemStyle: { color: '#722ed1' } },
        { value: 50000, name: '其他费用', itemStyle: { color: token.colorError } }
      ]
    }
  ]
});

// 日结算趋势图
const getDailyTrendOption = (token: any, themeMode: string) => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: themeMode === 'dark' ? 'rgba(20, 20, 20, 0.9)' : 'rgba(255, 255, 255, 0.9)',
    borderColor: token.colorBorderSecondary,
    textStyle: { color: token.colorText }
  },
  legend: {
    data: ['结算金额', '现货占比'],
    top: 0,
    textStyle: { color: token.colorTextSecondary }
  },
  grid: {
    left: '3%',
    right: '8%',
    bottom: '3%',
    top: '15%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: ['1/1', '1/2', '1/3', '1/4', '1/5', '1/6', '1/7'],
    axisLabel: { color: token.colorTextDescription },
    axisLine: { lineStyle: { color: themeMode === 'dark' ? token.colorBorderSecondary : 'rgba(0,0,0,0.15)' } }
  },
  yAxis: [
    {
      type: 'value',
      name: '万元',
      nameTextStyle: { color: token.colorTextDescription },
      axisLabel: {
        color: token.colorTextDescription,
        formatter: (value: number) => (value / 10000).toFixed(0)
      },
      axisLine: { show: true, lineStyle: { color: themeMode === 'dark' ? token.colorBorderSecondary : 'rgba(0,0,0,0.15)' } },
      splitLine: { lineStyle: { color: themeMode === 'dark' ? token.colorBorderSecondary : 'rgba(0,0,0,0.06)', type: 'dashed' } }
    },
    {
      type: 'value',
      name: '%',
      min: 0,
      max: 100,
      nameTextStyle: { color: token.colorTextDescription },
      axisLabel: { color: token.colorTextDescription },
      axisLine: { show: true, lineStyle: { color: themeMode === 'dark' ? token.colorBorderSecondary : 'rgba(0,0,0,0.15)' } },
      splitLine: { show: false }
    }
  ],
  series: [
    {
      name: '结算金额',
      type: 'bar',
      data: [1850000, 1920000, 1780000, 1950000, 1880000, 2100000, 2050000],
      itemStyle: { 
        color: token.colorPrimary,
        borderRadius: [4, 4, 0, 0]
      }
    },
    {
      name: '现货占比',
      type: 'line',
      yAxisIndex: 1,
      smooth: true,
      data: [18, 22, 15, 25, 20, 28, 24],
      lineStyle: { color: token.colorSuccess, width: 3 },
      itemStyle: { color: token.colorSuccess }
    }
  ]
});

const Settlement: React.FC = () => {
  const [selectedMonth, setSelectedMonth] = useState(dayjs());
  const { token } = theme.useToken();
  const { themeMode } = useSettingsStore();

  // 结算记录表格列
  const settlementColumns = [
    { 
      title: '结算凭证号', 
      dataIndex: 'id', 
      key: 'id',
      render: (text: string) => <Text copyable className="data-font" style={{ fontSize: 13 }}>{text}</Text>
    },
    { 
      title: '业务日期', 
      dataIndex: 'date', 
      key: 'date',
      render: (text: string) => <span className="data-font" style={{ fontSize: 13, color: token.colorTextSecondary }}>{text}</span>
    },
    { 
      title: '交易类型', 
      dataIndex: 'type', 
      key: 'type',
      render: (type: string) => (
        <Tag color={type === 'DAY_AHEAD' ? 'blue' : 'purple'} bordered={false}>
          {type === 'DAY_AHEAD' ? '现货结算' : '中长期结算'}
        </Tag>
      )
    },
    { 
      title: '结算电量', 
      dataIndex: 'quantity', 
      key: 'quantity',
      render: (val: number) => <span className="data-font">{val.toLocaleString()} MWh</span>
    },
    { 
      title: '均价 (元)', 
      dataIndex: 'avgPrice', 
      key: 'avgPrice',
      render: (val: number) => <span className="data-font">{val.toFixed(2)}</span>
    },
    { 
      title: '明细费用', 
      dataIndex: 'fee', 
      key: 'fee',
      render: (val: number) => <span className="data-font">{val.toFixed(2)}</span>
    },
    { 
      title: '实付总额 (元)', 
      dataIndex: 'netAmount', 
      key: 'netAmount',
      render: (val: number) => <Text strong className="data-font" style={{ color: token.colorError }}>{val.toLocaleString()}</Text>
    },
    { 
      title: '结算状态', 
      dataIndex: 'status', 
      key: 'status',
      render: (status: string) => (
        <Tag 
          icon={status === 'SETTLED' ? <CheckCircleOutlined /> : <ExclamationCircleOutlined />}
          color={status === 'SETTLED' ? 'success' : 'warning'}
          bordered={false}
        >
          {status === 'SETTLED' ? '结算完成' : '待对账'}
        </Tag>
      )
    },
    {
      title: '操作',
      key: 'action',
      render: () => (
        <Space size="middle">
          <Tooltip title="查看流水">
            <Button type="text" size="small" style={{ color: token.colorPrimary }}>详情</Button>
          </Tooltip>
          <Tooltip title="打印凭证">
            <Button type="text" size="small" icon={<PrinterOutlined />} />
          </Tooltip>
        </Space>
      )
    }
  ];

  return (
    <PageContainer
      header={{
        title: '资金结算中心',
        subTitle: '全维度交易结算流水与费用经营健康度分析',
        extra: [
          <Button key="download" icon={<DownloadOutlined />}>导出年度账单</Button>,
          <Button key="reconcile" type="primary" icon={<WalletOutlined />}>进入在线对账</Button>
        ]
      }}
    >
      {/* 结算核心指标 */}
      <Row gutter={[20, 20]}>
        <Col xs={24} sm={12} lg={6}>
          <StatisticCard
            className="hover-card"
            statistic={{
              title: <Text type="secondary" style={{ fontSize: 12 }}>本期结算电量总量</Text>,
              value: mockMonthlySummary.totalQuantity,
              suffix: <span style={{ fontSize: 12, marginLeft: 4 }}>MWh</span>,
              chart: <Progress 
                percent={85} 
                size="small" 
                showInfo={false} 
                strokeColor={token.colorPrimary} 
                trailColor={themeMode === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)'}
              />
            }}
            style={{ borderRadius: 12, border: 'none' }}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatisticCard
            className="hover-card"
            statistic={{
              title: <Text type="secondary" style={{ fontSize: 12 }}>交易总额 (Gross)</Text>,
              value: mockMonthlySummary.totalAmount / 10000,
              suffix: <span style={{ fontSize: 12, marginLeft: 4 }}>万元</span>,
              precision: 2
            }}
            style={{ borderRadius: 12, border: 'none' }}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatisticCard
            className="hover-card"
            statistic={{
              title: <Text type="secondary" style={{ fontSize: 12 }}>累计税费支出</Text>,
              value: mockMonthlySummary.totalFee / 10000,
              suffix: <span style={{ fontSize: 12, marginLeft: 4 }}>万元</span>,
              precision: 2,
              valueStyle: { color: token.colorWarning }
            }}
            style={{ borderRadius: 12, border: 'none' }}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatisticCard
            className="hover-card"
            statistic={{
              title: <Text type="secondary" style={{ fontSize: 12 }}>实际支付净额 (Net)</Text>,
              value: mockMonthlySummary.netAmount / 10000,
              suffix: <span style={{ fontSize: 12, marginLeft: 4 }}>万元</span>,
              precision: 2,
              valueStyle: { color: token.colorError }
            }}
            style={{ borderRadius: 12, border: 'none' }}
          />
        </Col>
      </Row>

      <Row gutter={[20, 20]} style={{ marginTop: 20 }}>
        {/* 费用构成分析 */}
        <Col xs={24} lg={10}>
          <Card 
            className="hover-card"
            title={
              <Space>
                <PieChartOutlined style={{ color: '#722ed1' }} />
                <span>费用经营结构</span>
              </Space>
            }
            style={{ borderRadius: 12, border: 'none' }}
          >
            <ReactECharts 
              key={themeMode}
              option={getFeeBreakdownOption(token, themeMode)} 
              style={{ height: 350 }} 
              theme={themeMode} 
            />
          </Card>
        </Col>

        {/* 结算趋势 */}
        <Col xs={24} lg={14}>
          <Card 
            className="hover-card"
            title={
              <Space>
                <BarChartOutlined style={{ color: token.colorPrimary }} />
                <span>结算动态趋势 (DA vs Overall)</span>
              </Space>
            }
            style={{ borderRadius: 12, border: 'none' }}
          >
            <ReactECharts 
              key={themeMode}
              option={getDailyTrendOption(token, themeMode)} 
              style={{ height: 350 }} 
              theme={themeMode} 
            />
          </Card>
        </Col>
      </Row>

      <div style={{ background: themeMode === 'dark' ? 'rgba(255,255,255,0.02)' : 'rgba(0,0,0,0.02)', borderRadius: 12, padding: 4, marginTop: 24 }}>
        <Tabs 
          defaultActiveKey="records" 
          centered
          tabBarExtraContent={{
            right: (
              <Space style={{ paddingRight: 16 }}>
                <DatePicker 
                  picker="month" 
                  value={selectedMonth}
                  onChange={(date) => date && setSelectedMonth(date)}
                  variant="borderless"
                  suffixIcon={<CalendarOutlined />}
                />
                <Button icon={<DownloadOutlined />} size="small">EXCEL 导出</Button>
              </Space>
            )
          }}
        >
          <Tabs.TabPane 
            tab={<Space><AccountBookOutlined /> 财务结算明细流水</Space>}
            key="records"
          >
            <div style={{ padding: '0 12px 12px' }}>
              <Table 
                columns={settlementColumns}
                dataSource={mockSettlementRecords}
                rowKey="id"
                pagination={{ pageSize: 8, showSizeChanger: false }}
                size="middle"
                summary={(data) => {
                  const totalQty = data.reduce((sum, r) => sum + r.quantity, 0);
                  const totalAmount = data.reduce((sum, r) => sum + r.amount, 0);
                  const totalFee = data.reduce((sum, r) => sum + r.fee, 0);
                  const totalNet = data.reduce((sum, r) => sum + r.netAmount, 0);
                  return (
                    <Table.Summary.Row style={{ backgroundColor: themeMode === 'dark' ? 'rgba(255,255,255,0.02)' : 'rgba(0,0,0,0.02)' }}>
                      <Table.Summary.Cell index={0} colSpan={3}><Text strong>月度执行汇总合计</Text></Table.Summary.Cell>
                      <Table.Summary.Cell index={3}><Text strong className="data-font">{totalQty.toLocaleString()} MWh</Text></Table.Summary.Cell>
                      <Table.Summary.Cell index={4}>-</Table.Summary.Cell>
                      <Table.Summary.Cell index={5}><Text strong className="data-font">{totalAmount.toLocaleString()}</Text></Table.Summary.Cell>
                      <Table.Summary.Cell index={6}><Text strong className="data-font">{totalFee.toFixed(2)}</Text></Table.Summary.Cell>
                      <Table.Summary.Cell index={7}><Text strong className="data-font" style={{ color: token.colorError }}>{totalNet.toLocaleString()}</Text></Table.Summary.Cell>
                      <Table.Summary.Cell index={8} colSpan={2}>-</Table.Summary.Cell>
                    </Table.Summary.Row>
                  );
                }}
              />
            </div>
          </Tabs.TabPane>

          <Tabs.TabPane 
            tab={<Space><FileSearchOutlined /> 成本费用多维透视</Space>}
            key="analysis"
          >
            <div style={{ padding: '12px 24px 24px' }}>
              <Descriptions 
                title={<span style={{ fontSize: 14, color: token.colorTextSecondary }}>本期结算周期：{selectedMonth.format('YYYY年MM月')}</span>} 
                bordered 
                column={{ xs: 1, sm: 2, lg: 3 }}
                labelStyle={{ background: themeMode === 'dark' ? 'rgba(255,255,255,0.02)' : 'rgba(0,0,0,0.03)', color: token.colorTextSecondary }}
                contentStyle={{ color: token.colorText }}
              >
                <Descriptions.Item label="中长期购电电量"><span className="data-font">{mockMonthlySummary.midLongQuantity.toLocaleString()} MWh</span></Descriptions.Item>
                <Descriptions.Item label="中长期加权价"><span className="data-font">{mockMonthlySummary.avgMidLongPrice.toFixed(2)} 元</span></Descriptions.Item>
                <Descriptions.Item label="中长期电费明细"><span className="data-font">{(mockMonthlySummary.midLongQuantity * mockMonthlySummary.avgMidLongPrice).toLocaleString()} 元</span></Descriptions.Item>
                
                <Descriptions.Item label="现货购电量汇总"><span className="data-font">{mockMonthlySummary.spotQuantity.toLocaleString()} MWh</span></Descriptions.Item>
                <Descriptions.Item label="现货加权成交价"><span className="data-font">{mockMonthlySummary.avgSpotPrice.toFixed(2)} 元</span></Descriptions.Item>
                <Descriptions.Item label="现货实时电费额"><span className="data-font">{(mockMonthlySummary.spotQuantity * mockMonthlySummary.avgSpotPrice).toLocaleString()} 元</span></Descriptions.Item>
                
                <Descriptions.Item label="固定输配电费"><span className="data-font">450,000.00 元</span></Descriptions.Item>
                <Descriptions.Item label="交易中心服务费"><span className="data-font">125,000.00 元</span></Descriptions.Item>
                <Descriptions.Item label="政府性基金及其他"><span className="data-font">50,000.00 元</span></Descriptions.Item>
              </Descriptions>

              <div style={{ marginTop: 32, padding: '24px 32px', background: `${token.colorError}08`, borderRadius: 12, border: `1px solid ${token.colorError}20`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <Text type="secondary" style={{ display: 'block', marginBottom: 4 }}>本期最终应付结算总额 (CNY)</Text>
                  <Text style={{ fontSize: 12, color: token.colorTextSecondary }}>含税及所有辅助服务分摊费用</Text>
                </div>
                <Statistic 
                  value={mockMonthlySummary.netAmount} 
                  suffix="元"
                  valueStyle={{ color: token.colorError, fontSize: 36, fontWeight: 700, letterSpacing: -1 }}
                  className="data-font"
                />
              </div>
            </div>
          </Tabs.TabPane>
        </Tabs>
      </div>
    </PageContainer>
  );
};

export default Settlement;
