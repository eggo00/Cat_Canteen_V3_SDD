/**
 * OrderStatusDisplay component
 * Displays current order status with visual indicator
 */

import React from 'react';
import { OrderStatus, ORDER_STATUS_DISPLAY } from '../../../shared/types/order';

/**
 * Status step configuration
 */
interface StatusStep {
  status: OrderStatus;
  label: string;
  icon: React.ReactNode;
}

/**
 * Status steps for tracking
 */
const STATUS_STEPS: StatusStep[] = [
  {
    status: 'pending',
    label: ORDER_STATUS_DISPLAY.pending,
    icon: (
      <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    ),
  },
  {
    status: 'confirmed',
    label: ORDER_STATUS_DISPLAY.confirmed,
    icon: (
      <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    ),
  },
  {
    status: 'preparing',
    label: ORDER_STATUS_DISPLAY.preparing,
    icon: (
      <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z"
        />
      </svg>
    ),
  },
  {
    status: 'ready',
    label: ORDER_STATUS_DISPLAY.ready,
    icon: (
      <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"
        />
      </svg>
    ),
  },
];

/**
 * Get status step index
 */
function getStatusIndex(status: OrderStatus): number {
  const index = STATUS_STEPS.findIndex((step) => step.status === status);
  return index >= 0 ? index : -1;
}

/**
 * OrderStatusDisplay props
 */
interface OrderStatusDisplayProps {
  /** Current order status */
  status: OrderStatus;
  /** Compact mode */
  compact?: boolean;
}

/**
 * OrderStatusDisplay component
 */
export function OrderStatusDisplay({
  status,
  compact = false,
}: OrderStatusDisplayProps): JSX.Element {
  const currentIndex = getStatusIndex(status);
  const isCancelled = status === 'cancelled';
  const isCompleted = status === 'completed';

  // Cancelled status display
  if (isCancelled) {
    return (
      <div className="flex flex-col items-center py-8">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-red-100 text-red-500">
          <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </div>
        <p className="mt-4 text-xl font-bold text-red-500">
          {ORDER_STATUS_DISPLAY.cancelled}
        </p>
        <p className="mt-1 text-gray-500">此訂單已被取消</p>
      </div>
    );
  }

  // Completed status display
  if (isCompleted) {
    return (
      <div className="flex flex-col items-center py-8">
        <div
          className="flex h-16 w-16 items-center justify-center rounded-full text-white"
          style={{ backgroundColor: 'var(--color-primary, #22C55E)' }}
        >
          <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>
        <p
          className="mt-4 text-xl font-bold"
          style={{ color: 'var(--color-primary, #22C55E)' }}
        >
          {ORDER_STATUS_DISPLAY.completed}
        </p>
        <p className="mt-1 text-gray-500">感謝您的訂購</p>
      </div>
    );
  }

  // Compact mode - just badge
  if (compact) {
    const step = STATUS_STEPS.find((s) => s.status === status);
    return (
      <span
        className="inline-flex items-center gap-1 rounded-full px-3 py-1 text-sm font-medium text-white"
        style={{ backgroundColor: 'var(--color-primary, #FF6B6B)' }}
      >
        {step?.icon}
        {step?.label}
      </span>
    );
  }

  // Full progress display
  return (
    <div className="py-4">
      <div className="flex items-center justify-between">
        {STATUS_STEPS.map((step, index) => {
          const isActive = index <= currentIndex;
          const isCurrent = index === currentIndex;

          return (
            <React.Fragment key={step.status}>
              {/* Step */}
              <div className="flex flex-col items-center">
                <div
                  className={`flex h-12 w-12 items-center justify-center rounded-full transition-colors ${
                    isActive
                      ? 'text-white'
                      : 'border-2 border-gray-200 bg-white text-gray-400'
                  } ${isCurrent ? 'ring-4 ring-opacity-30' : ''}`}
                  style={
                    isActive
                      ? {
                          backgroundColor: 'var(--color-primary, #FF6B6B)',
                        }
                      : undefined
                  }
                >
                  {step.icon}
                </div>
                <p
                  className={`mt-2 text-sm font-medium ${
                    isActive ? '' : 'text-gray-400'
                  }`}
                  style={isActive ? { color: 'var(--color-primary, #FF6B6B)' } : undefined}
                >
                  {step.label}
                </p>
              </div>

              {/* Connector */}
              {index < STATUS_STEPS.length - 1 && (
                <div
                  className={`mx-2 h-1 flex-1 rounded ${
                    index < currentIndex ? '' : 'bg-gray-200'
                  }`}
                  style={
                    index < currentIndex
                      ? { backgroundColor: 'var(--color-primary, #FF6B6B)' }
                      : undefined
                  }
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}

export default OrderStatusDisplay;
