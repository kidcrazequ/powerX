/**
 * PowerX 错误边界组件
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 捕获 React 渲染错误，提供优雅降级
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Button, Result, Typography, Space, Card } from 'antd';
import { ReloadOutlined, BugOutlined, HomeOutlined } from '@ant-design/icons';

const { Text, Paragraph } = Typography;

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ errorInfo });
    
    // 调用外部错误处理回调
    this.props.onError?.(error, errorInfo);
    
    // 记录错误到控制台
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    // 在生产环境可以发送到错误追踪服务
    // reportErrorToService(error, errorInfo);
  }

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  handleRetry = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    const { hasError, error, errorInfo } = this.state;
    const { children, fallback } = this.props;

    if (hasError) {
      // 使用自定义 fallback
      if (fallback) {
        return fallback;
      }

      // 默认错误页面
      return (
        <div style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: 24,
          background: '#f0f2f5'
        }}>
          <Card style={{ maxWidth: 600, width: '100%', textAlign: 'center' }}>
            <Result
              status="error"
              title="页面出现了一些问题"
              subTitle="我们已记录此错误，请尝试刷新页面或返回首页"
              extra={
                <Space>
                  <Button 
                    type="primary" 
                    icon={<ReloadOutlined />}
                    onClick={this.handleReload}
                  >
                    刷新页面
                  </Button>
                  <Button 
                    icon={<HomeOutlined />}
                    onClick={this.handleGoHome}
                  >
                    返回首页
                  </Button>
                </Space>
              }
            />
            
            {/* 开发环境显示错误详情 */}
            {process.env.NODE_ENV === 'development' && error && (
              <div style={{ 
                marginTop: 24, 
                textAlign: 'left',
                background: '#fafafa',
                padding: 16,
                borderRadius: 8,
                border: '1px solid #f0f0f0'
              }}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Text strong>
                    <BugOutlined style={{ marginRight: 8 }} />
                    错误详情 (仅开发环境可见)
                  </Text>
                  <Paragraph 
                    code 
                    copyable 
                    style={{ 
                      background: '#fff1f0', 
                      padding: 8, 
                      borderRadius: 4,
                      margin: 0
                    }}
                  >
                    {error.message}
                  </Paragraph>
                  {errorInfo && (
                    <pre style={{ 
                      fontSize: 12, 
                      overflow: 'auto', 
                      maxHeight: 200,
                      background: '#f6f6f6',
                      padding: 8,
                      borderRadius: 4,
                      margin: 0
                    }}>
                      {errorInfo.componentStack}
                    </pre>
                  )}
                </Space>
              </div>
            )}
          </Card>
        </div>
      );
    }

    return children;
  }
}

export default ErrorBoundary;


/**
 * 页面级错误边界
 * 用于包裹单个页面，错误不会影响整个应用
 */
export const PageErrorBoundary: React.FC<{ children: ReactNode }> = ({ children }) => {
  return (
    <ErrorBoundary
      fallback={
        <Result
          status="warning"
          title="此页面加载失败"
          subTitle="请刷新页面重试"
          extra={
            <Button 
              type="primary" 
              onClick={() => window.location.reload()}
            >
              刷新
            </Button>
          }
        />
      }
    >
      {children}
    </ErrorBoundary>
  );
};


/**
 * 组件级错误边界
 * 用于包裹单个组件，提供最小化的错误展示
 */
export const ComponentErrorBoundary: React.FC<{ 
  children: ReactNode;
  fallback?: ReactNode;
}> = ({ children, fallback }) => {
  return (
    <ErrorBoundary
      fallback={fallback || (
        <div style={{ 
          padding: 16, 
          textAlign: 'center', 
          color: '#ff4d4f' 
        }}>
          <Text type="danger">组件加载失败</Text>
        </div>
      )}
    >
      {children}
    </ErrorBoundary>
  );
};
