/**
 * HourlyChart component
 * Displays hourly order distribution
 */

import React, { useMemo } from 'react';
import { HourlyOrders } from '../../../shared/types/analytics';

interface HourlyChartProps {
  data: HourlyOrders[];
  peakHour: number | null;
  height?: number;
  className?: string;
}

/**
 * Format hour for display
 */
function formatHour(hour: number): string {
  return `${hour.toString().padStart(2, '0')}:00`;
}

/**
 * HourlyChart component
 */
export function HourlyChart({
  data,
  peakHour,
  height = 180,
  className = '',
}: HourlyChartProps): JSX.Element {
  // Calculate max for scaling
  const maxOrders = useMemo(() => {
    if (data.length === 0) return 0;
    return Math.max(...data.map((d) => d.orderCount));
  }, [data]);

  // Filter to show only business hours (6:00 - 23:00)
  const businessHours = useMemo(() => {
    return data.filter((d) => d.hour >= 6 && d.hour <= 23);
  }, [data]);

  if (data.length === 0) {
    return (
      <div
        className={`flex items-center justify-center rounded-lg border border-gray-200 bg-white ${className}`}
        style={{ height }}
      >
        <p className="text-gray-500">尚無訂單資料</p>
      </div>
    );
  }

  return (
    <div
      className={`rounded-lg border border-gray-200 bg-white p-4 ${className}`}
    >
      <div className="mb-4 flex items-center justify-between">
        <h3 className="font-bold text-gray-900">每小時訂單分佈</h3>
        {peakHour !== null && (
          <div className="text-sm">
            <span className="text-gray-500">尖峰時段：</span>
            <span
              className="ml-1 font-bold"
              style={{ color: 'var(--color-primary, #FF6B6B)' }}
            >
              {formatHour(peakHour)}
            </span>
          </div>
        )}
      </div>

      {/* Chart */}
      <div className="relative" style={{ height }}>
        {/* Bars container */}
        <div className="flex h-full items-end gap-0.5">
          {businessHours.map((hourData) => {
            const barHeight =
              maxOrders > 0
                ? (hourData.orderCount / maxOrders) * 100
                : 0;
            const isPeak = hourData.hour === peakHour;

            return (
              <div
                key={hourData.hour}
                className="group relative flex flex-1 flex-col items-center"
              >
                {/* Tooltip */}
                <div className="absolute bottom-full left-1/2 z-10 mb-2 hidden -translate-x-1/2 rounded bg-gray-900 px-2 py-1 text-xs text-white group-hover:block whitespace-nowrap">
                  <p className="font-medium">{formatHour(hourData.hour)}</p>
                  <p>{hourData.orderCount} 筆訂單</p>
                  <p>NT$ {hourData.totalRevenue.toLocaleString()}</p>
                </div>

                {/* Bar */}
                <div
                  className="w-full cursor-pointer rounded-t transition-all hover:opacity-80"
                  style={{
                    height: `${barHeight}%`,
                    minHeight: hourData.orderCount > 0 ? '4px' : '0',
                    backgroundColor: isPeak
                      ? 'var(--color-primary, #FF6B6B)'
                      : 'var(--color-secondary, #4ECDC4)',
                  }}
                />
              </div>
            );
          })}
        </div>
      </div>

      {/* X-axis labels */}
      <div className="mt-2 flex justify-between text-xs text-gray-400">
        <span>06:00</span>
        <span>12:00</span>
        <span>18:00</span>
        <span>23:00</span>
      </div>

      {/* Legend */}
      <div className="mt-4 flex items-center justify-center gap-4 text-xs">
        <div className="flex items-center gap-1">
          <div
            className="h-3 w-3 rounded"
            style={{ backgroundColor: 'var(--color-primary, #FF6B6B)' }}
          />
          <span className="text-gray-600">尖峰時段</span>
        </div>
        <div className="flex items-center gap-1">
          <div
            className="h-3 w-3 rounded"
            style={{ backgroundColor: 'var(--color-secondary, #4ECDC4)' }}
          />
          <span className="text-gray-600">一般時段</span>
        </div>
      </div>
    </div>
  );
}

export default HourlyChart;
