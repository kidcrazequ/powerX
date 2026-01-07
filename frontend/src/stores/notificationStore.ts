/**
 * PowerX 通知状态管理
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 使用 Zustand 管理系统通知
 */

import { create } from 'zustand';

/**
 * 通知类型
 */
export type NotificationType = 'info' | 'success' | 'warning' | 'error';

/**
 * 通知分类
 */
export type NotificationCategory = 'trade' | 'price' | 'system' | 'report';

/**
 * 通知项接口
 */
export interface NotificationItem {
  /** 通知ID */
  id: string;
  /** 通知标题 */
  title: string;
  /** 通知内容 */
  content: string;
  /** 通知类型 */
  type: NotificationType;
  /** 通知分类 */
  category: NotificationCategory;
  /** 创建时间 */
  createdAt: Date;
  /** 是否已读 */
  read: boolean;
}

/**
 * 通知状态接口
 */
interface NotificationState {
  /** 通知列表 */
  notifications: NotificationItem[];
  /** 通知面板是否可见 */
  visible: boolean;
  
  // Actions
  /** 添加通知 */
  addNotification: (notification: Omit<NotificationItem, 'id' | 'createdAt' | 'read'>) => void;
  /** 标记单个通知为已读 */
  markAsRead: (id: string) => void;
  /** 标记所有通知为已读 */
  markAllAsRead: () => void;
  /** 删除通知 */
  removeNotification: (id: string) => void;
  /** 清除所有通知 */
  clearAll: () => void;
  /** 设置面板可见性 */
  setVisible: (visible: boolean) => void;
  /** 获取未读数量 */
  getUnreadCount: () => number;
}

/**
 * 生成唯一ID
 */
const generateId = (): string => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * 初始模拟通知数据
 */
const initialNotifications: NotificationItem[] = [
  {
    id: '1',
    title: '订单成交通知',
    content: '您的广东现货买入订单已成交，成交量 100 MWh，成交价 485.32 元/MWh',
    type: 'success',
    category: 'trade',
    createdAt: new Date(Date.now() - 1000 * 60 * 5), // 5分钟前
    read: false,
  },
  {
    id: '2',
    title: '价格预警',
    content: '广东现货价格已突破 480 元/MWh 阈值，当前价格 485.32 元/MWh',
    type: 'warning',
    category: 'price',
    createdAt: new Date(Date.now() - 1000 * 60 * 30), // 30分钟前
    read: false,
  },
  {
    id: '3',
    title: '系统公告',
    content: '山东省明日预计新能源出力增加，电价可能下降，请关注市场变化',
    type: 'info',
    category: 'system',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2小时前
    read: false,
  },
  {
    id: '4',
    title: '日报生成完成',
    content: '2026年1月6日交易日报已生成，请前往报告中心查看',
    type: 'info',
    category: 'report',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 8), // 8小时前
    read: true,
  },
  {
    id: '5',
    title: '合约到期提醒',
    content: '您的浙江中长期月度合约将于3天后到期，请及时处理',
    type: 'warning',
    category: 'trade',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1天前
    read: true,
  },
];

/**
 * 通知 Store
 */
export const useNotificationStore = create<NotificationState>((set, get) => ({
  notifications: initialNotifications,
  visible: false,

  /**
   * 添加通知
   * @param notification 通知内容
   */
  addNotification: (notification) => {
    const newNotification: NotificationItem = {
      ...notification,
      id: generateId(),
      createdAt: new Date(),
      read: false,
    };
    set((state) => ({
      notifications: [newNotification, ...state.notifications],
    }));
  },

  /**
   * 标记单个通知为已读
   * @param id 通知ID
   */
  markAsRead: (id: string) => {
    set((state) => ({
      notifications: state.notifications.map((n) =>
        n.id === id ? { ...n, read: true } : n
      ),
    }));
  },

  /**
   * 标记所有通知为已读
   */
  markAllAsRead: () => {
    set((state) => ({
      notifications: state.notifications.map((n) => ({ ...n, read: true })),
    }));
  },

  /**
   * 删除通知
   * @param id 通知ID
   */
  removeNotification: (id: string) => {
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    }));
  },

  /**
   * 清除所有通知
   */
  clearAll: () => {
    set({ notifications: [] });
  },

  /**
   * 设置面板可见性
   * @param visible 是否可见
   */
  setVisible: (visible: boolean) => {
    set({ visible });
  },

  /**
   * 获取未读通知数量
   */
  getUnreadCount: () => {
    return get().notifications.filter((n) => !n.read).length;
  },
}));
