/**
 * PowerX WebSocket Hook
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * WebSocket 连接管理、自动重连、消息处理
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { useAuthStore } from '../stores/authStore';

// ============ 类型定义 ============

export type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'reconnecting';

export interface WebSocketMessage {
  type: string;
  channel?: string;
  data?: any;
  timestamp?: string;
  [key: string]: any;
}

export interface UseWebSocketOptions {
  url: string;
  enabled?: boolean;
  reconnect?: boolean;
  reconnectInterval?: number;
  reconnectAttempts?: number;
  heartbeatInterval?: number;
  onOpen?: (event: Event) => void;
  onClose?: (event: CloseEvent) => void;
  onError?: (event: Event) => void;
  onMessage?: (message: WebSocketMessage) => void;
  protocols?: string | string[];
}

export interface UseWebSocketResult {
  connectionState: ConnectionState;
  lastMessage: WebSocketMessage | null;
  sendMessage: (message: WebSocketMessage) => boolean;
  subscribe: (channels: string[]) => void;
  unsubscribe: (channels: string[]) => void;
  reconnect: () => void;
  disconnect: () => void;
}

// ============ WebSocket Hook ============

export function useWebSocket(options: UseWebSocketOptions): UseWebSocketResult {
  const {
    url,
    enabled = true,
    reconnect = true,
    reconnectInterval = 3000,
    reconnectAttempts = 5,
    heartbeatInterval = 30000,
    onOpen,
    onClose,
    onError,
    onMessage,
    protocols
  } = options;

  const token = useAuthStore((state) => state.token);
  
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCountRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const messageQueueRef = useRef<WebSocketMessage[]>([]);
  const mountedRef = useRef(true);

  // 构建完整 URL（包含 token）
  const getFullUrl = useCallback(() => {
    const baseUrl = url.startsWith('ws') ? url : `ws://${window.location.host}${url}`;
    const urlObj = new URL(baseUrl);
    
    if (token) {
      urlObj.searchParams.set('token', token);
    }
    
    return urlObj.toString();
  }, [url, token]);

  // 清除定时器
  const clearTimers = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
      heartbeatIntervalRef.current = null;
    }
  }, []);

  // 启动心跳
  const startHeartbeat = useCallback(() => {
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
    }
    
    heartbeatIntervalRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'ping' }));
      }
    }, heartbeatInterval);
  }, [heartbeatInterval]);

  // 处理消息队列
  const flushMessageQueue = useCallback(() => {
    if (wsRef.current?.readyState !== WebSocket.OPEN) return;
    
    while (messageQueueRef.current.length > 0) {
      const message = messageQueueRef.current.shift();
      if (message) {
        wsRef.current.send(JSON.stringify(message));
      }
    }
  }, []);

  // 连接 WebSocket
  const connect = useCallback(() => {
    if (!enabled || wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    clearTimers();
    setConnectionState('connecting');

    try {
      const fullUrl = getFullUrl();
      wsRef.current = new WebSocket(fullUrl, protocols);

      wsRef.current.onopen = (event) => {
        if (!mountedRef.current) return;
        
        console.log('[WebSocket] Connected:', url);
        setConnectionState('connected');
        reconnectCountRef.current = 0;
        
        startHeartbeat();
        flushMessageQueue();
        onOpen?.(event);
      };

      wsRef.current.onclose = (event) => {
        if (!mountedRef.current) return;
        
        console.log('[WebSocket] Closed:', event.code, event.reason);
        setConnectionState('disconnected');
        clearTimers();
        onClose?.(event);

        // 自动重连
        if (reconnect && reconnectCountRef.current < reconnectAttempts && event.code !== 4001) {
          setConnectionState('reconnecting');
          reconnectCountRef.current++;
          
          console.log(`[WebSocket] Reconnecting (${reconnectCountRef.current}/${reconnectAttempts})...`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval * Math.min(reconnectCountRef.current, 3));
        }
      };

      wsRef.current.onerror = (event) => {
        if (!mountedRef.current) return;
        
        console.error('[WebSocket] Error:', event);
        onError?.(event);
      };

      wsRef.current.onmessage = (event) => {
        if (!mountedRef.current) return;
        
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          
          // 忽略 pong 消息
          if (message.type === 'pong') return;
          
          setLastMessage(message);
          onMessage?.(message);
        } catch (e) {
          console.error('[WebSocket] Failed to parse message:', e);
        }
      };
    } catch (error) {
      console.error('[WebSocket] Connection error:', error);
      setConnectionState('disconnected');
    }
  }, [
    enabled, url, protocols, reconnect, reconnectAttempts, reconnectInterval,
    getFullUrl, clearTimers, startHeartbeat, flushMessageQueue, onOpen, onClose, onError, onMessage
  ]);

  // 断开连接
  const disconnect = useCallback(() => {
    clearTimers();
    reconnectCountRef.current = reconnectAttempts; // 防止自动重连
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'User disconnect');
      wsRef.current = null;
    }
    
    setConnectionState('disconnected');
  }, [clearTimers, reconnectAttempts]);

  // 重新连接
  const reconnectFn = useCallback(() => {
    reconnectCountRef.current = 0;
    disconnect();
    setTimeout(connect, 100);
  }, [disconnect, connect]);

  // 发送消息
  const sendMessage = useCallback((message: WebSocketMessage): boolean => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
      return true;
    }
    
    // 加入队列等待连接
    messageQueueRef.current.push(message);
    return false;
  }, []);

  // 订阅频道
  const subscribe = useCallback((channels: string[]) => {
    sendMessage({ type: 'subscribe', channels });
  }, [sendMessage]);

  // 取消订阅
  const unsubscribe = useCallback((channels: string[]) => {
    sendMessage({ type: 'unsubscribe', channels });
  }, [sendMessage]);

  // 初始化连接
  useEffect(() => {
    mountedRef.current = true;
    
    if (enabled) {
      connect();
    }

    return () => {
      mountedRef.current = false;
      clearTimers();
      
      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmount');
        wsRef.current = null;
      }
    };
  }, [enabled]); // 只在 enabled 变化时重新连接

  // URL 变化时重新连接
  useEffect(() => {
    if (enabled && wsRef.current?.readyState === WebSocket.OPEN) {
      reconnectFn();
    }
  }, [url, token]);

  return {
    connectionState,
    lastMessage,
    sendMessage,
    subscribe,
    unsubscribe,
    reconnect: reconnectFn,
    disconnect
  };
}

// ============ 便捷 Hooks ============

/**
 * 市场数据 WebSocket Hook
 */
export function useMarketWebSocket(province: string, onPriceUpdate?: (data: any) => void) {
  const baseUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
  
  return useWebSocket({
    url: `${baseUrl}/api/v1/ws/market/${province}`,
    enabled: !!province,
    onMessage: (message) => {
      if (message.type === 'price_update') {
        onPriceUpdate?.(message.data);
      }
    }
  });
}

/**
 * 订单更新 WebSocket Hook
 */
export function useOrdersWebSocket(onOrderUpdate?: (data: any) => void) {
  const baseUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
  const isAuthenticated = useAuthStore((state) => !!state.token);
  
  return useWebSocket({
    url: `${baseUrl}/api/v1/ws/orders`,
    enabled: isAuthenticated,
    onMessage: (message) => {
      if (message.type === 'order_update') {
        onOrderUpdate?.(message.data);
      }
    }
  });
}

/**
 * 通知 WebSocket Hook
 */
export function useNotificationsWebSocket(onNotification?: (data: any) => void) {
  const baseUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
  
  return useWebSocket({
    url: `${baseUrl}/api/v1/ws/notifications`,
    onMessage: (message) => {
      if (message.type === 'notification') {
        onNotification?.(message.data);
      }
    }
  });
}

export default useWebSocket;
