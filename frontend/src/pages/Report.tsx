/**
 * PowerX 报告中心页面 - 现代版
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * AI 自动生成交易报告
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
  Select,
  DatePicker,
  List,
  Spin,
  Modal,
  message,
  theme,
  Tooltip
} from 'antd';
import { 
  FileTextOutlined,
  DownloadOutlined,
  RobotOutlined,
  ReloadOutlined,
  EyeOutlined,
  FilePdfOutlined,
  FileExcelOutlined,
  SendOutlined
} from '@ant-design/icons';
import { PageContainer, ProCard } from '@ant-design/pro-components';
import dayjs from 'dayjs';

const { Text, Title, Paragraph } = Typography;
const { Option } = Select;

// 模拟报告列表
const mockReports = [
  { 
    id: 'RPT20260107001',
    title: '2026年1月第一周交易周报',
    type: 'WEEKLY',
    createTime: '2026-01-07 09:00:00',
    status: 'COMPLETED',
    summary: '本周累计交易电量 125,000 MWh，交易金额 5,812.5 万元，现货占比 20%。'
  },
  { 
    id: 'RPT20260106001',
    title: '2026年1月6日交易日报',
    type: 'DAILY',
    createTime: '2026-01-06 20:00:00',
    status: 'COMPLETED',
    summary: '今日交易电量 18,500 MWh，均价 488.32 元/MWh，较昨日上涨 1.2%。'
  },
  { 
    id: 'RPT20260101001',
    title: '2025年12月交易月报',
    type: 'MONTHLY',
    createTime: '2026-01-01 10:00:00',
    status: 'COMPLETED',
    summary: '上月累计交易电量 520,000 MWh，交易金额 2.42 亿元，完成年度目标进度 8.3%。'
  },
  { 
    id: 'RPT20260107002',
    title: '广东省现货市场分析专题报告',
    type: 'ANALYSIS',
    createTime: '2026-01-07 14:00:00',
    status: 'GENERATING',
    summary: 'AI 正在生成报告...'
  }
];

// 模拟报告预览内容
const mockReportContent = `
# 2026年1月第一周交易周报

**生成时间**: 2026-01-07 09:00:00
**生成方式**: AI 自动生成

---

## 一、交易概况

本周（2026年1月1日至1月7日），公司在广东电力交易中心完成各类交易如下：

| 交易类型 | 交易电量(MWh) | 交易金额(万元) | 均价(元/MWh) |
|---------|-------------|--------------|-------------|
| 中长期 | 100,000 | 4,650 | 465.00 |
| 日前现货 | 20,000 | 976 | 488.00 |
| 日内现货 | 5,000 | 246 | 492.00 |
| **合计** | **125,000** | **5,872** | **469.76** |

## 二、市场行情分析

### 2.1 价格走势

本周广东日前现货价格呈现以下特点：
- **均价**: 488.32 元/MWh，环比上涨 2.1%
- **最高价**: 612.45 元/MWh（1月5日 16:00）
- **最低价**: 398.20 元/MWh（1月3日 04:00）

### 2.2 影响因素

1. **负荷因素**: 受寒潮影响，本周用电负荷同比增长 8.5%
2. **供给因素**: 3台火电机组临时检修，装机容量减少 150 万千瓦
3. **新能源**: 风电出力偏弱，日均发电量较上周下降 12%

## 三、持仓分析

| 合同类型 | 剩余电量(MWh) | 合同价格(元) | 建议操作 |
|---------|-------------|-------------|---------|
| 年度长协 | 41,500 | 465.00 | 继续执行 |
| 月度双边 | 3,800 | 478.50 | 适时补充 |

## 四、风险提示

1. ⚠️ 下周预计持续低温，电价可能进一步上涨
2. ⚠️ 现货敞口占比达 20%，建议控制在 15% 以内
3. ⚠️ 关注 1月10日月度竞价，合理安排报价策略

## 五、AI 建议

基于当前市场情况，建议：
1. **增加中长期锁定比例**：将月度合同占比提高至 75%
2. **优化现货交易时段**：重点在凌晨低谷时段采购
3. **关注跨省交易机会**：浙江-广东价差有套利空间

---

*本报告由 PowerX AI 系统自动生成，仅供参考。*
`;

const Report: React.FC = () => {
  const [previewVisible, setPreviewVisible] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [selectedReportType, setSelectedReportType] = useState('DAILY');
  const { token } = theme.useToken();

  // 报告类型配置
  const reportTypeConfig: Record<string, { color: string; text: string }> = {
    DAILY: { color: 'blue', text: '日报' },
    WEEKLY: { color: 'purple', text: '周报' },
    MONTHLY: { color: 'orange', text: '月报' },
    ANALYSIS: { color: 'cyan', text: '专题分析' }
  };

  // 生成新报告
  const handleGenerateReport = () => {
    setGenerating(true);
    message.loading('AI 正在接入市场数据并分析中...', 2);
    setTimeout(() => {
      setGenerating(false);
      message.success('智能分析报告生成完成！');
    }, 3000);
  };

  // 报告表格列
  const reportColumns = [
    { 
      title: '报告编号', 
      dataIndex: 'id', 
      key: 'id',
      render: (text: string) => <Text copyable className="data-font" style={{ fontSize: 13 }}>{text}</Text>
    },
    { 
      title: '报告标题', 
      dataIndex: 'title', 
      key: 'title',
      render: (text: string) => <Text strong>{text}</Text>
    },
    { 
      title: '类型', 
      dataIndex: 'type', 
      key: 'type',
      render: (type: string) => (
        <Tag color={reportTypeConfig[type]?.color} bordered={false}>
          {reportTypeConfig[type]?.text}
        </Tag>
      )
    },
    { 
      title: '生成时间', 
      dataIndex: 'createTime', 
      key: 'createTime',
      render: (text: string) => <span className="data-font" style={{ fontSize: 13, color: token.colorTextSecondary }}>{text}</span>
    },
    { 
      title: '状态', 
      dataIndex: 'status', 
      key: 'status',
      render: (status: string) => (
        <Tag 
          icon={status === 'GENERATING' ? <Spin size="small" /> : null}
          color={status === 'COMPLETED' ? 'success' : 'processing'}
          bordered={false}
        >
          {status === 'COMPLETED' ? '已就绪' : '生成中'}
        </Tag>
      )
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Space size="middle">
          {record.status === 'COMPLETED' ? (
            <>
              <Tooltip title="预览">
                <Button 
                  type="text" 
                  size="small" 
                  icon={<EyeOutlined />}
                  onClick={() => setPreviewVisible(true)}
                  style={{ color: token.colorPrimary }}
                />
              </Tooltip>
              <Tooltip title="导出 PDF">
                <Button type="text" size="small" icon={<FilePdfOutlined />} style={{ color: token.colorError }} />
              </Tooltip>
              <Tooltip title="导出 Excel">
                <Button type="text" size="small" icon={<FileExcelOutlined />} style={{ color: token.colorSuccess }} />
              </Tooltip>
            </>
          ) : (
            <Text type="secondary" style={{ fontSize: 12 }}>处理中...</Text>
          )}
        </Space>
      )
    }
  ];

  return (
    <PageContainer
      header={{
        title: '分析报表中心',
        subTitle: '由 AI 驱动的市场交易分析与资产经营报告'
      }}
    >
      <Row gutter={[24, 24]}>
        {/* 快速生成 */}
        <Col xs={24} lg={8}>
          <Card 
            className="hover-card"
            title={
              <Space>
                <div style={{ 
                  width: 24, height: 24, borderRadius: 6, background: 'rgba(114, 46, 209, 0.1)', 
                  display: 'flex', alignItems: 'center', justifyContent: 'center' 
                }}>
                  <RobotOutlined style={{ color: '#722ed1', fontSize: 14 }} />
                </div>
                <span>智能报告工作站</span>
              </Space>
            }
            style={{ borderRadius: 12, border: 'none' }}
          >
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <div>
                <Text type="secondary" style={{ fontSize: 12 }}>分析任务类型</Text>
                <Select 
                  value={selectedReportType}
                  onChange={setSelectedReportType}
                  style={{ width: '100%', marginTop: 8 }}
                >
                  <Option value="DAILY">交易日报分析</Option>
                  <Option value="WEEKLY">周度经营回顾</Option>
                  <Option value="MONTHLY">月度结算报告</Option>
                  <Option value="ANALYSIS">市场专题研报</Option>
                </Select>
              </div>

              <div>
                <Text type="secondary" style={{ fontSize: 12 }}>分析时间跨度</Text>
                <DatePicker 
                  style={{ width: '100%', marginTop: 8 }}
                  picker={selectedReportType === 'MONTHLY' ? 'month' : selectedReportType === 'WEEKLY' ? 'week' : 'date'}
                  defaultValue={dayjs()}
                />
              </div>

              <div>
                <Text type="secondary" style={{ fontSize: 12 }}>包含分析维度</Text>
                <Select 
                  mode="multiple"
                  placeholder="选择包含内容"
                  style={{ width: '100%', marginTop: 8 }}
                  maxTagCount="responsive"
                  defaultValue={['trading', 'market', 'risk']}
                >
                  <Option value="trading">交易执行汇总</Option>
                  <Option value="market">现货市场深度分析</Option>
                  <Option value="position">资产持仓分布</Option>
                  <Option value="risk">风险敞口评估</Option>
                  <Option value="suggestion">智能优化策略建议</Option>
                </Select>
              </div>

              <Button 
                type="primary" 
                icon={<RobotOutlined />} 
                block
                loading={generating}
                onClick={handleGenerateReport}
                style={{ height: 44, borderRadius: 8, marginTop: 8, boxShadow: `0 4px 12px ${token.colorPrimary}40` }}
              >
                开始智能分析
              </Button>
            </Space>
          </Card>

          {/* 报告模板 */}
          <Card 
            className="hover-card"
            title={
              <Space>
                <FileTextOutlined style={{ color: token.colorPrimary }} />
                <span>分析模板库</span>
              </Space>
            }
            style={{ marginTop: 24, borderRadius: 12, border: 'none' }}
          >
            <List
              size="small"
              dataSource={[
                { title: '标准交易日报', desc: '核心价格、交易量、损益' },
                { title: '深度回顾周报', desc: '含多维趋势对比及预测对比' },
                { title: '月度经营报告', desc: '经营数据全面汇总' },
                { title: '市场洞察专题', desc: '针对特定市场事件的深度剖析' }
              ]}
              renderItem={(item) => (
                <List.Item
                  actions={[<Button type="link" size="small">加载</Button>]}
                  style={{ padding: '12px 0' }}
                >
                  <List.Item.Meta
                    avatar={<div style={{ 
                      width: 32, height: 32, borderRadius: 6, background: 'rgba(255,255,255,0.03)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center'
                    }}>
                      <FileTextOutlined style={{ color: token.colorTextSecondary }} />
                    </div>}
                    title={<Text style={{ fontSize: 13 }}>{item.title}</Text>}
                    description={<Text type="secondary" style={{ fontSize: 12 }}>{item.desc}</Text>}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>

        {/* 报告列表 */}
        <Col xs={24} lg={16}>
          <Card 
            className="hover-card"
            title={
              <Space>
                <ReloadOutlined style={{ color: token.colorSuccess }} />
                <span>归档分析报告库</span>
              </Space>
            }
            extra={
              <Button icon={<ReloadOutlined />} type="text" size="small">同步云端</Button>
            }
            style={{ borderRadius: 12, border: 'none' }}
          >
            <Table 
              columns={reportColumns}
              dataSource={mockReports}
              rowKey="id"
              pagination={{ pageSize: 8, showSizeChanger: false }}
              expandable={{
                expandedRowRender: (record) => (
                  <div style={{ padding: '0 16px', color: token.colorTextSecondary }}>
                    <Paragraph ellipsis={{ rows: 2 }} style={{ margin: 0 }}>
                      <Text strong style={{ marginRight: 8 }}>智能摘要:</Text>
                      {record.summary}
                    </Paragraph>
                  </div>
                )
              }}
            />
          </Card>
        </Col>
      </Row>

      {/* 报告预览弹窗 */}
      <Modal
        title={
          <Space>
            <RobotOutlined style={{ color: token.colorPrimary }} />
            <span>AI 智能报告预览</span>
          </Space>
        }
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        footer={[
          <Button key="pdf" icon={<FilePdfOutlined />}>导出 PDF</Button>,
          <Button key="excel" icon={<FileExcelOutlined />}>导出 Excel</Button>,
          <Button key="close" type="primary" onClick={() => setPreviewVisible(false)}>完成阅览</Button>
        ]}
        width={1000}
        centered
        styles={{ body: { padding: 0 } }}
      >
        <div 
          style={{ 
            height: 650, 
            overflowY: 'auto', 
            padding: 40,
            backgroundColor: '#0a0a0a',
            backgroundImage: 'radial-gradient(circle at 50% 0%, rgba(22, 119, 255, 0.05) 0%, transparent 50%)',
          }}
        >
          <div style={{ maxWidth: 800, margin: '0 auto' }}>
            <pre style={{ 
              whiteSpace: 'pre-wrap', 
              fontFamily: 'inherit',
              fontSize: 14,
              lineHeight: 1.8,
              color: 'rgba(255,255,255,0.85)',
              margin: 0 
            }}>
              {mockReportContent}
            </pre>
          </div>
        </div>
      </Modal>
    </PageContainer>
  );
};

export default Report;
