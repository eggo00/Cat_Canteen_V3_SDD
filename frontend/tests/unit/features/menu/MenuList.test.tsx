/**
 * Unit tests for MenuList component
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MenuList } from '../../../../src/features/menu/components/MenuList';
import { MenuItem as MenuItemType } from '../../../../src/shared/types/menu';

// Sample menu items for testing
const sampleMenuItems: MenuItemType[] = [
  {
    id: '1',
    categoryId: 'cat-1',
    name: '美式咖啡',
    description: '香醇美式咖啡',
    price: 100,
    displayOrder: 1,
    isAvailable: true,
  },
  {
    id: '2',
    categoryId: 'cat-1',
    name: '拿鐵咖啡',
    description: '濃郁拿鐵',
    price: 120,
    displayOrder: 2,
    isAvailable: true,
  },
  {
    id: '3',
    categoryId: 'cat-1',
    name: '卡布奇諾',
    description: '經典卡布奇諾',
    price: 130,
    displayOrder: 3,
    isAvailable: false,
  },
];

describe('MenuList', () => {
  it('should render menu items', () => {
    render(<MenuList items={sampleMenuItems} />);

    expect(screen.getByText('美式咖啡')).toBeInTheDocument();
    expect(screen.getByText('拿鐵咖啡')).toBeInTheDocument();
    expect(screen.getByText('卡布奇諾')).toBeInTheDocument();
  });

  it('should display loading skeleton when isLoading is true', () => {
    render(<MenuList items={[]} isLoading={true} />);

    expect(screen.getByTestId('menu-list-loading')).toBeInTheDocument();
  });

  it('should display empty state when no items', () => {
    render(<MenuList items={[]} />);

    expect(screen.getByTestId('menu-list-empty')).toBeInTheDocument();
    expect(screen.getByText('目前沒有菜單項目')).toBeInTheDocument();
  });

  it('should display custom empty message', () => {
    render(<MenuList items={[]} emptyMessage="沒有找到相關項目" />);

    expect(screen.getByText('沒有找到相關項目')).toBeInTheDocument();
  });

  it('should render price correctly', () => {
    render(<MenuList items={sampleMenuItems} />);

    expect(screen.getByText('NT$ 100')).toBeInTheDocument();
    expect(screen.getByText('NT$ 120')).toBeInTheDocument();
  });

  it('should show sold out indicator for unavailable items', () => {
    render(<MenuList items={sampleMenuItems} />);

    expect(screen.getByText('售完')).toBeInTheDocument();
  });

  it('should call onAddToCart when button is clicked', () => {
    const mockOnAddToCart = vi.fn();
    render(<MenuList items={sampleMenuItems} onAddToCart={mockOnAddToCart} />);

    const addToCartButtons = screen.getAllByText('加入購物車');
    fireEvent.click(addToCartButtons[0]);

    expect(mockOnAddToCart).toHaveBeenCalledWith(sampleMenuItems[0]);
  });

  it('should not show add to cart button for unavailable items', () => {
    const mockOnAddToCart = vi.fn();
    render(<MenuList items={sampleMenuItems} onAddToCart={mockOnAddToCart} />);

    // There should be 2 add to cart buttons (for available items only)
    const addToCartButtons = screen.getAllByText('加入購物車');
    expect(addToCartButtons).toHaveLength(2);
  });

  it('should render item descriptions', () => {
    render(<MenuList items={sampleMenuItems} />);

    expect(screen.getByText('香醇美式咖啡')).toBeInTheDocument();
    expect(screen.getByText('濃郁拿鐵')).toBeInTheDocument();
  });

  it('should render correct number of items', () => {
    render(<MenuList items={sampleMenuItems} />);

    const menuList = screen.getByTestId('menu-list');
    expect(menuList.children).toHaveLength(3);
  });

  it('should have correct data-testid for each menu item', () => {
    render(<MenuList items={sampleMenuItems} />);

    expect(screen.getByTestId('menu-item-1')).toBeInTheDocument();
    expect(screen.getByTestId('menu-item-2')).toBeInTheDocument();
    expect(screen.getByTestId('menu-item-3')).toBeInTheDocument();
  });
});
