/**
 * useOrders hook
 * Fetches and manages orders for a brand (admin/staff use)
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getOrdersByBrand,
  getActiveOrders,
  getOrdersByPhone,
  updateOrderStatus,
  confirmOrder,
  cancelOrder,
} from '../api/orderApi';
import { OrderResponse, Order, OrderStatus } from '../../../shared/types/order';
import { orderQueryKeys } from './useCreateOrder';

/**
 * Hook options
 */
interface UseOrdersOptions {
  /** Filter by status */
  status?: OrderStatus;
  /** Pagination skip */
  skip?: number;
  /** Pagination limit */
  limit?: number;
  /** Auto-refresh interval (default: 30000ms for active orders) */
  refreshInterval?: number;
}

/**
 * Hook return type
 */
interface UseOrdersReturn {
  /** Orders list */
  orders: OrderResponse[];
  /** Loading state */
  isLoading: boolean;
  /** Error state */
  error: Error | null;
  /** Refetch orders */
  refetch: () => void;
  /** Update order status */
  updateStatus: (orderId: string, status: OrderStatus) => Promise<Order>;
  /** Confirm order */
  confirm: (orderId: string) => Promise<Order>;
  /** Cancel order */
  cancel: (orderId: string) => Promise<Order>;
  /** Status mutation loading state */
  isUpdating: boolean;
}

/**
 * Hook for fetching all orders for a brand
 *
 * @param brandId - Brand ID
 * @param options - Hook options
 *
 * @example
 * ```tsx
 * function OrdersPage({ brandId }: { brandId: string }) {
 *   const {
 *     orders,
 *     isLoading,
 *     updateStatus,
 *     confirm,
 *     cancel,
 *   } = useOrders(brandId);
 *
 *   return (
 *     <OrderList
 *       orders={orders}
 *       onConfirm={(id) => confirm(id)}
 *       onCancel={(id) => cancel(id)}
 *     />
 *   );
 * }
 * ```
 */
export function useOrders(
  brandId: string | undefined,
  options: UseOrdersOptions = {}
): UseOrdersReturn {
  const { status, skip, limit, refreshInterval = 30000 } = options;
  const queryClient = useQueryClient();

  const {
    data: orders = [],
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: [...orderQueryKeys.ordersByBrand(brandId || ''), { status, skip, limit }],
    queryFn: () => getOrdersByBrand(brandId!, { status, skip, limit }),
    enabled: !!brandId,
    staleTime: 10000, // 10 seconds
    refetchInterval: refreshInterval,
  });

  // Update status mutation
  const updateStatusMutation = useMutation({
    mutationFn: ({ orderId, newStatus }: { orderId: string; newStatus: OrderStatus }) =>
      updateOrderStatus(orderId, { status: newStatus }),
    onSuccess: () => {
      if (brandId) {
        queryClient.invalidateQueries({
          queryKey: orderQueryKeys.ordersByBrand(brandId),
        });
        queryClient.invalidateQueries({
          queryKey: orderQueryKeys.activeOrders(brandId),
        });
      }
    },
  });

  // Confirm mutation
  const confirmMutation = useMutation({
    mutationFn: (orderId: string) => confirmOrder(orderId),
    onSuccess: () => {
      if (brandId) {
        queryClient.invalidateQueries({
          queryKey: orderQueryKeys.ordersByBrand(brandId),
        });
        queryClient.invalidateQueries({
          queryKey: orderQueryKeys.activeOrders(brandId),
        });
      }
    },
  });

  // Cancel mutation
  const cancelMutation = useMutation({
    mutationFn: (orderId: string) => cancelOrder(orderId),
    onSuccess: () => {
      if (brandId) {
        queryClient.invalidateQueries({
          queryKey: orderQueryKeys.ordersByBrand(brandId),
        });
        queryClient.invalidateQueries({
          queryKey: orderQueryKeys.activeOrders(brandId),
        });
      }
    },
  });

  return {
    orders,
    isLoading,
    error: error as Error | null,
    refetch,
    updateStatus: (orderId: string, newStatus: OrderStatus) =>
      updateStatusMutation.mutateAsync({ orderId, newStatus }),
    confirm: (orderId: string) => confirmMutation.mutateAsync(orderId),
    cancel: (orderId: string) => cancelMutation.mutateAsync(orderId),
    isUpdating:
      updateStatusMutation.isPending ||
      confirmMutation.isPending ||
      cancelMutation.isPending,
  };
}

/**
 * Hook for fetching active orders for a brand
 *
 * @param brandId - Brand ID
 * @param refreshInterval - Auto-refresh interval (default: 15000ms)
 */
export function useActiveOrders(
  brandId: string | undefined,
  refreshInterval = 15000
): Omit<UseOrdersReturn, 'updateStatus' | 'confirm' | 'cancel' | 'isUpdating'> {
  const {
    data: orders = [],
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: orderQueryKeys.activeOrders(brandId || ''),
    queryFn: () => getActiveOrders(brandId!),
    enabled: !!brandId,
    staleTime: 5000, // 5 seconds
    refetchInterval: refreshInterval,
  });

  return {
    orders,
    isLoading,
    error: error as Error | null,
    refetch,
  };
}

/**
 * Hook for fetching orders by phone number
 *
 * @param brandId - Brand ID
 * @param phone - Customer phone number
 */
export function useOrdersByPhone(
  brandId: string | undefined,
  phone: string | undefined
): Omit<UseOrdersReturn, 'updateStatus' | 'confirm' | 'cancel' | 'isUpdating'> {
  const {
    data: orders = [],
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: orderQueryKeys.ordersByPhone(brandId || '', phone || ''),
    queryFn: () => getOrdersByPhone(brandId!, phone!),
    enabled: !!brandId && !!phone,
    staleTime: 30000, // 30 seconds
  });

  return {
    orders,
    isLoading,
    error: error as Error | null,
    refetch,
  };
}

export default useOrders;
