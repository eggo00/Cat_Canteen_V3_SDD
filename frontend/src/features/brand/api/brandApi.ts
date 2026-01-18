/**
 * Brand API client
 * Handles all brand-related API requests
 */

import { get, post, patch, del } from '../../../shared/utils/api';
import {
  Brand,
  BrandResponse,
  CreateBrandRequest,
  UpdateBrandRequest,
  UpdateBrandThemeRequest,
  ThemeConfig,
} from '../../../shared/types/brand';

/**
 * API response transformer: Convert snake_case to camelCase
 */
function transformBrandResponse(data: Record<string, unknown>): BrandResponse {
  return {
    id: data.id as string,
    name: data.name as string,
    slug: data.slug as string,
    description: data.description as string | undefined,
    logoUrl: data.logo_url as string | undefined,
    themeConfig: transformThemeConfig(data.theme_config as Record<string, unknown>),
    isActive: data.is_active as boolean,
  };
}

/**
 * Transform theme config from snake_case to camelCase
 */
function transformThemeConfig(data: Record<string, unknown>): ThemeConfig {
  return {
    primaryColor: (data.primary_color || data.primaryColor) as string,
    secondaryColor: (data.secondary_color || data.secondaryColor) as string,
    accentColor: (data.accent_color || data.accentColor) as string | undefined,
    backgroundColor: (data.background_color || data.backgroundColor) as string | undefined,
    textColor: (data.text_color || data.textColor) as string | undefined,
    fontFamily: (data.font_family || data.fontFamily) as string | undefined,
    logoUrl: (data.logo_url || data.logoUrl) as string | undefined,
  };
}

/**
 * Transform theme config from camelCase to snake_case for API requests
 */
function transformThemeConfigToSnakeCase(theme: Partial<ThemeConfig>): Record<string, unknown> {
  const result: Record<string, unknown> = {};
  if (theme.primaryColor) result.primary_color = theme.primaryColor;
  if (theme.secondaryColor) result.secondary_color = theme.secondaryColor;
  if (theme.accentColor) result.accent_color = theme.accentColor;
  if (theme.backgroundColor) result.background_color = theme.backgroundColor;
  if (theme.textColor) result.text_color = theme.textColor;
  if (theme.fontFamily) result.font_family = theme.fontFamily;
  return result;
}

/**
 * Get brand by slug
 */
export async function getBrandBySlug(slug: string): Promise<BrandResponse> {
  const response = await get<Record<string, unknown>>(`/brands/slug/${slug}`);
  return transformBrandResponse(response);
}

/**
 * Get brand by ID
 */
export async function getBrandById(id: string): Promise<BrandResponse> {
  const response = await get<Record<string, unknown>>(`/brands/${id}`);
  return transformBrandResponse(response);
}

/**
 * List all brands
 */
export async function listBrands(options?: {
  activeOnly?: boolean;
  skip?: number;
  limit?: number;
}): Promise<BrandResponse[]> {
  const params = new URLSearchParams();
  if (options?.activeOnly !== undefined) {
    params.append('active_only', String(options.activeOnly));
  }
  if (options?.skip !== undefined) {
    params.append('skip', String(options.skip));
  }
  if (options?.limit !== undefined) {
    params.append('limit', String(options.limit));
  }

  const queryString = params.toString();
  const url = queryString ? `/brands?${queryString}` : '/brands';
  const response = await get<Record<string, unknown>[]>(url);
  return response.map(transformBrandResponse);
}

/**
 * Create a new brand
 */
export async function createBrand(data: CreateBrandRequest): Promise<BrandResponse> {
  const requestData = {
    name: data.name,
    slug: data.slug,
    description: data.description,
    logo_url: data.logoUrl,
    theme_config: transformThemeConfigToSnakeCase(data.themeConfig),
  };
  const response = await post<Record<string, unknown>>('/brands', requestData);
  return transformBrandResponse(response);
}

/**
 * Update brand
 */
export async function updateBrand(id: string, data: UpdateBrandRequest): Promise<BrandResponse> {
  const requestData: Record<string, unknown> = {};
  if (data.name !== undefined) requestData.name = data.name;
  if (data.description !== undefined) requestData.description = data.description;
  if (data.logoUrl !== undefined) requestData.logo_url = data.logoUrl;
  if (data.isActive !== undefined) requestData.is_active = data.isActive;

  const response = await patch<Record<string, unknown>>(`/brands/${id}`, requestData);
  return transformBrandResponse(response);
}

/**
 * Update brand theme
 */
export async function updateBrandTheme(id: string, theme: UpdateBrandThemeRequest): Promise<BrandResponse> {
  const requestData = {
    theme_config: transformThemeConfigToSnakeCase(theme.themeConfig),
  };
  const response = await patch<Record<string, unknown>>(`/brands/${id}`, requestData);
  return transformBrandResponse(response);
}

/**
 * Delete brand
 */
export async function deleteBrand(id: string): Promise<void> {
  await del(`/brands/${id}`);
}

export default {
  getBrandBySlug,
  getBrandById,
  listBrands,
  createBrand,
  updateBrand,
  updateBrandTheme,
  deleteBrand,
};
