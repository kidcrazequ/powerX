/**
 * PowerX 实时数据 Store
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 管理 WebSocket 推送的实时数据
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

// ============ 类型定义 ============

export interface RealtimePrice {
  province: string;
  price: number;
  prevPrice: number;
  changePercent: number;
  timestamp: string;
  trend: 'up' | 'down' | 'stable';
}

export interface OrderUpdate {
  orderId: string;
  status: string;
  filledQuantity?: number;
  filledPrice?: number;
  message?: string;
  timestamp: string;
}

export interface Notification {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

export interface ConnectionStatus {
  market: boolean;
  orders: boolean;
  notifications: boolean;
}

interface RealtimeState {
  // 实时价格: province -> RealtimePrice
  prices: Record<string, RealtimePrice>;
  
  // 订单更新队列
  orderUpdates: OrderUpdate[];
  
  // 通知队列
  notifications: Notification[];
  unreadCount: number;
  
  // 连接状态
  connectionStatus: ConnectionStatus;
  
  // Actions
  updatePrice: (province: string, price: number, changePercent: number) => void;
  addOrderUpdate: (update: OrderUpdate) => void;
  clearOrderUpdates: () => void;
  addNotification: (notification: Omit<Notification, 'id' | 'read'>) => void;
  markNotificationRead: (id: string) => void;
  markAllNotificationsRead: () => void;
  clearNotifications: () => void;
  setConnectionStatus: (channel: keyof ConnectionStatus, connected: boolean) => void;
}

// ============ Store 实现 ============

export const useRealtimeStore = create<RealtimeState>()(
  devtools(
    (set, get) => ({
      prices: {},
      orderUpdates: [],
      notifications: [],
      unreadCount: 0,
      connectionStatus: {
        market: false,
        orders: false,
        notifications: false
      },

      updatePrice: (province: string, price: number, changePercent: number) => {
        set((state) => {
          const prevData = state.prices[province];
          const prevPrice = prevData?.price || price;
          
          // 确定价格趋势
          let trend: 'up' | 'down' | 'stable' = 'stable';
          if (price > prevPrice) trend = 'up';
          else if (price < prevPrice) trend = 'down';

          return {
            prices: {
              ...state.prices,
              [province]: {
                province,
                price,
                prevPrice,
                changePercent,
                timestamp: new Date().toISOString(),
                trend
              }
            }
          };
        });
      },

      addOrderUpdate: (update: OrderUpdate) => {
        set((state) => ({
          orderUpdates: [update, ...state.orderUpdates].slice(0, 50) // 保留最近50条
        }));
      },

      clearOrderUpdates: () => {
        set({ orderUpdates: [] });
      },

      addNotification: (notification) => {
        const id = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const newNotification: Notification = {
          ...notification,
          id,
          read: false
        };

        set((state) => ({
          notifications: [newNotification, ...state.notifications].slice(0, 100),
          unreadCount: state.unreadCount + 1
        }));
      },

      markNotificationRead: (id: string) => {
        set((state) => {
          const notification = state.notifications.find((n) => n.id === id);
          if (!notification || notification.read) return state;

          return {
            notifications: state.notifications.map((n) =>
              n.id === id ? { ...n, read: true } : n
            ),
            unreadCount: Math.max(0, state.unreadCount - 1)
          };
        });
      },

      markAllNotificationsRead: () => {
        set((state) => ({
          notifications: state.notifications.map((n) => ({ ...n, read: true })),
          unreadCount: 0
        }));
      },

      clearNotifications: () => {
        set({ notifications: [], unreadCount: 0 });
      },

      setConnectionStatus: (channel: keyof ConnectionStatus, connected: boolean) => {
        set((state) => ({
          connectionStatus: {
            ...state.connectionStatus,
            [channel]: connected
          }
        }));
      }
    }),
    { name: 'realtime-store' }
  )
);

// ============ 选择器 ============

/**
 * 获取指定省份的实时价格
 */
export const selectRealtimePrice = (province: string) => (state: RealtimeState) =>
  state.prices[province];

/**
 * 获取所有省份的实时价格
 */
export const selectAllRealtimePrices = (state: RealtimeState) =>
  Object.values(state.prices);

/**
 * 获取未读通知数量
 */
export const selectUnreadCount = (state: RealtimeState) => state.unreadCount;

/**
 * 获取最近的订单更新
 */
export const selectRecentOrderUpdates = (limit: number = 10) => (state: RealtimeState) =>
  state.orderUpdates.slice(0, limit);

/**
 * 检查是否所有 WebSocket 都已连接
 */
export const selectIsFullyConnected = (state: RealtimeState) =>
  Object.values(state.connectionStatus).every(Boolean);

export default useRealtimeStore;
