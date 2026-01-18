/**
 * MenuList component
 * Displays a grid of menu items with loading and empty states
 */

import React from 'react';
import { MenuItem as MenuItemType } from '../../../shared/types/menu';
import { MenuItem } from './MenuItem';

/**
 * MenuList props
 */
interface MenuListProps {
  /** Menu items to display */
  items: MenuItemType[];
  /** Loading state */
  isLoading?: boolean;
  /** Click handler for adding items to cart */
  onAddToCart?: (item: MenuItemType) => void;
  /** Whether to show customization options */
  showCustomizations?: boolean;
  /** Empty state message */
  emptyMessage?: string;
  /** Number of columns (responsive by default) */
  columns?: 1 | 2 | 3 | 4;
}

/**
 * Loading skeleton for menu item
 */
function MenuItemSkeleton(): JSX.Element {
  return (
    <div className="animate-pulse rounded-lg border border-gray-200 bg-white p-4">
      <div className="mb-3 aspect-square w-full rounded-lg bg-gray-200" />
      <div className="space-y-2">
        <div className="h-5 w-3/4 rounded bg-gray-200" />
        <div className="h-4 w-full rounded bg-gray-200" />
        <div className="h-4 w-1/2 rounded bg-gray-200" />
        <div className="flex items-center justify-between pt-2">
          <div className="h-6 w-20 rounded bg-gray-200" />
          <div className="h-9 w-24 rounded-full bg-gray-200" />
        </div>
      </div>
    </div>
  );
}

/**
 * Grid class based on column count
 */
function getGridClass(columns?: 1 | 2 | 3 | 4): string {
  switch (columns) {
    case 1:
      return 'grid-cols-1';
    case 2:
      return 'grid-cols-1 sm:grid-cols-2';
    case 3:
      return 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3';
    case 4:
      return 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4';
    default:
      return 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4';
  }
}

/**
 * MenuList component
 *
 * @example
 * ```tsx
 * function MenuPage() {
 *   const { filteredItems, isLoading } = useMenu(brandId);
 *
 *   return (
 *     <MenuList
 *       items={filteredItems}
 *       isLoading={isLoading}
 *       onAddToCart={(item) => cart.add(item)}
 *     />
 *   );
 * }
 * ```
 */
export function MenuList({
  items,
  isLoading = false,
  onAddToCart,
  showCustomizations = true,
  emptyMessage = '目前沒有菜單項目',
  columns,
}: MenuListProps): JSX.Element {
  const gridClass = getGridClass(columns);

  // Loading state
  if (isLoading) {
    return (
      <div className={`grid gap-4 ${gridClass}`} data-testid="menu-list-loading">
        {Array.from({ length: 8 }).map((_, index) => (
          <MenuItemSkeleton key={index} />
        ))}
      </div>
    );
  }

  // Empty state
  if (items.length === 0) {
    return (
      <div
        className="flex flex-col items-center justify-center py-12 text-center"
        data-testid="menu-list-empty"
      >
        <svg
          className="mb-4 h-16 w-16 text-gray-300"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
          />
        </svg>
        <p className="text-lg text-gray-500">{emptyMessage}</p>
      </div>
    );
  }

  // Menu items grid
  return (
    <div className={`grid gap-4 ${gridClass}`} data-testid="menu-list">
      {items.map((item) => (
        <MenuItem
          key={item.id}
          item={item}
          onAddToCart={onAddToCart}
          showCustomizations={showCustomizations}
        />
      ))}
    </div>
  );
}

export default MenuList;
