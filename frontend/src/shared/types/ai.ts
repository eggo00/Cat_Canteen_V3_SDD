/**
 * AI feature types
 * TypeScript interfaces for AI recommendation API
 */

/**
 * A single recommended item from the AI service
 */
export interface RecommendationItem {
  itemId: string;
  itemName: string;
  score: number;  // 0.0 to 1.0
  reason: string;
  categoryName: string | null;
  price: number | null;
  imageUrl: string | null;
}

/**
 * AI recommendation response
 */
export interface RecommendationResponse {
  brandId: string;
  recommendations: RecommendationItem[];
  modelVersion: string;
  generatedAt: string;
}

/**
 * Demand prediction for a menu item
 */
export interface DemandPrediction {
  itemId: string;
  itemName: string;
  predictedQuantity: number;
  confidence: number;  // 0.0 to 1.0
  predictionDate: string;
}

/**
 * Demand forecast response
 */
export interface DemandForecastResponse {
  brandId: string;
  predictions: DemandPrediction[];
  forecastPeriodDays: number;
  modelVersion: string;
  generatedAt: string;
}

/**
 * User preference analysis result
 */
export interface UserPreference {
  userId: string | null;
  preferredCategories: string[];
  preferredPriceRange: [number, number] | null;
  dietaryPreferences: string[];
  orderFrequency: 'frequent' | 'regular' | 'occasional' | 'new';
}

/**
 * AI service status
 */
export interface AIStatus {
  status: 'ok' | 'degraded' | 'unavailable';
  modelVersion: string;
  featuresAvailable: string[];
  isStub: boolean;
}
