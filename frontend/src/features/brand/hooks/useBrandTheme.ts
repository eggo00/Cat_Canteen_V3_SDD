/**
 * useBrandTheme hook
 * Fetches brand data and applies theme automatically
 */

import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getBrandBySlug } from '../api/brandApi';
import { useTheme } from '../../../shared/hooks/useTheme';
import { BrandResponse } from '../../../shared/types/brand';

/**
 * Query key for brand theme
 */
export const brandThemeQueryKey = (slug: string) => ['brand', 'theme', slug];

/**
 * Hook options
 */
interface UseBrandThemeOptions {
  /** Whether to auto-apply theme when brand data is loaded */
  autoApply?: boolean;
  /** Callback when brand is loaded */
  onLoad?: (brand: BrandResponse) => void;
  /** Callback on error */
  onError?: (error: Error) => void;
}

/**
 * Hook return type
 */
interface UseBrandThemeReturn {
  /** Brand data */
  brand: BrandResponse | undefined;
  /** Loading state */
  isLoading: boolean;
  /** Error state */
  error: Error | null;
  /** Refetch brand data */
  refetch: () => void;
  /** Apply brand theme manually */
  applyBrandTheme: () => void;
}

/**
 * Hook for fetching brand data and applying theme
 *
 * @param slug - Brand slug to fetch
 * @param options - Hook options
 *
 * @example
 * ```tsx
 * function BrandPage({ slug }: { slug: string }) {
 *   const { brand, isLoading, error } = useBrandTheme(slug, {
 *     autoApply: true,
 *   });
 *
 *   if (isLoading) return <div>Loading...</div>;
 *   if (error) return <div>Error: {error.message}</div>;
 *
 *   return <div>Welcome to {brand?.name}</div>;
 * }
 * ```
 */
export function useBrandTheme(
  slug: string | undefined,
  options: UseBrandThemeOptions = {}
): UseBrandThemeReturn {
  const { autoApply = true, onLoad, onError } = options;
  const { setTheme } = useTheme();

  // Fetch brand data
  const {
    data: brand,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: brandThemeQueryKey(slug || ''),
    queryFn: () => getBrandBySlug(slug!),
    enabled: !!slug,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });

  // Apply theme when brand data is loaded
  useEffect(() => {
    if (brand && autoApply) {
      setTheme(brand.themeConfig);
      onLoad?.(brand);
    }
  }, [brand, autoApply, setTheme, onLoad]);

  // Handle error
  useEffect(() => {
    if (error) {
      onError?.(error as Error);
    }
  }, [error, onError]);

  // Manual theme apply function
  const applyBrandTheme = () => {
    if (brand) {
      setTheme(brand.themeConfig);
    }
  };

  return {
    brand,
    isLoading,
    error: error as Error | null,
    refetch,
    applyBrandTheme,
  };
}

export default useBrandTheme;
