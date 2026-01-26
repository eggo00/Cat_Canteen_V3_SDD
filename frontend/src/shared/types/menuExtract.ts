/**
 * Menu extraction types for AI-powered menu recognition
 */

export interface ExtractedMenuItem {
  name: string;
  price: number;
  description: string | null;
}

export interface ExtractedCategory {
  name: string;
  items: ExtractedMenuItem[];
}

export interface ExtractionStats {
  totalItems: number;
  itemsNeedReview: number;
}

export interface MenuExtractResponse {
  success: boolean;
  categories: ExtractedCategory[];
  rawText: string | null;
  errorMessage: string | null;
  warnings: string[];
  stats: ExtractionStats;
}

export interface MenuDraftItem {
  tempId: string;
  name: string;
  price: number;
  description: string | null;
  needsReview: boolean;
  reviewReason: string | null;
}

export interface MenuDraftCategory {
  tempId: string;
  name: string;
  items: MenuDraftItem[];
}

export interface MenuDraft {
  source: 'ai_extract' | 'json_import' | 'excel_import' | 'manual';
  brandId: string;
  categories: MenuDraftCategory[];
  warnings: string[];
  stats: ExtractionStats;
  createdAt: string;
  originalImageUrl: string | null;
  rawText: string | null;
  originalFileName: string | null;
}

export interface ExtractionQuota {
  brandDailyRemaining: number;
  userHourlyRemaining: number;
  globalRpmRemaining: number;
}
