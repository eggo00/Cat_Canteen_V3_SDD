/**
 * Main App component with routing and providers
 */

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from './theme/ThemeProvider';
import { ErrorBoundary } from './shared/components';
import { MenuPage } from './pages/MenuPage';
import { CartPage } from './pages/CartPage';
import { CheckoutPage } from './pages/CheckoutPage';
import { OrderStatusPage } from './pages/OrderStatusPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import LoginPage from './pages/LoginPage';
import { AdminRoute } from './features/auth';

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 2, // 2 minutes
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
});

/**
 * Home page - redirects to a default brand or shows brand selection
 */
function HomePage(): JSX.Element {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">Cat Canteen</h1>
        <p className="mt-2 text-gray-600">可白牌化智慧餐飲訂單系統平台</p>
        <p className="mt-4 text-sm text-gray-500">
          請輸入品牌 slug 來訪問菜單，例如：
          <code className="ml-1 rounded bg-gray-100 px-2 py-1">/brand/your-brand-slug</code>
        </p>
      </div>
    </div>
  );
}

/**
 * 404 Not Found page
 */
function NotFoundPage(): JSX.Element {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-300">404</h1>
        <p className="mt-4 text-xl text-gray-600">找不到此頁面</p>
        <a
          href="/"
          className="mt-6 inline-block rounded-lg bg-blue-500 px-6 py-2 text-white hover:bg-blue-600"
        >
          返回首頁
        </a>
      </div>
    </div>
  );
}

/**
 * Unauthorized page
 */
function UnauthorizedPage(): JSX.Element {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-300">403</h1>
        <p className="mt-4 text-xl text-gray-600">沒有權限訪問此頁面</p>
        <a
          href="/"
          className="mt-6 inline-block rounded-lg bg-blue-500 px-6 py-2 text-white hover:bg-blue-600"
        >
          返回首頁
        </a>
      </div>
    </div>
  );
}

/**
 * Main App component
 */
function App(): JSX.Element {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <BrowserRouter>
            <Routes>
            {/* Home page */}
            <Route path="/" element={<HomePage />} />

            {/* Auth routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/unauthorized" element={<UnauthorizedPage />} />

            {/* Brand routes - with dynamic theme loading */}
            <Route path="/:brandSlug/menu" element={<MenuPage />} />
            <Route path="/:brandSlug/cart" element={<CartPage />} />
            <Route path="/:brandSlug/checkout" element={<CheckoutPage />} />
            <Route path="/:brandSlug/order/:orderNumber" element={<OrderStatusPage />} />

            {/* Admin routes - protected */}
            <Route
              path="/:brandSlug/analytics"
              element={
                <AdminRoute>
                  <AnalyticsPage />
                </AdminRoute>
              }
            />

            {/* Legacy route support - redirect old brand URL to menu */}
            <Route path="/brand/:slug" element={<Navigate to="/:slug/menu" replace />} />

            {/* 404 Not Found */}
            <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </BrowserRouter>
        </ThemeProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
