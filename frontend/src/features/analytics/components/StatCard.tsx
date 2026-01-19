/**
 * StatCard component
 * Displays a single statistic with optional change indicator
 */

import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  change?: number | null;
  icon?: React.ReactNode;
  className?: string;
}

/**
 * Format change percentage with sign
 */
function formatChange(change: number): string {
  const sign = change >= 0 ? '+' : '';
  return `${sign}${change.toFixed(1)}%`;
}

/**
 * StatCard component
 */
export function StatCard({
  title,
  value,
  subtitle,
  change,
  icon,
  className = '',
}: StatCardProps): JSX.Element {
  const isPositive = change !== null && change !== undefined && change >= 0;
  const isNegative = change !== null && change !== undefined && change < 0;

  return (
    <div
      className={`rounded-lg border border-gray-200 bg-white p-6 ${className}`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
          {subtitle && (
            <p className="mt-1 text-sm text-gray-500">{subtitle}</p>
          )}
          {change !== null && change !== undefined && (
            <p
              className={`mt-2 text-sm font-medium ${
                isPositive ? 'text-green-600' : ''
              } ${isNegative ? 'text-red-600' : ''}`}
            >
              {formatChange(change)} 較上期
            </p>
          )}
        </div>
        {icon && (
          <div
            className="flex h-12 w-12 items-center justify-center rounded-lg"
            style={{ backgroundColor: 'var(--color-primary, #FF6B6B)', opacity: 0.1 }}
          >
            <span style={{ color: 'var(--color-primary, #FF6B6B)' }}>{icon}</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default StatCard;
