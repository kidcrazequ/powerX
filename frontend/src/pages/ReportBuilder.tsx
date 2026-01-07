/**
 * PowerX 报表生成器页面
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 */
import React, { useState, useEffect } from 'react';
import { 
  Card, Row, Col, Button, Space, Select, Input, Modal, Form, 
  Table, Tabs, Empty, message, Dropdown, theme, Tag 
} from 'antd';
import { 
  PlusOutlined, FileTextOutlined, DownloadOutlined, 
  EditOutlined, DeleteOutlined, PlayCircleOutlined,
  LineChartOutlined, BarChartOutlined, PieChartOutlined, TableOutlined
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';

interface Template {
  id: number;
  name: string;
  description: string;
  type: string;
  is_public: boolean;
}

interface ChartData {
  type: string;
  title: string;
  data: any;
}

const chartIcons: Record<string, React.ReactNode> = {
  line: <LineChartOutlined />,
  bar: <BarChartOutlined />,
  pie: <PieChartOutlined />,
  table: <TableOutlined />
};

const ReportBuilder: React.FC = () => {
  const { token } = theme.useToken();
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<number | null>(null);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [previewData, setPreviewData] = useState<any>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    // 模拟加载模板列表
    setTemplates([
      { id: 1, name: '日交易汇总报表', description: '每日交易数据汇总', type: 'trading', is_public: true },
      { id: 2, name: '月度结算报表', description: '月度结算数据分析', type: 'settlement', is_public: false },
      { id: 3, name: '风险敞口报表', description: '风险敞口监控报表', type: 'risk', is_public: false },
    ]);
  }, []);

  const handleCreateTemplate = () => {
    form.validateFields().then(values => {
      const newTemplate: Template = {
        id: templates.length + 1,
        ...values,
        is_public: false
      };
      setTemplates([...templates, newTemplate]);
      message.success('模板创建成功');
      setCreateModalVisible(false);
      form.resetFields();
    });
  };

  const handleGenerateReport = (templateId: number) => {
    message.loading('正在生成报表...', 1);
    setTimeout(() => {
      // 模拟生成报表数据
      setPreviewData({
        summary: { total_trades: 256, total_volume: 35420.5, total_amount: 2856000, avg_price: 412.5 },
        trends: Array.from({ length: 30 }, (_, i) => ({
          date: `2026-01-${String(i + 1).padStart(2, '0')}`,
          volume: Math.random() * 500 + 100,
          price: Math.random() * 100 + 350
        })),
        distribution: [
          { category: '现货交易', value: 45 },
          { category: '中长期交易', value: 35 },
          { category: '合同交易', value: 20 }
        ]
      });
      message.success('报表生成成功');
    }, 1000);
  };

  const lineChartOption = previewData ? {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: previewData.trends.map((t: any) => t.date.slice(5)) },
    yAxis: { type: 'value' },
    series: [{ data: previewData.trends.map((t: any) => t.price.toFixed(2)), type: 'line', smooth: true }]
  } : {};

  const pieChartOption = previewData ? {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie', radius: '60%',
      data: previewData.distribution.map((d: any) => ({ name: d.category, value: d.value }))
    }]
  } : {};

  const columns = [
    { title: '模板名称', dataIndex: 'name', key: 'name' },
    { title: '描述', dataIndex: 'description', key: 'description' },
    { title: '类型', dataIndex: 'type', key: 'type', render: (type: string) => (
      <Tag color={type === 'trading' ? 'blue' : type === 'settlement' ? 'green' : 'orange'}>{type}</Tag>
    )},
    { title: '公开', dataIndex: 'is_public', key: 'is_public', render: (v: boolean) => v ? '是' : '否' },
    { 
      title: '操作', key: 'action', 
      render: (_: any, record: Template) => (
        <Space>
          <Button type="link" size="small" icon={<PlayCircleOutlined />} onClick={() => handleGenerateReport(record.id)}>生成</Button>
          <Button type="link" size="small" icon={<EditOutlined />}>编辑</Button>
          <Button type="link" size="small" danger icon={<DeleteOutlined />}>删除</Button>
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: 24 }}>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0, color: token.colorTextHeading }}>
          <FileTextOutlined style={{ marginRight: 8 }} />
          报表生成器
        </h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateModalVisible(true)}>
          创建模板
        </Button>
      </div>

      <Tabs defaultActiveKey="templates" items={[
        {
          key: 'templates',
          label: '模板管理',
          children: (
            <Card>
              <Table dataSource={templates} columns={columns} rowKey="id" pagination={false} />
            </Card>
          )
        },
        {
          key: 'preview',
          label: '报表预览',
          children: previewData ? (
            <div>
              <Row gutter={16} style={{ marginBottom: 16 }}>
                <Col span={6}><Card><div style={{ textAlign: 'center' }}><div style={{ fontSize: 24, fontWeight: 'bold', color: token.colorPrimary }}>{previewData.summary.total_trades}</div><div>交易笔数</div></div></Card></Col>
                <Col span={6}><Card><div style={{ textAlign: 'center' }}><div style={{ fontSize: 24, fontWeight: 'bold', color: token.colorSuccess }}>{previewData.summary.total_volume.toLocaleString()}</div><div>总电量(MWh)</div></div></Card></Col>
                <Col span={6}><Card><div style={{ textAlign: 'center' }}><div style={{ fontSize: 24, fontWeight: 'bold', color: token.colorWarning }}>{(previewData.summary.total_amount / 10000).toFixed(1)}万</div><div>总金额</div></div></Card></Col>
                <Col span={6}><Card><div style={{ textAlign: 'center' }}><div style={{ fontSize: 24, fontWeight: 'bold' }}>{previewData.summary.avg_price}</div><div>均价(元/MWh)</div></div></Card></Col>
              </Row>
              <Row gutter={16}>
                <Col span={16}>
                  <Card title="价格走势">
                    <ReactECharts option={lineChartOption} style={{ height: 300 }} />
                  </Card>
                </Col>
                <Col span={8}>
                  <Card title="交易分布">
                    <ReactECharts option={pieChartOption} style={{ height: 300 }} />
                  </Card>
                </Col>
              </Row>
              <div style={{ marginTop: 16, textAlign: 'right' }}>
                <Space>
                  <Button icon={<DownloadOutlined />}>导出 PDF</Button>
                  <Button icon={<DownloadOutlined />}>导出 Excel</Button>
                </Space>
              </div>
            </div>
          ) : (
            <Card>
              <Empty description="请先选择模板并生成报表" />
            </Card>
          )
        }
      ]} />

      <Modal title="创建报表模板" open={createModalVisible} onOk={handleCreateTemplate} onCancel={() => setCreateModalVisible(false)}>
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="模板名称" rules={[{ required: true, message: '请输入模板名称' }]}>
            <Input placeholder="输入模板名称" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea placeholder="输入模板描述" rows={3} />
          </Form.Item>
          <Form.Item name="type" label="报表类型" rules={[{ required: true }]}>
            <Select placeholder="选择报表类型">
              <Select.Option value="trading">交易报表</Select.Option>
              <Select.Option value="settlement">结算报表</Select.Option>
              <Select.Option value="risk">风险报表</Select.Option>
              <Select.Option value="market">市场报表</Select.Option>
              <Select.Option value="custom">自定义</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ReportBuilder;
