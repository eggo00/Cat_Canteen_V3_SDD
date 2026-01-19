/**
 * useCart hook
 * Provides a convenient interface for cart operations
 */

import { useCallback, useMemo } from 'react';
import { useCartStore, CartItem } from '../store/cartStore';
import { MenuItem } from '../../../shared/types/menu';

/**
 * Customization selection for adding to cart
 */
interface CustomizationSelection {
  optionId: string;
  name: string;
  priceAdjustment: number;
}

/**
 * Hook return type
 */
interface UseCartReturn {
  /** Cart items */
  items: CartItem[];
  /** Total number of items (sum of quantities) */
  itemCount: number;
  /** Cart subtotal */
  subtotal: number;
  /** Current brand ID */
  brandId: string | null;
  /** Current brand slug */
  brandSlug: string | null;
  /** Whether cart is empty */
  isEmpty: boolean;

  /** Add item to cart */
  addItem: (
    menuItem: MenuItem,
    quantity?: number,
    customizations?: CustomizationSelection[],
    notes?: string
  ) => void;
  /** Remove item from cart */
  removeItem: (cartItemId: string) => void;
  /** Update item quantity */
  updateQuantity: (cartItemId: string, quantity: number) => void;
  /** Increment item quantity */
  incrementQuantity: (cartItemId: string) => void;
  /** Decrement item quantity */
  decrementQuantity: (cartItemId: string) => void;
  /** Update item notes */
  updateNotes: (cartItemId: string, notes: string) => void;
  /** Clear all items */
  clearCart: () => void;
  /** Set current brand */
  setBrand: (brandId: string, brandSlug: string) => void;
  /** Get subtotal for specific item */
  getItemSubtotal: (cartItemId: string) => number;
  /** Format price for display */
  formatPrice: (price: number) => string;
}

/**
 * Format price in TWD
 */
function formatPrice(price: number): string {
  return `NT$ ${price.toFixed(0)}`;
}

/**
 * Hook for cart operations
 *
 * @example
 * ```tsx
 * function CartButton() {
 *   const { itemCount, subtotal, formatPrice } = useCart();
 *
 *   return (
 *     <button>
 *       購物車 ({itemCount}) - {formatPrice(subtotal)}
 *     </button>
 *   );
 * }
 * ```
 */
export function useCart(): UseCartReturn {
  const store = useCartStore();

  // Memoized computed values
  const itemCount = useMemo(() => store.getItemCount(), [store.items]);
  const subtotal = useMemo(() => store.getSubtotal(), [store.items]);
  const isEmpty = useMemo(() => store.items.length === 0, [store.items]);

  // Wrapped actions with useCallback
  const addItem = useCallback(
    (
      menuItem: MenuItem,
      quantity = 1,
      customizations: CustomizationSelection[] = [],
      notes?: string
    ) => {
      store.addItem(menuItem, quantity, customizations, notes);
    },
    [store.addItem]
  );

  const removeItem = useCallback(
    (cartItemId: string) => {
      store.removeItem(cartItemId);
    },
    [store.removeItem]
  );

  const updateQuantity = useCallback(
    (cartItemId: string, quantity: number) => {
      store.updateQuantity(cartItemId, quantity);
    },
    [store.updateQuantity]
  );

  const incrementQuantity = useCallback(
    (cartItemId: string) => {
      const item = store.items.find((i) => i.id === cartItemId);
      if (item) {
        store.updateQuantity(cartItemId, item.quantity + 1);
      }
    },
    [store.items, store.updateQuantity]
  );

  const decrementQuantity = useCallback(
    (cartItemId: string) => {
      const item = store.items.find((i) => i.id === cartItemId);
      if (item && item.quantity > 1) {
        store.updateQuantity(cartItemId, item.quantity - 1);
      } else if (item) {
        store.removeItem(cartItemId);
      }
    },
    [store.items, store.updateQuantity, store.removeItem]
  );

  const updateNotes = useCallback(
    (cartItemId: string, notes: string) => {
      store.updateNotes(cartItemId, notes);
    },
    [store.updateNotes]
  );

  const clearCart = useCallback(() => {
    store.clearCart();
  }, [store.clearCart]);

  const setBrand = useCallback(
    (brandId: string, brandSlug: string) => {
      store.setBrand(brandId, brandSlug);
    },
    [store.setBrand]
  );

  const getItemSubtotal = useCallback(
    (cartItemId: string) => {
      return store.getItemSubtotal(cartItemId);
    },
    [store.getItemSubtotal]
  );

  return {
    items: store.items,
    itemCount,
    subtotal,
    brandId: store.brandId,
    brandSlug: store.brandSlug,
    isEmpty,
    addItem,
    removeItem,
    updateQuantity,
    incrementQuantity,
    decrementQuantity,
    updateNotes,
    clearCart,
    setBrand,
    getItemSubtotal,
    formatPrice,
  };
}

export default useCart;
