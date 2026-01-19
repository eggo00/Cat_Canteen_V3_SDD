/**
 * RevenueChart component
 * Displays daily revenue as a bar chart
 */

import React, { useMemo } from 'react';
import { DailyRevenue } from '../../../shared/types/analytics';

interface RevenueChartProps {
  data: DailyRevenue[];
  height?: number;
  className?: string;
}

/**
 * Format date for display
 */
function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return `${date.getMonth() + 1}/${date.getDate()}`;
}

/**
 * Format currency
 */
function formatCurrency(value: number): string {
  if (value >= 10000) {
    return `${(value / 1000).toFixed(0)}K`;
  }
  return value.toFixed(0);
}

/**
 * RevenueChart component
 */
export function RevenueChart({
  data,
  height = 200,
  className = '',
}: RevenueChartProps): JSX.Element {
  // Calculate max value for scaling
  const maxRevenue = useMemo(() => {
    if (data.length === 0) return 0;
    return Math.max(...data.map((d) => d.totalRevenue));
  }, [data]);

  // Calculate bar width based on data length
  const barWidth = useMemo(() => {
    if (data.length === 0) return 0;
    const maxBars = Math.min(data.length, 30);
    return Math.max(100 / maxBars - 2, 2);
  }, [data.length]);

  if (data.length === 0) {
    return (
      <div
        className={`flex items-center justify-center rounded-lg border border-gray-200 bg-white ${className}`}
        style={{ height }}
      >
        <p className="text-gray-500">尚無營收資料</p>
      </div>
    );
  }

  return (
    <div
      className={`rounded-lg border border-gray-200 bg-white p-4 ${className}`}
    >
      <h3 className="mb-4 font-bold text-gray-900">每日營收趨勢</h3>

      {/* Chart */}
      <div className="relative" style={{ height }}>
        {/* Y-axis labels */}
        <div className="absolute left-0 top-0 flex h-full flex-col justify-between text-xs text-gray-400">
          <span>{formatCurrency(maxRevenue)}</span>
          <span>{formatCurrency(maxRevenue / 2)}</span>
          <span>0</span>
        </div>

        {/* Bars container */}
        <div className="ml-12 flex h-full items-end gap-1 overflow-hidden">
          {data.slice(-30).map((day, index) => {
            const barHeight =
              maxRevenue > 0
                ? (day.totalRevenue / maxRevenue) * 100
                : 0;

            return (
              <div
                key={day.date}
                className="group relative flex flex-col items-center"
                style={{ width: `${barWidth}%` }}
              >
                {/* Tooltip */}
                <div className="absolute bottom-full left-1/2 z-10 mb-2 hidden -translate-x-1/2 rounded bg-gray-900 px-2 py-1 text-xs text-white group-hover:block whitespace-nowrap">
                  <p className="font-medium">{formatDate(day.date)}</p>
                  <p>NT$ {day.totalRevenue.toLocaleString()}</p>
                  <p>{day.orderCount} 筆訂單</p>
                </div>

                {/* Bar */}
                <div
                  className="w-full cursor-pointer rounded-t transition-all hover:opacity-80"
                  style={{
                    height: `${barHeight}%`,
                    minHeight: day.totalRevenue > 0 ? '4px' : '0',
                    backgroundColor: 'var(--color-primary, #FF6B6B)',
                  }}
                />
              </div>
            );
          })}
        </div>
      </div>

      {/* X-axis labels */}
      <div className="ml-12 mt-2 flex justify-between text-xs text-gray-400">
        {data.length > 0 && (
          <>
            <span>{formatDate(data[Math.max(0, data.length - 30)].date)}</span>
            <span>{formatDate(data[data.length - 1].date)}</span>
          </>
        )}
      </div>
    </div>
  );
}

export default RevenueChart;
