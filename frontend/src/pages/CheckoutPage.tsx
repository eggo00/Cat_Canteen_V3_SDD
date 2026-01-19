/**
 * CheckoutPage
 * Page for completing order checkout
 */

import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useCart } from '../features/cart/hooks/useCart';
import { useCreateOrder } from '../features/order/hooks/useCreateOrder';
import { CheckoutForm, CustomerFormData } from '../features/order/components/CheckoutForm';
import { OrderSummary } from '../features/order/components/OrderSummary';

/**
 * CheckoutPage component
 */
export function CheckoutPage(): JSX.Element {
  const { brandSlug } = useParams<{ brandSlug: string }>();
  const navigate = useNavigate();
  const { items, subtotal, isEmpty, getItemSubtotal, formatPrice } = useCart();
  const { createOrder, isLoading, error } = useCreateOrder();

  // Redirect if cart is empty
  React.useEffect(() => {
    if (isEmpty) {
      navigate(`/${brandSlug}/menu`, { replace: true });
    }
  }, [isEmpty, brandSlug, navigate]);

  const handleSubmit = async (customerInfo: CustomerFormData) => {
    try {
      const order = await createOrder(customerInfo);
      // Navigate to order confirmation
      navigate(`/${brandSlug}/order/${order.orderNumber}`);
    } catch (err) {
      // Error is handled by the hook
      console.error('Order creation failed:', err);
    }
  };

  const handleCancel = () => {
    navigate(`/${brandSlug}/menu`);
  };

  if (isEmpty) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <p className="text-gray-500">購物車是空的，正在返回菜單...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header
        className="sticky top-0 z-10 border-b border-gray-200 bg-white px-4 py-4"
        style={{ borderBottomColor: 'var(--color-primary, #FF6B6B)' }}
      >
        <div className="mx-auto max-w-lg">
          <h1 className="text-xl font-bold text-gray-900">結帳</h1>
        </div>
      </header>

      {/* Content */}
      <main className="mx-auto max-w-lg p-4">
        <div className="space-y-6">
          {/* Order Summary */}
          <OrderSummary
            items={items}
            subtotal={subtotal}
            getItemSubtotal={getItemSubtotal}
            formatPrice={formatPrice}
          />

          {/* Checkout Form */}
          <div className="rounded-lg border border-gray-200 bg-white p-4">
            <h3 className="mb-4 text-lg font-bold text-gray-900">顧客資訊</h3>
            <CheckoutForm
              onSubmit={handleSubmit}
              isLoading={isLoading}
              error={error?.message}
              onCancel={handleCancel}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

export default CheckoutPage;
