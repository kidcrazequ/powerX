/**
 * PowerX 图表组件
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 */
import React from 'react';
import { Spin, Empty, theme } from 'antd';
import ReactECharts from 'echarts-for-react';

type ChartType = 'line' | 'bar' | 'pie' | 'area';

interface ChartWidgetProps {
  type: ChartType;
  title?: string;
  data: Array<{ name: string; value: number }> | Array<{ x: string; y: number }>;
  loading?: boolean;
  height?: number;
  color?: string;
  showLegend?: boolean;
}

const ChartWidget: React.FC<ChartWidgetProps> = ({
  type,
  title,
  data,
  loading = false,
  height = 250,
  color,
  showLegend = false
}) => {
  const { token } = theme.useToken();

  if (loading) {
    return (
      <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Spin />
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Empty description="暂无数据" image={Empty.PRESENTED_IMAGE_SIMPLE} />
      </div>
    );
  }

  const getOption = () => {
    const chartColor = color || token.colorPrimary;

    // 检查数据格式
    const isNameValueFormat = 'name' in data[0] && 'value' in data[0];
    const isXYFormat = 'x' in data[0] && 'y' in data[0];

    switch (type) {
      case 'line':
      case 'area':
        return {
          tooltip: { trigger: 'axis' },
          xAxis: {
            type: 'category',
            data: isXYFormat 
              ? (data as Array<{ x: string; y: number }>).map(d => d.x)
              : (data as Array<{ name: string; value: number }>).map(d => d.name),
            axisLine: { lineStyle: { color: token.colorBorder } },
            axisLabel: { color: token.colorTextSecondary }
          },
          yAxis: {
            type: 'value',
            axisLine: { lineStyle: { color: token.colorBorder } },
            axisLabel: { color: token.colorTextSecondary },
            splitLine: { lineStyle: { color: token.colorBorder, type: 'dashed' } }
          },
          series: [{
            type: 'line',
            data: isXYFormat
              ? (data as Array<{ x: string; y: number }>).map(d => d.y)
              : (data as Array<{ name: string; value: number }>).map(d => d.value),
            smooth: true,
            itemStyle: { color: chartColor },
            areaStyle: type === 'area' ? { color: `${chartColor}30` } : undefined
          }],
          grid: { left: 50, right: 20, bottom: 30, top: 20 }
        };

      case 'bar':
        return {
          tooltip: { trigger: 'axis' },
          xAxis: {
            type: 'category',
            data: isXYFormat
              ? (data as Array<{ x: string; y: number }>).map(d => d.x)
              : (data as Array<{ name: string; value: number }>).map(d => d.name),
            axisLine: { lineStyle: { color: token.colorBorder } },
            axisLabel: { color: token.colorTextSecondary }
          },
          yAxis: {
            type: 'value',
            axisLine: { lineStyle: { color: token.colorBorder } },
            axisLabel: { color: token.colorTextSecondary },
            splitLine: { lineStyle: { color: token.colorBorder, type: 'dashed' } }
          },
          series: [{
            type: 'bar',
            data: isXYFormat
              ? (data as Array<{ x: string; y: number }>).map(d => d.y)
              : (data as Array<{ name: string; value: number }>).map(d => d.value),
            itemStyle: { color: chartColor, borderRadius: [4, 4, 0, 0] }
          }],
          grid: { left: 50, right: 20, bottom: 30, top: 20 }
        };

      case 'pie':
        return {
          tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
          legend: showLegend ? {
            orient: 'vertical',
            right: 10,
            top: 'center',
            textStyle: { color: token.colorTextSecondary }
          } : undefined,
          series: [{
            type: 'pie',
            radius: ['40%', '70%'],
            center: showLegend ? ['40%', '50%'] : ['50%', '50%'],
            data: (data as Array<{ name: string; value: number }>).map((d, i) => ({
              name: d.name,
              value: d.value
            })),
            label: { color: token.colorTextSecondary },
            emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.3)' } }
          }]
        };

      default:
        return {};
    }
  };

  return (
    <ReactECharts
      option={getOption()}
      style={{ height }}
      opts={{ renderer: 'canvas' }}
    />
  );
};

export default ChartWidget;
