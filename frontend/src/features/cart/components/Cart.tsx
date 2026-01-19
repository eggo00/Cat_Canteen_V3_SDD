/**
 * Cart component
 * Displays the shopping cart with all items and checkout button
 */

import React from 'react';
import { useCart } from '../hooks/useCart';
import { CartItem } from './CartItem';

/**
 * Cart props
 */
interface CartProps {
  /** Checkout handler */
  onCheckout?: () => void;
  /** Continue shopping handler */
  onContinueShopping?: () => void;
}

/**
 * Empty cart display
 */
function EmptyCart({ onContinueShopping }: { onContinueShopping?: () => void }): JSX.Element {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <svg
        className="mb-4 h-20 w-20 text-gray-300"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
        />
      </svg>
      <h3 className="text-lg font-semibold text-gray-700">購物車是空的</h3>
      <p className="mt-1 text-gray-500">快去選購美食吧！</p>
      {onContinueShopping && (
        <button
          onClick={onContinueShopping}
          className="mt-4 rounded-full px-6 py-2 text-white"
          style={{ backgroundColor: 'var(--color-primary, #FF6B6B)' }}
        >
          繼續選購
        </button>
      )}
    </div>
  );
}

/**
 * Cart component
 */
export function Cart({ onCheckout, onContinueShopping }: CartProps): JSX.Element {
  const {
    items,
    itemCount,
    subtotal,
    isEmpty,
    incrementQuantity,
    decrementQuantity,
    removeItem,
    updateNotes,
    clearCart,
    getItemSubtotal,
    formatPrice,
  } = useCart();

  if (isEmpty) {
    return <EmptyCart onContinueShopping={onContinueShopping} />;
  }

  return (
    <div className="flex flex-col" data-testid="cart">
      {/* Cart header */}
      <div className="flex items-center justify-between border-b border-gray-200 pb-4">
        <h2 className="text-xl font-bold text-gray-900">
          購物車 <span className="text-gray-500">({itemCount})</span>
        </h2>
        <button
          onClick={clearCart}
          className="text-sm text-gray-500 hover:text-red-500"
        >
          清空購物車
        </button>
      </div>

      {/* Cart items */}
      <div className="mt-4 space-y-4">
        {items.map((item) => (
          <CartItem
            key={item.id}
            item={item}
            subtotal={getItemSubtotal(item.id)}
            onIncrement={() => incrementQuantity(item.id)}
            onDecrement={() => decrementQuantity(item.id)}
            onRemove={() => removeItem(item.id)}
            onUpdateNotes={(notes) => updateNotes(item.id, notes)}
          />
        ))}
      </div>

      {/* Cart footer */}
      <div className="mt-6 border-t border-gray-200 pt-4">
        {/* Subtotal */}
        <div className="flex items-center justify-between">
          <span className="text-gray-600">小計</span>
          <span className="text-xl font-bold" style={{ color: 'var(--color-primary, #FF6B6B)' }}>
            {formatPrice(subtotal)}
          </span>
        </div>

        {/* Actions */}
        <div className="mt-4 flex flex-col gap-2">
          <button
            onClick={onCheckout}
            className="w-full rounded-lg py-3 text-center font-semibold text-white transition-opacity hover:opacity-90"
            style={{ backgroundColor: 'var(--color-primary, #FF6B6B)' }}
          >
            前往結帳
          </button>
          {onContinueShopping && (
            <button
              onClick={onContinueShopping}
              className="w-full rounded-lg border border-gray-300 py-3 text-center font-semibold text-gray-700 transition-colors hover:bg-gray-50"
            >
              繼續選購
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default Cart;
