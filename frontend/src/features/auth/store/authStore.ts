/**
 * Auth Store using Zustand
 * Manages authentication state with persistence
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { User, UserRole } from '../../../shared/types/auth';
import { setAuthToken, clearAuthToken } from '../../../shared/utils/api';
import * as authApi from '../api/authApi';

/**
 * Auth state interface
 */
interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshAuth: () => Promise<boolean>;
  fetchCurrentUser: () => Promise<void>;
  clearError: () => void;

  // Permission helpers
  hasRole: (role: UserRole) => boolean;
  hasMinRole: (minRole: UserRole) => boolean;
  canAccessBrand: (brandId: string) => boolean;
  isAdmin: () => boolean;
  isSuperAdmin: () => boolean;
}

/**
 * Role hierarchy for permission checks
 */
const roleHierarchy: Record<UserRole, number> = {
  customer: 1,
  staff: 2,
  admin: 3,
  super_admin: 4,
};

/**
 * Auth store with persistence
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      /**
       * Login with email and password
       */
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });

        try {
          const response = await authApi.login({ email, password });

          // Set token in axios interceptor
          setAuthToken(response.accessToken);

          set({
            user: response.user,
            accessToken: response.accessToken,
            refreshToken: response.refreshToken,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: unknown) {
          const message =
            error instanceof Error ? error.message : 'Login failed';
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
            error: message,
          });
          throw error;
        }
      },

      /**
       * Logout and clear auth state
       */
      logout: () => {
        clearAuthToken();
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
        });
      },

      /**
       * Refresh authentication tokens
       */
      refreshAuth: async () => {
        const state = get();
        if (!state.refreshToken) {
          return false;
        }

        try {
          const response = await authApi.refreshToken({
            refreshToken: state.refreshToken,
          });

          setAuthToken(response.accessToken);

          set({
            accessToken: response.accessToken,
            refreshToken: response.refreshToken,
          });

          return true;
        } catch {
          // Refresh failed, logout
          get().logout();
          return false;
        }
      },

      /**
       * Fetch current user information
       */
      fetchCurrentUser: async () => {
        set({ isLoading: true, error: null });

        try {
          const user = await authApi.getCurrentUser();
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch {
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      },

      /**
       * Clear error state
       */
      clearError: () => {
        set({ error: null });
      },

      /**
       * Check if user has a specific role
       */
      hasRole: (role: UserRole) => {
        const { user } = get();
        return user?.role === role;
      },

      /**
       * Check if user has at least the minimum required role
       */
      hasMinRole: (minRole: UserRole) => {
        const { user } = get();
        if (!user) return false;
        return roleHierarchy[user.role] >= roleHierarchy[minRole];
      },

      /**
       * Check if user can access a specific brand
       */
      canAccessBrand: (brandId: string) => {
        const { user } = get();
        if (!user) return false;

        // Super admin can access all brands
        if (user.role === 'super_admin') return true;

        // Other users can only access their brand
        return user.brandId === brandId;
      },

      /**
       * Check if user is admin (or super_admin)
       */
      isAdmin: () => {
        const { user } = get();
        return user?.role === 'admin' || user?.role === 'super_admin';
      },

      /**
       * Check if user is super_admin
       */
      isSuperAdmin: () => {
        const { user } = get();
        return user?.role === 'super_admin';
      },
    }),
    {
      name: 'cat-canteen-auth',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrate: () => (state) => {
        // Set auth token on rehydrate
        if (state?.accessToken) {
          setAuthToken(state.accessToken);
        }
      },
    }
  )
);

export default useAuthStore;
