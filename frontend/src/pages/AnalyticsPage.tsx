/**
 * AnalyticsPage
 * Dashboard for viewing analytics and reports
 */

import React from 'react';
import { useParams } from 'react-router-dom';
import { useBrandTheme } from '../features/brand/hooks/useBrandTheme';
import { useAnalytics } from '../features/analytics/hooks/useAnalytics';
import {
  StatCard,
  RevenueChart,
  TopItemsChart,
  HourlyChart,
  DateRangePicker,
} from '../features/analytics/components';
import { ReportType } from '../shared/types/analytics';

/**
 * Format currency in TWD
 */
function formatCurrency(value: number): string {
  return `NT$ ${value.toLocaleString()}`;
}

/**
 * Loading skeleton
 */
function LoadingSkeleton(): JSX.Element {
  return (
    <div className="animate-pulse space-y-6">
      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-32 rounded-lg bg-gray-200" />
        ))}
      </div>
      <div className="h-64 rounded-lg bg-gray-200" />
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div className="h-80 rounded-lg bg-gray-200" />
        <div className="h-80 rounded-lg bg-gray-200" />
      </div>
    </div>
  );
}

/**
 * Error display
 */
function ErrorDisplay({ message }: { message: string }): JSX.Element {
  return (
    <div className="flex min-h-[50vh] items-center justify-center">
      <div className="text-center">
        <svg
          className="mx-auto h-16 w-16 text-red-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
        <h2 className="mt-4 text-xl font-semibold text-gray-700">載入失敗</h2>
        <p className="mt-2 text-gray-500">{message}</p>
      </div>
    </div>
  );
}

/**
 * AnalyticsPage component
 */
export function AnalyticsPage(): JSX.Element {
  const { brandSlug } = useParams<{ brandSlug: string }>();

  // Fetch brand data and apply theme
  const { brand, isLoading: brandLoading, error: brandError } = useBrandTheme(brandSlug);

  // Fetch analytics data
  const {
    summary,
    summaryLoading,
    summaryError,
    revenue,
    revenueLoading,
    topItems,
    topItemsLoading,
    hourly,
    hourlyLoading,
    days,
    setDays,
    exportData,
    isExporting,
    refetch,
  } = useAnalytics(brand?.id, {
    defaultDays: 30,
    refreshInterval: 60000, // Refresh every minute
  });

  // Handle export
  const handleExport = async (type: ReportType) => {
    try {
      await exportData(type);
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  // Loading state
  if (brandLoading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="mx-auto max-w-7xl">
          <LoadingSkeleton />
        </div>
      </div>
    );
  }

  // Error state
  if (brandError) {
    return <ErrorDisplay message={brandError.message || '無法載入品牌資料'} />;
  }

  if (!brand) {
    return <ErrorDisplay message="找不到此品牌" />;
  }

  const isLoading = summaryLoading || revenueLoading || topItemsLoading || hourlyLoading;

  return (
    <div
      className="min-h-screen"
      style={{
        backgroundColor: 'var(--color-background, #F9FAFB)',
        fontFamily: 'var(--font-family, Inter, system-ui, sans-serif)',
      }}
    >
      {/* Header */}
      <header
        className="border-b bg-white px-6 py-4"
        style={{ borderBottomColor: 'var(--color-primary, #FF6B6B)' }}
      >
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">營運數據分析</h1>
            <p className="text-sm text-gray-500">{brand.name}</p>
          </div>

          <div className="flex items-center gap-4">
            <DateRangePicker days={days} onDaysChange={setDays} />

            {/* Refresh button */}
            <button
              onClick={refetch}
              className="rounded-lg border border-gray-200 p-2 text-gray-600 hover:bg-gray-50"
              title="重新整理"
            >
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
            </button>

            {/* Export dropdown */}
            <div className="relative group">
              <button
                className="flex items-center gap-2 rounded-lg px-4 py-2 text-white"
                style={{ backgroundColor: 'var(--color-primary, #FF6B6B)' }}
                disabled={isExporting}
              >
                {isExporting ? (
                  <svg className="h-5 w-5 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                    />
                  </svg>
                ) : (
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                )}
                匯出報表
              </button>

              {/* Dropdown menu */}
              <div className="absolute right-0 top-full z-10 hidden pt-2 group-hover:block">
                <div className="rounded-lg border border-gray-200 bg-white py-1 shadow-lg">
                  <button
                    onClick={() => handleExport('summary')}
                    className="w-full px-4 py-2 text-left text-sm hover:bg-gray-50"
                  >
                    綜合報表
                  </button>
                  <button
                    onClick={() => handleExport('revenue')}
                    className="w-full px-4 py-2 text-left text-sm hover:bg-gray-50"
                  >
                    營收報表
                  </button>
                  <button
                    onClick={() => handleExport('top_items')}
                    className="w-full px-4 py-2 text-left text-sm hover:bg-gray-50"
                  >
                    熱銷品項報表
                  </button>
                  <button
                    onClick={() => handleExport('hourly')}
                    className="w-full px-4 py-2 text-left text-sm hover:bg-gray-50"
                  >
                    時段分析報表
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="mx-auto max-w-7xl p-6">
        {isLoading && !summary ? (
          <LoadingSkeleton />
        ) : summaryError ? (
          <ErrorDisplay message={summaryError.message || '無法載入分析資料'} />
        ) : (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <StatCard
                title="總營收"
                value={formatCurrency(summary?.totalRevenue || 0)}
                change={summary?.revenueChange}
                icon={
                  <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                }
              />
              <StatCard
                title="總訂單數"
                value={(summary?.totalOrders || 0).toLocaleString()}
                subtitle={`${summary?.period || ''}`}
                icon={
                  <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
                    />
                  </svg>
                }
              />
              <StatCard
                title="平均客單價"
                value={formatCurrency(summary?.averageOrderValue || 0)}
                icon={
                  <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
                    />
                  </svg>
                }
              />
              <StatCard
                title="尖峰時段"
                value={
                  summary?.peakHour !== null
                    ? `${summary.peakHour.toString().padStart(2, '0')}:00`
                    : '—'
                }
                subtitle={
                  summary?.peakHourOrders
                    ? `${summary.peakHourOrders} 筆訂單`
                    : undefined
                }
                icon={
                  <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                }
              />
            </div>

            {/* Revenue Chart */}
            <RevenueChart data={revenue?.dailyRevenue || []} height={250} />

            {/* Two column layout for Top Items and Hourly */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              <TopItemsChart items={topItems?.items || []} />
              <HourlyChart
                data={hourly?.hourlyData || []}
                peakHour={hourly?.peakHour || null}
                height={250}
              />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default AnalyticsPage;
