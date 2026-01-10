/**
 * Order-related TypeScript types
 */

export type OrderStatus = 'pending' | 'preparing' | 'completed' | 'cancelled';

export interface OrderCustomization {
  optionType: string;
  name: string;
  priceAdjustment: number;
}

export interface OrderItem {
  id: string;
  orderId: string;
  menuItemId?: string;
  menuItemName: string;
  unitPrice: number;
  quantity: number;
  customizations?: OrderCustomization[];
  subtotal: number;
}

export interface Order {
  id: string;
  brandId: string;
  orderNumber: string;
  customerName: string;
  customerPhone: string;
  customerEmail?: string;
  status: OrderStatus;
  totalAmount: number;
  notes?: string;
  orderItems: OrderItem[];
  createdAt: string;
  updatedAt: string;
}

export interface CreateOrderItemRequest {
  menuItemId: string;
  quantity: number;
  customizations?: {
    optionType: string;
    name: string;
    priceAdjustment: number;
  }[];
}

export interface CreateOrderRequest {
  customerName: string;
  customerPhone: string;
  customerEmail?: string;
  notes?: string;
  items: CreateOrderItemRequest[];
}

export interface OrderResponse {
  id: string;
  orderNumber: string;
  customerName: string;
  status: OrderStatus;
  totalAmount: number;
  orderItems: OrderItem[];
  createdAt: string;
}

export interface UpdateOrderStatusRequest {
  status: OrderStatus;
}
