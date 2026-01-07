/**
 * ExposureMonitor 组件测试
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 */
import { describe, it, expect } from 'vitest';

describe('ExposureMonitor', () => {
  it('should export default component', async () => {
    const module = await import('../ExposureMonitor');
    expect(module.default).toBeDefined();
  });

  it('should be a function component', async () => {
    const { default: ExposureMonitor } = await import('../ExposureMonitor');
    expect(typeof ExposureMonitor).toBe('function');
  });
});
