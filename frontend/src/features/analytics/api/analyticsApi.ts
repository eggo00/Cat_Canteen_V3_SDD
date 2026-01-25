/**
 * Analytics API client
 * Handles all analytics-related API requests
 */

import { get } from '../../../shared/utils/api';
import {
  RevenueStats,
  DailyRevenue,
  TopItemsResponse,
  TopItem,
  HourlyDistribution,
  HourlyOrders,
  AnalyticsSummary,
  ReportType,
} from '../../../shared/types/analytics';

/**
 * Transform daily revenue from snake_case API response
 */
function transformDailyRevenue(data: Record<string, unknown>): DailyRevenue {
  return {
    date: data.date as string,
    totalRevenue: data.total_revenue as number,
    orderCount: data.order_count as number,
    averageOrderValue: data.average_order_value as number,
  };
}

/**
 * Transform revenue stats from snake_case API response
 */
function transformRevenueStats(data: Record<string, unknown>): RevenueStats {
  const dailyRevenue = (data.daily_revenue as Record<string, unknown>[]) || [];
  return {
    brandId: data.brand_id as string,
    startDate: data.start_date as string,
    endDate: data.end_date as string,
    totalRevenue: data.total_revenue as number,
    totalOrders: data.total_orders as number,
    averageOrderValue: data.average_order_value as number,
    dailyRevenue: dailyRevenue.map(transformDailyRevenue),
    revenueChangePercentage: data.revenue_change_percentage as number | null,
  };
}

/**
 * Transform top item from snake_case API response
 */
function transformTopItem(data: Record<string, unknown>): TopItem {
  return {
    menuItemId: data.menu_item_id as string | null,
    menuItemName: data.menu_item_name as string,
    quantitySold: data.quantity_sold as number,
    totalRevenue: data.total_revenue as number,
    percentageOfTotal: data.percentage_of_total as number,
    rank: data.rank as number,
  };
}

/**
 * Transform top items response from snake_case API response
 */
function transformTopItemsResponse(data: Record<string, unknown>): TopItemsResponse {
  const items = (data.items as Record<string, unknown>[]) || [];
  return {
    brandId: data.brand_id as string,
    startDate: data.start_date as string,
    endDate: data.end_date as string,
    items: items.map(transformTopItem),
  };
}

/**
 * Transform hourly orders from snake_case API response
 */
function transformHourlyOrders(data: Record<string, unknown>): HourlyOrders {
  return {
    hour: data.hour as number,
    orderCount: data.order_count as number,
    totalRevenue: data.total_revenue as number,
    averageOrderValue: data.average_order_value as number,
    percentageOfTotal: data.percentage_of_total as number,
  };
}

/**
 * Transform hourly distribution from snake_case API response
 */
function transformHourlyDistribution(data: Record<string, unknown>): HourlyDistribution {
  const hourlyData = (data.hourly_data as Record<string, unknown>[]) || [];
  return {
    brandId: data.brand_id as string,
    startDate: data.start_date as string,
    endDate: data.end_date as string,
    hourlyData: hourlyData.map(transformHourlyOrders),
    peakHour: data.peak_hour as number | null,
    peakHourOrders: data.peak_hour_orders as number | null,
  };
}

/**
 * Transform analytics summary from snake_case API response
 */
function transformAnalyticsSummary(data: Record<string, unknown>): AnalyticsSummary {
  const topItems = (data.top_items as Record<string, unknown>[]) || [];
  return {
    brandId: data.brand_id as string,
    period: data.period as string,
    totalRevenue: data.total_revenue as number,
    totalOrders: data.total_orders as number,
    averageOrderValue: data.average_order_value as number,
    revenueChange: data.revenue_change as number | null,
    topItems: topItems.map(transformTopItem),
    peakHour: data.peak_hour as number | null,
    peakHourOrders: data.peak_hour_orders as number | null,
  };
}

/**
 * Build query string for date range
 */
function buildDateQuery(startDate?: string, endDate?: string): string {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  const query = params.toString();
  return query ? `?${query}` : '';
}

/**
 * Get revenue statistics for a brand
 */
export async function getRevenueStats(
  brandId: string,
  startDate?: string,
  endDate?: string
): Promise<RevenueStats> {
  const query = buildDateQuery(startDate, endDate);
  const response = await get<Record<string, unknown>>(
    `/analytics/brands/${brandId}/revenue${query}`
  );
  return transformRevenueStats(response);
}

/**
 * Get top selling items for a brand
 */
export async function getTopItems(
  brandId: string,
  options?: {
    startDate?: string;
    endDate?: string;
    limit?: number;
  }
): Promise<TopItemsResponse> {
  const params = new URLSearchParams();
  if (options?.startDate) params.append('start_date', options.startDate);
  if (options?.endDate) params.append('end_date', options.endDate);
  if (options?.limit) params.append('limit', String(options.limit));

  const query = params.toString();
  const url = `/analytics/brands/${brandId}/top-items${query ? `?${query}` : ''}`;

  const response = await get<Record<string, unknown>>(url);
  return transformTopItemsResponse(response);
}

/**
 * Get hourly order distribution for a brand
 */
export async function getOrdersByHour(
  brandId: string,
  startDate?: string,
  endDate?: string
): Promise<HourlyDistribution> {
  const query = buildDateQuery(startDate, endDate);
  const response = await get<Record<string, unknown>>(
    `/analytics/brands/${brandId}/orders-by-hour${query}`
  );
  return transformHourlyDistribution(response);
}

/**
 * Get analytics summary for a brand
 */
export async function getAnalyticsSummary(
  brandId: string,
  days: number = 30
): Promise<AnalyticsSummary> {
  const response = await get<Record<string, unknown>>(
    `/analytics/brands/${brandId}/summary?days=${days}`
  );
  return transformAnalyticsSummary(response);
}

/**
 * Export analytics report as CSV
 */
export async function exportReport(
  brandId: string,
  reportType: ReportType,
  startDate?: string,
  endDate?: string
): Promise<Blob> {
  const query = buildDateQuery(startDate, endDate);
  const url = `/analytics/brands/${brandId}/export/${reportType}${query}`;

  // Use fetch directly for blob response
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/v1';
  const response = await fetch(`${baseUrl}${url}`, {
    method: 'GET',
    headers: {
      'Accept': 'text/csv',
    },
  });

  if (!response.ok) {
    throw new Error(`Export failed: ${response.statusText}`);
  }

  return response.blob();
}

/**
 * Download exported report
 */
export function downloadReport(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}

export default {
  getRevenueStats,
  getTopItems,
  getOrdersByHour,
  getAnalyticsSummary,
  exportReport,
  downloadReport,
};
