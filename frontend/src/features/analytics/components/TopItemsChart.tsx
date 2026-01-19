/**
 * TopItemsChart component
 * Displays top selling items as horizontal bar chart
 */

import React from 'react';
import { TopItem } from '../../../shared/types/analytics';

interface TopItemsChartProps {
  items: TopItem[];
  className?: string;
}

/**
 * Format currency
 */
function formatCurrency(value: number): string {
  return `NT$ ${value.toLocaleString()}`;
}

/**
 * TopItemsChart component
 */
export function TopItemsChart({
  items,
  className = '',
}: TopItemsChartProps): JSX.Element {
  if (items.length === 0) {
    return (
      <div
        className={`flex items-center justify-center rounded-lg border border-gray-200 bg-white p-6 ${className}`}
      >
        <p className="text-gray-500">尚無銷售資料</p>
      </div>
    );
  }

  // Get max quantity for bar scaling
  const maxQuantity = Math.max(...items.map((item) => item.quantitySold));

  return (
    <div
      className={`rounded-lg border border-gray-200 bg-white p-4 ${className}`}
    >
      <h3 className="mb-4 font-bold text-gray-900">熱銷品項 Top {items.length}</h3>

      <div className="space-y-3">
        {items.map((item) => {
          const barWidth =
            maxQuantity > 0
              ? (item.quantitySold / maxQuantity) * 100
              : 0;

          return (
            <div key={item.rank} className="group">
              {/* Item info */}
              <div className="mb-1 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span
                    className="flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold text-white"
                    style={{
                      backgroundColor:
                        item.rank <= 3
                          ? 'var(--color-primary, #FF6B6B)'
                          : '#9CA3AF',
                    }}
                  >
                    {item.rank}
                  </span>
                  <span className="font-medium text-gray-900 truncate max-w-[150px]">
                    {item.menuItemName}
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-sm font-bold text-gray-900">
                    {item.quantitySold}
                  </span>
                  <span className="text-sm text-gray-500 ml-1">份</span>
                </div>
              </div>

              {/* Bar */}
              <div className="h-4 w-full overflow-hidden rounded-full bg-gray-100">
                <div
                  className="h-full rounded-full transition-all"
                  style={{
                    width: `${barWidth}%`,
                    backgroundColor:
                      item.rank <= 3
                        ? 'var(--color-primary, #FF6B6B)'
                        : 'var(--color-secondary, #4ECDC4)',
                  }}
                />
              </div>

              {/* Revenue info */}
              <div className="mt-1 flex justify-between text-xs text-gray-500">
                <span>{item.percentageOfTotal.toFixed(1)}% 佔比</span>
                <span>{formatCurrency(item.totalRevenue)}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default TopItemsChart;
