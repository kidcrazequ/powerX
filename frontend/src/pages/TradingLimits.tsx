/**
 * PowerX 交易限额管理页面
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 */

import React, { useState } from 'react';
import { Card, Table, Button, Modal, Form, Input, Select, InputNumber, Switch, Space, Tag, message, theme, Progress } from 'antd';
import { PageContainer } from '@ant-design/pro-components';
import { PlusOutlined, EditOutlined, DeleteOutlined, WarningOutlined } from '@ant-design/icons';
import { useSettingsStore } from '../stores/settingsStore';

const { Option } = Select;

interface TradingLimit {
  id: number;
  name: string;
  limit_type: string;
  limit_value: number;
  province: string | null;
  direction: string | null;
  is_enabled: boolean;
  current_usage?: number;
}

const mockLimits: TradingLimit[] = [
  { id: 1, name: '每日交易量限额', limit_type: 'DAILY_QUANTITY', limit_value: 5000, province: null, direction: null, is_enabled: true, current_usage: 2350 },
  { id: 2, name: '每日交易金额限额', limit_type: 'DAILY_AMOUNT', limit_value: 2500000, province: null, direction: null, is_enabled: true, current_usage: 1200000 },
  { id: 3, name: '单笔交易量限额', limit_type: 'SINGLE_QUANTITY', limit_value: 500, province: null, direction: null, is_enabled: true },
  { id: 4, name: '广东省买入限额', limit_type: 'DAILY_QUANTITY', limit_value: 1000, province: '广东', direction: 'BUY', is_enabled: true, current_usage: 450 },
];

const limitTypeLabels: Record<string, string> = {
  'DAILY_AMOUNT': '每日交易金额',
  'DAILY_QUANTITY': '每日交易数量',
  'SINGLE_AMOUNT': '单笔交易金额',
  'SINGLE_QUANTITY': '单笔交易数量',
  'POSITION': '持仓限额'
};

const TradingLimits: React.FC = () => {
  const { token } = theme.useToken();
  const { themeMode } = useSettingsStore();
  const [limits, setLimits] = useState<TradingLimit[]>(mockLimits);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingLimit, setEditingLimit] = useState<TradingLimit | null>(null);
  const [form] = Form.useForm();

  const showModal = (limit?: TradingLimit) => {
    setEditingLimit(limit || null);
    if (limit) {
      form.setFieldsValue(limit);
    } else {
      form.resetFields();
    }
    setIsModalVisible(true);
  };

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      if (editingLimit) {
        setLimits(limits.map(l => l.id === editingLimit.id ? { ...l, ...values } : l));
        message.success('限额更新成功');
      } else {
        const newLimit = { ...values, id: Date.now(), is_enabled: true };
        setLimits([...limits, newLimit]);
        message.success('限额创建成功');
      }
      setIsModalVisible(false);
    } catch (error) {
      message.error('请检查表单');
    }
  };

  const handleDelete = (id: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除此限额配置吗？',
      onOk: () => {
        setLimits(limits.filter(l => l.id !== id));
        message.success('已删除');
      }
    });
  };

  const toggleEnabled = (id: number) => {
    setLimits(limits.map(l => l.id === id ? { ...l, is_enabled: !l.is_enabled } : l));
  };

  const columns = [
    { title: '名称', dataIndex: 'name', key: 'name' },
    {
      title: '类型', dataIndex: 'limit_type', key: 'limit_type',
      render: (type: string) => <Tag color="blue">{limitTypeLabels[type] || type}</Tag>
    },
    {
      title: '限额值', dataIndex: 'limit_value', key: 'limit_value',
      render: (value: number, record: TradingLimit) => {
        const unit = record.limit_type.includes('AMOUNT') ? ' 元' : ' MWh';
        return <span style={{ fontFamily: 'JetBrains Mono', fontWeight: 600 }}>{value.toLocaleString()}{unit}</span>;
      }
    },
    {
      title: '使用进度', key: 'usage',
      render: (_: any, record: TradingLimit) => {
        if (record.current_usage === undefined) return '-';
        const percent = Math.round((record.current_usage / record.limit_value) * 100);
        return (
          <Progress
            percent={percent}
            size="small"
            status={percent > 80 ? 'exception' : 'active'}
            style={{ width: 120 }}
          />
        );
      }
    },
    {
      title: '适用范围', key: 'scope',
      render: (_: any, record: TradingLimit) => (
        <Space>
          {record.province && <Tag>{record.province}</Tag>}
          {record.direction && <Tag color={record.direction === 'BUY' ? 'green' : 'red'}>{record.direction === 'BUY' ? '买入' : '卖出'}</Tag>}
          {!record.province && !record.direction && <Tag>全局</Tag>}
        </Space>
      )
    },
    {
      title: '状态', dataIndex: 'is_enabled', key: 'is_enabled',
      render: (enabled: boolean, record: TradingLimit) => (
        <Switch checked={enabled} onChange={() => toggleEnabled(record.id)} size="small" />
      )
    },
    {
      title: '操作', key: 'action',
      render: (_: any, record: TradingLimit) => (
        <Space>
          <Button type="text" icon={<EditOutlined />} onClick={() => showModal(record)}>编辑</Button>
          <Button type="text" danger icon={<DeleteOutlined />} onClick={() => handleDelete(record.id)}>删除</Button>
        </Space>
      )
    }
  ];

  return (
    <PageContainer
      header={{
        title: '交易限额管理',
        subTitle: '配置交易限额规则，控制风险敞口',
        extra: [
          <Button key="add" type="primary" icon={<PlusOutlined />} onClick={() => showModal()}>新增限额</Button>
        ]
      }}
    >
      <Card style={{ borderRadius: 12 }}>
        <Table dataSource={limits} columns={columns} rowKey="id" pagination={false} />
      </Card>

      <Modal
        title={editingLimit ? '编辑限额' : '新增限额'}
        open={isModalVisible}
        onOk={handleOk}
        onCancel={() => setIsModalVisible(false)}
        okText="保存"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="限额名称" rules={[{ required: true }]}>
            <Input placeholder="输入限额名称" />
          </Form.Item>
          <Form.Item name="limit_type" label="限额类型" rules={[{ required: true }]}>
            <Select placeholder="选择限额类型">
              {Object.entries(limitTypeLabels).map(([value, label]) => (
                <Option key={value} value={value}>{label}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="limit_value" label="限额值" rules={[{ required: true }]}>
            <InputNumber min={0} style={{ width: '100%' }} placeholder="输入限额值" />
          </Form.Item>
          <Form.Item name="province" label="适用省份">
            <Select placeholder="选择省份(不选则全局)" allowClear>
              <Option value="广东">广东</Option>
              <Option value="浙江">浙江</Option>
              <Option value="山东">山东</Option>
              <Option value="江苏">江苏</Option>
            </Select>
          </Form.Item>
          <Form.Item name="direction" label="适用方向">
            <Select placeholder="选择方向(不选则全部)" allowClear>
              <Option value="BUY">买入</Option>
              <Option value="SELL">卖出</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </PageContainer>
  );
};

export default TradingLimits;
