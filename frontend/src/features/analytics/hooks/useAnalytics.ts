/**
 * useAnalytics hook
 * Fetches and manages analytics data
 */

import { useState, useCallback } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  getRevenueStats,
  getTopItems,
  getOrdersByHour,
  getAnalyticsSummary,
  exportReport,
  downloadReport,
} from '../api/analyticsApi';
import {
  RevenueStats,
  TopItemsResponse,
  HourlyDistribution,
  AnalyticsSummary,
  ReportType,
  DateRange,
} from '../../../shared/types/analytics';

/**
 * Query keys for analytics
 */
export const analyticsQueryKeys = {
  revenue: (brandId: string, startDate?: string, endDate?: string) =>
    ['analytics', 'revenue', brandId, startDate, endDate],
  topItems: (brandId: string, startDate?: string, endDate?: string, limit?: number) =>
    ['analytics', 'topItems', brandId, startDate, endDate, limit],
  hourly: (brandId: string, startDate?: string, endDate?: string) =>
    ['analytics', 'hourly', brandId, startDate, endDate],
  summary: (brandId: string, days: number) =>
    ['analytics', 'summary', brandId, days],
};

/**
 * Hook options
 */
interface UseAnalyticsOptions {
  /** Default number of days for analysis */
  defaultDays?: number;
  /** Auto-refresh interval in ms */
  refreshInterval?: number;
}

/**
 * Hook return type
 */
interface UseAnalyticsReturn {
  // Summary data
  summary: AnalyticsSummary | undefined;
  summaryLoading: boolean;
  summaryError: Error | null;

  // Revenue data
  revenue: RevenueStats | undefined;
  revenueLoading: boolean;
  revenueError: Error | null;

  // Top items data
  topItems: TopItemsResponse | undefined;
  topItemsLoading: boolean;
  topItemsError: Error | null;

  // Hourly data
  hourly: HourlyDistribution | undefined;
  hourlyLoading: boolean;
  hourlyError: Error | null;

  // Date range
  dateRange: DateRange;
  setDateRange: (range: DateRange) => void;
  days: number;
  setDays: (days: number) => void;

  // Export
  exportData: (type: ReportType, filename?: string) => Promise<void>;
  isExporting: boolean;

  // Refresh
  refetch: () => void;
}

/**
 * Helper to format date as YYYY-MM-DD
 */
function formatDate(date: Date): string {
  return date.toISOString().split('T')[0];
}

/**
 * Helper to get date range from days
 */
function getDateRangeFromDays(days: number): DateRange {
  const endDate = new Date();
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);

  return {
    startDate: formatDate(startDate),
    endDate: formatDate(endDate),
  };
}

/**
 * Hook for fetching and managing analytics data
 *
 * @param brandId - Brand ID to fetch analytics for
 * @param options - Hook options
 */
export function useAnalytics(
  brandId: string | undefined,
  options: UseAnalyticsOptions = {}
): UseAnalyticsReturn {
  const { defaultDays = 30, refreshInterval } = options;

  // State
  const [days, setDays] = useState(defaultDays);
  const [dateRange, setDateRangeState] = useState<DateRange>(() =>
    getDateRangeFromDays(defaultDays)
  );

  // Update date range when days changes
  const setDaysWithRange = useCallback((newDays: number) => {
    setDays(newDays);
    setDateRangeState(getDateRangeFromDays(newDays));
  }, []);

  const setDateRange = useCallback((range: DateRange) => {
    setDateRangeState(range);
  }, []);

  // Summary query
  const {
    data: summary,
    isLoading: summaryLoading,
    error: summaryError,
    refetch: refetchSummary,
  } = useQuery({
    queryKey: analyticsQueryKeys.summary(brandId || '', days),
    queryFn: () => getAnalyticsSummary(brandId!, days),
    enabled: !!brandId,
    staleTime: 60000, // 1 minute
    refetchInterval: refreshInterval,
  });

  // Revenue query
  const {
    data: revenue,
    isLoading: revenueLoading,
    error: revenueError,
    refetch: refetchRevenue,
  } = useQuery({
    queryKey: analyticsQueryKeys.revenue(
      brandId || '',
      dateRange.startDate || undefined,
      dateRange.endDate || undefined
    ),
    queryFn: () =>
      getRevenueStats(
        brandId!,
        dateRange.startDate || undefined,
        dateRange.endDate || undefined
      ),
    enabled: !!brandId,
    staleTime: 60000,
    refetchInterval: refreshInterval,
  });

  // Top items query
  const {
    data: topItems,
    isLoading: topItemsLoading,
    error: topItemsError,
    refetch: refetchTopItems,
  } = useQuery({
    queryKey: analyticsQueryKeys.topItems(
      brandId || '',
      dateRange.startDate || undefined,
      dateRange.endDate || undefined,
      10
    ),
    queryFn: () =>
      getTopItems(brandId!, {
        startDate: dateRange.startDate || undefined,
        endDate: dateRange.endDate || undefined,
        limit: 10,
      }),
    enabled: !!brandId,
    staleTime: 60000,
    refetchInterval: refreshInterval,
  });

  // Hourly query
  const {
    data: hourly,
    isLoading: hourlyLoading,
    error: hourlyError,
    refetch: refetchHourly,
  } = useQuery({
    queryKey: analyticsQueryKeys.hourly(
      brandId || '',
      dateRange.startDate || undefined,
      dateRange.endDate || undefined
    ),
    queryFn: () =>
      getOrdersByHour(
        brandId!,
        dateRange.startDate || undefined,
        dateRange.endDate || undefined
      ),
    enabled: !!brandId,
    staleTime: 60000,
    refetchInterval: refreshInterval,
  });

  // Export mutation
  const exportMutation = useMutation({
    mutationFn: async ({
      type,
      filename,
    }: {
      type: ReportType;
      filename?: string;
    }) => {
      const blob = await exportReport(
        brandId!,
        type,
        dateRange.startDate || undefined,
        dateRange.endDate || undefined
      );
      const defaultFilename = `${type}_${dateRange.startDate || 'all'}_${dateRange.endDate || 'now'}.csv`;
      downloadReport(blob, filename || defaultFilename);
    },
  });

  // Refetch all data
  const refetch = useCallback(() => {
    refetchSummary();
    refetchRevenue();
    refetchTopItems();
    refetchHourly();
  }, [refetchSummary, refetchRevenue, refetchTopItems, refetchHourly]);

  // Export helper
  const exportData = useCallback(
    async (type: ReportType, filename?: string) => {
      await exportMutation.mutateAsync({ type, filename });
    },
    [exportMutation]
  );

  return {
    // Summary
    summary,
    summaryLoading,
    summaryError: summaryError as Error | null,

    // Revenue
    revenue,
    revenueLoading,
    revenueError: revenueError as Error | null,

    // Top items
    topItems,
    topItemsLoading,
    topItemsError: topItemsError as Error | null,

    // Hourly
    hourly,
    hourlyLoading,
    hourlyError: hourlyError as Error | null,

    // Date range
    dateRange,
    setDateRange,
    days,
    setDays: setDaysWithRange,

    // Export
    exportData,
    isExporting: exportMutation.isPending,

    // Refresh
    refetch,
  };
}

export default useAnalytics;
