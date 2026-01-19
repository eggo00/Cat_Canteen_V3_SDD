/**
 * useCreateOrder hook
 * Handles order creation with cart integration
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createOrder } from '../api/orderApi';
import { useCart } from '../../cart/hooks/useCart';
import { CreateOrderRequest, OrderResponse } from '../../../shared/types/order';

/**
 * Query keys for orders
 */
export const orderQueryKeys = {
  order: (orderNumber: string) => ['order', orderNumber],
  orderById: (orderId: string) => ['order', 'id', orderId],
  ordersByBrand: (brandId: string) => ['orders', 'brand', brandId],
  activeOrders: (brandId: string) => ['orders', 'brand', brandId, 'active'],
  ordersByPhone: (brandId: string, phone: string) => ['orders', 'brand', brandId, 'phone', phone],
};

/**
 * Customer info for order
 */
interface CustomerInfo {
  customerName: string;
  customerPhone: string;
  customerEmail?: string;
  notes?: string;
}

/**
 * Hook return type
 */
interface UseCreateOrderReturn {
  /** Create order mutation */
  createOrder: (customerInfo: CustomerInfo) => Promise<OrderResponse>;
  /** Whether order is being created */
  isLoading: boolean;
  /** Error from order creation */
  error: Error | null;
  /** Whether order was successfully created */
  isSuccess: boolean;
  /** Created order data */
  order: OrderResponse | undefined;
  /** Reset mutation state */
  reset: () => void;
}

/**
 * Hook for creating orders from cart
 *
 * @example
 * ```tsx
 * function CheckoutPage() {
 *   const { createOrder, isLoading, error, isSuccess, order } = useCreateOrder();
 *
 *   const handleSubmit = async (customerInfo: CustomerInfo) => {
 *     try {
 *       const createdOrder = await createOrder(customerInfo);
 *       // Navigate to order confirmation
 *       navigate(`/order/${createdOrder.orderNumber}`);
 *     } catch (err) {
 *       // Error is also available via the hook
 *     }
 *   };
 *
 *   return (
 *     <CheckoutForm onSubmit={handleSubmit} isLoading={isLoading} error={error} />
 *   );
 * }
 * ```
 */
export function useCreateOrder(): UseCreateOrderReturn {
  const queryClient = useQueryClient();
  const { items, brandId, clearCart } = useCart();

  const mutation = useMutation({
    mutationFn: async (customerInfo: CustomerInfo) => {
      if (!brandId) {
        throw new Error('Brand ID is required to create an order');
      }

      if (items.length === 0) {
        throw new Error('Cart is empty');
      }

      // Transform cart items to order items
      const orderRequest: CreateOrderRequest = {
        customerName: customerInfo.customerName,
        customerPhone: customerInfo.customerPhone,
        customerEmail: customerInfo.customerEmail,
        notes: customerInfo.notes,
        items: items.map((item) => ({
          menuItemId: item.menuItemId,
          quantity: item.quantity,
          customizations: item.customizations.map((c) => ({
            optionType: c.optionId, // Use optionId as optionType
            name: c.name,
            priceAdjustment: c.priceAdjustment,
          })),
        })),
      };

      return createOrder(brandId, orderRequest);
    },
    onSuccess: (data) => {
      // Clear the cart after successful order
      clearCart();

      // Invalidate order queries
      if (brandId) {
        queryClient.invalidateQueries({
          queryKey: orderQueryKeys.ordersByBrand(brandId),
        });
        queryClient.invalidateQueries({
          queryKey: orderQueryKeys.activeOrders(brandId),
        });
      }

      // Cache the new order
      queryClient.setQueryData(orderQueryKeys.order(data.orderNumber), data);
    },
  });

  return {
    createOrder: mutation.mutateAsync,
    isLoading: mutation.isPending,
    error: mutation.error as Error | null,
    isSuccess: mutation.isSuccess,
    order: mutation.data,
    reset: mutation.reset,
  };
}

export default useCreateOrder;
