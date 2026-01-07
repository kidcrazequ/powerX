/**
 * PowerX 电子签章页面
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 */
import React, { useState } from 'react';
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  Input,
  Upload,
  Tag,
  Space,
  Typography,
  Statistic,
  Row,
  Col,
  message,
  Steps,
  Result,
} from 'antd';
import {
  SafetyCertificateOutlined,
  FileProtectOutlined,
  UploadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  PlusOutlined,
} from '@ant-design/icons';

const { Text, Paragraph } = Typography;

// 模拟证书数据
const mockCertificate = {
  certificate_id: 'CERT-A1B2C3D4E5F6',
  subject_name: '广东电力交易中心有限公司',
  issuer: 'PowerX CA',
  valid_from: '2026-01-01',
  valid_until: '2029-01-01',
  is_active: true,
};

// 模拟签章记录
const mockSignatures = [
  {
    signature_id: 'SIG-A1B2C3D4E5F6',
    document_id: 'CONTRACT-2026-001',
    document_type: 'contract',
    signer_name: '广东电力交易中心有限公司',
    status: 'verified',
    created_at: '2026-01-07 10:30:00',
  },
  {
    signature_id: 'SIG-G7H8I9J0K1L2',
    document_id: 'AGREEMENT-2026-015',
    document_type: 'agreement',
    signer_name: '广东电力交易中心有限公司',
    status: 'signed',
    created_at: '2026-01-06 15:20:00',
  },
];

const statusColors: Record<string, string> = {
  pending: 'blue',
  signed: 'green',
  verified: 'success',
  rejected: 'error',
  expired: 'default',
};

const statusLabels: Record<string, string> = {
  pending: '待签署',
  signed: '已签署',
  verified: '已验证',
  rejected: '已拒绝',
  expired: '已过期',
};

const DigitalSignature: React.FC = () => {
  const [certificate, setCertificate] = useState(mockCertificate);
  const [signatures, setSignatures] = useState(mockSignatures);
  const [signModalVisible, setSignModalVisible] = useState(false);
  const [verifyModalVisible, setVerifyModalVisible] = useState(false);
  const [createCertModalVisible, setCreateCertModalVisible] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [form] = Form.useForm();

  const handleSign = async () => {
    setCurrentStep(1);
    setTimeout(() => {
      setCurrentStep(2);
      message.success('文档签署成功');
    }, 2000);
  };

  const handleVerify = async () => {
    message.success('签名验证通过');
    setVerifyModalVisible(false);
  };

  const signatureColumns = [
    {
      title: '签章ID',
      dataIndex: 'signature_id',
      key: 'signature_id',
      render: (text: string) => (
        <Text code>{text}</Text>
      ),
    },
    {
      title: '文档ID',
      dataIndex: 'document_id',
      key: 'document_id',
    },
    {
      title: '文档类型',
      dataIndex: 'document_type',
      key: 'document_type',
      render: (type: string) => (
        <Tag>
          {type === 'contract' ? '合同' : type === 'agreement' ? '协议' : '报告'}
        </Tag>
      ),
    },
    {
      title: '签署人',
      dataIndex: 'signer_name',
      key: 'signer_name',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={statusColors[status]} icon={
          status === 'verified' ? <CheckCircleOutlined /> : 
          status === 'rejected' ? <CloseCircleOutlined /> : null
        }>
          {statusLabels[status]}
        </Tag>
      ),
    },
    {
      title: '签署时间',
      dataIndex: 'created_at',
      key: 'created_at',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Space>
          <Button type="link" size="small">查看</Button>
          {record.status === 'signed' && (
            <Button type="link" size="small" onClick={() => setVerifyModalVisible(true)}>
              验证
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="已签署文档"
              value={signatures.length}
              prefix={<FileProtectOutlined />}
              suffix="份"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已验证签名"
              value={signatures.filter(s => s.status === 'verified').length}
              prefix={<CheckCircleOutlined />}
              suffix="份"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="证书状态"
              value={certificate ? '有效' : '无'}
              valueStyle={{ color: certificate ? '#52c41a' : '#f5222d' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="证书有效期"
              value={certificate?.valid_until || '-'}
            />
          </Card>
        </Col>
      </Row>

      {/* 证书信息 */}
      <Card
        title={
          <Space>
            <SafetyCertificateOutlined />
            <span>我的签章证书</span>
          </Space>
        }
        style={{ marginBottom: 24 }}
        extra={
          !certificate && (
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setCreateCertModalVisible(true)}
            >
              申请证书
            </Button>
          )
        }
      >
        {certificate ? (
          <Row gutter={24}>
            <Col span={6}>
              <div style={{ textAlign: 'center', padding: 20 }}>
                <SafetyCertificateOutlined style={{ fontSize: 64, color: '#52c41a' }} />
                <div style={{ marginTop: 8 }}>
                  <Tag color="success">证书有效</Tag>
                </div>
              </div>
            </Col>
            <Col span={18}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <Text type="secondary">证书ID：</Text>
                  <Text code>{certificate.certificate_id}</Text>
                </div>
                <div>
                  <Text type="secondary">主体名称：</Text>
                  <Text strong>{certificate.subject_name}</Text>
                </div>
                <div>
                  <Text type="secondary">颁发机构：</Text>
                  <Text>{certificate.issuer}</Text>
                </div>
                <div>
                  <Text type="secondary">有效期：</Text>
                  <Text>{certificate.valid_from} 至 {certificate.valid_until}</Text>
                </div>
              </Space>
            </Col>
          </Row>
        ) : (
          <Result
            status="info"
            title="暂无签章证书"
            subTitle="请先申请数字签章证书"
            extra={
              <Button type="primary" onClick={() => setCreateCertModalVisible(true)}>
                申请证书
              </Button>
            }
          />
        )}
      </Card>

      {/* 签章记录 */}
      <Card
        title={
          <Space>
            <FileProtectOutlined />
            <span>签章记录</span>
          </Space>
        }
        extra={
          <Space>
            <Button onClick={() => setVerifyModalVisible(true)}>
              验证签名
            </Button>
            <Button
              type="primary"
              icon={<FileProtectOutlined />}
              onClick={() => setSignModalVisible(true)}
              disabled={!certificate}
            >
              签署文档
            </Button>
          </Space>
        }
      >
        <Table
          columns={signatureColumns}
          dataSource={signatures}
          rowKey="signature_id"
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* 签署文档弹窗 */}
      <Modal
        title="签署文档"
        open={signModalVisible}
        onCancel={() => {
          setSignModalVisible(false);
          setCurrentStep(0);
        }}
        footer={null}
        width={600}
      >
        <Steps
          current={currentStep}
          items={[
            { title: '上传文档' },
            { title: '签署中' },
            { title: '完成' },
          ]}
          style={{ marginBottom: 24 }}
        />

        {currentStep === 0 && (
          <Form form={form} layout="vertical">
            <Form.Item
              name="document_id"
              label="文档ID"
              rules={[{ required: true }]}
            >
              <Input placeholder="输入文档ID" />
            </Form.Item>
            <Form.Item
              name="document_type"
              label="文档类型"
              rules={[{ required: true }]}
            >
              <Input placeholder="例如：contract, agreement" />
            </Form.Item>
            <Form.Item
              name="file"
              label="上传文档"
              rules={[{ required: true }]}
            >
              <Upload.Dragger maxCount={1}>
                <p className="ant-upload-drag-icon">
                  <UploadOutlined />
                </p>
                <p>点击或拖拽文件到此处上传</p>
              </Upload.Dragger>
            </Form.Item>
            <Button type="primary" onClick={handleSign}>
              开始签署
            </Button>
          </Form>
        )}

        {currentStep === 1 && (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <SafetyCertificateOutlined spin style={{ fontSize: 48, color: '#1890ff' }} />
            <p style={{ marginTop: 16 }}>正在签署文档...</p>
          </div>
        )}

        {currentStep === 2 && (
          <Result
            status="success"
            title="签署成功"
            subTitle="文档已成功签署，签名已记录"
            extra={
              <Button onClick={() => {
                setSignModalVisible(false);
                setCurrentStep(0);
              }}>
                完成
              </Button>
            }
          />
        )}
      </Modal>

      {/* 验证签名弹窗 */}
      <Modal
        title="验证签名"
        open={verifyModalVisible}
        onCancel={() => setVerifyModalVisible(false)}
        footer={null}
        width={500}
      >
        <Form layout="vertical" onFinish={handleVerify}>
          <Form.Item
            name="signature_id"
            label="签章ID"
            rules={[{ required: true }]}
          >
            <Input placeholder="输入签章ID" />
          </Form.Item>
          <Form.Item
            name="file"
            label="上传原始文档"
            rules={[{ required: true }]}
          >
            <Upload.Dragger maxCount={1}>
              <p className="ant-upload-drag-icon">
                <UploadOutlined />
              </p>
              <p>上传需要验证的文档</p>
            </Upload.Dragger>
          </Form.Item>
          <Button type="primary" htmlType="submit">
            验证签名
          </Button>
        </Form>
      </Modal>
    </div>
  );
};

export default DigitalSignature;
