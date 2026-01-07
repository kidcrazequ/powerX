/**
 * PowerX 个人信息页面
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 用户个人信息编辑与密码修改
 */

import React, { useState } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Form, 
  Input, 
  Button, 
  Avatar, 
  Typography,
  Space,
  Divider,
  message,
  theme,
  Tabs,
  Upload
} from 'antd';
import { 
  UserOutlined, 
  MailOutlined, 
  LockOutlined,
  SafetyCertificateOutlined,
  EditOutlined,
  SaveOutlined,
  CameraOutlined
} from '@ant-design/icons';
import { PageContainer } from '@ant-design/pro-components';
import type { UploadProps } from 'antd';

import { useAuthStore } from '../stores/authStore';

const { Text, Title, Paragraph } = Typography;

/**
 * 个人信息页面组件
 */
const Profile: React.FC = () => {
  const { user, setUser } = useAuthStore();
  const { token } = theme.useToken();
  const [profileForm] = Form.useForm();
  const [passwordForm] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [passwordLoading, setPasswordLoading] = useState(false);

  /**
   * 处理个人信息表单提交
   * @param values 表单值
   */
  const handleProfileSubmit = async (values: any) => {
    setLoading(true);
    try {
      // 模拟 API 调用
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 更新用户信息
      if (user) {
        setUser({
          ...user,
          name: values.name,
          email: values.email,
        });
      }
      
      message.success('个人信息更新成功！');
    } catch (error) {
      message.error('更新失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  /**
   * 处理密码修改表单提交
   * @param values 表单值
   */
  const handlePasswordSubmit = async (values: any) => {
    setPasswordLoading(true);
    try {
      // 模拟 API 调用
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      message.success('密码修改成功！');
      passwordForm.resetFields();
    } catch (error) {
      message.error('密码修改失败，请稍后重试');
    } finally {
      setPasswordLoading(false);
    }
  };

  /**
   * 头像上传配置
   */
  const uploadProps: UploadProps = {
    name: 'avatar',
    showUploadList: false,
    beforeUpload: (file) => {
      const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png';
      if (!isJpgOrPng) {
        message.error('只能上传 JPG/PNG 格式的图片！');
      }
      const isLt2M = file.size / 1024 / 1024 < 2;
      if (!isLt2M) {
        message.error('图片大小不能超过 2MB！');
      }
      return false; // 阻止自动上传，实际项目中需要实现上传逻辑
    },
  };

  /**
   * 获取角色显示名称
   * @param role 角色代码
   */
  const getRoleName = (role: string): string => {
    const roleMap: Record<string, string> = {
      'admin': '系统管理员',
      'trader': '交易员',
      'analyst': '分析师',
      'viewer': '观察者',
    };
    return roleMap[role] || role;
  };

  return (
    <PageContainer
      header={{
        title: '个人信息',
        subTitle: '管理您的账户信息和安全设置',
      }}
    >
      <Row gutter={[24, 24]}>
        {/* 左侧：用户卡片 */}
        <Col xs={24} lg={8}>
          <Card 
            className="hover-card"
            style={{ borderRadius: 12, border: 'none', textAlign: 'center' }}
          >
            {/* 头像区域 */}
            <div style={{ position: 'relative', display: 'inline-block', marginBottom: 24 }}>
              <Avatar 
                size={120} 
                icon={<UserOutlined />}
                style={{ 
                  backgroundColor: token.colorPrimary,
                  boxShadow: `0 8px 24px ${token.colorPrimary}40`
                }}
              />
              <Upload {...uploadProps}>
                <Button 
                  type="primary"
                  shape="circle"
                  size="small"
                  icon={<CameraOutlined />}
                  style={{
                    position: 'absolute',
                    bottom: 0,
                    right: 0,
                    boxShadow: '0 2px 8px rgba(0,0,0,0.3)'
                  }}
                />
              </Upload>
            </div>

            {/* 用户信息 */}
            <Title level={4} style={{ marginBottom: 4 }}>
              {user?.name || '用户'}
            </Title>
            <Text type="secondary">@{user?.username || 'username'}</Text>

            <Divider style={{ margin: '20px 0' }} />

            {/* 角色信息 */}
            <div style={{ 
              background: 'rgba(255,255,255,0.03)', 
              padding: '16px 20px', 
              borderRadius: 8,
              textAlign: 'left'
            }}>
              <Space direction="vertical" size={12} style={{ width: '100%' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Text type="secondary">用户角色</Text>
                  <Text strong style={{ color: token.colorPrimary }}>
                    {getRoleName(user?.role || '')}
                  </Text>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Text type="secondary">账户状态</Text>
                  <Text strong style={{ color: token.colorSuccess }}>
                    {user?.is_active ? '正常' : '已禁用'}
                  </Text>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Text type="secondary">用户ID</Text>
                  <Text copyable className="data-font">{user?.id || '-'}</Text>
                </div>
              </Space>
            </div>
          </Card>
        </Col>

        {/* 右侧：编辑表单 */}
        <Col xs={24} lg={16}>
          <Card 
            className="hover-card"
            style={{ borderRadius: 12, border: 'none' }}
          >
            <Tabs
              defaultActiveKey="info"
              items={[
                {
                  key: 'info',
                  label: (
                    <Space>
                      <EditOutlined />
                      编辑资料
                    </Space>
                  ),
                  children: (
                    <Form
                      form={profileForm}
                      layout="vertical"
                      initialValues={{
                        username: user?.username,
                        email: user?.email,
                        name: user?.name,
                      }}
                      onFinish={handleProfileSubmit}
                      requiredMark={false}
                      style={{ maxWidth: 500, marginTop: 16 }}
                    >
                      <Form.Item
                        label="用户名"
                        name="username"
                      >
                        <Input 
                          prefix={<UserOutlined style={{ color: token.colorTextSecondary }} />}
                          disabled
                          variant="filled"
                          style={{ borderRadius: 8 }}
                        />
                      </Form.Item>

                      <Form.Item
                        label="邮箱地址"
                        name="email"
                        rules={[
                          { required: true, message: '请输入邮箱地址' },
                          { type: 'email', message: '请输入有效的邮箱地址' }
                        ]}
                      >
                        <Input 
                          prefix={<MailOutlined style={{ color: token.colorTextSecondary }} />}
                          placeholder="请输入邮箱地址"
                          variant="filled"
                          style={{ borderRadius: 8 }}
                        />
                      </Form.Item>

                      <Form.Item
                        label="显示名称"
                        name="name"
                        rules={[{ required: true, message: '请输入显示名称' }]}
                      >
                        <Input 
                          prefix={<UserOutlined style={{ color: token.colorTextSecondary }} />}
                          placeholder="请输入显示名称"
                          variant="filled"
                          style={{ borderRadius: 8 }}
                        />
                      </Form.Item>

                      <Form.Item style={{ marginTop: 32 }}>
                        <Button 
                          type="primary" 
                          htmlType="submit" 
                          loading={loading}
                          icon={<SaveOutlined />}
                          style={{ borderRadius: 8, height: 40, paddingInline: 24 }}
                        >
                          保存修改
                        </Button>
                      </Form.Item>
                    </Form>
                  ),
                },
                {
                  key: 'password',
                  label: (
                    <Space>
                      <SafetyCertificateOutlined />
                      修改密码
                    </Space>
                  ),
                  children: (
                    <Form
                      form={passwordForm}
                      layout="vertical"
                      onFinish={handlePasswordSubmit}
                      requiredMark={false}
                      style={{ maxWidth: 500, marginTop: 16 }}
                    >
                      <Form.Item
                        label="当前密码"
                        name="currentPassword"
                        rules={[{ required: true, message: '请输入当前密码' }]}
                      >
                        <Input.Password 
                          prefix={<LockOutlined style={{ color: token.colorTextSecondary }} />}
                          placeholder="请输入当前密码"
                          variant="filled"
                          style={{ borderRadius: 8 }}
                        />
                      </Form.Item>

                      <Form.Item
                        label="新密码"
                        name="newPassword"
                        rules={[
                          { required: true, message: '请输入新密码' },
                          { min: 6, message: '密码长度至少为6位' }
                        ]}
                      >
                        <Input.Password 
                          prefix={<LockOutlined style={{ color: token.colorTextSecondary }} />}
                          placeholder="请输入新密码"
                          variant="filled"
                          style={{ borderRadius: 8 }}
                        />
                      </Form.Item>

                      <Form.Item
                        label="确认新密码"
                        name="confirmPassword"
                        dependencies={['newPassword']}
                        rules={[
                          { required: true, message: '请确认新密码' },
                          ({ getFieldValue }) => ({
                            validator(_, value) {
                              if (!value || getFieldValue('newPassword') === value) {
                                return Promise.resolve();
                              }
                              return Promise.reject(new Error('两次输入的密码不一致'));
                            },
                          }),
                        ]}
                      >
                        <Input.Password 
                          prefix={<LockOutlined style={{ color: token.colorTextSecondary }} />}
                          placeholder="请再次输入新密码"
                          variant="filled"
                          style={{ borderRadius: 8 }}
                        />
                      </Form.Item>

                      <Paragraph type="secondary" style={{ fontSize: 12, marginBottom: 24 }}>
                        密码应包含至少6个字符，建议使用字母、数字和特殊字符的组合。
                      </Paragraph>

                      <Form.Item>
                        <Button 
                          type="primary" 
                          htmlType="submit" 
                          loading={passwordLoading}
                          icon={<SafetyCertificateOutlined />}
                          style={{ borderRadius: 8, height: 40, paddingInline: 24 }}
                        >
                          确认修改
                        </Button>
                      </Form.Item>
                    </Form>
                  ),
                },
              ]}
            />
          </Card>
        </Col>
      </Row>
    </PageContainer>
  );
};

export default Profile;
