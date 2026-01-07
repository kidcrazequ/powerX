/**
 * PowerX 系统设置页面
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 主题、通知、默认省份、语言设置
 */

import React from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Switch, 
  Select, 
  Typography,
  Space,
  Divider,
  Button,
  message,
  theme,
  List
} from 'antd';
import { 
  BulbOutlined,
  BellOutlined,
  GlobalOutlined,
  EnvironmentOutlined,
  SyncOutlined,
  CheckOutlined
} from '@ant-design/icons';
import { PageContainer } from '@ant-design/pro-components';

import { useSettingsStore, ThemeMode, Language } from '../stores/settingsStore';

const { Text, Title, Paragraph } = Typography;

/**
 * 省份选项配置
 */
const PROVINCES = [
  { value: '广东', label: '广东' },
  { value: '浙江', label: '浙江' },
  { value: '山东', label: '山东' },
  { value: '山西', label: '山西' },
  { value: '甘肃', label: '甘肃' },
];

/**
 * 语言选项配置
 */
const LANGUAGES = [
  { value: 'zh-CN', label: '简体中文' },
  { value: 'en-US', label: 'English' },
];

/**
 * 系统设置页面组件
 */
const Settings: React.FC = () => {
  const { token } = theme.useToken();
  const {
    themeMode,
    defaultProvince,
    language,
    notifications,
    setThemeMode,
    setDefaultProvince,
    setLanguage,
    setNotification,
    resetSettings,
  } = useSettingsStore();

  /**
   * 处理主题切换
   * @param checked 是否为深色模式
   */
  const handleThemeChange = (checked: boolean) => {
    const mode: ThemeMode = checked ? 'dark' : 'light';
    setThemeMode(mode);
    message.success(`已切换为${checked ? '深色' : '浅色'}模式`);
  };

  /**
   * 处理省份变更
   * @param value 省份名称
   */
  const handleProvinceChange = (value: string) => {
    setDefaultProvince(value);
    message.success(`默认市场已设置为 ${value}`);
  };

  /**
   * 处理语言变更
   * @param value 语言代码
   */
  const handleLanguageChange = (value: Language) => {
    setLanguage(value);
    message.success('语言设置已更新');
  };

  /**
   * 处理重置设置
   */
  const handleResetSettings = () => {
    resetSettings();
    message.success('已恢复默认设置');
  };

  /**
   * 通知设置项配置
   */
  const notificationItems = [
    {
      key: 'tradeReminder',
      title: '交易提醒',
      description: '订单成交、委托状态变化等交易相关通知',
      checked: notifications.tradeReminder,
    },
    {
      key: 'priceAlert',
      title: '价格预警',
      description: '价格触发预设阈值时发送提醒',
      checked: notifications.priceAlert,
    },
    {
      key: 'systemNotice',
      title: '系统公告',
      description: '市场规则变化、系统维护等重要公告',
      checked: notifications.systemNotice,
    },
  ];

  return (
    <PageContainer
      header={{
        title: '系统设置',
        subTitle: '自定义您的使用偏好',
        extra: [
          <Button 
            key="reset" 
            icon={<SyncOutlined />}
            onClick={handleResetSettings}
          >
            恢复默认
          </Button>
        ]
      }}
    >
      <Row gutter={[24, 24]}>
        {/* 外观设置 */}
        <Col xs={24} lg={12}>
          <Card 
            className="hover-card"
            title={
              <Space>
                <BulbOutlined style={{ color: token.colorWarning }} />
                <span>外观设置</span>
              </Space>
            }
            style={{ borderRadius: 12, border: 'none' }}
          >
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              padding: '16px 0'
            }}>
              <div>
                <Text strong style={{ display: 'block', marginBottom: 4 }}>深色模式</Text>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  开启后界面将使用深色主题，保护眼睛
                </Text>
              </div>
              <Switch 
                checked={themeMode === 'dark'}
                onChange={handleThemeChange}
                checkedChildren="开"
                unCheckedChildren="关"
              />
            </div>

            <Divider style={{ margin: '8px 0' }} />

            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              padding: '16px 0'
            }}>
              <div>
                <Text strong style={{ display: 'block', marginBottom: 4 }}>界面语言</Text>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  选择系统显示语言
                </Text>
              </div>
              <Select
                value={language}
                onChange={handleLanguageChange}
                options={LANGUAGES}
                style={{ width: 140 }}
                variant="filled"
              />
            </div>
          </Card>
        </Col>

        {/* 市场设置 */}
        <Col xs={24} lg={12}>
          <Card 
            className="hover-card"
            title={
              <Space>
                <EnvironmentOutlined style={{ color: token.colorPrimary }} />
                <span>市场设置</span>
              </Space>
            }
            style={{ borderRadius: 12, border: 'none' }}
          >
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              padding: '16px 0'
            }}>
              <div>
                <Text strong style={{ display: 'block', marginBottom: 4 }}>默认交易市场</Text>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  登录后自动选择的省级电力市场
                </Text>
              </div>
              <Select
                value={defaultProvince}
                onChange={handleProvinceChange}
                options={PROVINCES}
                style={{ width: 140 }}
                variant="filled"
              />
            </div>

            <Divider style={{ margin: '8px 0' }} />

            {/* 当前市场信息 */}
            <div style={{ 
              background: themeMode === 'dark' ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.02)',
              padding: 16,
              borderRadius: 8,
              marginTop: 16
            }}>
              <Space direction="vertical" size={8} style={{ width: '100%' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Text type="secondary">当前选中市场</Text>
                  <Text strong style={{ color: token.colorPrimary }}>{defaultProvince}</Text>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Text type="secondary">市场类型</Text>
                  <Text>现货 + 中长期</Text>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Text type="secondary">交易状态</Text>
                  <Text style={{ color: token.colorSuccess }}>
                    <CheckOutlined style={{ marginRight: 4 }} />
                    正常运行
                  </Text>
                </div>
              </Space>
            </div>
          </Card>
        </Col>

        {/* 通知设置 */}
        <Col span={24}>
          <Card 
            className="hover-card"
            title={
              <Space>
                <BellOutlined style={{ color: token.colorInfo }} />
                <span>通知设置</span>
              </Space>
            }
            style={{ borderRadius: 12, border: 'none' }}
          >
            <List
              dataSource={notificationItems}
              renderItem={(item) => (
                <List.Item
                  style={{ padding: '20px 0' }}
                  actions={[
                    <Switch 
                      key={item.key}
                      checked={item.checked}
                      onChange={(checked) => setNotification(item.key as any, checked)}
                      checkedChildren="开"
                      unCheckedChildren="关"
                    />
                  ]}
                >
                  <List.Item.Meta
                    title={<Text strong>{item.title}</Text>}
                    description={<Text type="secondary" style={{ fontSize: 12 }}>{item.description}</Text>}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>

        {/* 关于信息 */}
        <Col span={24}>
          <Card 
            className="hover-card"
            title={
              <Space>
                <GlobalOutlined style={{ color: token.colorTextSecondary }} />
                <span>关于系统</span>
              </Space>
            }
            style={{ borderRadius: 12, border: 'none' }}
          >
            <Row gutter={[24, 16]}>
              <Col xs={24} sm={12} md={6}>
                <div style={{ textAlign: 'center', padding: 16 }}>
                  <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>系统版本</Text>
                  <Text strong className="data-font" style={{ fontSize: 18 }}>v1.0.0</Text>
                </div>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <div style={{ textAlign: 'center', padding: 16 }}>
                  <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>构建日期</Text>
                  <Text strong className="data-font" style={{ fontSize: 18 }}>2026-01-07</Text>
                </div>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <div style={{ textAlign: 'center', padding: 16 }}>
                  <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>技术栈</Text>
                  <Text strong style={{ fontSize: 18 }}>React + Ant Design</Text>
                </div>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <div style={{ textAlign: 'center', padding: 16 }}>
                  <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>开发团队</Text>
                  <Text strong style={{ fontSize: 18 }}>PowerX Team</Text>
                </div>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </PageContainer>
  );
};

export default Settings;
