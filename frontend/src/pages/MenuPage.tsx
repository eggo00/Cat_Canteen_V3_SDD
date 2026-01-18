/**
 * MenuPage component
 * Main menu page with brand theme and menu display
 */

import React, { useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { useBrandTheme } from '../features/brand/hooks/useBrandTheme';
import { useMenu } from '../features/menu/hooks/useMenu';
import { MenuList, CategoryFilter } from '../features/menu/components';
import { MenuItem as MenuItemType } from '../shared/types/menu';

/**
 * Search input component
 */
function SearchInput({
  value,
  onChange,
  placeholder = '搜尋菜單...',
}: {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}): JSX.Element {
  return (
    <div className="relative">
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full rounded-lg border border-gray-300 py-2 pl-10 pr-4 text-sm focus:border-transparent focus:outline-none focus:ring-2"
        style={{
          '--tw-ring-color': 'var(--color-primary, #FF6B6B)',
        } as React.CSSProperties}
        data-testid="menu-search"
      />
      <svg
        className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
        />
      </svg>
    </div>
  );
}

/**
 * Brand header component
 */
function BrandHeader({
  name,
  description,
  logoUrl,
}: {
  name: string;
  description?: string;
  logoUrl?: string;
}): JSX.Element {
  return (
    <header
      className="rounded-lg p-6 text-white"
      style={{ backgroundColor: 'var(--color-primary, #FF6B6B)' }}
    >
      <div className="flex items-center gap-4">
        {logoUrl && (
          <img
            src={logoUrl}
            alt={`${name} logo`}
            className="h-16 w-16 rounded-full bg-white object-cover p-1"
          />
        )}
        <div>
          <h1 className="text-2xl font-bold">{name}</h1>
          {description && <p className="mt-1 text-sm opacity-90">{description}</p>}
        </div>
      </div>
    </header>
  );
}

/**
 * Error display component
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
        <h2 className="mt-4 text-xl font-semibold text-gray-700">發生錯誤</h2>
        <p className="mt-2 text-gray-500">{message}</p>
      </div>
    </div>
  );
}

/**
 * Loading display component
 */
function LoadingDisplay(): JSX.Element {
  return (
    <div className="flex min-h-[50vh] items-center justify-center">
      <div className="text-center">
        <div
          className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-t-transparent"
          style={{ borderColor: 'var(--color-primary, #FF6B6B)', borderTopColor: 'transparent' }}
        />
        <p className="mt-4 text-gray-500">載入中...</p>
      </div>
    </div>
  );
}

/**
 * MenuPage component
 */
export function MenuPage(): JSX.Element {
  const { slug } = useParams<{ slug: string }>();

  // Fetch brand data and apply theme
  const { brand, isLoading: brandLoading, error: brandError } = useBrandTheme(slug);

  // Fetch menu data
  const {
    categories,
    filteredItems,
    isLoading: menuLoading,
    error: menuError,
    selectedCategoryId,
    searchTerm,
    setSelectedCategory,
    setSearchTerm,
  } = useMenu(brand?.id);

  // Handle add to cart (placeholder for now)
  const handleAddToCart = useCallback((item: MenuItemType) => {
    console.log('Add to cart:', item);
    // TODO: Implement cart functionality in Phase 4
  }, []);

  // Loading state
  if (brandLoading) {
    return <LoadingDisplay />;
  }

  // Error state
  if (brandError) {
    return <ErrorDisplay message={brandError.message || '無法載入品牌資料'} />;
  }

  if (!brand) {
    return <ErrorDisplay message="找不到此品牌" />;
  }

  return (
    <div
      className="min-h-screen"
      style={{
        backgroundColor: 'var(--color-background, #FFFFFF)',
        color: 'var(--color-text, #2C3E50)',
        fontFamily: 'var(--font-family, Inter, system-ui, sans-serif)',
      }}
    >
      <div className="mx-auto max-w-7xl px-4 py-6">
        {/* Brand header */}
        <BrandHeader
          name={brand.name}
          description={brand.description}
          logoUrl={brand.logoUrl}
        />

        {/* Search and filters */}
        <div className="mt-6 space-y-4">
          <SearchInput value={searchTerm} onChange={setSearchTerm} />

          <CategoryFilter
            categories={categories}
            selectedId={selectedCategoryId}
            onSelect={setSelectedCategory}
            isLoading={menuLoading}
          />
        </div>

        {/* Menu list */}
        <div className="mt-6">
          {menuError ? (
            <ErrorDisplay message={menuError.message || '無法載入菜單'} />
          ) : (
            <MenuList
              items={filteredItems}
              isLoading={menuLoading}
              onAddToCart={handleAddToCart}
              emptyMessage={
                searchTerm
                  ? `找不到「${searchTerm}」相關的項目`
                  : '目前沒有菜單項目'
              }
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default MenuPage;
