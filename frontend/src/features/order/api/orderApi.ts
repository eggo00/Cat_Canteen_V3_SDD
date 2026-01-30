/**
 * Order API client
 * Handles all order-related API requests
 */

import { get, post, patch } from '../../../shared/utils/api';
import {
  Order,
  OrderResponse,
  CreateOrderRequest,
  UpdateOrderStatusRequest,
  OrderStatus,
  OrderItem,
} from '../../../shared/types/order';

/**
 * Transform order item from snake_case API response
 */
function transformOrderItem(data: Record<string, unknown>): OrderItem {
  const customizations = (data.customizations as Record<string, unknown>[] | undefined) || [];
  return {
    id: data.id as string,
    orderId: data.order_id as string,
    menuItemId: data.menu_item_id as string | undefined,
    menuItemName: data.menu_item_name as string,
    unitPrice: data.unit_price as number,
    quantity: data.quantity as number,
    customizations: customizations.map((c) => ({
      optionType: c.option_type as string,
      name: c.name as string,
      priceAdjustment: c.price_adjustment as number,
    })),
    subtotal: data.subtotal as number,
  };
}

/**
 * Transform order from snake_case API response to camelCase
 */
function transformOrderResponse(data: Record<string, unknown>): OrderResponse {
  // Backend returns 'items' not 'order_items'
  const items = (data.items as Record<string, unknown>[] | undefined) ||
                (data.order_items as Record<string, unknown>[] | undefined) || [];
  return {
    id: data.id as string,
    orderNumber: data.order_number as string,
    customerName: data.customer_name as string,
    status: data.status as OrderStatus,
    // Backend returns 'total' not 'total_amount'
    totalAmount: (data.total as number) ?? (data.total_amount as number) ?? 0,
    orderItems: items.map(transformOrderItem),
    createdAt: data.created_at as string,
  };
}

/**
 * Transform full order from snake_case API response
 */
function transformOrder(data: Record<string, unknown>): Order {
  // Backend returns 'items' not 'order_items'
  const items = (data.items as Record<string, unknown>[] | undefined) ||
                (data.order_items as Record<string, unknown>[] | undefined) || [];
  return {
    id: data.id as string,
    brandId: data.brand_id as string,
    orderNumber: data.order_number as string,
    customerName: data.customer_name as string,
    customerPhone: data.customer_phone as string,
    customerEmail: data.customer_email as string | undefined,
    status: data.status as OrderStatus,
    // Backend returns 'total' not 'total_amount'
    totalAmount: (data.total as number) ?? (data.total_amount as number) ?? 0,
    notes: data.notes as string | undefined,
    orderItems: items.map(transformOrderItem),
    createdAt: data.created_at as string,
    updatedAt: data.updated_at as string,
  };
}

/**
 * Transform create order request to snake_case for API
 */
function transformCreateOrderRequest(data: CreateOrderRequest): Record<string, unknown> {
  return {
    customer_name: data.customerName,
    customer_phone: data.customerPhone,
    customer_email: data.customerEmail,
    notes: data.notes,
    items: data.items.map((item) => ({
      menu_item_id: item.menuItemId,
      quantity: item.quantity,
      customizations: item.customizations?.map((c) => ({
        option_type: c.optionType,
        name: c.name,
        price_adjustment: c.priceAdjustment,
      })),
    })),
  };
}

/**
 * Create a new order for a brand
 */
export async function createOrder(
  brandId: string,
  data: CreateOrderRequest
): Promise<OrderResponse> {
  const requestData = transformCreateOrderRequest(data);
  const response = await post<Record<string, unknown>>(
    `/orders/brands/${brandId}`,
    requestData
  );
  return transformOrderResponse(response);
}

/**
 * Get order by order number
 */
export async function getOrderByNumber(orderNumber: string): Promise<Order> {
  const response = await get<Record<string, unknown>>(`/orders/${orderNumber}`);
  return transformOrder(response);
}

/**
 * Get order by ID
 */
export async function getOrderById(orderId: string): Promise<Order> {
  const response = await get<Record<string, unknown>>(`/orders/id/${orderId}`);
  return transformOrder(response);
}

/**
 * Get orders by phone number
 */
export async function getOrdersByPhone(
  brandId: string,
  phone: string
): Promise<OrderResponse[]> {
  const response = await get<Record<string, unknown>[]>(
    `/orders/brands/${brandId}/phone/${encodeURIComponent(phone)}`
  );
  return response.map(transformOrderResponse);
}

/**
 * Get all orders for a brand
 */
export async function getOrdersByBrand(
  brandId: string,
  options?: {
    status?: OrderStatus;
    skip?: number;
    limit?: number;
  }
): Promise<OrderResponse[]> {
  const params = new URLSearchParams();
  if (options?.status) {
    params.append('status', options.status);
  }
  if (options?.skip !== undefined) {
    params.append('skip', String(options.skip));
  }
  if (options?.limit !== undefined) {
    params.append('limit', String(options.limit));
  }

  const queryString = params.toString();
  const url = queryString
    ? `/orders/brands/${brandId}?${queryString}`
    : `/orders/brands/${brandId}`;
  const response = await get<{ orders: Record<string, unknown>[] }>(url);
  return (response.orders || []).map(transformOrderResponse);
}

/**
 * Get active orders for a brand (pending, confirmed, preparing, ready)
 */
export async function getActiveOrders(brandId: string): Promise<OrderResponse[]> {
  const response = await get<Record<string, unknown>[]>(
    `/orders/brands/${brandId}/active`
  );
  return response.map(transformOrderResponse);
}

/**
 * Update order status
 */
export async function updateOrderStatus(
  orderId: string,
  data: UpdateOrderStatusRequest
): Promise<Order> {
  const response = await patch<Record<string, unknown>>(
    `/orders/${orderId}/status`,
    { status: data.status }
  );
  return transformOrder(response);
}

/**
 * Confirm an order
 */
export async function confirmOrder(orderId: string): Promise<Order> {
  const response = await post<Record<string, unknown>>(
    `/orders/${orderId}/confirm`,
    {}
  );
  return transformOrder(response);
}

/**
 * Cancel an order
 */
export async function cancelOrder(orderId: string): Promise<Order> {
  const response = await post<Record<string, unknown>>(
    `/orders/${orderId}/cancel`,
    {}
  );
  return transformOrder(response);
}

export default {
  createOrder,
  getOrderByNumber,
  getOrderById,
  getOrdersByPhone,
  getOrdersByBrand,
  getActiveOrders,
  updateOrderStatus,
  confirmOrder,
  cancelOrder,
};
