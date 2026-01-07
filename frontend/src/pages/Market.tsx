/**
 * PowerX 市场数据页面 - 现代版
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 展示各省电力市场数据和分析
 */

import React, { useState } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Select, 
  Table, 
  Tag, 
  Space, 
  Typography, 
  Tabs, 
  DatePicker, 
  Statistic,
  theme
} from 'antd';
import { 
  LineChartOutlined,
  AreaChartOutlined,
  ThunderboltOutlined,
  RiseOutlined,
  FallOutlined,
  GlobalOutlined,
  CalendarOutlined
} from '@ant-design/icons';
import { PageContainer, StatisticCard } from '@ant-design/pro-components';
import ReactECharts from 'echarts-for-react';
import dayjs from 'dayjs';
import { useSettingsStore } from '../stores/settingsStore';

const { Text, Title } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;

// 模拟各省电价数据
const mockProvinceData: Record<string, any> = {
  '广东': {
    avgPrice: 485.32,
    maxPrice: 612.45,
    minPrice: 398.20,
    volume: 125840,
    priceChange: 2.66,
    hourlyPrices: [445, 428, 412, 398, 405, 418, 456, 498, 512, 525, 518, 502, 495, 488, 478, 485, 492, 505, 515, 508, 495, 478, 462, 448]
  },
  '浙江': {
    avgPrice: 492.18,
    maxPrice: 598.30,
    minPrice: 412.50,
    volume: 98560,
    priceChange: -1.25,
    hourlyPrices: [455, 438, 422, 412, 418, 428, 465, 502, 520, 538, 532, 518, 505, 498, 488, 495, 502, 515, 525, 518, 502, 485, 468, 455]
  },
  '山东': {
    avgPrice: 452.45,
    maxPrice: 542.80,
    minPrice: -25.00,
    volume: 156780,
    priceChange: -3.82,
    hourlyPrices: [320, 280, 245, 198, -25, 85, 320, 428, 465, 498, 512, 495, 478, 465, 448, 458, 475, 498, 520, 508, 485, 412, 365, 328]
  }
};

// 价格热力图配置
const getHeatmapOption = (province: string, token: any, themeMode: string) => {
  const data = mockProvinceData[province].hourlyPrices;
  const hours = Array.from({ length: 24 }, (_, i) => `${i.toString().padStart(2, '0')}:00`);
  const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
  
  const heatmapData: number[][] = [];
  for (let d = 0; d < 7; d++) {
    for (let h = 0; h < 24; h++) {
      const basePrice = data[h];
      const variation = (Math.random() - 0.5) * 50;
      heatmapData.push([h, d, Math.round(basePrice + variation)]);
    }
  }

  return {
    tooltip: {
      position: 'top',
      backgroundColor: themeMode === 'dark' ? 'rgba(20, 20, 20, 0.9)' : 'rgba(255, 255, 255, 0.9)',
      borderColor: token.colorBorderSecondary,
      textStyle: { color: token.colorText },
      formatter: (params: any) => {
        return `${days[params.value[1]]} ${hours[params.value[0]]}<br/>电价: <span style="color:${token.colorPrimary};font-weight:bold">${params.value[2]}</span> 元/MWh`;
      }
    },
    grid: {
      left: '3%',
      right: '8%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: hours,
      splitArea: { show: true },
      axisLabel: { color: token.colorTextDescription },
      axisLine: { lineStyle: { color: themeMode === 'dark' ? token.colorBorderSecondary : 'rgba(0,0,0,0.15)' } }
    },
    yAxis: {
      type: 'category',
      data: days,
      splitArea: { show: true },
      axisLabel: { color: token.colorTextDescription },
      axisLine: { lineStyle: { color: themeMode === 'dark' ? token.colorBorderSecondary : 'rgba(0,0,0,0.15)' } }
    },
    visualMap: {
      min: province === '山东' ? -50 : 350,
      max: 600,
      calculable: true,
      orient: 'vertical',
      right: '2%',
      top: 'center',
      textStyle: { color: token.colorTextDescription },
      inRange: {
        color: ['#1677ff', '#faad14', '#f5222d']
      }
    },
    series: [{
      name: '电价',
      type: 'heatmap',
      data: heatmapData,
      label: { show: false },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  };
};

// 价格走势对比图
const getComparisonChartOption = (token: any, themeMode: string) => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'cross' },
    backgroundColor: themeMode === 'dark' ? 'rgba(20, 20, 20, 0.9)' : 'rgba(255, 255, 255, 0.9)',
    borderColor: token.colorBorderSecondary,
    textStyle: { color: token.colorText }
  },
  legend: {
    data: ['广东', '浙江', '山东'],
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
    boundaryGap: false,
    data: Array.from({ length: 24 }, (_, i) => `${i.toString().padStart(2, '0')}:00`),
    axisLabel: { color: token.colorTextDescription },
    axisLine: { lineStyle: { color: themeMode === 'dark' ? token.colorBorderSecondary : 'rgba(0,0,0,0.15)' } }
  },
  yAxis: {
    type: 'value',
    name: '元/MWh',
    min: -50,
    max: 600,
    axisLabel: { color: token.colorTextDescription },
    nameTextStyle: { color: token.colorTextDescription },
    axisLine: { show: true, lineStyle: { color: themeMode === 'dark' ? token.colorBorderSecondary : 'rgba(0,0,0,0.15)' } },
    splitLine: { lineStyle: { color: themeMode === 'dark' ? token.colorBorderSecondary : 'rgba(0,0,0,0.06)', type: 'dashed' } }
  },
  series: [
    {
      name: '广东',
      type: 'line',
      smooth: true,
      data: mockProvinceData['广东'].hourlyPrices,
      lineStyle: { color: '#1890ff', width: 2 },
      itemStyle: { color: '#1890ff' }
    },
    {
      name: '浙江',
      type: 'line',
      smooth: true,
      data: mockProvinceData['浙江'].hourlyPrices,
      lineStyle: { color: '#52c41a', width: 2 },
      itemStyle: { color: '#52c41a' }
    },
    {
      name: '山东',
      type: 'line',
      smooth: true,
      data: mockProvinceData['山东'].hourlyPrices,
      lineStyle: { color: '#faad14', width: 2 },
      itemStyle: { color: '#faad14' }
    }
  ]
});

// 成交量图配置
const getVolumeChartOption = (token: any, themeMode: string) => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: themeMode === 'dark' ? 'rgba(20, 20, 20, 0.9)' : 'rgba(255, 255, 255, 0.9)',
    borderColor: token.colorBorderSecondary,
    textStyle: { color: token.colorText }
  },
  legend: {
    data: ['广东', '浙江', '山东'],
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
    data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
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
      name: '广东',
      type: 'bar',
      data: [12580, 15420, 14230, 16890, 15840, 8920, 7650],
      itemStyle: { color: '#1890ff' }
    },
    {
      name: '浙江',
      type: 'bar',
      data: [9856, 11280, 10450, 12350, 11560, 6820, 5980],
      itemStyle: { color: '#52c41a' }
    },
    {
      name: '山东',
      type: 'bar',
      data: [15678, 18240, 16890, 19560, 18340, 10250, 9120],
      itemStyle: { color: '#faad14' }
    }
  ]
});

const Market: React.FC = () => {
  const [selectedProvince, setSelectedProvince] = useState('广东');
  const provinceData = mockProvinceData[selectedProvince];
  const { token } = theme.useToken();
  const { themeMode } = useSettingsStore();

  // 历史价格表格列
  const priceColumns = [
    { title: '时段', dataIndex: 'hour', key: 'hour', render: (text: string) => <span className="data-font">{text}</span> },
    { 
      title: '日前价格', 
      dataIndex: 'dayAhead', 
      key: 'dayAhead',
      render: (val: number) => <span className="data-font">{val.toFixed(2)} 元</span>
    },
    { 
      title: '实时价格', 
      dataIndex: 'realtime', 
      key: 'realtime',
      render: (val: number) => <span className="data-font">{val.toFixed(2)} 元</span>
    },
    { 
      title: '成交量', 
      dataIndex: 'volume', 
      key: 'volume',
      render: (val: number) => <span className="data-font">{val.toLocaleString()} MWh</span>
    },
    { 
      title: '趋势', 
      dataIndex: 'change', 
      key: 'change',
      render: (val: number) => (
        <Space>
          {val >= 0 ? <RiseOutlined style={{ color: token.colorSuccess }} /> : <FallOutlined style={{ color: token.colorError }} />}
          <Text className="data-font" style={{ color: val >= 0 ? token.colorSuccess : token.colorError }}>
            {val >= 0 ? '+' : ''}{val.toFixed(2)}%
          </Text>
        </Space>
      )
    }
  ];

  // 生成表格数据
  const priceTableData = Array.from({ length: 24 }, (_, i) => ({
    key: i,
    hour: `${i.toString().padStart(2, '0')}:00`,
    dayAhead: provinceData.hourlyPrices[i],
    realtime: provinceData.hourlyPrices[i] + (Math.random() - 0.5) * 10,
    volume: Math.round(1000 + Math.random() * 2000),
    change: (Math.random() - 0.5) * 10
  }));

  return (
    <PageContainer
      header={{
        title: '市场数据终端',
        subTitle: '全省电力市场多维实时监测与深度行情分析'
      }}
    >
      <Row gutter={[24, 24]}>
        <Col span={24}>
          <Card 
            className="hover-card"
            style={{ borderRadius: 12, border: 'none' }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
              <Space size="large">
                <div>
                  <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>区域选择</Text>
                  <Select 
                    value={selectedProvince} 
                    onChange={setSelectedProvince}
                    style={{ width: 120 }}
                    variant="borderless"
                    suffixIcon={<GlobalOutlined />}
                  >
                    <Option value="广东">广东市场</Option>
                    <Option value="浙江">浙江市场</Option>
                    <Option value="山东">山东市场</Option>
                  </Select>
                </div>
                <div>
                  <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>时间跨度</Text>
                  <RangePicker 
                    defaultValue={[dayjs().subtract(7, 'day'), dayjs()]}
                    variant="borderless"
                    suffixIcon={<CalendarOutlined />}
                  />
                </div>
              </Space>
              
              <Row gutter={48}>
                <Col>
                  <Statistic 
                    title={<Text type="secondary" style={{ fontSize: 12 }}>日均电价 (MCP)</Text>}
                    value={provinceData.avgPrice} 
                    suffix={<span style={{ fontSize: 12 }}>元/MWh</span>}
                    precision={2}
                    valueStyle={{ fontSize: 24 }}
                  />
                </Col>
                <Col>
                  <Statistic 
                    title={<Text type="secondary" style={{ fontSize: 12 }}>日内峰值</Text>}
                    value={provinceData.maxPrice} 
                    suffix={<span style={{ fontSize: 12 }}>元/MWh</span>}
                    valueStyle={{ color: token.colorError, fontSize: 24 }}
                    precision={2}
                  />
                </Col>
                <Col>
                  <Statistic 
                    title={<Text type="secondary" style={{ fontSize: 12 }}>日内谷值</Text>}
                    value={provinceData.minPrice} 
                    suffix={<span style={{ fontSize: 12 }}>元/MWh</span>}
                    valueStyle={{ color: provinceData.minPrice < 0 ? token.colorError : token.colorSuccess, fontSize: 24 }}
                    precision={2}
                  />
                </Col>
              </Row>
            </div>
          </Card>
        </Col>
      </Row>

      <div style={{ background: themeMode === 'dark' ? 'rgba(255,255,255,0.02)' : 'rgba(0,0,0,0.02)', borderRadius: 12, padding: 4, marginTop: 24 }}>
        <Tabs defaultActiveKey="comparison" centered>
          <Tabs.TabPane 
            tab={<Space><LineChartOutlined /> 价格走势对比</Space>}
            key="comparison"
          >
            <div style={{ padding: '12px 24px 24px' }}>
              <ReactECharts 
                key={themeMode}
                option={getComparisonChartOption(token, themeMode)} 
                style={{ height: 450 }} 
                theme={themeMode} 
              />
            </div>
          </Tabs.TabPane>

          <Tabs.TabPane 
            tab={<Space><AreaChartOutlined /> 价格热力分布</Space>}
            key="heatmap"
          >
            <div style={{ padding: '12px 24px 24px' }}>
              <ReactECharts 
                key={themeMode}
                option={getHeatmapOption(selectedProvince, token, themeMode)} 
                style={{ height: 450 }} 
                theme={themeMode} 
              />
              {selectedProvince === '山东' && (
                <div style={{ marginTop: 16, padding: '8px 16px', background: `${token.colorPrimary}15`, borderRadius: 6 }}>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    <ThunderboltOutlined style={{ color: token.colorPrimary, marginRight: 8 }} />
                    山东电力市场特色：支持负电价机制。图表中蓝色深色区域代表新能源消纳高峰导致的低价/负价时段。
                  </Text>
                </div>
              )}
            </div>
          </Tabs.TabPane>

          <Tabs.TabPane 
            tab={<Space><ThunderboltOutlined /> 市场成交活跃度</Space>}
            key="volume"
          >
            <div style={{ padding: '12px 24px 24px' }}>
              <ReactECharts 
                key={themeMode}
                option={getVolumeChartOption(token, themeMode)} 
                style={{ height: 450 }} 
                theme={themeMode} 
              />
            </div>
          </Tabs.TabPane>
        </Tabs>
      </div>

      <Card 
        className="hover-card"
        title={
          <Space>
            <AreaChartOutlined style={{ color: token.colorSuccess }} />
            <span>实时量价明细清单</span>
          </Space>
        }
        style={{ marginTop: 24, borderRadius: 12, border: 'none' }}
      >
        <Table 
          columns={priceColumns}
          dataSource={priceTableData}
          pagination={{ pageSize: 8, showSizeChanger: false }}
          size="middle"
          scroll={{ x: 600 }}
        />
      </Card>
    </PageContainer>
  );
};

export default Market;
