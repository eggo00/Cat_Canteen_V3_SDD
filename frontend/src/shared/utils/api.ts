/**
 * API client using axios
 * Centralized HTTP client with auth, error handling, and interceptors
 */
import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// Determine API URL based on environment
const getApiBaseUrl = (): string => {
  // First check for explicit environment variable
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }

  // Auto-detect based on current hostname (for Zeabur deployment)
  const hostname = window.location.hostname;
  if (hostname.includes('zeabur.app')) {
    // Production: use Zeabur backend URL
    return 'https://cat-canteen-backend.zeabur.app/v1';
  }

  // Development: use localhost
  return 'http://localhost:8000/v1';
};

const API_BASE_URL = getApiBaseUrl();

/**
 * Create axios instance with default configuration
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor to add auth token
 */
apiClient.interceptors.request.use(
  (config) => {
    // Get token from localStorage
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor for error handling
 */
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError) => {
    // Handle specific error cases
    if (error.response) {
      const status = error.response.status;

      switch (status) {
        case 401:
          // Unauthorized - clear token and redirect to login
          localStorage.removeItem('authToken');
          window.location.href = '/login';
          break;
        case 403:
          // Forbidden - show access denied message
          console.error('Access denied:', error.response.data);
          break;
        case 404:
          // Not found
          console.error('Resource not found:', error.response.data);
          break;
        case 429:
          // Rate limit exceeded
          console.error('Rate limit exceeded. Please try again later.');
          break;
        case 500:
          // Internal server error
          console.error('Server error:', error.response.data);
          break;
        default:
          console.error('API error:', error.response.data);
      }
    } else if (error.request) {
      // Request was made but no response received
      console.error('Network error: No response from server');
    } else {
      // Something happened in setting up the request
      console.error('Request error:', error.message);
    }

    return Promise.reject(error);
  }
);

/**
 * Generic GET request
 */
export const get = async <T>(url: string, config?: AxiosRequestConfig): Promise<T> => {
  const response = await apiClient.get<T>(url, config);
  return response.data;
};

/**
 * Generic POST request
 */
export const post = async <T, D = any>(
  url: string,
  data?: D,
  config?: AxiosRequestConfig
): Promise<T> => {
  const response = await apiClient.post<T>(url, data, config);
  return response.data;
};

/**
 * Generic PUT request
 */
export const put = async <T, D = any>(
  url: string,
  data?: D,
  config?: AxiosRequestConfig
): Promise<T> => {
  const response = await apiClient.put<T>(url, data, config);
  return response.data;
};

/**
 * Generic PATCH request
 */
export const patch = async <T, D = any>(
  url: string,
  data?: D,
  config?: AxiosRequestConfig
): Promise<T> => {
  const response = await apiClient.patch<T>(url, data, config);
  return response.data;
};

/**
 * Generic DELETE request
 */
export const del = async <T>(url: string, config?: AxiosRequestConfig): Promise<T> => {
  const response = await apiClient.delete<T>(url, config);
  return response.data;
};

/**
 * Set auth token
 */
export const setAuthToken = (token: string | null): void => {
  if (token) {
    localStorage.setItem('authToken', token);
  } else {
    localStorage.removeItem('authToken');
  }
};

/**
 * Get auth token
 */
export const getAuthToken = (): string | null => {
  return localStorage.getItem('authToken');
};

/**
 * Clear auth token
 */
export const clearAuthToken = (): void => {
  localStorage.removeItem('authToken');
};

export default apiClient;
