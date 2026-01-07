/**
 * PowerX 时间轴播放器组件
 * 创建日期: 2026-01-07
 * 作者: zhi.qu
 */
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Slider, Button, Space, Select, theme } from 'antd';
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  StepBackwardOutlined,
  StepForwardOutlined,
  FastBackwardOutlined
} from '@ant-design/icons';

interface TimelinePlayerProps {
  totalFrames: number;
  currentFrame: number;
  onFrameChange: (frame: number) => void;
  onPlayStateChange?: (isPlaying: boolean) => void;
  formatLabel?: (frame: number) => string;
  speed?: number;
  onSpeedChange?: (speed: number) => void;
}

const TimelinePlayer: React.FC<TimelinePlayerProps> = ({
  totalFrames,
  currentFrame,
  onFrameChange,
  onPlayStateChange,
  formatLabel,
  speed = 1,
  onSpeedChange
}) => {
  const { token } = theme.useToken();
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentSpeed, setCurrentSpeed] = useState(speed);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (isPlaying && currentFrame < totalFrames - 1) {
      timerRef.current = setTimeout(() => {
        onFrameChange(currentFrame + 1);
      }, 1000 / currentSpeed);
    } else if (currentFrame >= totalFrames - 1) {
      setIsPlaying(false);
      onPlayStateChange?.(false);
    }
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [isPlaying, currentFrame, totalFrames, currentSpeed, onFrameChange, onPlayStateChange]);

  const handlePlay = useCallback(() => {
    setIsPlaying(true);
    onPlayStateChange?.(true);
  }, [onPlayStateChange]);

  const handlePause = useCallback(() => {
    setIsPlaying(false);
    onPlayStateChange?.(false);
  }, [onPlayStateChange]);

  const handleReset = useCallback(() => {
    setIsPlaying(false);
    onPlayStateChange?.(false);
    onFrameChange(0);
  }, [onFrameChange, onPlayStateChange]);

  const handleSpeedChange = useCallback((newSpeed: number) => {
    setCurrentSpeed(newSpeed);
    onSpeedChange?.(newSpeed);
  }, [onSpeedChange]);

  return (
    <div style={{ 
      display: 'flex', 
      alignItems: 'center', 
      gap: 16, 
      padding: '12px 16px',
      background: token.colorBgContainer,
      borderRadius: 8,
      border: `1px solid ${token.colorBorder}`
    }}>
      {/* 控制按钮 */}
      <Space size="small">
        <Button 
          type="text" 
          icon={<FastBackwardOutlined />} 
          onClick={handleReset}
          title="重置"
        />
        <Button 
          type="text" 
          icon={<StepBackwardOutlined />} 
          onClick={() => onFrameChange(Math.max(0, currentFrame - 1))}
          disabled={currentFrame === 0}
          title="上一帧"
        />
        {isPlaying ? (
          <Button 
            type="primary" 
            icon={<PauseCircleOutlined />} 
            onClick={handlePause}
            title="暂停"
          />
        ) : (
          <Button 
            type="primary" 
            icon={<PlayCircleOutlined />} 
            onClick={handlePlay}
            disabled={currentFrame >= totalFrames - 1}
            title="播放"
          />
        )}
        <Button 
          type="text" 
          icon={<StepForwardOutlined />} 
          onClick={() => onFrameChange(Math.min(totalFrames - 1, currentFrame + 1))}
          disabled={currentFrame >= totalFrames - 1}
          title="下一帧"
        />
      </Space>

      {/* 进度条 */}
      <div style={{ flex: 1 }}>
        <Slider
          value={currentFrame}
          min={0}
          max={totalFrames - 1}
          onChange={onFrameChange}
          tooltip={{ 
            formatter: (val) => formatLabel ? formatLabel(val || 0) : `${val}` 
          }}
        />
      </div>

      {/* 当前时间显示 */}
      <div style={{ 
        minWidth: 80, 
        textAlign: 'center',
        fontFamily: 'monospace',
        fontSize: 16,
        fontWeight: 'bold',
        color: token.colorPrimary
      }}>
        {formatLabel ? formatLabel(currentFrame) : `${currentFrame}/${totalFrames - 1}`}
      </div>

      {/* 速度选择 */}
      <Select
        value={currentSpeed}
        onChange={handleSpeedChange}
        style={{ width: 80 }}
        size="small"
        options={[
          { value: 0.5, label: '0.5x' },
          { value: 1, label: '1x' },
          { value: 2, label: '2x' },
          { value: 5, label: '5x' },
          { value: 10, label: '10x' }
        ]}
      />
    </div>
  );
};

export default TimelinePlayer;
