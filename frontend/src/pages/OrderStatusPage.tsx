/**
 * OrderStatusPage
 * Page for viewing order status and details
 */

import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useOrderStatus } from '../features/order/hooks/useOrderStatus';
import { OrderStatusDisplay } from '../features/order/components/OrderStatusDisplay';
import { ORDER_STATUS_DISPLAY } from '../shared/types/order';

/**
 * Format date for display
 */
function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Format price in TWD
 */
function formatPrice(price: number): string {
  return `NT$ ${price.toFixed(0)}`;
}

/**
 * OrderStatusPage component
 */
export function OrderStatusPage(): JSX.Element {
  const { brandSlug, orderNumber } = useParams<{
    brandSlug: string;
    orderNumber: string;
  }>();
  const navigate = useNavigate();
  const { order, isLoading, error, status, isActive } = useOrderStatus(orderNumber);

  const handleBackToMenu = () => {
    navigate(`/${brandSlug}/menu`);
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div
            className="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-4 border-t-transparent"
            style={{ borderColor: 'var(--color-primary, #FF6B6B)', borderTopColor: 'transparent' }}
          />
          <p className="text-gray-500">載入訂單資訊...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !order) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="mb-4 flex h-16 w-16 mx-auto items-center justify-center rounded-full bg-red-100">
            <svg
              className="h-8 w-8 text-red-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-gray-900">找不到訂單</h2>
          <p className="mt-2 text-gray-500">
            {error?.message || '無法載入訂單資訊'}
          </p>
          <button
            onClick={handleBackToMenu}
            className="mt-4 rounded-full px-6 py-2 text-white"
            style={{ backgroundColor: 'var(--color-primary, #FF6B6B)' }}
          >
            返回菜單
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header
        className="sticky top-0 z-10 border-b bg-white px-4 py-4"
        style={{ borderBottomColor: 'var(--color-primary, #FF6B6B)' }}
      >
        <div className="mx-auto max-w-lg">
          <h1 className="text-xl font-bold text-gray-900">訂單狀態</h1>
        </div>
      </header>

      {/* Content */}
      <main className="mx-auto max-w-lg p-4">
        <div className="space-y-4">
          {/* Order Number Card */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 text-center">
            <p className="text-sm text-gray-500">訂單編號</p>
            <p
              className="mt-1 text-3xl font-bold"
              style={{ color: 'var(--color-primary, #FF6B6B)' }}
            >
              {order.orderNumber}
            </p>
            <p className="mt-2 text-sm text-gray-500">
              {formatDate(order.createdAt)}
            </p>
          </div>

          {/* Status Display */}
          <div className="rounded-lg border border-gray-200 bg-white p-4">
            <OrderStatusDisplay status={status!} />
            {isActive && (
              <p className="mt-4 text-center text-sm text-gray-500">
                頁面會自動更新訂單狀態
              </p>
            )}
          </div>

          {/* Customer Info */}
          <div className="rounded-lg border border-gray-200 bg-white p-4">
            <h3 className="mb-3 font-bold text-gray-900">顧客資訊</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">姓名</span>
                <span className="font-medium text-gray-900">{order.customerName}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">電話</span>
                <span className="font-medium text-gray-900">{order.customerPhone}</span>
              </div>
              {order.customerEmail && (
                <div className="flex justify-between">
                  <span className="text-gray-500">電子郵件</span>
                  <span className="font-medium text-gray-900">{order.customerEmail}</span>
                </div>
              )}
              {order.notes && (
                <div className="pt-2 border-t border-gray-100">
                  <span className="text-gray-500">備註</span>
                  <p className="mt-1 text-gray-700">{order.notes}</p>
                </div>
              )}
            </div>
          </div>

          {/* Order Items */}
          <div className="rounded-lg border border-gray-200 bg-white p-4">
            <h3 className="mb-3 font-bold text-gray-900">訂單明細</h3>
            <div className="space-y-3">
              {order.orderItems.map((item) => (
                <div key={item.id} className="flex justify-between">
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">
                      {item.menuItemName} x {item.quantity}
                    </p>
                    {item.customizations && item.customizations.length > 0 && (
                      <p className="text-sm text-gray-500">
                        {item.customizations.map((c) => c.name).join('、')}
                      </p>
                    )}
                  </div>
                  <span className="font-medium text-gray-700">
                    {formatPrice(item.subtotal)}
                  </span>
                </div>
              ))}
            </div>

            {/* Total */}
            <div className="mt-4 border-t border-gray-200 pt-4">
              <div className="flex items-center justify-between">
                <span className="text-lg font-bold text-gray-900">總計</span>
                <span
                  className="text-xl font-bold"
                  style={{ color: 'var(--color-primary, #FF6B6B)' }}
                >
                  {formatPrice(order.totalAmount)}
                </span>
              </div>
            </div>
          </div>

          {/* Actions */}
          <button
            onClick={handleBackToMenu}
            className="w-full rounded-lg border border-gray-300 py-3 font-semibold text-gray-700 transition-colors hover:bg-gray-50"
          >
            返回菜單
          </button>
        </div>
      </main>
    </div>
  );
}

export default OrderStatusPage;
