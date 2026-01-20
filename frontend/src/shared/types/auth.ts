/**
 * Authentication types
 * TypeScript interfaces for auth API
 */

/**
 * User role enum
 */
export type UserRole = 'customer' | 'staff' | 'admin' | 'super_admin';

/**
 * User data from API
 */
export interface User {
  id: string;
  email: string;
  name: string | null;
  role: UserRole;
  brandId: string | null;
  isActive: boolean;
}

/**
 * Login request data
 */
export interface LoginRequest {
  email: string;
  password: string;
}

/**
 * Login response from API
 */
export interface LoginResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
  tokenType: string;
}

/**
 * Token refresh request
 */
export interface RefreshTokenRequest {
  refreshToken: string;
}

/**
 * Token response from API
 */
export interface TokenResponse {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
}

/**
 * User creation request
 */
export interface CreateUserRequest {
  email: string;
  password: string;
  name?: string;
  role: UserRole;
  brandId?: string;
}

/**
 * Password change request
 */
export interface ChangePasswordRequest {
  currentPassword: string;
  newPassword: string;
}

/**
 * Auth state stored in localStorage
 */
export interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
}
