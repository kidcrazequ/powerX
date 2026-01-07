/**
 * PowerX 合同管理页面 - 现代深色版
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 合同详情、执行跟踪、分解管理
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
  Descriptions,
  Timeline,
  Progress,
  Tabs,
  Statistic,
  Modal,
  Form,
  InputNumber,
  DatePicker,
  Alert,
  message,
  theme,
  Tooltip
} from 'antd';
import { 
  FileTextOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  SyncOutlined,
  HistoryOutlined,
  SplitCellsOutlined,
  SafetyCertificateOutlined,
  InfoCircleOutlined,
  CarryOutOutlined
} from '@ant-design/icons';
import { PageContainer, StatisticCard } from '@ant-design/pro-components';
import ReactECharts from 'echarts-for-react';
import { useSettingsStore } from '../stores/settingsStore';

const { Text, Title, Paragraph } = Typography;

// 模拟合同详情
const mockContractDetail = {
  id: 'YL2026001',
  type: 'YEARLY',
  typeName: '年度长协',
  counterparty: '华能广东电厂',
  counterpartyType: 'GENERATOR',
  province: '广东',
  totalQuantity: 50000,
  price: 465.00,
  executedQuantity: 8500,
  remainingQuantity: 41500,
  startDate: '2026-01-01',
  endDate: '2026-12-31',
  status: 'ACTIVE',
  signDate: '2025-12-15',
  monthlyPlan: [4000, 4200, 4500, 4300, 4100, 3800, 3600, 3500, 3800, 4200, 4500, 5500]
};

// 模拟执行记录
const mockExecutionRecords = [
  { id: 1, date: '2026-01-07', quantity: 150, price: 465.00, status: 'SETTLED' },
  { id: 2, date: '2026-01-06', quantity: 145, price: 465.00, status: 'SETTLED' },
  { id: 3, date: '2026-01-05', quantity: 160, price: 465.00, status: 'SETTLED' },
  { id: 4, date: '2026-01-04', quantity: 155, price: 465.00, status: 'SETTLED' },
  { id: 5, date: '2026-01-03', quantity: 148, price: 465.00, status: 'PENDING' }
];

// 月度分解计划图
const getMonthlyPlanOption = (token: any, themeMode: string) => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: themeMode === 'dark' ? 'rgba(20, 20, 20, 0.9)' : 'rgba(255, 255, 255, 0.9)',
    borderColor: token.colorBorderSecondary,
    textStyle: { color: token.colorText }
  },
  legend: {
    data: ['计划电量', '已执行'],
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
    data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
    axisLabel: { color: token.colorTextDescription },
    axisLine: { lineStyle: { color: themeMode === 'dark' ? token.colorBorderSecondary : 'rgba(0,0,0,0.15)' } }
  },
  yAxis: {
    type: 'value',
    name: 'MWh',
    axisLabel: { color: token.colorTextDescription },
    nameTextStyle: { color: token.colorTextDescription },
    axisLine: { show: true, lineStyle: { color: themeMode === 'dark' ? token.colorBorderSecondary : 'rgba(0,0,0,0.15)' } },
    splitLine: { lineStyle: { color: themeMode === 'dark' ? token.colorBorderSecondary : 'rgba(0,0,0,0.06)', type: 'dashed' } }
  },
  series: [
    {
      name: '计划电量',
      type: 'bar',
      data: mockContractDetail.monthlyPlan,
      itemStyle: { 
        color: token.colorPrimary,
        borderRadius: [4, 4, 0, 0]
      }
    },
    {
      name: '已执行',
      type: 'bar',
      data: [3800, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      itemStyle: { 
        color: token.colorSuccess,
        borderRadius: [4, 4, 0, 0]
      }
    }
  ]
});

const Contract: React.FC = () => {
  const [decomposeModalVisible, setDecomposeModalVisible] = useState(false);
  const [form] = Form.useForm();
  const { token } = theme.useToken();
  const { themeMode } = useSettingsStore();

  // 执行记录表格列
  const executionColumns = [
    { title: '执行日期', dataIndex: 'date', key: 'date', render: (text: string) => <span className="data-font">{text}</span> },
    { 
      title: '执行电量 (MWh)', 
      dataIndex: 'quantity', 
      key: 'quantity',
      render: (val: number) => <span className="data-font">{val.toLocaleString()}</span>
    },
    { 
      title: '单价 (元)', 
      dataIndex: 'price', 
      key: 'price',
      render: (val: number) => <span className="data-font">{val.toFixed(2)}</span>
    },
    { 
      title: '预计金额 (元)', 
      key: 'amount',
      render: (_: any, record: any) => <span className="data-font" style={{ fontWeight: 600 }}>{(record.quantity * record.price).toLocaleString()}</span>
    },
    { 
      title: '结算状态', 
      dataIndex: 'status', 
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'SETTLED' ? 'success' : 'processing'} bordered={false}>
          {status === 'SETTLED' ? '已结算' : '待结算'}
        </Tag>
      )
    }
  ];

  // 提交分解计划
  const handleDecompose = (values: any) => {
    message.loading('正在同步月度分解曲线...', 1);
    setTimeout(() => {
      message.success('月度分解计划更新成功！');
      setDecomposeModalVisible(false);
      form.resetFields();
    }, 1200);
  };

  const contract = mockContractDetail;
  const executePercent = Math.round(contract.executedQuantity / contract.totalQuantity * 100);

  return (
    <PageContainer
      header={{
        title: '资产合约详情',
        subTitle: '合同全生命周期管理与月度执行曲线跟踪',
        extra: [
          <Button key="export" icon={<HistoryOutlined />}>导出执行报告</Button>,
          <Button key="edit" type="primary" ghost>修改基本信息</Button>
        ]
      }}
    >
      <Row gutter={[20, 20]}>
        <Col xs={24} lg={16}>
          <Card 
            className="hover-card"
            title={
              <Space>
                <div style={{ width: 24, height: 24, borderRadius: 6, background: `${token.colorPrimary}20`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <FileTextOutlined style={{ color: token.colorPrimary, fontSize: 14 }} />
                </div>
                <span>合约基础要素</span>
                <Tag color="purple" bordered={false} style={{ marginLeft: 8 }}>{contract.typeName}</Tag>
                <Tag color="success" bordered={false}>执行中</Tag>
              </Space>
            }
            style={{ borderRadius: 12, border: 'none' }}
          >
            <Descriptions 
              column={{ xs: 1, sm: 2, lg: 3 }} 
              labelStyle={{ color: token.colorTextSecondary }}
              contentStyle={{ color: token.colorText }}
            >
              <Descriptions.Item label="合约编号">
                <Text copyable strong className="data-font">{contract.id}</Text>
              </Descriptions.Item>
              <Descriptions.Item label="交易对手方">{contract.counterparty}</Descriptions.Item>
              <Descriptions.Item label="资产归属">{contract.province}电力市场</Descriptions.Item>
              <Descriptions.Item label="合约总量">
                <Text strong className="data-font">{contract.totalQuantity.toLocaleString()}</Text> MWh
              </Descriptions.Item>
              <Descriptions.Item label="约定价格">
                <Text strong className="data-font" style={{ color: token.colorInfo }}>{contract.price.toFixed(2)}</Text> 元/MWh
              </Descriptions.Item>
              <Descriptions.Item label="预估总值">
                <Text strong className="data-font">{(contract.totalQuantity * contract.price).toLocaleString()}</Text> 元
              </Descriptions.Item>
              <Descriptions.Item label="签约日期">{contract.signDate}</Descriptions.Item>
              <Descriptions.Item label="履约期限">{contract.startDate} 至 {contract.endDate}</Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          <Card 
            className="hover-card"
            title={<span>履约进度健康度</span>}
            style={{ borderRadius: 12, border: 'none' }}
          >
            <div style={{ textAlign: 'center', margin: '20px 0' }}>
              <Progress 
                type="dashboard" 
                percent={executePercent}
                strokeColor={{ '0%': token.colorPrimary, '100%': token.colorSuccess }}
                trailColor={themeMode === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.06)'}
                width={160}
              />
            </div>
            <Row gutter={16}>
              <Col span={12}>
                <div style={{ background: 'rgba(255,255,255,0.03)', padding: 12, borderRadius: 8, textAlign: 'center' }}>
                  <Text type="secondary" style={{ fontSize: 11, display: 'block' }}>已执行 (MWh)</Text>
                  <Text strong className="data-font" style={{ fontSize: 18, color: token.colorSuccess }}>{contract.executedQuantity.toLocaleString()}</Text>
                </div>
              </Col>
              <Col span={12}>
                <div style={{ background: 'rgba(255,255,255,0.03)', padding: 12, borderRadius: 8, textAlign: 'center' }}>
                  <Text type="secondary" style={{ fontSize: 11, display: 'block' }}>待执行 (MWh)</Text>
                  <Text strong className="data-font" style={{ fontSize: 18 }}>{contract.remainingQuantity.toLocaleString()}</Text>
                </div>
              </Col>
            </Row>
            <Button 
              type="primary" 
              icon={<SplitCellsOutlined />}
              block 
              style={{ marginTop: 24, height: 40, borderRadius: 8, boxShadow: `0 4px 12px ${token.colorPrimary}30` }}
              onClick={() => setDecomposeModalVisible(true)}
            >
              更新月度分解计划
            </Button>
          </Card>
        </Col>
      </Row>

      <div style={{ background: 'rgba(255,255,255,0.02)', borderRadius: 12, padding: 4, marginTop: 20 }}>
        <Tabs defaultActiveKey="plan" centered>
          <Tabs.TabPane 
            tab={<Space><SyncOutlined /> 月度履约分布</Space>}
            key="plan"
          >
            <div style={{ padding: '12px 24px 24px' }}>
              <ReactECharts 
                key={themeMode}
                option={getMonthlyPlanOption(token, themeMode)} 
                style={{ height: 380 }} 
                theme={themeMode} 
              />
            </div>
          </Tabs.TabPane>

          <Tabs.TabPane 
            tab={<Space><HistoryOutlined /> 日常执行流水</Space>}
            key="history"
          >
            <div style={{ padding: '0 12px 12px' }}>
              <Table 
                columns={executionColumns}
                dataSource={mockExecutionRecords}
                rowKey="id"
                pagination={{ pageSize: 8, showSizeChanger: false }}
                size="middle"
                summary={(data) => {
                  const totalQty = data.reduce((sum, r) => sum + r.quantity, 0);
                  const totalAmount = data.reduce((sum, r) => sum + r.quantity * r.price, 0);
                  return (
                    <Table.Summary.Row>
                      <Table.Summary.Cell index={0}><Text strong>合计执行</Text></Table.Summary.Cell>
                      <Table.Summary.Cell index={1}><Text strong className="data-font">{totalQty.toLocaleString()}</Text></Table.Summary.Cell>
                      <Table.Summary.Cell index={2}>-</Table.Summary.Cell>
                      <Table.Summary.Cell index={3}><Text strong className="data-font">{totalAmount.toLocaleString()}</Text></Table.Summary.Cell>
                      <Table.Summary.Cell index={4}>-</Table.Summary.Cell>
                    </Table.Summary.Row>
                  );
                }}
              />
            </div>
          </Tabs.TabPane>

          <Tabs.TabPane 
            tab={<Space><ClockCircleOutlined /> 资产变更日志</Space>}
            key="log"
          >
            <div style={{ padding: '24px 40px' }}>
              <Timeline
                mode="left"
                items={[
                  {
                    color: token.colorSuccess,
                    dot: <CarryOutOutlined style={{ fontSize: 16 }} />,
                    children: (
                      <div style={{ marginLeft: 12 }}>
                        <Text strong style={{ fontSize: 14 }}>资产开始执行</Text>
                        <Paragraph type="secondary" style={{ fontSize: 12, marginTop: 4 }}>进入 2026 年度履约周期，系统自动激活现货结算匹配</Paragraph>
                        <Text type="secondary" style={{ fontSize: 11 }}>2026-01-01 00:00:00</Text>
                      </div>
                    )
                  },
                  {
                    color: token.colorPrimary,
                    children: (
                      <div style={{ marginLeft: 12 }}>
                        <Text strong style={{ fontSize: 14 }}>月度分解计划锁定</Text>
                        <Paragraph type="secondary" style={{ fontSize: 12, marginTop: 4 }}>交易员 zhi.qu 提交并确认了年度 12 个月的分解电量曲线</Paragraph>
                        <Text type="secondary" style={{ fontSize: 11 }}>2025-12-28 10:30:00</Text>
                      </div>
                    )
                  },
                  {
                    color: token.colorPrimary,
                    dot: <SafetyCertificateOutlined style={{ fontSize: 16 }} />,
                    children: (
                      <div style={{ marginLeft: 12 }}>
                        <Text strong style={{ fontSize: 14 }}>合约风控审核通过</Text>
                        <Paragraph type="secondary" style={{ fontSize: 12, marginTop: 4 }}>法律合规部与风控中心完成线上双重签署</Paragraph>
                        <Text type="secondary" style={{ fontSize: 11 }}>2025-12-15 15:20:00</Text>
                      </div>
                    )
                  }
                ]}
              />
            </div>
          </Tabs.TabPane>
        </Tabs>
      </div>

      {/* 月度分解弹窗 */}
      <Modal
        title={
          <Space>
            <SplitCellsOutlined style={{ color: token.colorPrimary }} />
            <span>月度电量计划分解</span>
          </Space>
        }
        open={decomposeModalVisible}
        onCancel={() => setDecomposeModalVisible(false)}
        footer={null}
        width={650}
        centered
      >
        <Alert 
          message="规则提醒" 
          description="分解总量必须等于合同总量 (50,000 MWh)，当前误差范围允许 ±1%。" 
          type="info" 
          showIcon 
          style={{ marginBottom: 24, borderRadius: 8 }}
        />
        <Form form={form} layout="vertical" onFinish={handleDecompose} requiredMark={false}>
          <Row gutter={[20, 12]}>
            {['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'].map((month, index) => (
              <Col span={8} key={month}>
                <Form.Item 
                  label={<Text style={{ fontSize: 12 }}>{month}</Text>} 
                  name={`month${index + 1}`}
                  initialValue={mockContractDetail.monthlyPlan[index]}
                >
                  <InputNumber 
                    style={{ width: '100%', borderRadius: 6 }} 
                    min={0} 
                    suffix="MWh" 
                    variant="filled"
                  />
                </Form.Item>
              </Col>
            ))}
          </Row>
          <div style={{ marginTop: 32, display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
            <Button onClick={() => setDecomposeModalVisible(false)} style={{ borderRadius: 6 }}>取消</Button>
            <Button type="primary" htmlType="submit" style={{ borderRadius: 6, padding: '0 24px' }}>确认并同步</Button>
          </div>
        </Form>
      </Modal>
    </PageContainer>
  );
};

export default Contract;
