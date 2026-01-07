/**
 * PowerX 实时价格组件
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 显示实时市场价格，带价格变动动画
 */

import React, { useEffect, useState } from 'react';
import { Card, Statistic, Tag, Space, Tooltip } from 'antd';
import { 
  ArrowUpOutlined, 
  ArrowDownOutlined, 
  MinusOutlined,
  SyncOutlined,
  DisconnectOutlined 
} from '@ant-design/icons';
import { useMarketWebSocket, ConnectionState } from '../hooks/useWebSocket';
import { useRealtimeStore } from '../stores/realtimeStore';

// ============ 类型定义 ============

interface RealtimePriceProps {
  province: string;
  showCard?: boolean;
  showConnection?: boolean;
  onPriceUpdate?: (price: number, changePercent: number) => void;
}

interface PriceData {
  price: number;
  prevPrice: number;
  changePercent: number;
  trend: 'up' | 'down' | 'stable';
  timestamp: string;
}

// ============ 样式 ============

const styles = {
  container: {
    position: 'relative' as const
  },
  priceUp: {
    color: '#52c41a'
  },
  priceDown: {
    color: '#ff4d4f'
  },
  priceStable: {
    color: '#8c8c8c'
  },
  flash: {
    animation: 'priceFlash 0.5s ease-out'
  },
  connectionIndicator: {
    position: 'absolute' as const,
    top: 8,
    right: 8
  }
};

// ============ 组件 ============

const RealtimePrice: React.FC<RealtimePriceProps> = ({
  province,
  showCard = true,
  showConnection = true,
  onPriceUpdate
}) => {
  const [priceData, setPriceData] = useState<PriceData | null>(null);
  const [isFlashing, setIsFlashing] = useState(false);
  
  const { updatePrice } = useRealtimeStore();

  // WebSocket 连接
  const { connectionState, lastMessage } = useMarketWebSocket(province, (data) => {
    const newPriceData: PriceData = {
      price: data.price,
      prevPrice: data.prev_price,
      changePercent: data.change_percent,
      trend: data.trend,
      timestamp: data.timestamp
    };
    
    setPriceData(newPriceData);
    
    // 更新全局 store
    updatePrice(province, data.price, data.change_percent);
    
    // 触发闪烁动画
    setIsFlashing(true);
    setTimeout(() => setIsFlashing(false), 500);
    
    // 回调
    onPriceUpdate?.(data.price, data.change_percent);
  });

  // 获取趋势图标
  const getTrendIcon = () => {
    if (!priceData) return <MinusOutlined />;
    
    switch (priceData.trend) {
      case 'up':
        return <ArrowUpOutlined style={styles.priceUp} />;
      case 'down':
        return <ArrowDownOutlined style={styles.priceDown} />;
      default:
        return <MinusOutlined style={styles.priceStable} />;
    }
  };

  // 获取价格颜色
  const getPriceColor = () => {
    if (!priceData) return styles.priceStable;
    
    switch (priceData.trend) {
      case 'up':
        return styles.priceUp;
      case 'down':
        return styles.priceDown;
      default:
        return styles.priceStable;
    }
  };

  // 获取连接状态标签
  const getConnectionTag = () => {
    switch (connectionState) {
      case 'connected':
        return (
          <Tag color="success" icon={<SyncOutlined spin />}>
            实时
          </Tag>
        );
      case 'connecting':
      case 'reconnecting':
        return (
          <Tag color="processing" icon={<SyncOutlined spin />}>
            连接中
          </Tag>
        );
      case 'disconnected':
        return (
          <Tag color="error" icon={<DisconnectOutlined />}>
            断开
          </Tag>
        );
      default:
        return null;
    }
  };

  // 价格显示内容
  const priceContent = (
    <div style={styles.container}>
      {showConnection && (
        <div style={styles.connectionIndicator}>
          {getConnectionTag()}
        </div>
      )}
      
      <Statistic
        title={`${province} 实时电价`}
        value={priceData?.price ?? '--'}
        precision={2}
        suffix="元/MWh"
        prefix={getTrendIcon()}
        valueStyle={{
          ...getPriceColor(),
          transition: 'color 0.3s',
          ...(isFlashing ? { transform: 'scale(1.05)' } : {})
        }}
      />
      
      {priceData && (
        <Space style={{ marginTop: 8 }}>
          <Tooltip title="相比上次更新">
            <span style={getPriceColor()}>
              {priceData.changePercent >= 0 ? '+' : ''}
              {priceData.changePercent.toFixed(2)}%
            </span>
          </Tooltip>
          <span style={{ color: '#8c8c8c', fontSize: 12 }}>
            {new Date(priceData.timestamp).toLocaleTimeString()}
          </span>
        </Space>
      )}
    </div>
  );

  if (showCard) {
    return (
      <Card 
        size="small" 
        style={{ 
          minWidth: 200,
          borderRadius: 8,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}
      >
        {priceContent}
      </Card>
    );
  }

  return priceContent;
};

// ============ 多省份价格面板 ============

interface MultiProvincePriceProps {
  provinces?: string[];
}

export const MultiProvincePrice: React.FC<MultiProvincePriceProps> = ({
  provinces = ['广东', '浙江', '山东', '山西', '甘肃']
}) => {
  return (
    <Space wrap>
      {provinces.map((province) => (
        <RealtimePrice 
          key={province} 
          province={province}
          showConnection={false}
        />
      ))}
    </Space>
  );
};

export default RealtimePrice;
