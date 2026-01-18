/**
 * Theme configuration logic for CSS variable injection
 * Handles dynamic theme loading and CSS variable management
 */

import { ThemeConfig } from '../shared/types/brand';

/**
 * Default theme configuration
 */
export const defaultTheme: ThemeConfig = {
  primaryColor: '#FF6B6B',
  secondaryColor: '#4ECDC4',
  accentColor: '#FFE66D',
  backgroundColor: '#FFFFFF',
  textColor: '#2C3E50',
  fontFamily: 'Inter, system-ui, sans-serif',
};

/**
 * CSS variable mapping from ThemeConfig properties to CSS custom properties
 */
const cssVariableMapping: Record<keyof ThemeConfig, string> = {
  primaryColor: '--color-primary',
  secondaryColor: '--color-secondary',
  accentColor: '--color-accent',
  backgroundColor: '--color-background',
  textColor: '--color-text',
  fontFamily: '--font-family',
  logoUrl: '--logo-url',
};

/**
 * Apply theme to document root by setting CSS custom properties
 */
export function applyTheme(theme: Partial<ThemeConfig>): void {
  const root = document.documentElement;
  const mergedTheme = { ...defaultTheme, ...theme };

  Object.entries(mergedTheme).forEach(([key, value]) => {
    if (value !== undefined) {
      const cssVar = cssVariableMapping[key as keyof ThemeConfig];
      if (cssVar) {
        if (key === 'logoUrl') {
          root.style.setProperty(cssVar, `url(${value})`);
        } else {
          root.style.setProperty(cssVar, value);
        }
      }
    }
  });
}

/**
 * Remove all theme CSS custom properties from document root
 */
export function clearTheme(): void {
  const root = document.documentElement;

  Object.values(cssVariableMapping).forEach((cssVar) => {
    root.style.removeProperty(cssVar);
  });
}

/**
 * Get current theme from CSS custom properties
 */
export function getCurrentTheme(): ThemeConfig {
  const root = document.documentElement;
  const computedStyle = getComputedStyle(root);

  const theme: ThemeConfig = {
    primaryColor: computedStyle.getPropertyValue('--color-primary').trim() || defaultTheme.primaryColor,
    secondaryColor: computedStyle.getPropertyValue('--color-secondary').trim() || defaultTheme.secondaryColor,
    accentColor: computedStyle.getPropertyValue('--color-accent').trim() || defaultTheme.accentColor,
    backgroundColor: computedStyle.getPropertyValue('--color-background').trim() || defaultTheme.backgroundColor,
    textColor: computedStyle.getPropertyValue('--color-text').trim() || defaultTheme.textColor,
    fontFamily: computedStyle.getPropertyValue('--font-family').trim() || defaultTheme.fontFamily,
  };

  return theme;
}

/**
 * Generate CSS string from theme config (useful for SSR or style tags)
 */
export function generateThemeCSS(theme: Partial<ThemeConfig>): string {
  const mergedTheme = { ...defaultTheme, ...theme };
  const cssVars: string[] = [];

  Object.entries(mergedTheme).forEach(([key, value]) => {
    if (value !== undefined) {
      const cssVar = cssVariableMapping[key as keyof ThemeConfig];
      if (cssVar) {
        if (key === 'logoUrl') {
          cssVars.push(`${cssVar}: url(${value});`);
        } else {
          cssVars.push(`${cssVar}: ${value};`);
        }
      }
    }
  });

  return `:root {\n  ${cssVars.join('\n  ')}\n}`;
}

/**
 * Validate hex color format
 */
export function isValidHexColor(color: string): boolean {
  return /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/.test(color);
}

/**
 * Validate theme config
 */
export function validateThemeConfig(theme: Partial<ThemeConfig>): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (theme.primaryColor && !isValidHexColor(theme.primaryColor)) {
    errors.push('Invalid primaryColor format. Must be a valid hex color.');
  }
  if (theme.secondaryColor && !isValidHexColor(theme.secondaryColor)) {
    errors.push('Invalid secondaryColor format. Must be a valid hex color.');
  }
  if (theme.accentColor && !isValidHexColor(theme.accentColor)) {
    errors.push('Invalid accentColor format. Must be a valid hex color.');
  }
  if (theme.backgroundColor && !isValidHexColor(theme.backgroundColor)) {
    errors.push('Invalid backgroundColor format. Must be a valid hex color.');
  }
  if (theme.textColor && !isValidHexColor(theme.textColor)) {
    errors.push('Invalid textColor format. Must be a valid hex color.');
  }

  return { valid: errors.length === 0, errors };
}
