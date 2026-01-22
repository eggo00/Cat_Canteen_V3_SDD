/**
 * CartItem component
 * Displays a single item in the cart with quantity controls
 */

import { CartItem as CartItemType } from '../store/cartStore';

/**
 * CartItem props
 */
interface CartItemProps {
  /** Cart item data */
  item: CartItemType;
  /** Subtotal for this item */
  subtotal: number;
  /** Increment quantity handler */
  onIncrement: () => void;
  /** Decrement quantity handler */
  onDecrement: () => void;
  /** Remove item handler */
  onRemove: () => void;
  /** Update notes handler */
  onUpdateNotes?: (notes: string) => void;
}

/**
 * Format price in TWD
 */
function formatPrice(price: number): string {
  return `NT$ ${price.toFixed(0)}`;
}

/**
 * CartItem component
 */
export function CartItem({
  item,
  subtotal,
  onIncrement,
  onDecrement,
  onRemove,
  onUpdateNotes: _onUpdateNotes,
}: CartItemProps): JSX.Element {
  return (
    <div
      className="flex gap-4 rounded-lg border border-gray-200 bg-white p-4"
      data-testid={`cart-item-${item.id}`}
    >
      {/* Image */}
      {item.imageUrl && (
        <div className="h-20 w-20 shrink-0 overflow-hidden rounded-lg bg-gray-100">
          <img
            src={item.imageUrl}
            alt={item.menuItemName}
            className="h-full w-full object-cover"
          />
        </div>
      )}

      {/* Content */}
      <div className="flex flex-1 flex-col">
        {/* Name and remove button */}
        <div className="flex items-start justify-between">
          <h3 className="font-semibold text-gray-900">{item.menuItemName}</h3>
          <button
            onClick={onRemove}
            className="text-gray-400 hover:text-red-500"
            aria-label="移除商品"
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Customizations */}
        {item.customizations.length > 0 && (
          <p className="mt-1 text-sm text-gray-500">
            {item.customizations.map((c) => c.name).join('、')}
          </p>
        )}

        {/* Notes */}
        {item.notes && (
          <p className="mt-1 text-sm text-gray-400">備註：{item.notes}</p>
        )}

        {/* Price and quantity controls */}
        <div className="mt-auto flex items-center justify-between pt-2">
          {/* Quantity controls */}
          <div className="flex items-center gap-2">
            <button
              onClick={onDecrement}
              className="flex h-8 w-8 items-center justify-center rounded-full border border-gray-300 text-gray-600 hover:bg-gray-100"
              aria-label="減少數量"
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
              </svg>
            </button>
            <span className="w-8 text-center font-medium">{item.quantity}</span>
            <button
              onClick={onIncrement}
              className="flex h-8 w-8 items-center justify-center rounded-full border border-gray-300 text-gray-600 hover:bg-gray-100"
              aria-label="增加數量"
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 4v16m8-8H4"
                />
              </svg>
            </button>
          </div>

          {/* Subtotal */}
          <span
            className="font-bold"
            style={{ color: 'var(--color-primary, #FF6B6B)' }}
          >
            {formatPrice(subtotal)}
          </span>
        </div>
      </div>
    </div>
  );
}

export default CartItem;
