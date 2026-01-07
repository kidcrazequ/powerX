/**
 * PowerX API 服务
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * Axios 实例和 API 调用封装
 * 包含统一错误处理、自动重试机制
 */

import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { message, notification } from 'antd';
import { useAuthStore } from '../stores/authStore';

// ============ 类型定义 ============

interface APIResponse<T = any> {
  code: number;
  message: string;
  success: boolean;
  data?: T;
  detail?: any;
  timestamp?: string;
}

interface APIError {
  code: number;
  message: string;
  detail?: any;
}

interface RetryConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
  _retryCount?: number;
}

// ============ 错误码映射 ============

const ERROR_MESSAGES: Record<number, string> = {
  400: '请求参数错误',
  401: '登录已过期，请重新登录',
  403: '权限不足，无法执行此操作',
  404: '请求的资源不存在',
  409: '数据冲突，请刷新后重试',
  429: '请求过于频繁，请稍后再试',
  500: '服务器错误，请稍后重试',
  502: '网关错误',
  503: '服务暂时不可用',
  504: '网关超时'
};

// ============ 重试配置 ============

const RETRY_CONFIG = {
  maxRetries: 3,
  retryDelay: 1000,
  retryStatusCodes: [408, 500, 502, 503, 504, 0], // 0 表示网络错误
};

// ============ 工具函数 ============

/**
 * 延迟函数
 */
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * 判断是否应该重试
 */
const shouldRetry = (error: AxiosError): boolean => {
  // 网络错误
  if (!error.response) {
    return true;
  }
  
  // 特定状态码
  const status = error.response.status;
  return RETRY_CONFIG.retryStatusCodes.includes(status);
};

/**
 * 解析错误响应
 */
const parseError = (error: AxiosError<APIResponse>): APIError => {
  if (error.response?.data) {
    const data = error.response.data;
    return {
      code: data.code || error.response.status,
      message: data.message || ERROR_MESSAGES[error.response.status] || '未知错误',
      detail: data.detail
    };
  }
  
  if (error.response) {
    return {
      code: error.response.status,
      message: ERROR_MESSAGES[error.response.status] || '请求失败'
    };
  }
  
  // 网络错误
  if (error.code === 'ECONNABORTED') {
    return { code: 0, message: '请求超时，请检查网络连接' };
  }
  
  return { code: 0, message: '网络连接失败，请检查网络' };
};

/**
 * 显示错误消息
 */
const showError = (apiError: APIError, silent: boolean = false) => {
  if (silent) return;
  
  // 401 错误特殊处理，使用 notification
  if (apiError.code === 401) {
    notification.warning({
      message: '登录已过期',
      description: '请重新登录',
      duration: 3
    });
    return;
  }
  
  // 其他错误使用 message
  message.error(apiError.message);
};

// ============ 创建 Axios 实例 ============

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// ============ 请求拦截器 ============

api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // 添加请求时间戳（用于调试）
    (config as any)._requestTime = Date.now();
    
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// ============ 响应拦截器 ============

api.interceptors.response.use(
  (response) => {
    // 记录请求耗时（开发环境）
    if (import.meta.env.DEV) {
      const requestTime = (response.config as any)._requestTime;
      if (requestTime) {
        const duration = Date.now() - requestTime;
        console.debug(`[API] ${response.config.method?.toUpperCase()} ${response.config.url} - ${duration}ms`);
      }
    }
    
    return response;
  },
  async (error: AxiosError<APIResponse>) => {
    const config = error.config as RetryConfig;
    
    if (!config) {
      return Promise.reject(error);
    }
    
    // 初始化重试计数
    config._retryCount = config._retryCount || 0;
    
    // 处理 401 错误 - 尝试刷新令牌
    if (error.response?.status === 401 && !config._retry) {
      config._retry = true;
      
      const refreshToken = useAuthStore.getState().refreshToken;
      if (refreshToken) {
        try {
          const response = await axios.post(
            `${api.defaults.baseURL}/auth/refresh`,
            { refresh_token: refreshToken }
          );
          
          const { access_token, refresh_token: newRefreshToken } = response.data;
          useAuthStore.getState().setTokens(access_token, newRefreshToken);
          
          config.headers.Authorization = `Bearer ${access_token}`;
          return api(config);
        } catch (refreshError) {
          useAuthStore.getState().logout();
          showError({ code: 401, message: '登录已过期，请重新登录' });
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      } else {
        useAuthStore.getState().logout();
        window.location.href = '/login';
      }
    }
    
    // 自动重试逻辑（仅对特定错误类型）
    if (shouldRetry(error) && config._retryCount < RETRY_CONFIG.maxRetries) {
      config._retryCount += 1;
      
      console.warn(`[API] Retry attempt ${config._retryCount}/${RETRY_CONFIG.maxRetries} for ${config.url}`);
      
      // 指数退避延迟
      const delayMs = RETRY_CONFIG.retryDelay * Math.pow(2, config._retryCount - 1);
      await delay(delayMs);
      
      return api(config);
    }
    
    // 解析并显示错误
    const apiError = parseError(error);
    const silent = (config as any)._silent || false;
    showError(apiError, silent);
    
    // 增强错误对象
    const enhancedError = Object.assign(error, { apiError });
    
    return Promise.reject(enhancedError);
  }
);

// ============ 请求包装器 ============

/**
 * 静默请求 - 不显示错误消息
 */
export const silentRequest = <T = any>(config: Parameters<typeof api.request>[0]) => {
  return api.request<T>({ ...config, _silent: true } as any);
};

/**
 * 带取消功能的请求
 */
export const cancelableRequest = <T = any>(config: Parameters<typeof api.request>[0]) => {
  const controller = new AbortController();
  
  const promise = api.request<T>({
    ...config,
    signal: controller.signal
  });
  
  return {
    promise,
    cancel: () => controller.abort()
  };
};

// ============ 认证 API ============

export const authApi = {
  login: (username: string, password: string) =>
    api.post('/auth/login', { username, password }),

  register: (data: { username: string; password: string; email: string; name: string }) =>
    api.post('/auth/register', data),

  refresh: (refreshToken: string) =>
    api.post('/auth/refresh', { refresh_token: refreshToken }),

  me: () => api.get('/auth/me'),

  logout: () => api.post('/auth/logout')
};

// ============ 交易 API ============

export const tradingApi = {
  createOrder: (data: {
    province: string;
    market_type: string;
    direction: string;
    price: number;
    quantity_mwh: number;
  }) => api.post('/trading/orders', data),

  getOrders: (params?: { market_type?: string; status?: string }) =>
    api.get('/trading/orders', { params }),

  getOrder: (orderId: string) =>
    api.get(`/trading/orders/${orderId}`),

  cancelOrder: (orderId: string) =>
    api.delete(`/trading/orders/${orderId}`),

  getPositions: () => api.get('/trading/positions'),

  getStatistics: (params?: { start_date?: string; end_date?: string }) =>
    api.get('/trading/statistics', { params })
};

// ============ 市场数据 API ============

export const marketApi = {
  getSummary: (province: string) =>
    api.get(`/market/summary/${province}`),

  getPrices: (province: string, params?: { start_date?: string; end_date?: string }) =>
    api.get(`/market/prices/${province}`, { params }),

  getHourlyPrices: (province: string, targetDate?: string) =>
    api.get(`/market/hourly/${province}`, { params: { target_date: targetDate } }),

  getComparison: (provinces: string[], targetDate?: string) =>
    api.get('/market/comparison', { 
      params: { provinces: provinces.join(','), target_date: targetDate } 
    }),

  getRealtimePrice: (province: string) =>
    api.get(`/market/realtime/${province}`),

  getProvinces: () => api.get('/market/provinces')
};

// ============ 合同 API ============

export const contractApi = {
  createContract: (data: {
    contract_type: string;
    counterparty: string;
    province: string;
    total_quantity_mwh: number;
    price: number;
    start_date: string;
    end_date: string;
  }) => api.post('/contracts', data),

  getContracts: (params?: { contract_type?: string; status?: string }) =>
    api.get('/contracts', { params }),

  getContract: (contractId: string) =>
    api.get(`/contracts/${contractId}`),

  decomposeContract: (contractId: string, monthlyQuantities: number[]) =>
    api.post(`/contracts/${contractId}/decompose`, {
      contract_id: contractId,
      monthly_quantities: monthlyQuantities
    }),

  getExecutionRecords: (contractId: string) =>
    api.get(`/contracts/${contractId}/executions`)
};

// ============ 结算 API ============

export const settlementApi = {
  getRecords: (params?: { 
    settlement_type?: string; 
    status?: string;
    start_date?: string;
    end_date?: string;
  }) => api.get('/settlement/records', { params }),

  getRecord: (recordId: string) =>
    api.get(`/settlement/records/${recordId}`),

  getMonthlySummary: (year: number, month: number) =>
    api.get('/settlement/summary/monthly', { params: { year, month } }),

  getFeeBreakdown: (year: number, month: number) =>
    api.get('/settlement/fee-breakdown', { params: { year, month } }),

  getDailyTrend: (startDate: string, endDate: string) =>
    api.get('/settlement/daily-trend', { params: { start_date: startDate, end_date: endDate } }),

  exportReport: (year: number, month: number, format: string = 'pdf') =>
    api.post('/settlement/export', null, { params: { year, month, format } })
};

// ============ AI API ============

export const aiApi = {
  chat: (message: string, context?: Array<{ role: string; content: string }>) =>
    api.post('/ai/chat', { message, context }),

  predict: (province: string, marketType: string = 'DAY_AHEAD', hours: number = 24) =>
    api.post('/ai/predict', { province, market_type: marketType, hours }),

  getStrategy: (data: {
    province: string;
    participant_type: string;
    quantity_mwh: number;
    risk_preference?: string;
  }) => api.post('/ai/strategy', data),

  getCapabilities: () => api.get('/ai/capabilities')
};

// ============ 报告 API ============

export const reportApi = {
  generate: (data: {
    report_type: string;
    target_date?: string;
    include_sections?: string[];
  }) => api.post('/reports/generate', data),

  getReports: (params?: { report_type?: string; status?: string }) =>
    api.get('/reports', { params }),

  getReport: (reportId: string) =>
    api.get(`/reports/${reportId}`),

  downloadReport: (reportId: string, format: string = 'pdf') =>
    api.get(`/reports/${reportId}/download`, { params: { format } }),

  getTemplates: () => api.get('/reports/templates')
};

export default api;
