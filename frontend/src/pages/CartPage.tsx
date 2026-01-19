/**
 * CartPage
 * Page for viewing and managing shopping cart
 */

import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Cart } from '../features/cart/components/Cart';

/**
 * CartPage component
 */
export function CartPage(): JSX.Element {
  const { brandSlug } = useParams<{ brandSlug: string }>();
  const navigate = useNavigate();

  const handleCheckout = () => {
    navigate(`/${brandSlug}/checkout`);
  };

  const handleContinueShopping = () => {
    navigate(`/${brandSlug}/menu`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header
        className="sticky top-0 z-10 border-b border-gray-200 bg-white px-4 py-4"
        style={{ borderBottomColor: 'var(--color-primary, #FF6B6B)' }}
      >
        <div className="mx-auto flex max-w-lg items-center">
          <button
            onClick={handleContinueShopping}
            className="mr-4 text-gray-600 hover:text-gray-900"
          >
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
          </button>
          <h1 className="text-xl font-bold text-gray-900">購物車</h1>
        </div>
      </header>

      {/* Content */}
      <main className="mx-auto max-w-lg p-4">
        <Cart onCheckout={handleCheckout} onContinueShopping={handleContinueShopping} />
      </main>
    </div>
  );
}

export default CartPage;
