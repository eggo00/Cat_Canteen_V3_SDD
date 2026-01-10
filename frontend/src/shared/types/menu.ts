/**
 * Menu-related TypeScript types
 */

export interface CustomizationOption {
  id: string;
  menuItemId: string;
  optionType: string; // 'topping', 'sweetness', 'temperature', etc.
  name: string;
  priceAdjustment: number;
  constraints?: Record<string, any>;
  displayOrder: number;
}

export interface MenuItem {
  id: string;
  categoryId: string;
  name: string;
  description?: string;
  price: number;
  imageUrl?: string;
  displayOrder: number;
  isAvailable: boolean;
  customizationOptions?: CustomizationOption[];
}

export interface Category {
  id: string;
  brandId: string;
  name: string;
  description?: string;
  displayOrder: number;
  isActive: boolean;
  menuItems?: MenuItem[];
}

export interface Menu {
  categories: Category[];
}

export interface UploadMenuRequest {
  categories: {
    name: string;
    description?: string;
    displayOrder?: number;
    menuItems: {
      name: string;
      description?: string;
      price: number;
      imageUrl?: string;
      displayOrder?: number;
      customizationOptions?: {
        optionType: string;
        name: string;
        priceAdjustment?: number;
      }[];
    }[];
  }[];
}

export interface MenuResponse {
  categories: Category[];
}
