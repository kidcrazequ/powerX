/**
 * PowerX 预测对账页面
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 展示 AI 预测与实际结果的对比分析
 */

import React, { useState, useEffect } from 'react';
import { 
  Card, Table, Button, Space, Tag, Statistic, Row, Col, DatePicker, 
  Select, message, theme
} from 'antd';
import { 
  CheckCircleOutlined, CloseCircleOutlined, SyncOutlined,
  RiseOutlined, PercentageOutlined, AimOutlined, ReloadOutlined
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { useSettingsStore } from '../stores/settingsStore';
import api from '../services/api';

const { useToken } = theme;

interface PredictionRecord {
  prediction_id: string;
  prediction_type: string;
  province: string;
  target_time: string;
  predicted_value: number;
  actual_value?: number;
  error_percentage?: number;
  within_range: boolean;
  is_reconciled: boolean;
}

interface AccuracyMetrics {
  total_predictions: number;
  mape: number;
  range_hit_rate: number;
  trend_accuracy: number;
}

const PredictionReconciliation: React.FC = () => {
  const { token } = useToken();
  const { themeMode } = useSettingsStore();
  const [records, setRecords] = useState<PredictionRecord[]>([]);
  const [metrics, setMetrics] = useState<AccuracyMetrics | null>(null);
  const [trendData, setTrendData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [reconciling, setReconciling] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      // 模拟数据
      setRecords([
        {
          prediction_id: 'PRED-20260107-ABC123',
          prediction_type: 'price',
          province: 'guangdong',
          target_time: '2026-01-07T10:00:00',
          predicted_value: 450.5,
          actual_value: 448.2,
          error_percentage: 0.51,
          within_range: true,
          is_reconciled: true
        },
        {
          prediction_id: 'PRED-20260107-DEF456',
          prediction_type: 'price',
          province: 'guangdong',
          target_time: '2026-01-07T11:00:00',
          predicted_value: 455.0,
          actual_value: 460.5,
          error_percentage: 1.21,
          within_range: true,
          is_reconciled: true
        },
        {
          prediction_id: 'PRED-20260107-GHI789',
          prediction_type: 'load',
          province: 'guangdong',
          target_time: '2026-01-07T12:00:00',
          predicted_value: 12500,
          actual_value: null,
          error_percentage: null,
          within_range: false,
          is_reconciled: false
        }
      ]);

      setMetrics({
        total_predictions: 156,
        mape: 2.35,
        range_hit_rate: 0.89,
        trend_accuracy: 0.78
      });

      setTrendData([
        { date: '01-01', mape: 3.2, range_hit_rate: 0.85 },
        { date: '01-02', mape: 2.8, range_hit_rate: 0.87 },
        { date: '01-03', mape: 2.5, range_hit_rate: 0.88 },
        { date: '01-04', mape: 2.3, range_hit_rate: 0.90 },
        { date: '01-05', mape: 2.1, range_hit_rate: 0.91 },
        { date: '01-06', mape: 2.4, range_hit_rate: 0.89 },
        { date: '01-07', mape: 2.2, range_hit_rate: 0.92 }
      ]);
    } catch (error) {
      message.error('加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  const handleReconcile = async () => {
    setReconciling(true);
    try {
      await api.post('/prediction/reconcile/batch');
      message.success('对账完成');
      loadData();
    } catch (error) {
      message.error('对账失败');
    } finally {
      setReconciling(false);
    }
  };

  const getChartOption = () => ({
    tooltip: { 
      trigger: 'axis',
      backgroundColor: themeMode === 'dark' ? 'rgba(20, 20, 20, 0.9)' : 'rgba(255, 255, 255, 0.95)',
      borderColor: token.colorBorderSecondary,
      textStyle: { color: token.colorText }
    },
    legend: { 
      data: ['MAPE (%)', '区间命中率'], 
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
      data: trendData.map(d => d.date),
      axisLine: { lineStyle: { color: token.colorBorderSecondary } },
      axisLabel: { color: token.colorTextSecondary }
    },
    yAxis: [
      { 
        type: 'value', 
        name: 'MAPE (%)', 
        position: 'left',
        axisLine: { lineStyle: { color: token.colorBorderSecondary } },
        axisLabel: { color: token.colorTextSecondary },
        nameTextStyle: { color: token.colorTextSecondary },
        splitLine: { lineStyle: { color: token.colorBorderSecondary, type: 'dashed' } }
      },
      { 
        type: 'value', 
        name: '命中率', 
        position: 'right', 
        max: 1,
        axisLine: { lineStyle: { color: token.colorBorderSecondary } },
        axisLabel: { color: token.colorTextSecondary },
        nameTextStyle: { color: token.colorTextSecondary },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: 'MAPE (%)',
        type: 'line',
        data: trendData.map(d => d.mape),
        smooth: true,
        itemStyle: { color: token.colorPrimary },
        lineStyle: { color: token.colorPrimary, width: 2 }
      },
      {
        name: '区间命中率',
        type: 'bar',
        yAxisIndex: 1,
        data: trendData.map(d => d.range_hit_rate),
        itemStyle: { 
          color: token.colorSuccess,
          borderRadius: [4, 4, 0, 0]
        }
      }
    ]
  });

  const columns = [
    {
      title: '预测ID',
      dataIndex: 'prediction_id',
      key: 'prediction_id',
      render: (text: string) => <Tag color="blue">{text}</Tag>
    },
    {
      title: '类型',
      dataIndex: 'prediction_type',
      key: 'prediction_type',
      render: (type: string) => {
        const labels: Record<string, string> = {
          price: '价格预测',
          load: '负荷预测',
          trend: '趋势预测'
        };
        return labels[type] || type;
      }
    },
    {
      title: '目标时间',
      dataIndex: 'target_time',
      key: 'target_time',
      render: (time: string) => new Date(time).toLocaleString()
    },
    {
      title: '预测值',
      dataIndex: 'predicted_value',
      key: 'predicted_value',
      render: (val: number) => val?.toFixed(2)
    },
    {
      title: '实际值',
      dataIndex: 'actual_value',
      key: 'actual_value',
      render: (val: number) => val ? val.toFixed(2) : '-'
    },
    {
      title: '误差',
      dataIndex: 'error_percentage',
      key: 'error_percentage',
      render: (val: number) => {
        if (val === null) return '-';
        const color = val < 2 ? 'green' : val < 5 ? 'orange' : 'red';
        return <Tag color={color}>{val.toFixed(2)}%</Tag>;
      }
    },
    {
      title: '区间命中',
      dataIndex: 'within_range',
      key: 'within_range',
      render: (hit: boolean, record: PredictionRecord) => {
        if (!record.is_reconciled) return '-';
        return hit ? 
          <CheckCircleOutlined style={{ color: token.colorSuccess }} /> : 
          <CloseCircleOutlined style={{ color: token.colorError }} />;
      }
    },
    {
      title: '状态',
      dataIndex: 'is_reconciled',
      key: 'is_reconciled',
      render: (reconciled: boolean) => (
        <Tag color={reconciled ? 'success' : 'warning'}>
          {reconciled ? '已对账' : '待对账'}
        </Tag>
      )
    }
  ];

  return (
    <div style={{ padding: 24 }}>
      {/* 统计卡片 */}
      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总预测数"
              value={metrics?.total_predictions || 0}
              prefix={<AimOutlined />}
              valueStyle={{ color: token.colorPrimary }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="平均误差 (MAPE)"
              value={metrics?.mape || 0}
              suffix="%"
              precision={2}
              prefix={<PercentageOutlined />}
              valueStyle={{ color: token.colorSuccess }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="区间命中率"
              value={(metrics?.range_hit_rate || 0) * 100}
              suffix="%"
              precision={1}
              valueStyle={{ color: token.colorWarning }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="趋势准确率"
              value={(metrics?.trend_accuracy || 0) * 100}
              suffix="%"
              precision={1}
              prefix={<RiseOutlined />}
              valueStyle={{ color: token.colorInfo }}
            />
          </Card>
        </Col>
      </Row>

      {/* 趋势图表 */}
      <Card
        title={
          <Space>
            <RiseOutlined style={{ color: token.colorPrimary }} />
            <span>准确率趋势</span>
          </Space>
        }
        style={{ marginTop: 16 }}
        extra={
          <Button icon={<ReloadOutlined />} onClick={loadData}>刷新</Button>
        }
      >
        <ReactECharts 
          key={themeMode}
          option={getChartOption()} 
          style={{ height: 300 }} 
        />
      </Card>

      {/* 对账记录 */}
      <Card
        title={
          <Space>
            <AimOutlined style={{ color: token.colorPrimary }} />
            <span>预测对账记录</span>
          </Space>
        }
        style={{ marginTop: 16 }}
        extra={
          <Space>
            <Select defaultValue="price" style={{ width: 120 }}>
              <Select.Option value="price">价格预测</Select.Option>
              <Select.Option value="load">负荷预测</Select.Option>
              <Select.Option value="all">全部</Select.Option>
            </Select>
            <Button
              type="primary"
              icon={<SyncOutlined spin={reconciling} />}
              onClick={handleReconcile}
              loading={reconciling}
            >
              批量对账
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={records}
          rowKey="prediction_id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  );
};

export default PredictionReconciliation;
