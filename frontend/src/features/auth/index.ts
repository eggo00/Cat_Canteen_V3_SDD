/**
 * Auth feature public exports
 */

// Store
export { useAuthStore } from './store/authStore';

// Hooks
export {
  useAuth,
  useRequireAuth,
  useRequireRole,
  useRequireBrandAccess,
  useLogin,
  useLogout,
} from './hooks/useAuth';

// Components
export {
  ProtectedRoute,
  AdminRoute,
  StaffRoute,
  SuperAdminRoute,
} from './components';

// API
export * as authApi from './api/authApi';
