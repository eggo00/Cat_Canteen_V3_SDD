/**
 * AI API client
 * Handles all AI recommendation, prediction, and menu extraction API requests
 */

import { get } from '../../../shared/utils/api';
import apiClient from '../../../shared/utils/api';
import {
  AIStatus,
  DemandForecastResponse,
  DemandPrediction,
  RecommendationItem,
  RecommendationResponse,
  UserPreference,
} from '../../../shared/types/ai';
import {
  MenuDraft,
  MenuDraftItem,
  MenuDraftCategory,
  ExtractionStats,
  ExtractionQuota,
} from '../../../shared/types/menuExtract';

/**
 * Transform recommendation item from snake_case API response
 */
function transformRecommendationItem(
  data: Record<string, unknown>
): RecommendationItem {
  return {
    itemId: data.item_id as string,
    itemName: data.item_name as string,
    score: data.score as number,
    reason: data.reason as string,
    categoryName: data.category_name as string | null,
    price: data.price as number | null,
    imageUrl: data.image_url as string | null,
  };
}

/**
 * Transform recommendation response from snake_case API
 */
function transformRecommendationResponse(
  data: Record<string, unknown>
): RecommendationResponse {
  const recommendations =
    (data.recommendations as Record<string, unknown>[]) || [];
  return {
    brandId: data.brand_id as string,
    recommendations: recommendations.map(transformRecommendationItem),
    modelVersion: data.model_version as string,
    generatedAt: data.generated_at as string,
  };
}

/**
 * Transform demand prediction from snake_case API
 */
function transformDemandPrediction(
  data: Record<string, unknown>
): DemandPrediction {
  return {
    itemId: data.item_id as string,
    itemName: data.item_name as string,
    predictedQuantity: data.predicted_quantity as number,
    confidence: data.confidence as number,
    predictionDate: data.prediction_date as string,
  };
}

/**
 * Transform demand forecast response from snake_case API
 */
function transformDemandForecastResponse(
  data: Record<string, unknown>
): DemandForecastResponse {
  const predictions = (data.predictions as Record<string, unknown>[]) || [];
  return {
    brandId: data.brand_id as string,
    predictions: predictions.map(transformDemandPrediction),
    forecastPeriodDays: data.forecast_period_days as number,
    modelVersion: data.model_version as string,
    generatedAt: data.generated_at as string,
  };
}

/**
 * Transform user preference from snake_case API
 */
function transformUserPreference(
  data: Record<string, unknown>
): UserPreference {
  return {
    userId: data.user_id as string | null,
    preferredCategories: data.preferred_categories as string[],
    preferredPriceRange: data.preferred_price_range as [number, number] | null,
    dietaryPreferences: data.dietary_preferences as string[],
    orderFrequency: data.order_frequency as UserPreference['orderFrequency'],
  };
}

/**
 * Transform AI status from snake_case API
 */
function transformAIStatus(data: Record<string, unknown>): AIStatus {
  return {
    status: data.status as AIStatus['status'],
    modelVersion: data.model_version as string,
    featuresAvailable: data.features_available as string[],
    isStub: data.is_stub as boolean,
  };
}

/**
 * Get AI service status
 */
export async function getAIStatus(): Promise<AIStatus> {
  const response = await get<Record<string, unknown>>('/ai/status');
  return transformAIStatus(response);
}

/**
 * Get AI recommendations for a brand by slug
 */
export async function getRecommendations(
  brandSlug: string,
  options?: {
    userId?: string;
    limit?: number;
  }
): Promise<RecommendationResponse> {
  const params = new URLSearchParams();
  if (options?.userId) {
    params.append('user_id', options.userId);
  }
  if (options?.limit) {
    params.append('limit', String(options.limit));
  }

  const queryString = params.toString();
  const url = queryString
    ? `/ai/brands/slug/${brandSlug}/recommendations?${queryString}`
    : `/ai/brands/slug/${brandSlug}/recommendations`;

  const response = await get<Record<string, unknown>>(url);
  return transformRecommendationResponse(response);
}

/**
 * Get AI recommendations for a brand by ID
 */
export async function getRecommendationsById(
  brandId: string,
  options?: {
    userId?: string;
    limit?: number;
  }
): Promise<RecommendationResponse> {
  const params = new URLSearchParams();
  if (options?.userId) {
    params.append('user_id', options.userId);
  }
  if (options?.limit) {
    params.append('limit', String(options.limit));
  }

  const queryString = params.toString();
  const url = queryString
    ? `/ai/brands/${brandId}/recommendations?${queryString}`
    : `/ai/brands/${brandId}/recommendations`;

  const response = await get<Record<string, unknown>>(url);
  return transformRecommendationResponse(response);
}

/**
 * Get demand forecast for a brand
 */
export async function getDemandForecast(
  brandId: string,
  forecastDays: number = 7
): Promise<DemandForecastResponse> {
  const response = await get<Record<string, unknown>>(
    `/ai/brands/${brandId}/demand-forecast?forecast_days=${forecastDays}`
  );
  return transformDemandForecastResponse(response);
}

/**
 * Get user preferences analysis
 */
export async function getUserPreferences(
  brandId: string,
  userId?: string
): Promise<UserPreference> {
  const url = userId
    ? `/ai/brands/${brandId}/user-preferences?user_id=${userId}`
    : `/ai/brands/${brandId}/user-preferences`;

  const response = await get<Record<string, unknown>>(url);
  return transformUserPreference(response);
}

// ============================================================================
// Menu Extraction API functions
// ============================================================================

/**
 * Transform menu draft item from snake_case API response
 */
function transformMenuDraftItem(data: Record<string, unknown>): MenuDraftItem {
  return {
    tempId: data.temp_id as string,
    name: data.name as string,
    price: data.price as number,
    description: data.description as string | null,
    needsReview: data.needs_review as boolean,
    reviewReason: data.review_reason as string | null,
  };
}

/**
 * Transform menu draft category from snake_case API response
 */
function transformMenuDraftCategory(data: Record<string, unknown>): MenuDraftCategory {
  const items = (data.items as Record<string, unknown>[]) || [];
  return {
    tempId: data.temp_id as string,
    name: data.name as string,
    items: items.map(transformMenuDraftItem),
  };
}

/**
 * Transform extraction stats from snake_case API response
 */
function transformExtractionStats(data: Record<string, unknown>): ExtractionStats {
  return {
    totalItems: data.total_items as number,
    itemsNeedReview: data.items_need_review as number,
  };
}

/**
 * Transform menu draft from snake_case API response
 */
function transformMenuDraft(data: Record<string, unknown>): MenuDraft {
  const categories = (data.categories as Record<string, unknown>[]) || [];
  const stats = data.stats as Record<string, unknown>;
  return {
    source: data.source as MenuDraft['source'],
    brandId: data.brand_id as string,
    categories: categories.map(transformMenuDraftCategory),
    warnings: data.warnings as string[],
    stats: transformExtractionStats(stats),
    createdAt: data.created_at as string,
    originalImageUrl: data.original_image_url as string | null,
    rawText: data.raw_text as string | null,
    originalFileName: data.original_file_name as string | null,
  };
}

/**
 * Transform extraction quota from snake_case API response
 */
function transformExtractionQuota(data: Record<string, unknown>): ExtractionQuota {
  return {
    brandDailyRemaining: data.brand_daily_remaining as number,
    userHourlyRemaining: data.user_hourly_remaining as number,
    globalRpmRemaining: data.global_rpm_remaining as number,
  };
}

/**
 * Extract menu from image using AI
 */
export async function extractMenuFromImage(
  image: File,
  brandId: string,
  userId: string
): Promise<MenuDraft> {
  const formData = new FormData();
  formData.append('image', image);
  formData.append('brand_id', brandId);
  formData.append('user_id', userId);

  const response = await apiClient.post<Record<string, unknown>>('/ai/menu/extract', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return transformMenuDraft(response.data);
}

/**
 * Get AI extraction quota
 */
export async function getExtractionQuota(
  brandId: string,
  userId: string
): Promise<ExtractionQuota> {
  const response = await get<Record<string, unknown>>(
    `/ai/menu/extract/quota?brand_id=${brandId}&user_id=${userId}`
  );
  return transformExtractionQuota(response);
}

export default {
  getAIStatus,
  getRecommendations,
  getRecommendationsById,
  getDemandForecast,
  getUserPreferences,
  extractMenuFromImage,
  getExtractionQuota,
};
