/**
 * Auth hooks for authentication state and operations
 */

import { useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { UserRole } from '../../../shared/types/auth';

/**
 * Main auth hook providing authentication state and methods
 */
export function useAuth() {
  const {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    refreshAuth,
    fetchCurrentUser,
    clearError,
    hasRole,
    hasMinRole,
    canAccessBrand,
    isAdmin,
    isSuperAdmin,
  } = useAuthStore();

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    refreshAuth,
    fetchCurrentUser,
    clearError,
    hasRole,
    hasMinRole,
    canAccessBrand,
    isAdmin,
    isSuperAdmin,
  };
}

/**
 * Hook for requiring authentication
 * Redirects to login if not authenticated
 */
export function useRequireAuth(redirectTo = '/login') {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading, fetchCurrentUser, user } = useAuth();

  useEffect(() => {
    // Check auth state on mount
    if (!isLoading && !isAuthenticated) {
      navigate(redirectTo, { replace: true });
    }
  }, [isAuthenticated, isLoading, navigate, redirectTo]);

  // Verify token is still valid by fetching current user
  useEffect(() => {
    if (isAuthenticated && !user) {
      fetchCurrentUser().catch(() => {
        navigate(redirectTo, { replace: true });
      });
    }
  }, [isAuthenticated, user, fetchCurrentUser, navigate, redirectTo]);

  return { isAuthenticated, isLoading, user };
}

/**
 * Hook for requiring a specific role
 * Redirects to unauthorized page if role not met
 */
export function useRequireRole(
  requiredRole: UserRole,
  redirectTo = '/unauthorized'
) {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading, hasMinRole, user } = useAuth();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      if (!hasMinRole(requiredRole)) {
        navigate(redirectTo, { replace: true });
      }
    }
  }, [isAuthenticated, isLoading, hasMinRole, requiredRole, navigate, redirectTo]);

  return { isAuthenticated, isLoading, user, hasPermission: hasMinRole(requiredRole) };
}

/**
 * Hook for requiring brand access
 */
export function useRequireBrandAccess(brandId: string, redirectTo = '/unauthorized') {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading, canAccessBrand, user } = useAuth();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      if (!canAccessBrand(brandId)) {
        navigate(redirectTo, { replace: true });
      }
    }
  }, [isAuthenticated, isLoading, canAccessBrand, brandId, navigate, redirectTo]);

  return { isAuthenticated, isLoading, user, hasAccess: canAccessBrand(brandId) };
}

/**
 * Hook for login form handling
 */
export function useLogin() {
  const navigate = useNavigate();
  const { login, isLoading, error, clearError, user } = useAuth();

  const handleLogin = useCallback(
    async (email: string, password: string, redirectTo?: string) => {
      try {
        await login(email, password);
        // Redirect after successful login
        if (redirectTo) {
          navigate(redirectTo, { replace: true });
        } else {
          // Default redirect based on role
          navigate('/', { replace: true });
        }
      } catch {
        // Error is handled in the store
      }
    },
    [login, navigate]
  );

  return {
    login: handleLogin,
    isLoading,
    error,
    clearError,
    user,
  };
}

/**
 * Hook for logout handling
 */
export function useLogout() {
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleLogout = useCallback(
    (redirectTo = '/login') => {
      logout();
      navigate(redirectTo, { replace: true });
    },
    [logout, navigate]
  );

  return { logout: handleLogout };
}

export default useAuth;
