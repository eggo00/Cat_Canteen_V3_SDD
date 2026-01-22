/**
 * MenuItem component
 * Displays a single menu item with price and customization options
 */

import { MenuItem as MenuItemType } from '../../../shared/types/menu';

/**
 * MenuItem props
 */
interface MenuItemProps {
  /** Menu item data */
  item: MenuItemType;
  /** Click handler for adding to cart */
  onAddToCart?: (item: MenuItemType) => void;
  /** Whether to show customization options */
  showCustomizations?: boolean;
}

/**
 * Format price in TWD
 */
function formatPrice(price: number): string {
  return `NT$ ${price.toFixed(0)}`;
}

/**
 * MenuItem component
 */
export function MenuItem({
  item,
  onAddToCart,
  showCustomizations = false,
}: MenuItemProps): JSX.Element {
  const handleClick = () => {
    onAddToCart?.(item);
  };

  return (
    <div
      className="group relative flex flex-col rounded-lg border border-gray-200 bg-white p-4 shadow-sm transition-all hover:shadow-md"
      data-testid={`menu-item-${item.id}`}
    >
      {/* Image */}
      {item.imageUrl && (
        <div className="mb-3 aspect-square w-full overflow-hidden rounded-lg bg-gray-100">
          <img
            src={item.imageUrl}
            alt={item.name}
            className="h-full w-full object-cover transition-transform group-hover:scale-105"
          />
        </div>
      )}

      {/* Content */}
      <div className="flex flex-1 flex-col">
        {/* Name and availability */}
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-lg font-semibold text-gray-900">{item.name}</h3>
          {!item.isAvailable && (
            <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500">
              售完
            </span>
          )}
        </div>

        {/* Description */}
        {item.description && (
          <p className="mt-1 line-clamp-2 text-sm text-gray-500">{item.description}</p>
        )}

        {/* Customization options preview */}
        {showCustomizations && item.customizationOptions && item.customizationOptions.length > 0 && (
          <div className="mt-2">
            <p className="text-xs text-gray-400">
              可選：
              {item.customizationOptions
                .slice(0, 3)
                .map((opt) => opt.name)
                .join('、')}
              {item.customizationOptions.length > 3 && '...'}
            </p>
          </div>
        )}

        {/* Price and action */}
        <div className="mt-auto flex items-center justify-between pt-3">
          <span
            className="text-lg font-bold"
            style={{ color: 'var(--color-primary, #FF6B6B)' }}
          >
            {formatPrice(item.price)}
          </span>

          {onAddToCart && item.isAvailable && (
            <button
              onClick={handleClick}
              className="rounded-full px-4 py-2 text-sm font-medium text-white transition-colors"
              style={{
                backgroundColor: 'var(--color-primary, #FF6B6B)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.opacity = '0.9';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.opacity = '1';
              }}
            >
              加入購物車
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default MenuItem;
