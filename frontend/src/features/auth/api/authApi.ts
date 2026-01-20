/**
 * Auth API client
 * Handles all authentication-related API requests
 */

import { get, post, put, del } from '../../../shared/utils/api';
import {
  User,
  LoginRequest,
  LoginResponse,
  RefreshTokenRequest,
  TokenResponse,
  CreateUserRequest,
  ChangePasswordRequest,
} from '../../../shared/types/auth';

/**
 * Transform user from snake_case API response to camelCase
 */
function transformUser(data: Record<string, unknown>): User {
  return {
    id: data.id as string,
    email: data.email as string,
    name: data.name as string | null,
    role: data.role as User['role'],
    brandId: data.brand_id as string | null,
    isActive: data.is_active as boolean,
  };
}

/**
 * Transform login response from snake_case API response
 */
function transformLoginResponse(data: Record<string, unknown>): LoginResponse {
  return {
    user: transformUser(data.user as Record<string, unknown>),
    accessToken: data.access_token as string,
    refreshToken: data.refresh_token as string,
    tokenType: data.token_type as string,
  };
}

/**
 * Transform token response from snake_case API response
 */
function transformTokenResponse(data: Record<string, unknown>): TokenResponse {
  return {
    accessToken: data.access_token as string,
    refreshToken: data.refresh_token as string,
    tokenType: data.token_type as string,
  };
}

/**
 * Login with email and password
 */
export async function login(data: LoginRequest): Promise<LoginResponse> {
  const response = await post<Record<string, unknown>>('/auth/login', data);
  return transformLoginResponse(response);
}

/**
 * Refresh authentication tokens
 */
export async function refreshToken(
  data: RefreshTokenRequest
): Promise<TokenResponse> {
  const response = await post<Record<string, unknown>>('/auth/refresh', {
    refresh_token: data.refreshToken,
  });
  return transformTokenResponse(response);
}

/**
 * Get current user information
 */
export async function getCurrentUser(): Promise<User> {
  const response = await get<Record<string, unknown>>('/auth/me');
  return transformUser(response);
}

/**
 * Register a new user (admin only)
 */
export async function registerUser(data: CreateUserRequest): Promise<User> {
  const response = await post<Record<string, unknown>>('/auth/register', {
    email: data.email,
    password: data.password,
    name: data.name,
    role: data.role,
    brand_id: data.brandId,
  });
  return transformUser(response);
}

/**
 * Change password
 */
export async function changePassword(
  data: ChangePasswordRequest
): Promise<User> {
  const response = await put<Record<string, unknown>>('/auth/password', {
    current_password: data.currentPassword,
    new_password: data.newPassword,
  });
  return transformUser(response);
}

/**
 * Get all users (admin only)
 */
export async function getUsers(options?: {
  role?: string;
  brandId?: string;
  skip?: number;
  limit?: number;
}): Promise<User[]> {
  const params = new URLSearchParams();
  if (options?.role) {
    params.append('role', options.role);
  }
  if (options?.brandId) {
    params.append('brand_id', options.brandId);
  }
  if (options?.skip !== undefined) {
    params.append('skip', String(options.skip));
  }
  if (options?.limit !== undefined) {
    params.append('limit', String(options.limit));
  }

  const queryString = params.toString();
  const url = queryString ? `/auth/users?${queryString}` : '/auth/users';
  const response = await get<Record<string, unknown>[]>(url);
  return response.map(transformUser);
}

/**
 * Get user by ID (admin only)
 */
export async function getUserById(userId: string): Promise<User> {
  const response = await get<Record<string, unknown>>(`/auth/users/${userId}`);
  return transformUser(response);
}

/**
 * Delete user (admin only)
 */
export async function deleteUser(userId: string): Promise<void> {
  await del(`/auth/users/${userId}`);
}

export default {
  login,
  refreshToken,
  getCurrentUser,
  registerUser,
  changePassword,
  getUsers,
  getUserById,
  deleteUser,
};
