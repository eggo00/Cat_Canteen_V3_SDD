/**
 * Unit tests for useTheme hook
 */

import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import React from 'react';
import { ThemeProvider } from '../../../../src/theme/ThemeProvider';
import { useTheme } from '../../../../src/shared/hooks/useTheme';

// Wrapper component with ThemeProvider
function createWrapper(initialTheme?: Record<string, string>) {
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return React.createElement(ThemeProvider, { initialTheme }, children);
  };
}

describe('useTheme', () => {
  beforeEach(() => {
    document.documentElement.style.cssText = '';
  });

  afterEach(() => {
    document.documentElement.style.cssText = '';
  });

  it('should return theme object with all properties', () => {
    const { result } = renderHook(() => useTheme(), {
      wrapper: createWrapper(),
    });

    expect(result.current.theme).toBeDefined();
    expect(result.current.theme.primaryColor).toBe('#FF6B6B');
    expect(result.current.theme.secondaryColor).toBe('#4ECDC4');
  });

  it('should return setTheme function', () => {
    const { result } = renderHook(() => useTheme(), {
      wrapper: createWrapper(),
    });

    expect(typeof result.current.setTheme).toBe('function');
  });

  it('should return resetTheme function', () => {
    const { result } = renderHook(() => useTheme(), {
      wrapper: createWrapper(),
    });

    expect(typeof result.current.resetTheme).toBe('function');
  });

  it('should return getColor function that returns correct colors', () => {
    const { result } = renderHook(() => useTheme(), {
      wrapper: createWrapper({ primaryColor: '#AABBCC', secondaryColor: '#DDEEFF' }),
    });

    expect(result.current.getColor('primaryColor')).toBe('#AABBCC');
    expect(result.current.getColor('secondaryColor')).toBe('#DDEEFF');
  });

  it('should return fontFamily', () => {
    const { result } = renderHook(() => useTheme(), {
      wrapper: createWrapper({ fontFamily: 'Roboto, sans-serif' }),
    });

    expect(result.current.fontFamily).toBe('Roboto, sans-serif');
  });

  it('should return default fontFamily when not specified', () => {
    const { result } = renderHook(() => useTheme(), {
      wrapper: createWrapper(),
    });

    expect(result.current.fontFamily).toBe('Inter, system-ui, sans-serif');
  });

  it('should return cssVariables object', () => {
    const { result } = renderHook(() => useTheme(), {
      wrapper: createWrapper({ primaryColor: '#111111' }),
    });

    expect(result.current.cssVariables).toBeDefined();
    expect(result.current.cssVariables['--color-primary']).toBe('#111111');
  });

  it('should update theme when setTheme is called', async () => {
    const { result } = renderHook(() => useTheme(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      result.current.setTheme({ primaryColor: '#FFFFFF' });
    });

    expect(result.current.theme.primaryColor).toBe('#FFFFFF');
  });

  it('should reset theme to defaults when resetTheme is called', async () => {
    const { result } = renderHook(() => useTheme(), {
      wrapper: createWrapper({ primaryColor: '#123456' }),
    });

    expect(result.current.theme.primaryColor).toBe('#123456');

    await act(async () => {
      result.current.resetTheme();
    });

    expect(result.current.theme.primaryColor).toBe('#FF6B6B');
  });

  it('should track loading state', () => {
    const { result } = renderHook(() => useTheme(), {
      wrapper: createWrapper(),
    });

    expect(typeof result.current.isLoading).toBe('boolean');
  });
});
