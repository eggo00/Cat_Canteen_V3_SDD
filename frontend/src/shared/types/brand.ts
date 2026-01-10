/**
 * Brand-related TypeScript types
 */

export interface ThemeConfig {
  primaryColor: string;
  secondaryColor: string;
  accentColor?: string;
  fontFamily?: string;
  logoUrl?: string;
  [key: string]: string | undefined; // Allow additional theme properties
}

export interface Brand {
  id: string;
  name: string;
  slug: string;
  description?: string;
  logoUrl?: string;
  themeConfig: ThemeConfig;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface CreateBrandRequest {
  name: string;
  slug: string;
  description?: string;
  logoUrl?: string;
  themeConfig: ThemeConfig;
}

export interface UpdateBrandRequest {
  name?: string;
  description?: string;
  logoUrl?: string;
  isActive?: boolean;
}

export interface UpdateBrandThemeRequest {
  themeConfig: ThemeConfig;
}

export interface BrandResponse {
  id: string;
  name: string;
  slug: string;
  description?: string;
  logoUrl?: string;
  themeConfig: ThemeConfig;
  isActive: boolean;
}
