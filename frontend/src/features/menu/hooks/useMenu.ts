/**
 * useMenu hook
 * Fetches and manages menu data with filtering and search capabilities
 */

import { useMemo, useState, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getMenu, getCategories } from '../api/menuApi';
import { Category, MenuItem, MenuResponse } from '../../../shared/types/menu';

/**
 * Query keys for menu
 */
export const menuQueryKeys = {
  menu: (brandId: string) => ['menu', brandId],
  categories: (brandId: string) => ['menu', 'categories', brandId],
};

/**
 * Hook options
 */
interface UseMenuOptions {
  /** Initial category filter */
  initialCategoryId?: string;
  /** Initial search term */
  initialSearch?: string;
}

/**
 * Hook return type
 */
interface UseMenuReturn {
  /** Full menu data */
  menu: MenuResponse | undefined;
  /** All categories */
  categories: Category[];
  /** Filtered menu items based on current filters */
  filteredItems: MenuItem[];
  /** Loading state */
  isLoading: boolean;
  /** Error state */
  error: Error | null;
  /** Currently selected category ID */
  selectedCategoryId: string | null;
  /** Current search term */
  searchTerm: string;
  /** Set category filter */
  setSelectedCategory: (categoryId: string | null) => void;
  /** Set search term */
  setSearchTerm: (term: string) => void;
  /** Clear all filters */
  clearFilters: () => void;
  /** Refetch menu data */
  refetch: () => void;
  /** Get items for a specific category */
  getItemsByCategory: (categoryId: string) => MenuItem[];
}

/**
 * Hook for fetching and managing menu data
 *
 * @param brandId - Brand ID to fetch menu for
 * @param options - Hook options
 *
 * @example
 * ```tsx
 * function MenuPage({ brandId }: { brandId: string }) {
 *   const {
 *     categories,
 *     filteredItems,
 *     isLoading,
 *     selectedCategoryId,
 *     setSelectedCategory,
 *     searchTerm,
 *     setSearchTerm,
 *   } = useMenu(brandId);
 *
 *   return (
 *     <div>
 *       <CategoryFilter
 *         categories={categories}
 *         selectedId={selectedCategoryId}
 *         onSelect={setSelectedCategory}
 *       />
 *       <SearchInput value={searchTerm} onChange={setSearchTerm} />
 *       <MenuList items={filteredItems} />
 *     </div>
 *   );
 * }
 * ```
 */
export function useMenu(brandId: string | undefined, options: UseMenuOptions = {}): UseMenuReturn {
  const { initialCategoryId = null, initialSearch = '' } = options;

  // Filter state
  const [selectedCategoryId, setSelectedCategoryId] = useState<string | null>(initialCategoryId);
  const [searchTerm, setSearchTerm] = useState(initialSearch);

  // Fetch menu data
  const {
    data: menu,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: menuQueryKeys.menu(brandId || ''),
    queryFn: () => getMenu(brandId!),
    enabled: !!brandId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });

  // Extract categories from menu
  const categories = useMemo(() => {
    return menu?.categories || [];
  }, [menu]);

  // Get all menu items flattened
  const allItems = useMemo(() => {
    return categories.flatMap((category) => category.menuItems || []);
  }, [categories]);

  // Filter items based on current filters
  const filteredItems = useMemo(() => {
    let items = allItems;

    // Filter by category
    if (selectedCategoryId) {
      const category = categories.find((c) => c.id === selectedCategoryId);
      items = category?.menuItems || [];
    }

    // Filter by search term
    if (searchTerm.trim()) {
      const lowerSearch = searchTerm.toLowerCase().trim();
      items = items.filter(
        (item) =>
          item.name.toLowerCase().includes(lowerSearch) ||
          item.description?.toLowerCase().includes(lowerSearch)
      );
    }

    return items;
  }, [allItems, categories, selectedCategoryId, searchTerm]);

  // Set category filter
  const setSelectedCategory = useCallback((categoryId: string | null) => {
    setSelectedCategoryId(categoryId);
  }, []);

  // Set search term
  const handleSetSearchTerm = useCallback((term: string) => {
    setSearchTerm(term);
  }, []);

  // Clear all filters
  const clearFilters = useCallback(() => {
    setSelectedCategoryId(null);
    setSearchTerm('');
  }, []);

  // Get items for a specific category
  const getItemsByCategory = useCallback(
    (categoryId: string): MenuItem[] => {
      const category = categories.find((c) => c.id === categoryId);
      return category?.menuItems || [];
    },
    [categories]
  );

  return {
    menu,
    categories,
    filteredItems,
    isLoading,
    error: error as Error | null,
    selectedCategoryId,
    searchTerm,
    setSelectedCategory,
    setSearchTerm: handleSetSearchTerm,
    clearFilters,
    refetch,
    getItemsByCategory,
  };
}

export default useMenu;
