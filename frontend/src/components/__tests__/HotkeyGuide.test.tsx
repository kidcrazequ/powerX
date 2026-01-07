/**
 * HotkeyGuide 组件测试
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 */
import { describe, it, expect } from 'vitest';

describe('HotkeyGuide', () => {
  it('should export default component', async () => {
    const module = await import('../HotkeyGuide');
    expect(module.default).toBeDefined();
  });

  it('should be a function component', async () => {
    const { default: HotkeyGuide } = await import('../HotkeyGuide');
    expect(typeof HotkeyGuide).toBe('function');
  });
});
