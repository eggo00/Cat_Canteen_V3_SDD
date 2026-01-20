/**
 * AI Recommendations hooks
 * React hooks for consuming AI recommendation API
 */

import { useQuery } from '@tanstack/react-query';
import {
  getRecommendations,
  getRecommendationsById,
  getDemandForecast,
  getUserPreferences,
  getAIStatus,
} from '../api/aiApi';
import {
  AIStatus,
  DemandForecastResponse,
  RecommendationResponse,
  UserPreference,
} from '../../../shared/types/ai';

/**
 * Hook for fetching AI recommendations by brand slug
 */
export function useRecommendations(
  brandSlug: string,
  options?: {
    userId?: string;
    limit?: number;
    enabled?: boolean;
  }
) {
  return useQuery<RecommendationResponse, Error>({
    queryKey: ['recommendations', brandSlug, options?.userId, options?.limit],
    queryFn: () =>
      getRecommendations(brandSlug, {
        userId: options?.userId,
        limit: options?.limit,
      }),
    enabled: options?.enabled !== false && !!brandSlug,
    staleTime: 1000 * 60 * 5, // 5 minutes
    gcTime: 1000 * 60 * 10, // 10 minutes (formerly cacheTime)
  });
}

/**
 * Hook for fetching AI recommendations by brand ID
 */
export function useRecommendationsById(
  brandId: string,
  options?: {
    userId?: string;
    limit?: number;
    enabled?: boolean;
  }
) {
  return useQuery<RecommendationResponse, Error>({
    queryKey: ['recommendations', 'id', brandId, options?.userId, options?.limit],
    queryFn: () =>
      getRecommendationsById(brandId, {
        userId: options?.userId,
        limit: options?.limit,
      }),
    enabled: options?.enabled !== false && !!brandId,
    staleTime: 1000 * 60 * 5, // 5 minutes
    gcTime: 1000 * 60 * 10, // 10 minutes
  });
}

/**
 * Hook for fetching demand forecast
 */
export function useDemandForecast(
  brandId: string,
  options?: {
    forecastDays?: number;
    enabled?: boolean;
  }
) {
  return useQuery<DemandForecastResponse, Error>({
    queryKey: ['demandForecast', brandId, options?.forecastDays],
    queryFn: () => getDemandForecast(brandId, options?.forecastDays),
    enabled: options?.enabled !== false && !!brandId,
    staleTime: 1000 * 60 * 30, // 30 minutes
    gcTime: 1000 * 60 * 60, // 1 hour
  });
}

/**
 * Hook for fetching user preferences
 */
export function useUserPreferences(
  brandId: string,
  options?: {
    userId?: string;
    enabled?: boolean;
  }
) {
  return useQuery<UserPreference, Error>({
    queryKey: ['userPreferences', brandId, options?.userId],
    queryFn: () => getUserPreferences(brandId, options?.userId),
    enabled: options?.enabled !== false && !!brandId,
    staleTime: 1000 * 60 * 15, // 15 minutes
    gcTime: 1000 * 60 * 30, // 30 minutes
  });
}

/**
 * Hook for fetching AI service status
 */
export function useAIStatus(enabled: boolean = true) {
  return useQuery<AIStatus, Error>({
    queryKey: ['aiStatus'],
    queryFn: getAIStatus,
    enabled,
    staleTime: 1000 * 60 * 5, // 5 minutes
    gcTime: 1000 * 60 * 10, // 10 minutes
  });
}

export default {
  useRecommendations,
  useRecommendationsById,
  useDemandForecast,
  useUserPreferences,
  useAIStatus,
};
