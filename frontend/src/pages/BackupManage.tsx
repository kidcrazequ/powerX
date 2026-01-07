/**
 * PowerX 备份管理页面
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 */
import React, { useState } from 'react';
import { Card, Table, Button, Modal, Progress, Space, Tag, message, theme, Statistic, Row, Col } from 'antd';
import { PageContainer } from '@ant-design/pro-components';
import { PlusOutlined, DownloadOutlined, DeleteOutlined, CloudOutlined, ReloadOutlined } from '@ant-design/icons';

interface Backup {
  name: string;
  type: string;
  created_at: string;
  size_mb: number;
}

const mockBackups: Backup[] = [
  { name: 'backup_20260107_100000', type: 'full', created_at: '2026-01-07 10:00:00', size_mb: 125.5 },
  { name: 'backup_20260106_100000', type: 'full', created_at: '2026-01-06 10:00:00', size_mb: 118.2 },
  { name: 'backup_20260105_100000', type: 'full', created_at: '2026-01-05 10:00:00', size_mb: 112.8 },
];

const BackupManage: React.FC = () => {
  const { token } = theme.useToken();
  const [backups, setBackups] = useState<Backup[]>(mockBackups);
  const [creating, setCreating] = useState(false);

  const handleCreate = () => {
    setCreating(true);
    setTimeout(() => {
      const newBackup: Backup = {
        name: `backup_${new Date().toISOString().replace(/[-:T.Z]/g, '').slice(0, 14)}`,
        type: 'full',
        created_at: new Date().toLocaleString(),
        size_mb: Math.round(Math.random() * 50 + 100)
      };
      setBackups([newBackup, ...backups]);
      setCreating(false);
      message.success('备份创建成功');
    }, 2000);
  };

  const handleRestore = (name: string) => {
    Modal.confirm({
      title: '确认恢复',
      content: `确定要恢复到备份 ${name} 吗？当前数据将被覆盖。`,
      okText: '确认恢复',
      okButtonProps: { danger: true },
      onOk: () => message.success('备份恢复成功')
    });
  };

  const handleDelete = (name: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定删除此备份？',
      onOk: () => {
        setBackups(backups.filter(b => b.name !== name));
        message.success('备份已删除');
      }
    });
  };

  const columns = [
    { title: '备份名称', dataIndex: 'name' },
    { title: '类型', dataIndex: 'type', render: (t: string) => <Tag color="blue">{t === 'full' ? '完整备份' : '增量备份'}</Tag> },
    { title: '创建时间', dataIndex: 'created_at' },
    { title: '大小', dataIndex: 'size_mb', render: (s: number) => `${s} MB` },
    {
      title: '操作', key: 'action',
      render: (_: any, r: Backup) => (
        <Space>
          <Button type="link" icon={<ReloadOutlined />} onClick={() => handleRestore(r.name)}>恢复</Button>
          <Button type="link" danger icon={<DeleteOutlined />} onClick={() => handleDelete(r.name)}>删除</Button>
        </Space>
      )
    }
  ];

  const totalSize = backups.reduce((sum, b) => sum + b.size_mb, 0);

  return (
    <PageContainer
      header={{
        title: '备份管理',
        subTitle: '管理系统数据备份和恢复',
        extra: [<Button key="create" type="primary" icon={<PlusOutlined />} loading={creating} onClick={handleCreate}>创建备份</Button>]
      }}
    >
      <Row gutter={[20, 20]} style={{ marginBottom: 20 }}>
        <Col xs={12} lg={6}>
          <Card style={{ borderRadius: 12 }}><Statistic title="备份数量" value={backups.length} prefix={<CloudOutlined />} /></Card>
        </Col>
        <Col xs={12} lg={6}>
          <Card style={{ borderRadius: 12 }}><Statistic title="总占用空间" value={totalSize.toFixed(1)} suffix="MB" /></Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card style={{ borderRadius: 12 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>磁盘使用率</span>
              <span>45%</span>
            </div>
            <Progress percent={45} showInfo={false} strokeColor={token.colorPrimary} />
            <div style={{ color: token.colorTextSecondary, fontSize: 12, marginTop: 4 }}>180 GB / 400 GB</div>
          </Card>
        </Col>
      </Row>

      <Card title="备份列表" style={{ borderRadius: 12 }}>
        <Table dataSource={backups} columns={columns} rowKey="name" pagination={false} />
      </Card>
    </PageContainer>
  );
};

export default BackupManage;
