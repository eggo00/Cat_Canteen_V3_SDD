/**
 * Cart Store using Zustand
 * Manages shopping cart state with persistence
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { MenuItem, CustomizationOption } from '../../../shared/types/menu';

/**
 * Cart item with quantity and customizations
 */
export interface CartItem {
  id: string;
  menuItemId: string;
  menuItemName: string;
  unitPrice: number;
  quantity: number;
  customizations: Array<{
    optionId: string;
    name: string;
    priceAdjustment: number;
  }>;
  notes?: string;
  imageUrl?: string;
}

/**
 * Cart state interface
 */
interface CartState {
  items: CartItem[];
  brandId: string | null;
  brandSlug: string | null;

  // Actions
  addItem: (
    menuItem: MenuItem,
    quantity?: number,
    customizations?: Array<{
      optionId: string;
      name: string;
      priceAdjustment: number;
    }>,
    notes?: string
  ) => void;
  removeItem: (cartItemId: string) => void;
  updateQuantity: (cartItemId: string, quantity: number) => void;
  updateNotes: (cartItemId: string, notes: string) => void;
  clearCart: () => void;
  setBrand: (brandId: string, brandSlug: string) => void;

  // Computed
  getItemCount: () => number;
  getSubtotal: () => number;
  getItemSubtotal: (cartItemId: string) => number;
}

/**
 * Generate a unique cart item ID
 */
function generateCartItemId(): string {
  return `cart-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
}

/**
 * Calculate item subtotal including customizations
 */
function calculateItemSubtotal(item: CartItem): number {
  const customizationTotal = item.customizations.reduce(
    (sum, c) => sum + c.priceAdjustment,
    0
  );
  return (item.unitPrice + customizationTotal) * item.quantity;
}

/**
 * Cart store with persistence
 */
export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],
      brandId: null,
      brandSlug: null,

      /**
       * Add item to cart
       */
      addItem: (menuItem, quantity = 1, customizations = [], notes) => {
        const state = get();

        // Check if same item with same customizations exists
        const existingItem = state.items.find(
          (item) =>
            item.menuItemId === menuItem.id &&
            JSON.stringify(item.customizations) === JSON.stringify(customizations)
        );

        if (existingItem) {
          // Update quantity of existing item
          set({
            items: state.items.map((item) =>
              item.id === existingItem.id
                ? { ...item, quantity: item.quantity + quantity }
                : item
            ),
          });
        } else {
          // Add new item
          const newItem: CartItem = {
            id: generateCartItemId(),
            menuItemId: menuItem.id,
            menuItemName: menuItem.name,
            unitPrice: menuItem.price,
            quantity,
            customizations,
            notes,
            imageUrl: menuItem.imageUrl,
          };

          set({ items: [...state.items, newItem] });
        }
      },

      /**
       * Remove item from cart
       */
      removeItem: (cartItemId) => {
        set({
          items: get().items.filter((item) => item.id !== cartItemId),
        });
      },

      /**
       * Update item quantity
       */
      updateQuantity: (cartItemId, quantity) => {
        if (quantity < 1) {
          // Remove item if quantity is 0 or less
          get().removeItem(cartItemId);
          return;
        }

        set({
          items: get().items.map((item) =>
            item.id === cartItemId ? { ...item, quantity } : item
          ),
        });
      },

      /**
       * Update item notes
       */
      updateNotes: (cartItemId, notes) => {
        set({
          items: get().items.map((item) =>
            item.id === cartItemId ? { ...item, notes } : item
          ),
        });
      },

      /**
       * Clear all items from cart
       */
      clearCart: () => {
        set({ items: [] });
      },

      /**
       * Set the current brand for the cart
       */
      setBrand: (brandId, brandSlug) => {
        const state = get();

        // If brand changes, clear the cart
        if (state.brandId && state.brandId !== brandId) {
          set({ items: [], brandId, brandSlug });
        } else {
          set({ brandId, brandSlug });
        }
      },

      /**
       * Get total number of items (sum of quantities)
       */
      getItemCount: () => {
        return get().items.reduce((sum, item) => sum + item.quantity, 0);
      },

      /**
       * Get cart subtotal
       */
      getSubtotal: () => {
        return get().items.reduce(
          (sum, item) => sum + calculateItemSubtotal(item),
          0
        );
      },

      /**
       * Get subtotal for a specific item
       */
      getItemSubtotal: (cartItemId) => {
        const item = get().items.find((i) => i.id === cartItemId);
        return item ? calculateItemSubtotal(item) : 0;
      },
    }),
    {
      name: 'cat-canteen-cart',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        items: state.items,
        brandId: state.brandId,
        brandSlug: state.brandSlug,
      }),
    }
  )
);

export default useCartStore;
