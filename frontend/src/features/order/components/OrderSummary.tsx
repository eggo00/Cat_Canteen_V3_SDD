/**
 * OrderSummary component
 * Displays order summary with items and total
 */

import { CartItem } from '../../cart/store/cartStore';

/**
 * OrderSummary props
 */
interface OrderSummaryProps {
  /** Cart items */
  items: CartItem[];
  /** Subtotal amount */
  subtotal: number;
  /** Get item subtotal */
  getItemSubtotal: (itemId: string) => number;
  /** Format price */
  formatPrice: (price: number) => string;
}

/**
 * OrderSummary component
 */
export function OrderSummary({
  items,
  subtotal,
  getItemSubtotal,
  formatPrice,
}: OrderSummaryProps): JSX.Element {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="mb-4 text-lg font-bold text-gray-900">訂單明細</h3>

      {/* Items */}
      <div className="space-y-3">
        {items.map((item) => (
          <div key={item.id} className="flex justify-between">
            <div className="flex-1">
              <p className="font-medium text-gray-900">
                {item.menuItemName} x {item.quantity}
              </p>
              {item.customizations.length > 0 && (
                <p className="text-sm text-gray-500">
                  {item.customizations.map((c) => c.name).join('、')}
                </p>
              )}
              {item.notes && (
                <p className="text-sm text-gray-400">備註：{item.notes}</p>
              )}
            </div>
            <span className="font-medium text-gray-700">
              {formatPrice(getItemSubtotal(item.id))}
            </span>
          </div>
        ))}
      </div>

      {/* Divider */}
      <div className="my-4 border-t border-gray-200" />

      {/* Total */}
      <div className="flex items-center justify-between">
        <span className="text-lg font-bold text-gray-900">總計</span>
        <span
          className="text-xl font-bold"
          style={{ color: 'var(--color-primary, #FF6B6B)' }}
        >
          {formatPrice(subtotal)}
        </span>
      </div>
    </div>
  );
}

export default OrderSummary;
