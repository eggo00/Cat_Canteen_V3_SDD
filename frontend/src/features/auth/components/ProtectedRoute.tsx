/**
 * Protected Route Component
 * Wraps routes that require authentication or specific roles
 */

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { UserRole } from '../../../shared/types/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: UserRole;
  brandId?: string;
  redirectTo?: string;
}

/**
 * Loading spinner component
 */
function LoadingSpinner() {
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        flexDirection: 'column',
        gap: '1rem',
      }}
    >
      <div
        style={{
          width: '40px',
          height: '40px',
          border: '4px solid #f3f3f3',
          borderTop: '4px solid var(--color-primary, #3498db)',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
        }}
      />
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
      <span>Loading...</span>
    </div>
  );
}

/**
 * Protected route wrapper
 * Handles authentication and authorization checks
 */
export function ProtectedRoute({
  children,
  requiredRole,
  brandId,
  redirectTo = '/login',
}: ProtectedRouteProps) {
  const location = useLocation();
  const { isAuthenticated, isLoading, hasMinRole, canAccessBrand, user } =
    useAuth();

  // Show loading while checking auth state
  if (isLoading) {
    return <LoadingSpinner />;
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated || !user) {
    return (
      <Navigate
        to={redirectTo}
        state={{ from: location.pathname }}
        replace
      />
    );
  }

  // Check role requirement
  if (requiredRole && !hasMinRole(requiredRole)) {
    return (
      <Navigate
        to="/unauthorized"
        state={{ from: location.pathname }}
        replace
      />
    );
  }

  // Check brand access
  if (brandId && !canAccessBrand(brandId)) {
    return (
      <Navigate
        to="/unauthorized"
        state={{ from: location.pathname }}
        replace
      />
    );
  }

  return <>{children}</>;
}

/**
 * Admin-only route wrapper
 */
export function AdminRoute({
  children,
  redirectTo = '/login',
}: Omit<ProtectedRouteProps, 'requiredRole'>) {
  return (
    <ProtectedRoute requiredRole="admin" redirectTo={redirectTo}>
      {children}
    </ProtectedRoute>
  );
}

/**
 * Staff-only route wrapper
 */
export function StaffRoute({
  children,
  redirectTo = '/login',
}: Omit<ProtectedRouteProps, 'requiredRole'>) {
  return (
    <ProtectedRoute requiredRole="staff" redirectTo={redirectTo}>
      {children}
    </ProtectedRoute>
  );
}

/**
 * Super admin-only route wrapper
 */
export function SuperAdminRoute({
  children,
  redirectTo = '/login',
}: Omit<ProtectedRouteProps, 'requiredRole'>) {
  return (
    <ProtectedRoute requiredRole="super_admin" redirectTo={redirectTo}>
      {children}
    </ProtectedRoute>
  );
}

export default ProtectedRoute;
