/**
 * Unit tests for ThemeProvider component
 */

import { render, screen, act } from '@testing-library/react';
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { ThemeProvider, useThemeContext } from '../../../src/theme/ThemeProvider';

// Test component to access theme context
function TestComponent() {
  const { theme, setTheme, resetTheme, isLoading } = useThemeContext();
  return (
    <div>
      <span data-testid="primary-color">{theme.primaryColor}</span>
      <span data-testid="secondary-color">{theme.secondaryColor}</span>
      <span data-testid="is-loading">{isLoading ? 'loading' : 'ready'}</span>
      <button data-testid="set-theme" onClick={() => setTheme({ primaryColor: '#000000' })}>
        Set Theme
      </button>
      <button data-testid="reset-theme" onClick={() => resetTheme()}>
        Reset Theme
      </button>
    </div>
  );
}

describe('ThemeProvider', () => {
  beforeEach(() => {
    // Clear any existing CSS variables
    document.documentElement.style.cssText = '';
  });

  afterEach(() => {
    document.documentElement.style.cssText = '';
  });

  it('should provide default theme values', () => {
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(screen.getByTestId('primary-color').textContent).toBe('#FF6B6B');
    expect(screen.getByTestId('secondary-color').textContent).toBe('#4ECDC4');
  });

  it('should accept initial theme configuration', () => {
    render(
      <ThemeProvider initialTheme={{ primaryColor: '#123456', secondaryColor: '#654321' }}>
        <TestComponent />
      </ThemeProvider>
    );

    expect(screen.getByTestId('primary-color').textContent).toBe('#123456');
    expect(screen.getByTestId('secondary-color').textContent).toBe('#654321');
  });

  it('should apply CSS variables to document root', () => {
    render(
      <ThemeProvider initialTheme={{ primaryColor: '#AABBCC' }}>
        <TestComponent />
      </ThemeProvider>
    );

    const root = document.documentElement;
    expect(root.style.getPropertyValue('--color-primary')).toBe('#AABBCC');
  });

  it('should update theme when setTheme is called', async () => {
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    const setThemeButton = screen.getByTestId('set-theme');

    await act(async () => {
      setThemeButton.click();
    });

    expect(screen.getByTestId('primary-color').textContent).toBe('#000000');
  });

  it('should reset theme to defaults when resetTheme is called', async () => {
    render(
      <ThemeProvider initialTheme={{ primaryColor: '#123456' }}>
        <TestComponent />
      </ThemeProvider>
    );

    expect(screen.getByTestId('primary-color').textContent).toBe('#123456');

    const resetButton = screen.getByTestId('reset-theme');

    await act(async () => {
      resetButton.click();
    });

    expect(screen.getByTestId('primary-color').textContent).toBe('#FF6B6B');
  });

  it('should throw error when useThemeContext is used outside ThemeProvider', () => {
    // Suppress console.error for this test
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    expect(() => {
      render(<TestComponent />);
    }).toThrow('useThemeContext must be used within a ThemeProvider');

    consoleSpy.mockRestore();
  });

  it('should preserve other theme properties when updating', async () => {
    render(
      <ThemeProvider initialTheme={{ primaryColor: '#111111', secondaryColor: '#222222' }}>
        <TestComponent />
      </ThemeProvider>
    );

    const setThemeButton = screen.getByTestId('set-theme');

    await act(async () => {
      setThemeButton.click();
    });

    // Primary should be updated
    expect(screen.getByTestId('primary-color').textContent).toBe('#000000');
    // Secondary should be preserved
    expect(screen.getByTestId('secondary-color').textContent).toBe('#222222');
  });
});
