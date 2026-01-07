/**
 * useHotkeys Hook 测试
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 */
import { describe, it, expect } from 'vitest';

describe('useHotkeys', () => {
  it('should export useHotkeys hook', async () => {
    const module = await import('../useHotkeys');
    expect(module.useHotkeys).toBeDefined();
    expect(typeof module.useHotkeys).toBe('function');
  });

  it('should export defaultHotkeys', async () => {
    const { defaultHotkeys } = await import('../useHotkeys');
    expect(defaultHotkeys).toBeDefined();
    expect(Array.isArray(defaultHotkeys)).toBe(true);
    expect(defaultHotkeys.length).toBeGreaterThan(0);
  });

  it('should have correct hotkey structure', async () => {
    const { defaultHotkeys } = await import('../useHotkeys');
    const hotkey = defaultHotkeys[0];
    expect(hotkey).toHaveProperty('key');
    expect(hotkey).toHaveProperty('description');
  });
});
