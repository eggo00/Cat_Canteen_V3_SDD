/**
 * ThemeProvider component for dynamic theme loading
 * Provides theme context and handles CSS variable injection
 */

import React, { createContext, useContext, useEffect, useState, useCallback, ReactNode } from 'react';
import { ThemeConfig } from '../shared/types/brand';
import { applyTheme, clearTheme, defaultTheme } from './themeConfig';

/**
 * Theme context value interface
 */
interface ThemeContextValue {
  theme: ThemeConfig;
  setTheme: (theme: Partial<ThemeConfig>) => void;
  resetTheme: () => void;
  isLoading: boolean;
}

/**
 * Theme context with default values
 */
const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

/**
 * Theme provider props
 */
interface ThemeProviderProps {
  children: ReactNode;
  initialTheme?: Partial<ThemeConfig>;
}

/**
 * ThemeProvider component
 * Wraps application and provides theme context with CSS variable injection
 */
export function ThemeProvider({ children, initialTheme }: ThemeProviderProps): JSX.Element {
  const [theme, setThemeState] = useState<ThemeConfig>(() => ({
    ...defaultTheme,
    ...initialTheme,
  }));
  const [isLoading, setIsLoading] = useState(false);

  // Apply theme to document on mount and theme changes
  useEffect(() => {
    applyTheme(theme);
    return () => {
      // Cleanup: don't clear theme on unmount to prevent flickering
    };
  }, [theme]);

  // Set theme with partial updates
  const setTheme = useCallback((newTheme: Partial<ThemeConfig>) => {
    setIsLoading(true);
    setThemeState((prev) => {
      const merged = { ...prev, ...newTheme };
      return merged;
    });
    // Small delay to allow CSS transition
    setTimeout(() => setIsLoading(false), 50);
  }, []);

  // Reset to default theme
  const resetTheme = useCallback(() => {
    setIsLoading(true);
    clearTheme();
    setThemeState(defaultTheme);
    applyTheme(defaultTheme);
    setTimeout(() => setIsLoading(false), 50);
  }, []);

  const contextValue: ThemeContextValue = {
    theme,
    setTheme,
    resetTheme,
    isLoading,
  };

  return <ThemeContext.Provider value={contextValue}>{children}</ThemeContext.Provider>;
}

/**
 * Hook to access theme context
 * Must be used within a ThemeProvider
 */
export function useThemeContext(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useThemeContext must be used within a ThemeProvider');
  }
  return context;
}

export { ThemeContext };
export type { ThemeContextValue, ThemeProviderProps };
