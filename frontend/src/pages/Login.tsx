/**
 * PowerX 登录页面 - 现代版
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 */

import React, { useState } from 'react';
import { 
  Form, 
  Input, 
  Button, 
  Typography, 
  Space, 
  message,
  Divider,
  ConfigProvider,
  theme
} from 'antd';
import { 
  UserOutlined, 
  LockOutlined, 
  ThunderboltOutlined,
  GlobalOutlined,
  SafetyCertificateOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { useSettingsStore } from '../stores/settingsStore';
import { authApi } from '../services/api';

const { Title, Text } = Typography;

interface LoginForm {
  username: string;
  password: string;
}

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuthStore();
  const { themeMode } = useSettingsStore();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: LoginForm) => {
    setLoading(true);
    try {
      const response = await authApi.login(values.username, values.password);
      const { access_token, refresh_token } = response.data;
      
      login(access_token, refresh_token);
      message.success('登录成功！欢迎回到 PowerX');
      navigate('/');
    } catch (error: any) {
      // 演示环境下如果接口报错，也允许模拟登录，方便展示美化效果
      if (process.env.NODE_ENV === 'development') {
        handleDemoLogin();
      } else {
        message.error(error.response?.data?.detail || '登录失败，请检查用户名和密码');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = () => {
    login('demo-token', 'demo-refresh-token', {
      id: 1,
      username: 'admin',
      email: 'admin@powerx.ai',
      name: '系统管理员',
      role: 'admin',
      is_active: true
    });
    message.success('演示模式登录成功！');
    navigate('/');
  };

  return (
    <ConfigProvider
      theme={{
        algorithm: themeMode === 'dark' ? theme.darkAlgorithm : theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1677ff',
          borderRadius: 8,
          colorBgContainer: themeMode === 'dark' ? '#141414' : '#ffffff',
        }
      }}
    >
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        background: themeMode === 'dark' ? '#000' : '#f0f2f5',
        overflow: 'hidden',
        position: 'relative',
        transition: 'all 0.3s'
      }}>
        {/* 背景装饰 */}
        <div style={{
          position: 'absolute',
          top: '-10%',
          right: '-5%',
          width: '60%',
          height: '60%',
          background: 'radial-gradient(circle, rgba(22, 119, 255, 0.1) 0%, transparent 70%)',
          filter: 'blur(80px)',
          zIndex: 1
        }} />
        <div style={{
          position: 'absolute',
          bottom: '-10%',
          left: '-5%',
          width: '50%',
          height: '50%',
          background: 'radial-gradient(circle, rgba(114, 46, 209, 0.08) 0%, transparent 70%)',
          filter: 'blur(80px)',
          zIndex: 1
        }} />

        {/* 左侧：视觉展示 */}
        <div style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          padding: '0 80px',
          zIndex: 2,
          background: themeMode === 'dark' 
            ? 'linear-gradient(to right, rgba(0,0,0,0.8), transparent)' 
            : 'linear-gradient(to right, rgba(255,255,255,0.95), transparent)',
          borderRight: themeMode === 'dark' 
            ? '1px solid rgba(255,255,255,0.05)' 
            : '1px solid rgba(0,0,0,0.05)'
        }}>
          <div style={{ maxWidth: 500 }}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: 24 }}>
              <div style={{
                width: 48,
                height: 48,
                background: 'linear-gradient(135deg, #1677ff 0%, #722ed1 100%)',
                borderRadius: 12,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginRight: 16,
                boxShadow: themeMode === 'dark' 
                  ? '0 0 20px rgba(22, 119, 255, 0.4)' 
                  : '0 4px 12px rgba(22, 119, 255, 0.2)'
              }}>
                <ThunderboltOutlined style={{ fontSize: 24, color: '#fff' }} />
              </div>
              <Title level={1} style={{ 
                margin: 0, 
                fontSize: 36, 
                letterSpacing: -1, 
                color: themeMode === 'dark' ? '#fff' : '#141414' 
              }}>
                Power<span style={{ color: '#1677ff' }}>X</span>
              </Title>
            </div>
            
            <Title level={2} style={{ 
              color: themeMode === 'dark' ? 'rgba(255,255,255,0.9)' : 'rgba(0,0,0,0.85)', 
              marginBottom: 16, 
              fontWeight: 600 
            }}>
              下一代智能电力交易大脑
            </Title>
            <Text style={{ 
              color: themeMode === 'dark' ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.45)', 
              fontSize: 18, 
              display: 'block', 
              marginBottom: 48, 
              lineHeight: 1.6 
            }}>
              基于深度学习的市场价格预测，自动化的现货交易策略，为您提供专业、稳健、高效的电力资产管理方案。
            </Text>

            <Space size={40}>
              <div>
                <Title level={3} style={{ margin: 0, color: '#1677ff' }}>98.5%</Title>
                <Text style={{ color: themeMode === 'dark' ? 'rgba(255,255,255,0.4)' : 'rgba(0,0,0,0.45)' }}>预测准确率</Text>
              </div>
              <div style={{ width: 1, height: 40, background: themeMode === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)' }} />
              <div>
                <Title level={3} style={{ margin: 0, color: '#52c41a' }}>24/7</Title>
                <Text style={{ color: themeMode === 'dark' ? 'rgba(255,255,255,0.4)' : 'rgba(0,0,0,0.45)' }}>实时市场监控</Text>
              </div>
              <div style={{ width: 1, height: 40, background: themeMode === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)' }} />
              <div>
                <Title level={3} style={{ margin: 0, color: '#faad14' }}>10k+</Title>
                <Text style={{ color: themeMode === 'dark' ? 'rgba(255,255,255,0.4)' : 'rgba(0,0,0,0.45)' }}>日均交易量</Text>
              </div>
            </Space>
          </div>
        </div>

        {/* 右侧：登录表单 */}
        <div style={{
          width: 500,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 2,
          padding: '0 40px'
        }}>
          <div className="glass-morphism" style={{
            width: '100%',
            maxWidth: 400,
            padding: '48px 40px',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)'
          }}>
            <div style={{ marginBottom: 40 }}>
              <Title level={3} style={{ marginBottom: 8 }}>用户登录</Title>
              <Text type="secondary">请输入您的凭据以访问交易终端</Text>
            </div>

            <Form
              name="login"
              onFinish={onFinish}
              layout="vertical"
              size="large"
              requiredMark={false}
            >
              <Form.Item
                name="username"
                rules={[{ required: true, message: '请输入用户名' }]}
              >
                <Input 
                  prefix={<UserOutlined style={{ color: themeMode === 'dark' ? 'rgba(255,255,255,0.25)' : 'rgba(0,0,0,0.25)' }} />} 
                  placeholder="用户名 / 邮箱" 
                  style={{ 
                    background: themeMode === 'dark' ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.02)', 
                    borderColor: themeMode === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)' 
                  }}
                />
              </Form.Item>

              <Form.Item
                name="password"
                rules={[{ required: true, message: '请输入密码' }]}
                style={{ marginBottom: 12 }}
              >
                <Input.Password 
                  prefix={<LockOutlined style={{ color: themeMode === 'dark' ? 'rgba(255,255,255,0.25)' : 'rgba(0,0,0,0.25)' }} />} 
                  placeholder="登录密码" 
                  style={{ 
                    background: themeMode === 'dark' ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.02)', 
                    borderColor: themeMode === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)' 
                  }}
                />
              </Form.Item>

              <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 24 }}>
                <Button type="link" size="small" style={{ padding: 0, color: themeMode === 'dark' ? 'rgba(255,255,255,0.45)' : 'rgba(0,0,0,0.45)' }}>
                  忘记密码？
                </Button>
              </div>

              <Form.Item>
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  block 
                  loading={loading}
                  style={{
                    height: 48,
                    fontSize: 16,
                    fontWeight: 600,
                    boxShadow: '0 4px 12px rgba(22, 119, 255, 0.3)'
                  }}
                >
                  进入终端
                </Button>
              </Form.Item>
            </Form>

            <Divider plain style={{ margin: '24px 0' }}>
              <Text type="secondary" style={{ fontSize: 12 }}>其他访问方式</Text>
            </Divider>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <Button 
                block 
                icon={<SafetyCertificateOutlined />} 
                onClick={handleDemoLogin}
                style={{ 
                  background: 'transparent', 
                  borderColor: themeMode === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)' 
                }}
              >
                演示入口
              </Button>
              <Button 
                block 
                icon={<GlobalOutlined />} 
                style={{ 
                  background: 'transparent', 
                  borderColor: themeMode === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)' 
                }}
              >
                SSO 登录
              </Button>
            </div>

            <div style={{ marginTop: 32, textAlign: 'center' }}>
              <Text style={{ fontSize: 12, color: themeMode === 'dark' ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.3)' }}>
                © 2026 PowerX Intelligence. All rights reserved.
              </Text>
            </div>
          </div>
        </div>
      </div>
    </ConfigProvider>
  );
};

export default Login;
