/**
 * PowerX 通知设置页面
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 */
import React, { useState } from 'react';
import { Card, Table, Button, Modal, Form, Input, Select, Switch, Space, Tag, message, theme } from 'antd';
import { PageContainer } from '@ant-design/pro-components';
import { PlusOutlined, DeleteOutlined, MailOutlined, WechatOutlined, DingdingOutlined, ApiOutlined } from '@ant-design/icons';

const { Option } = Select;

interface Channel {
  id: number;
  channel_type: string;
  channel_name: string;
  is_enabled: boolean;
  is_verified: boolean;
  notify_on_trade: boolean;
  notify_on_alert: boolean;
}

const mockChannels: Channel[] = [
  { id: 1, channel_type: 'EMAIL', channel_name: 'work@company.com', is_enabled: true, is_verified: true, notify_on_trade: true, notify_on_alert: true },
  { id: 2, channel_type: 'WECHAT', channel_name: '企业微信机器人', is_enabled: true, is_verified: true, notify_on_trade: false, notify_on_alert: true },
];

const channelIcons: Record<string, React.ReactNode> = {
  'EMAIL': <MailOutlined />,
  'WECHAT': <WechatOutlined style={{ color: '#07c160' }} />,
  'DINGTALK': <DingdingOutlined style={{ color: '#1890ff' }} />,
  'WEBHOOK': <ApiOutlined />
};

const channelLabels: Record<string, string> = {
  'EMAIL': '电子邮件',
  'WECHAT': '企业微信',
  'DINGTALK': '钉钉',
  'WEBHOOK': 'Webhook'
};

const NotificationSettings: React.FC = () => {
  const { token } = theme.useToken();
  const [channels, setChannels] = useState<Channel[]>(mockChannels);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [form] = Form.useForm();

  const handleAdd = async () => {
    try {
      const values = await form.validateFields();
      const newChannel: Channel = {
        id: Date.now(), ...values, is_enabled: true, is_verified: false
      };
      setChannels([...channels, newChannel]);
      message.success('通知渠道添加成功');
      setIsModalVisible(false);
      form.resetFields();
    } catch (error) {
      message.error('请检查表单');
    }
  };

  const handleDelete = (id: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定删除此通知渠道？',
      onOk: () => {
        setChannels(channels.filter(c => c.id !== id));
        message.success('已删除');
      }
    });
  };

  const toggleSwitch = (id: number, field: keyof Channel) => {
    setChannels(channels.map(c => c.id === id ? { ...c, [field]: !c[field] } : c));
  };

  const columns = [
    {
      title: '渠道', key: 'channel',
      render: (_: any, r: Channel) => (
        <Space>
          {channelIcons[r.channel_type]}
          <span>{r.channel_name}</span>
          {r.is_verified && <Tag color="success" style={{ marginLeft: 8 }}>已验证</Tag>}
        </Space>
      )
    },
    { title: '类型', dataIndex: 'channel_type', render: (t: string) => <Tag>{channelLabels[t]}</Tag> },
    { title: '启用', dataIndex: 'is_enabled', render: (v: boolean, r: Channel) => <Switch size="small" checked={v} onChange={() => toggleSwitch(r.id, 'is_enabled')} /> },
    { title: '交易通知', dataIndex: 'notify_on_trade', render: (v: boolean, r: Channel) => <Switch size="small" checked={v} onChange={() => toggleSwitch(r.id, 'notify_on_trade')} /> },
    { title: '预警通知', dataIndex: 'notify_on_alert', render: (v: boolean, r: Channel) => <Switch size="small" checked={v} onChange={() => toggleSwitch(r.id, 'notify_on_alert')} /> },
    { title: '操作', key: 'action', render: (_: any, r: Channel) => <Button type="text" danger icon={<DeleteOutlined />} onClick={() => handleDelete(r.id)}>删除</Button> }
  ];

  return (
    <PageContainer
      header={{
        title: '通知设置',
        subTitle: '配置消息推送渠道和通知偏好',
        extra: [<Button key="add" type="primary" icon={<PlusOutlined />} onClick={() => setIsModalVisible(true)}>添加渠道</Button>]
      }}
    >
      <Card style={{ borderRadius: 12 }}>
        <Table dataSource={channels} columns={columns} rowKey="id" pagination={false} />
      </Card>

      <Modal title="添加通知渠道" open={isModalVisible} onOk={handleAdd} onCancel={() => setIsModalVisible(false)} okText="添加">
        <Form form={form} layout="vertical">
          <Form.Item name="channel_type" label="渠道类型" rules={[{ required: true }]}>
            <Select placeholder="选择渠道类型">
              {Object.entries(channelLabels).map(([k, v]) => <Option key={k} value={k}>{channelIcons[k]} {v}</Option>)}
            </Select>
          </Form.Item>
          <Form.Item name="channel_name" label="渠道名称/地址" rules={[{ required: true }]}>
            <Input placeholder="输入邮箱地址或Webhook名称" />
          </Form.Item>
        </Form>
      </Modal>
    </PageContainer>
  );
};

export default NotificationSettings;
