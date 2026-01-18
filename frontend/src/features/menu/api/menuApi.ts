/**
 * Menu API client
 * Handles all menu-related API requests
 */

import { get, post, patch, del } from '../../../shared/utils/api';
import {
  Category,
  MenuItem,
  CustomizationOption,
  MenuResponse,
  UploadMenuRequest,
} from '../../../shared/types/menu';

/**
 * Transform category response from snake_case to camelCase
 */
function transformCategory(data: Record<string, unknown>): Category {
  const menuItems = data.menu_items as Record<string, unknown>[] | undefined;
  return {
    id: data.id as string,
    brandId: data.brand_id as string,
    name: data.name as string,
    description: data.description as string | undefined,
    displayOrder: data.display_order as number,
    isActive: data.is_active !== false,
    menuItems: menuItems?.map(transformMenuItem),
  };
}

/**
 * Transform menu item response from snake_case to camelCase
 */
function transformMenuItem(data: Record<string, unknown>): MenuItem {
  const customizationOptions = data.customization_options as Record<string, unknown>[] | undefined;
  return {
    id: data.id as string,
    categoryId: data.category_id as string,
    name: data.name as string,
    description: data.description as string | undefined,
    price: data.price as number,
    imageUrl: data.image_url as string | undefined,
    displayOrder: data.display_order as number,
    isAvailable: data.is_available !== false,
    customizationOptions: customizationOptions?.map(transformCustomizationOption),
  };
}

/**
 * Transform customization option from snake_case to camelCase
 */
function transformCustomizationOption(data: Record<string, unknown>): CustomizationOption {
  return {
    id: data.id as string,
    menuItemId: data.menu_item_id as string,
    optionType: data.option_type as string,
    name: data.name as string,
    priceAdjustment: data.price_adjustment as number,
    constraints: data.constraints as Record<string, unknown> | undefined,
    displayOrder: data.display_order as number,
  };
}

/**
 * Transform menu response
 */
function transformMenuResponse(data: Record<string, unknown>): MenuResponse {
  const categories = data.categories as Record<string, unknown>[];
  return {
    categories: categories?.map(transformCategory) || [],
  };
}

/**
 * Get full menu for a brand
 */
export async function getMenu(brandId: string): Promise<MenuResponse> {
  const response = await get<Record<string, unknown>>(`/brands/${brandId}/menu`);
  return transformMenuResponse(response);
}

/**
 * Upload menu JSON for a brand
 */
export async function uploadMenu(brandId: string, data: UploadMenuRequest): Promise<MenuResponse> {
  // Transform to snake_case for API
  const requestData = {
    categories: data.categories.map((cat) => ({
      name: cat.name,
      description: cat.description,
      display_order: cat.displayOrder,
      menu_items: cat.menuItems.map((item) => ({
        name: item.name,
        description: item.description,
        price: item.price,
        image_url: item.imageUrl,
        display_order: item.displayOrder,
        customization_options: item.customizationOptions?.map((opt) => ({
          option_type: opt.optionType,
          name: opt.name,
          price_adjustment: opt.priceAdjustment,
        })),
      })),
    })),
  };
  const response = await post<Record<string, unknown>>(`/brands/${brandId}/menu`, requestData);
  return transformMenuResponse(response);
}

/**
 * Get categories for a brand
 */
export async function getCategories(brandId: string, includeItems = true): Promise<Category[]> {
  const url = includeItems
    ? `/brands/${brandId}/menu/categories?include_items=true`
    : `/brands/${brandId}/menu/categories`;
  const response = await get<Record<string, unknown>[]>(url);
  return response.map(transformCategory);
}

/**
 * Get single category by ID
 */
export async function getCategoryById(brandId: string, categoryId: string): Promise<Category> {
  const response = await get<Record<string, unknown>>(
    `/brands/${brandId}/menu/categories/${categoryId}`
  );
  return transformCategory(response);
}

/**
 * Create category
 */
export async function createCategory(
  brandId: string,
  data: { name: string; description?: string; displayOrder?: number }
): Promise<Category> {
  const requestData = {
    name: data.name,
    description: data.description,
    display_order: data.displayOrder,
  };
  const response = await post<Record<string, unknown>>(
    `/brands/${brandId}/menu/categories`,
    requestData
  );
  return transformCategory(response);
}

/**
 * Update category
 */
export async function updateCategory(
  brandId: string,
  categoryId: string,
  data: { name?: string; description?: string; displayOrder?: number }
): Promise<Category> {
  const requestData: Record<string, unknown> = {};
  if (data.name !== undefined) requestData.name = data.name;
  if (data.description !== undefined) requestData.description = data.description;
  if (data.displayOrder !== undefined) requestData.display_order = data.displayOrder;

  const response = await patch<Record<string, unknown>>(
    `/brands/${brandId}/menu/categories/${categoryId}`,
    requestData
  );
  return transformCategory(response);
}

/**
 * Delete category
 */
export async function deleteCategory(brandId: string, categoryId: string): Promise<void> {
  await del(`/brands/${brandId}/menu/categories/${categoryId}`);
}

/**
 * Get menu items for a category
 */
export async function getMenuItems(brandId: string, categoryId: string): Promise<MenuItem[]> {
  const response = await get<Record<string, unknown>[]>(
    `/brands/${brandId}/menu/categories/${categoryId}/items`
  );
  return response.map(transformMenuItem);
}

export default {
  getMenu,
  uploadMenu,
  getCategories,
  getCategoryById,
  createCategory,
  updateCategory,
  deleteCategory,
  getMenuItems,
};
