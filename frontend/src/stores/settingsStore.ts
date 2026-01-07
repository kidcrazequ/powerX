/**
 * PowerX 系统设置状态管理
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 使用 Zustand 管理用户偏好设置
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * 主题模式类型
 */
export type ThemeMode = 'dark' | 'light';

/**
 * 语言类型
 */
export type Language = 'zh-CN' | 'en-US';

/**
 * 通知设置接口
 */
interface NotificationSettings {
  /** 交易提醒 */
  tradeReminder: boolean;
  /** 价格预警 */
  priceAlert: boolean;
  /** 系统公告 */
  systemNotice: boolean;
}

/**
 * 设置状态接口
 */
interface SettingsState {
  /** 主题模式 */
  themeMode: ThemeMode;
  /** 默认省份 */
  defaultProvince: string;
  /** 语言设置 */
  language: Language;
  /** 通知设置 */
  notifications: NotificationSettings;
  
  // Actions
  /** 设置主题模式 */
  setThemeMode: (mode: ThemeMode) => void;
  /** 设置默认省份 */
  setDefaultProvince: (province: string) => void;
  /** 设置语言 */
  setLanguage: (language: Language) => void;
  /** 设置通知选项 */
  setNotification: (key: keyof NotificationSettings, value: boolean) => void;
  /** 重置所有设置 */
  resetSettings: () => void;
}

/**
 * 默认设置
 */
const defaultSettings = {
  themeMode: 'dark' as ThemeMode,
  defaultProvince: '广东',
  language: 'zh-CN' as Language,
  notifications: {
    tradeReminder: true,
    priceAlert: true,
    systemNotice: true,
  },
};

/**
 * 系统设置 Store
 */
export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      ...defaultSettings,

      /**
       * 设置主题模式
       * @param mode 主题模式（dark/light）
       */
      setThemeMode: (mode: ThemeMode) => {
        set({ themeMode: mode });
      },

      /**
       * 设置默认省份
       * @param province 省份名称
       */
      setDefaultProvince: (province: string) => {
        set({ defaultProvince: province });
      },

      /**
       * 设置语言
       * @param language 语言代码
       */
      setLanguage: (language: Language) => {
        set({ language });
      },

      /**
       * 设置通知选项
       * @param key 通知类型
       * @param value 开关状态
       */
      setNotification: (key: keyof NotificationSettings, value: boolean) => {
        set((state) => ({
          notifications: {
            ...state.notifications,
            [key]: value,
          },
        }));
      },

      /**
       * 重置所有设置为默认值
       */
      resetSettings: () => {
        set(defaultSettings);
      },
    }),
    {
      name: 'powerx-settings-storage',
      partialize: (state) => ({
        themeMode: state.themeMode,
        defaultProvince: state.defaultProvince,
        language: state.language,
        notifications: state.notifications,
      }),
    }
  )
);
