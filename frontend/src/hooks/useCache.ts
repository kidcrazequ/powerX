/**
 * PowerX 前端缓存 Hook
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 基于 Zustand 的请求缓存机制
 */

import { create } from 'zustand';
import { useCallback, useEffect, useRef } from 'react';

// ============ 类型定义 ============

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  expiresAt: number;
}

interface CacheState {
  cache: Map<string, CacheEntry<any>>;
  set: <T>(key: string, data: T, ttl?: number) => void;
  get: <T>(key: string) => T | null;
  has: (key: string) => boolean;
  remove: (key: string) => void;
  clear: (prefix?: string) => void;
  getStats: () => { size: number; keys: string[] };
}

interface UseCacheOptions<T> {
  key: string;
  fetcher: () => Promise<T>;
  ttl?: number;           // 缓存时间（毫秒），默认 5 分钟
  staleTime?: number;     // 数据过期时间（毫秒），过期后后台刷新
  enabled?: boolean;      // 是否启用
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
  refetchOnWindowFocus?: boolean;
  refetchInterval?: number;
}

interface UseCacheResult<T> {
  data: T | null;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  isFetching: boolean;
  isStale: boolean;
  refetch: () => Promise<void>;
  invalidate: () => void;
}

// ============ 缓存 Store ============

const DEFAULT_TTL = 5 * 60 * 1000; // 5 分钟

export const useCacheStore = create<CacheState>((set, get) => ({
  cache: new Map(),

  set: <T>(key: string, data: T, ttl: number = DEFAULT_TTL) => {
    const now = Date.now();
    const entry: CacheEntry<T> = {
      data,
      timestamp: now,
      expiresAt: now + ttl
    };

    set((state) => {
      const newCache = new Map(state.cache);
      newCache.set(key, entry);
      return { cache: newCache };
    });
  },

  get: <T>(key: string): T | null => {
    const entry = get().cache.get(key) as CacheEntry<T> | undefined;
    
    if (!entry) {
      return null;
    }

    // 检查是否过期
    if (Date.now() > entry.expiresAt) {
      // 删除过期条目
      get().remove(key);
      return null;
    }

    return entry.data;
  },

  has: (key: string): boolean => {
    const entry = get().cache.get(key);
    if (!entry) return false;
    
    // 检查是否过期
    if (Date.now() > entry.expiresAt) {
      get().remove(key);
      return false;
    }
    
    return true;
  },

  remove: (key: string) => {
    set((state) => {
      const newCache = new Map(state.cache);
      newCache.delete(key);
      return { cache: newCache };
    });
  },

  clear: (prefix?: string) => {
    if (!prefix) {
      set({ cache: new Map() });
      return;
    }

    set((state) => {
      const newCache = new Map(state.cache);
      for (const key of newCache.keys()) {
        if (key.startsWith(prefix)) {
          newCache.delete(key);
        }
      }
      return { cache: newCache };
    });
  },

  getStats: () => {
    const cache = get().cache;
    return {
      size: cache.size,
      keys: Array.from(cache.keys())
    };
  }
}));

// ============ 缓存 Hook ============

export function useCache<T>(options: UseCacheOptions<T>): UseCacheResult<T> {
  const {
    key,
    fetcher,
    ttl = DEFAULT_TTL,
    staleTime = ttl / 2,
    enabled = true,
    onSuccess,
    onError,
    refetchOnWindowFocus = false,
    refetchInterval
  } = options;

  const cacheStore = useCacheStore();
  const [state, setState] = useReducer(
    (prev: any, next: Partial<any>) => ({ ...prev, ...next }),
    {
      data: null as T | null,
      isLoading: false,
      isError: false,
      error: null as Error | null,
      isFetching: false,
      isStale: false
    }
  );

  const mountedRef = useRef(true);
  const fetchingRef = useRef(false);

  // 获取缓存的时间戳
  const getCacheTimestamp = useCallback((): number | null => {
    const entry = cacheStore.cache.get(key);
    return entry?.timestamp || null;
  }, [cacheStore.cache, key]);

  // 检查数据是否过期
  const checkIsStale = useCallback((): boolean => {
    const timestamp = getCacheTimestamp();
    if (!timestamp) return true;
    return Date.now() - timestamp > staleTime;
  }, [getCacheTimestamp, staleTime]);

  // 获取数据
  const fetchData = useCallback(async (background = false) => {
    if (fetchingRef.current) return;
    fetchingRef.current = true;

    if (!background) {
      setState({ isLoading: true, isFetching: true });
    } else {
      setState({ isFetching: true });
    }

    try {
      const data = await fetcher();
      
      if (mountedRef.current) {
        cacheStore.set(key, data, ttl);
        setState({
          data,
          isLoading: false,
          isError: false,
          error: null,
          isFetching: false,
          isStale: false
        });
        onSuccess?.(data);
      }
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      
      if (mountedRef.current) {
        setState({
          isLoading: false,
          isError: true,
          error,
          isFetching: false
        });
        onError?.(error);
      }
    } finally {
      fetchingRef.current = false;
    }
  }, [fetcher, key, ttl, cacheStore, onSuccess, onError]);

  // 手动刷新
  const refetch = useCallback(async () => {
    await fetchData(false);
  }, [fetchData]);

  // 使缓存失效
  const invalidate = useCallback(() => {
    cacheStore.remove(key);
    setState({ isStale: true });
  }, [cacheStore, key]);

  // 初始化和缓存检查
  useEffect(() => {
    if (!enabled) return;

    // 尝试从缓存获取
    const cachedData = cacheStore.get<T>(key);
    if (cachedData) {
      setState({ 
        data: cachedData, 
        isLoading: false,
        isStale: checkIsStale()
      });

      // 如果数据过期，后台刷新
      if (checkIsStale()) {
        fetchData(true);
      }
    } else {
      // 无缓存，执行请求
      fetchData(false);
    }
  }, [enabled, key]);

  // 窗口焦点刷新
  useEffect(() => {
    if (!refetchOnWindowFocus || !enabled) return;

    const handleFocus = () => {
      if (checkIsStale()) {
        fetchData(true);
      }
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [refetchOnWindowFocus, enabled, checkIsStale, fetchData]);

  // 定时刷新
  useEffect(() => {
    if (!refetchInterval || !enabled) return;

    const intervalId = setInterval(() => {
      fetchData(true);
    }, refetchInterval);

    return () => clearInterval(intervalId);
  }, [refetchInterval, enabled, fetchData]);

  // 清理
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  return {
    data: state.data,
    isLoading: state.isLoading,
    isError: state.isError,
    error: state.error,
    isFetching: state.isFetching,
    isStale: state.isStale,
    refetch,
    invalidate
  };
}

// 简化版 useReducer
function useReducer<S>(
  reducer: (prev: S, next: Partial<S>) => S,
  initialState: S
): [S, (action: Partial<S>) => void] {
  const [state, setState] = create<{ value: S; dispatch: (action: Partial<S>) => void }>((set) => ({
    value: initialState,
    dispatch: (action: Partial<S>) => set((s) => ({ value: reducer(s.value, action) }))
  }))();

  // 使用 React 的 useReducer 代替
  const [reactState, reactDispatch] = require('react').useReducer(reducer, initialState);
  return [reactState, reactDispatch];
}

// ============ 预定义缓存键 ============

export const CacheKeys = {
  MARKET_SUMMARY: (province: string) => `market:summary:${province}`,
  MARKET_PRICES: (province: string, date: string) => `market:prices:${province}:${date}`,
  MARKET_HOURLY: (province: string) => `market:hourly:${province}`,
  PROVINCES: 'provinces',
  USER_PROFILE: 'user:profile',
  TRADING_STATS: 'trading:stats',
  CONTRACTS: 'contracts:list',
  AI_CAPABILITIES: 'ai:capabilities'
};

// ============ 工具函数 ============

/**
 * 清除所有市场相关缓存
 */
export function clearMarketCache() {
  useCacheStore.getState().clear('market:');
}

/**
 * 清除用户相关缓存
 */
export function clearUserCache() {
  useCacheStore.getState().clear('user:');
}

/**
 * 清除所有缓存
 */
export function clearAllCache() {
  useCacheStore.getState().clear();
}
