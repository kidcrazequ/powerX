/**
 * PowerX 认证状态管理
 * 
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 * 
 * 使用 Zustand 管理用户认证状态
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: number;
  username: string;
  email: string;
  name: string;
  role: string;
  is_active: boolean;
}

interface AuthState {
  token: string | null;
  refreshToken: string | null;
  user: User | null;
  isAuthenticated: boolean;
  
  // Actions
  setTokens: (accessToken: string, refreshToken: string) => void;
  setUser: (user: User) => void;
  login: (accessToken: string, refreshToken: string, user?: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      refreshToken: null,
      user: null,
      isAuthenticated: false,

      setTokens: (accessToken: string, refreshToken: string) => {
        set({
          token: accessToken,
          refreshToken: refreshToken,
          isAuthenticated: true
        });
      },

      setUser: (user: User) => {
        set({ user });
      },

      login: (accessToken: string, refreshToken: string, user?: User) => {
        set({
          token: accessToken,
          refreshToken: refreshToken,
          user: user || null,
          isAuthenticated: true
        });
      },

      logout: () => {
        set({
          token: null,
          refreshToken: null,
          user: null,
          isAuthenticated: false
        });
      }
    }),
    {
      name: 'powerx-auth-storage',
      partialize: (state) => ({
        token: state.token,
        refreshToken: state.refreshToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
);
