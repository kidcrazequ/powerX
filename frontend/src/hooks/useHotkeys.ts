/**
 * PowerX 快捷键 Hook
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 */
import { useEffect, useCallback } from 'react';

interface HotkeyConfig {
  key: string;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  handler: () => void;
  description?: string;
}

export const useHotkeys = (hotkeys: HotkeyConfig[]) => {
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    for (const hotkey of hotkeys) {
      const keyMatch = event.key.toLowerCase() === hotkey.key.toLowerCase();
      const ctrlMatch = hotkey.ctrl ? (event.ctrlKey || event.metaKey) : !(event.ctrlKey || event.metaKey);
      const shiftMatch = hotkey.shift ? event.shiftKey : !event.shiftKey;
      const altMatch = hotkey.alt ? event.altKey : !event.altKey;

      if (keyMatch && ctrlMatch && shiftMatch && altMatch) {
        event.preventDefault();
        hotkey.handler();
        break;
      }
    }
  }, [hotkeys]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);
};

// 预定义的快捷键配置
export const defaultHotkeys = [
  { key: 't', ctrl: true, description: '新建交易' },
  { key: 's', ctrl: true, description: '保存' },
  { key: '/', ctrl: true, description: '显示快捷键帮助' },
  { key: 'Escape', description: '关闭弹窗' },
  { key: 'r', ctrl: true, description: '刷新数据' },
  { key: 'd', ctrl: true, description: '跳转到仪表盘' },
];

export default useHotkeys;
