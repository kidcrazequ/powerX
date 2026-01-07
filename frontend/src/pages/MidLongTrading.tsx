/**
 * PowerX 中长期交易页面 - 现代深色版
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 年度长协、月度竞价、月度双边交易管理
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
  Typography,
  Tabs,
  InputNumber,
  DatePicker,
  Modal,
  message,
  Steps,
  Descriptions,
  Progress,
  theme,
  Tooltip,
  Divider
} from 'antd';
import { 
  FileTextOutlined,
  CalendarOutlined,
  ShoppingOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  PlusOutlined,
  FileProtectOutlined,
  ContainerOutlined,
  HistoryOutlined,
  AuditOutlined
} from '@ant-design/icons';
import { PageContainer, StatisticCard } from '@ant-design/pro-components';
import dayjs from 'dayjs';
import { useSettingsStore } from '../stores/settingsStore';

const { Text, Title } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;

// 模拟合同数据
const mockContracts = [
  { 
    id: 'YL2026001', 
    type: 'YEARLY',
    counterparty: '华能广东电厂',
    totalQuantity: 50000,
    price: 465.00,
    executedQuantity: 8500,
    startDate: '2026-01-01',
    endDate: '2026-12-31',
    status: 'ACTIVE'
  },
  { 
    id: 'MB2026002', 
    type: 'MONTHLY_BILATERAL',
    counterparty: '大唐发电',
    totalQuantity: 5000,
    price: 478.50,
    executedQuantity: 1200,
    startDate: '2026-01-01',
    endDate: '2026-01-31',
    status: 'ACTIVE'
  },
  { 
    id: 'MA2026003', 
    type: 'MONTHLY_AUCTION',
    counterparty: '竞价成交',
    totalQuantity: 3000,
    price: 485.20,
    executedQuantity: 3000,
    startDate: '2026-01-01',
    endDate: '2026-01-31',
    status: 'COMPLETED'
  }
];

// 模拟竞价记录
const mockAuctionRecords = [
  { id: 1, time: '2026-01-05 10:00', quantity: 1000, bidPrice: 480, clearPrice: 478.5, status: 'MATCHED' },
  { id: 2, time: '2026-01-05 10:00', quantity: 500, bidPrice: 475, clearPrice: 478.5, status: 'NOT_MATCHED' },
  { id: 3, time: '2026-01-05 10:00', quantity: 1500, bidPrice: 485, clearPrice: 478.5, status: 'MATCHED' }
];

const MidLongTrading: React.FC = () => {
  const [form] = Form.useForm();
  const [contractModalVisible, setContractModalVisible] = useState(false);
  const [auctionModalVisible, setAuctionModalVisible] = useState(false);
  const { token } = theme.useToken();
  const { themeMode } = useSettingsStore();

  // 合同类型配置
  const contractTypeConfig: Record<string, { color: string; text: string }> = {
    YEARLY: { color: 'purple', text: '年度长协' },
    MONTHLY_BILATERAL: { color: 'blue', text: '月度双边' },
    MONTHLY_AUCTION: { color: 'orange', text: '月度竞价' }
  };

  // 合同表格列
  const contractColumns = [
    { 
      title: '合同/协议编号', 
      dataIndex: 'id', 
      key: 'id',
      render: (text: string) => <Text copyable className="data-font" style={{ fontSize: 13 }}>{text}</Text>
    },
    { 
      title: '类型', 
      dataIndex: 'type', 
      key: 'type',
      render: (type: string) => (
        <Tag color={contractTypeConfig[type]?.color} bordered={false}>
          {contractTypeConfig[type]?.text}
        </Tag>
      )
    },
    { 
      title: '签约主体 (对手方)', 
      dataIndex: 'counterparty', 
      key: 'counterparty',
      render: (text: string) => <Text strong>{text}</Text>
    },
    { 
      title: '合同电量', 
      dataIndex: 'totalQuantity', 
      key: 'totalQuantity',
      render: (val: number) => <span className="data-font">{val.toLocaleString()} MWh</span>
    },
    { 
      title: '结算价格', 
      dataIndex: 'price', 
      key: 'price',
      render: (val: number) => <span className="data-font" style={{ fontWeight: 600 }}>{val.toFixed(2)}</span>
    },
    { 
      title: '执行履约进度', 
      key: 'progress',
      width: 200,
      render: (_: any, record: any) => {
        const percent = Math.round(record.executedQuantity / record.totalQuantity * 100);
        return (
          <Space direction="vertical" size={0} style={{ width: '100%' }}>
            <Progress 
              percent={percent} 
              size="small" 
              strokeColor={{ '0%': token.colorPrimary, '100%': token.colorInfoActive }}
              trailColor={themeMode === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)'}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Text type="secondary" style={{ fontSize: 11 }}>{record.executedQuantity.toLocaleString()} 已执行</Text>
              <Text type="secondary" style={{ fontSize: 11 }}>{percent}%</Text>
            </div>
          </Space>
        );
      }
    },
    { 
      title: '有效期', 
      key: 'period',
      render: (_: any, record: any) => (
        <Space direction="vertical" size={0}>
          <Text style={{ fontSize: 12 }}>{record.startDate}</Text>
          <Text type="secondary" style={{ fontSize: 12 }}>至 {record.endDate}</Text>
        </Space>
      )
    },
    { 
      title: '履约状态', 
      dataIndex: 'status', 
      key: 'status',
      render: (status: string) => {
        const config: Record<string, { color: string; text: string }> = {
          ACTIVE: { color: 'processing', text: '执行中' },
          COMPLETED: { color: 'success', text: '已结算' },
          PENDING: { color: 'warning', text: '待生效' }
        };
        return <Tag color={config[status]?.color} bordered={false}>{config[status]?.text}</Tag>;
      }
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Space size="middle">
          <Button type="text" size="small" style={{ color: token.colorPrimary }}>详情</Button>
          {record.status === 'ACTIVE' && (
            <Button type="text" size="small" style={{ color: token.colorSuccess }}>分解</Button>
          )}
        </Space>
      )
    }
  ];

  // 竞价记录表格列
  const auctionColumns = [
    { title: '申报时间', dataIndex: 'time', key: 'time', render: (text: string) => <span className="data-font">{text}</span> },
    { 
      title: '申报量 (MWh)', 
      dataIndex: 'quantity', 
      key: 'quantity',
      render: (val: number) => <span className="data-font">{val.toLocaleString()}</span>
    },
    { 
      title: '申报价格', 
      dataIndex: 'bidPrice', 
      key: 'bidPrice',
      render: (val: number) => <span className="data-font">{val.toFixed(2)}</span>
    },
    { 
      title: '出清价格', 
      dataIndex: 'clearPrice', 
      key: 'clearPrice',
      render: (val: number) => <span className="data-font" style={{ color: token.colorSuccess }}>{val.toFixed(2)}</span>
    },
    { 
      title: '成交状态', 
      dataIndex: 'status', 
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'MATCHED' ? 'success' : 'error'} bordered={false}>
          {status === 'MATCHED' ? '已成交' : '未成交'}
        </Tag>
      )
    }
  ];

  // 提交新合同
  const handleSubmitContract = (values: any) => {
    message.loading('正在创建资产合同库记录...', 1.5);
    setTimeout(() => {
      message.success('中长期资产合同创建成功！');
      setContractModalVisible(false);
      form.resetFields();
    }, 1500);
  };

  return (
    <PageContainer
      header={{
        title: '中长期资产管理',
        subTitle: '年度长协、月度竞价及中长期资产配置组合管理',
        extra: [
          <Button key="audit" icon={<AuditOutlined />}>合同审计</Button>,
          <Button key="history" icon={<HistoryOutlined />}>变更历史</Button>
        ]
      }}
    >
      {/* 核心指标 */}
      <Row gutter={[20, 20]}>
        <Col xs={24} sm={12} lg={6}>
          <StatisticCard
            className="hover-card"
            statistic={{
              title: <Text type="secondary" style={{ fontSize: 12 }}>年度合同总量 (Yearly)</Text>,
              value: 50000,
              suffix: <span style={{ fontSize: 12, marginLeft: 4 }}>MWh</span>,
              description: <Tag color="purple" bordered={false} style={{ borderRadius: 4 }}>2026FY</Tag>
            }}
            style={{ borderRadius: 12, border: 'none' }}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatisticCard
            className="hover-card"
            statistic={{
              title: <Text type="secondary" style={{ fontSize: 12 }}>本月待结算电量</Text>,
              value: 8000,
              suffix: <span style={{ fontSize: 12, marginLeft: 4 }}>MWh</span>,
              icon: <div style={{ width: 32, height: 32, borderRadius: 8, background: 'rgba(250, 173, 20, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <ClockCircleOutlined style={{ color: token.colorWarning }} />
              </div>
            }}
            style={{ borderRadius: 12, border: 'none' }}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatisticCard
            className="hover-card"
            statistic={{
              title: <Text type="secondary" style={{ fontSize: 12 }}>资产库已执行总量</Text>,
              value: 12700,
              suffix: <span style={{ fontSize: 12, marginLeft: 4 }}>MWh</span>,
              chart: <Progress 
                percent={25.4} 
                size="small" 
                showInfo={false} 
                strokeColor={token.colorSuccess} 
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
              title: <Text type="secondary" style={{ fontSize: 12 }}>资产库加权均价</Text>,
              value: 472.35,
              suffix: <span style={{ fontSize: 12, marginLeft: 4 }}>元/MWh</span>,
              icon: <div style={{ width: 32, height: 32, borderRadius: 8, background: 'rgba(114, 46, 209, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <FileProtectOutlined style={{ color: '#722ed1' }} />
              </div>
            }}
            style={{ borderRadius: 12, border: 'none' }}
          />
        </Col>
      </Row>

      <div style={{ background: themeMode === 'dark' ? 'rgba(255,255,255,0.02)' : 'rgba(0,0,0,0.02)', borderRadius: 12, padding: 4, marginTop: 24 }}>
        <Tabs 
          defaultActiveKey="contracts" 
          centered
          tabBarExtraContent={{
            right: (
              <Space style={{ paddingRight: 16 }}>
                <Button 
                  type="primary" 
                  icon={<PlusOutlined />}
                  onClick={() => setContractModalVisible(true)}
                  style={{ borderRadius: 6, boxShadow: `0 4px 12px ${token.colorPrimary}40` }}
                >
                  登记新合同
                </Button>
                <Button 
                  icon={<ShoppingOutlined />}
                  onClick={() => setAuctionModalVisible(true)}
                  style={{ borderRadius: 6 }}
                >
                  参与月度竞价
                </Button>
              </Space>
            )
          }}
        >
          <Tabs.TabPane 
            tab={<Space><ContainerOutlined /> 资产合同库</Space>}
            key="contracts"
          >
            <div style={{ padding: '0 12px 12px' }}>
              <Table 
                columns={contractColumns}
                dataSource={mockContracts}
                rowKey="id"
                pagination={{ pageSize: 8, showSizeChanger: false }}
                size="middle"
              />
            </div>
          </Tabs.TabPane>

          <Tabs.TabPane 
            tab={<Space><CalendarOutlined /> 竞价申报流水</Space>}
            key="auction"
          >
            <div style={{ padding: '0 12px 12px' }}>
              <Table 
                columns={auctionColumns}
                dataSource={mockAuctionRecords}
                rowKey="id"
                pagination={{ pageSize: 8, showSizeChanger: false }}
                size="middle"
              />
            </div>
          </Tabs.TabPane>
        </Tabs>
      </div>

      {/* 新建合同弹窗 */}
      <Modal
        title={
          <Space>
            <FileTextOutlined style={{ color: token.colorPrimary }} />
            <span>登记新资产合同</span>
          </Space>
        }
        open={contractModalVisible}
        onCancel={() => setContractModalVisible(false)}
        footer={null}
        width={650}
        centered
      >
        <Form 
          form={form} 
          layout="vertical" 
          onFinish={handleSubmitContract}
          requiredMark={false}
          style={{ marginTop: 12 }}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item 
                label={<Text type="secondary" style={{ fontSize: 12 }}>合同分类</Text>} 
                name="type" 
                rules={[{ required: true }]}
              >
                <Select placeholder="请选择合同类型" variant="filled">
                  <Option value="YEARLY">年度长协协议</Option>
                  <Option value="MONTHLY_BILATERAL">月度双边协议</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item 
                label={<Text type="secondary" style={{ fontSize: 12 }}>签约对手方</Text>} 
                name="counterparty" 
                rules={[{ required: true }]}
              >
                <Select placeholder="请选择交易对手" variant="filled">
                  <Option value="华能广东电厂">华能广东电厂</Option>
                  <Option value="大唐发电">大唐发电</Option>
                  <Option value="国电投">国电投</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item 
                label={<Text type="secondary" style={{ fontSize: 12 }}>协议总量 (MWh)</Text>} 
                name="quantity" 
                rules={[{ required: true }]}
              >
                <InputNumber style={{ width: '100%', borderRadius: 6 }} min={100} variant="filled" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item 
                label={<Text type="secondary" style={{ fontSize: 12 }}>协议价格 (元/MWh)</Text>} 
                name="price" 
                rules={[{ required: true }]}
              >
                <InputNumber style={{ width: '100%', borderRadius: 6 }} min={0} max={1500} precision={2} variant="filled" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item 
            label={<Text type="secondary" style={{ fontSize: 12 }}>协议履约期限</Text>} 
            name="period" 
            rules={[{ required: true }]}
          >
            <RangePicker style={{ width: '100%', borderRadius: 6 }} variant="filled" />
          </Form.Item>

          <div style={{ marginTop: 32, display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
            <Button onClick={() => setContractModalVisible(false)} style={{ borderRadius: 6 }}>取消</Button>
            <Button type="primary" htmlType="submit" style={{ borderRadius: 6, padding: '0 24px' }}>确认登记</Button>
          </div>
        </Form>
      </Modal>

      {/* 参与竞价弹窗 */}
      <Modal
        title={
          <Space>
            <ShoppingOutlined style={{ color: '#722ed1' }} />
            <span>月度竞价申报柜台</span>
          </Space>
        }
        open={auctionModalVisible}
        onCancel={() => setAuctionModalVisible(false)}
        footer={null}
        width={500}
        centered
      >
        <Steps 
          current={0} 
          size="small"
          style={{ marginBottom: 32, marginTop: 12 }}
          items={[
            { title: '填写申报' },
            { title: '风控校验' },
            { title: '提交确认' }
          ]}
        />

        <Form layout="vertical" requiredMark={false}>
          <Form.Item label={<Text type="secondary" style={{ fontSize: 12 }}>目标交易月份</Text>}>
            <DatePicker picker="month" style={{ width: '100%', borderRadius: 6 }} variant="filled" defaultValue={dayjs().add(1, 'month')} />
          </Form.Item>

          <Form.Item label={<Text type="secondary" style={{ fontSize: 12 }}>申报总电量 (MWh)</Text>}>
            <InputNumber style={{ width: '100%', borderRadius: 6 }} min={100} placeholder="最小申报单位: 100MWh" variant="filled" />
          </Form.Item>

          <Form.Item label={<Text type="secondary" style={{ fontSize: 12 }}>申报限价 (元/MWh)</Text>}>
            <InputNumber style={{ width: '100%', borderRadius: 6 }} min={0} max={1500} precision={2} placeholder="输入您的心理最高价" variant="filled" />
          </Form.Item>

          <Divider style={{ margin: '24px 0' }} />

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
            <Button onClick={() => setAuctionModalVisible(false)} style={{ borderRadius: 6 }}>取消</Button>
            <Button type="primary" style={{ borderRadius: 6, padding: '0 24px', background: '#722ed1', borderColor: '#722ed1' }}>提交竞价申报</Button>
          </div>
        </Form>
      </Modal>
    </PageContainer>
  );
};

export default MidLongTrading;
