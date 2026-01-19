/**
 * Analytics types
 */

// ==================== Revenue Statistics ====================

export interface DailyRevenue {
  date: string;
  totalRevenue: number;
  orderCount: number;
  averageOrderValue: number;
}

export interface RevenueStats {
  brandId: string;
  startDate: string;
  endDate: string;
  totalRevenue: number;
  totalOrders: number;
  averageOrderValue: number;
  dailyRevenue: DailyRevenue[];
  revenueChangePercentage: number | null;
}

// ==================== Top Items ====================

export interface TopItem {
  menuItemId: string | null;
  menuItemName: string;
  quantitySold: number;
  totalRevenue: number;
  percentageOfTotal: number;
  rank: number;
}

export interface TopItemsResponse {
  brandId: string;
  startDate: string;
  endDate: string;
  items: TopItem[];
}

// ==================== Hourly Distribution ====================

export interface HourlyOrders {
  hour: number;
  orderCount: number;
  totalRevenue: number;
  averageOrderValue: number;
  percentageOfTotal: number;
}

export interface HourlyDistribution {
  brandId: string;
  startDate: string;
  endDate: string;
  hourlyData: HourlyOrders[];
  peakHour: number | null;
  peakHourOrders: number | null;
}

// ==================== Analytics Summary ====================

export interface AnalyticsSummary {
  brandId: string;
  period: string;
  totalRevenue: number;
  totalOrders: number;
  averageOrderValue: number;
  revenueChange: number | null;
  topItems: TopItem[];
  peakHour: number | null;
  peakHourOrders: number | null;
}

// ==================== Export ====================

export type ReportType = 'revenue' | 'top_items' | 'hourly' | 'summary';

export interface DateRange {
  startDate: string | null;
  endDate: string | null;
}
