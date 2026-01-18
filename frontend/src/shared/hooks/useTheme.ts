/**
 * useTheme hook for accessing and managing theme
 * Provides simplified interface for theme operations
 */

import { useCallback, useMemo } from 'react';
import { ThemeConfig } from '../types/brand';
import { useThemeContext } from '../../theme/ThemeProvider';

/**
 * Hook return type
 */
interface UseThemeReturn {
  /** Current theme configuration */
  theme: ThemeConfig;
  /** Update theme with partial values */
  setTheme: (theme: Partial<ThemeConfig>) => void;
  /** Reset to default theme */
  resetTheme: () => void;
  /** Whether theme is currently being updated */
  isLoading: boolean;
  /** Get specific theme color */
  getColor: (colorName: keyof Pick<ThemeConfig, 'primaryColor' | 'secondaryColor' | 'accentColor' | 'backgroundColor' | 'textColor'>) => string;
  /** Get font family */
  fontFamily: string;
  /** CSS variables object for inline styles */
  cssVariables: Record<string, string>;
}

/**
 * Hook for accessing and managing application theme
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { theme, setTheme, getColor } = useTheme();
 *
 *   return (
 *     <div style={{ backgroundColor: getColor('primaryColor') }}>
 *       <button onClick={() => setTheme({ primaryColor: '#FF0000' })}>
 *         Change Primary Color
 *       </button>
 *     </div>
 *   );
 * }
 * ```
 */
export function useTheme(): UseThemeReturn {
  const { theme, setTheme, resetTheme, isLoading } = useThemeContext();

  // Get specific color from theme
  const getColor = useCallback(
    (colorName: keyof Pick<ThemeConfig, 'primaryColor' | 'secondaryColor' | 'accentColor' | 'backgroundColor' | 'textColor'>): string => {
      return theme[colorName] || '';
    },
    [theme]
  );

  // Memoized font family
  const fontFamily = useMemo(() => theme.fontFamily || 'Inter, system-ui, sans-serif', [theme.fontFamily]);

  // CSS variables object for inline styles
  const cssVariables = useMemo(
    () => ({
      '--color-primary': theme.primaryColor,
      '--color-secondary': theme.secondaryColor,
      '--color-accent': theme.accentColor || '',
      '--color-background': theme.backgroundColor || '',
      '--color-text': theme.textColor || '',
      '--font-family': theme.fontFamily || '',
    }),
    [theme]
  );

  return {
    theme,
    setTheme,
    resetTheme,
    isLoading,
    getColor,
    fontFamily,
    cssVariables,
  };
}

export default useTheme;
