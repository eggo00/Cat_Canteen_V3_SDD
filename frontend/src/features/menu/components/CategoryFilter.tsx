/**
 * CategoryFilter component
 * Horizontal scrollable category filter tabs
 */

import { Category } from '../../../shared/types/menu';

/**
 * CategoryFilter props
 */
interface CategoryFilterProps {
  /** Categories to display */
  categories: Category[];
  /** Currently selected category ID */
  selectedId: string | null;
  /** Selection handler */
  onSelect: (categoryId: string | null) => void;
  /** Show "All" option */
  showAll?: boolean;
  /** "All" label text */
  allLabel?: string;
  /** Loading state */
  isLoading?: boolean;
}

/**
 * Loading skeleton for category filter
 */
function CategoryFilterSkeleton(): JSX.Element {
  return (
    <div className="flex gap-2 overflow-x-auto pb-2" data-testid="category-filter-loading">
      {Array.from({ length: 5 }).map((_, index) => (
        <div
          key={index}
          className="h-10 w-20 shrink-0 animate-pulse rounded-full bg-gray-200"
        />
      ))}
    </div>
  );
}

/**
 * CategoryFilter component
 *
 * @example
 * ```tsx
 * function MenuPage() {
 *   const { categories, selectedCategoryId, setSelectedCategory } = useMenu(brandId);
 *
 *   return (
 *     <CategoryFilter
 *       categories={categories}
 *       selectedId={selectedCategoryId}
 *       onSelect={setSelectedCategory}
 *     />
 *   );
 * }
 * ```
 */
export function CategoryFilter({
  categories,
  selectedId,
  onSelect,
  showAll = true,
  allLabel = '全部',
  isLoading = false,
}: CategoryFilterProps): JSX.Element {
  if (isLoading) {
    return <CategoryFilterSkeleton />;
  }

  if (categories.length === 0) {
    return <></>;
  }

  return (
    <div
      className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide"
      data-testid="category-filter"
      role="tablist"
      aria-label="菜單分類"
    >
      {/* All option */}
      {showAll && (
        <button
          onClick={() => onSelect(null)}
          className={`shrink-0 rounded-full px-4 py-2 text-sm font-medium transition-all ${
            selectedId === null
              ? 'text-white shadow-md'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
          style={
            selectedId === null
              ? { backgroundColor: 'var(--color-primary, #FF6B6B)' }
              : undefined
          }
          role="tab"
          aria-selected={selectedId === null}
          data-testid="category-filter-all"
        >
          {allLabel}
        </button>
      )}

      {/* Category tabs */}
      {categories.map((category) => {
        const isSelected = selectedId === category.id;
        return (
          <button
            key={category.id}
            onClick={() => onSelect(category.id)}
            className={`shrink-0 rounded-full px-4 py-2 text-sm font-medium transition-all ${
              isSelected
                ? 'text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
            style={
              isSelected
                ? { backgroundColor: 'var(--color-primary, #FF6B6B)' }
                : undefined
            }
            role="tab"
            aria-selected={isSelected}
            data-testid={`category-filter-${category.id}`}
          >
            {category.name}
            {category.menuItems && (
              <span className="ml-1 opacity-70">({category.menuItems.length})</span>
            )}
          </button>
        );
      })}
    </div>
  );
}

export default CategoryFilter;
