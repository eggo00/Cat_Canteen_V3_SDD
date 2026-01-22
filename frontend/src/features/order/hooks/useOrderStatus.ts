/**
 * useOrderStatus hook
 * Fetches and tracks order status with polling support
 */

import { useQuery } from '@tanstack/react-query';
import { getOrderByNumber, getOrderById } from '../api/orderApi';
import { Order, OrderStatus, ORDER_STATUS_DISPLAY } from '../../../shared/types/order';
import { orderQueryKeys } from './useCreateOrder';

/**
 * Active statuses that should be polled
 */
const ACTIVE_STATUSES: OrderStatus[] = ['pending', 'confirmed', 'preparing', 'ready'];

/**
 * Hook options
 */
interface UseOrderStatusOptions {
  /** Poll interval in ms for active orders (default: 10000) */
  pollInterval?: number;
  /** Whether to enable polling (default: true for active orders) */
  enablePolling?: boolean;
}

/**
 * Hook return type
 */
interface UseOrderStatusReturn {
  /** Order data */
  order: Order | undefined;
  /** Loading state */
  isLoading: boolean;
  /** Error state */
  error: Error | null;
  /** Current status */
  status: OrderStatus | undefined;
  /** Current status display text */
  statusDisplay: string | undefined;
  /** Whether order is active (not completed/cancelled) */
  isActive: boolean;
  /** Whether order is completed */
  isCompleted: boolean;
  /** Whether order is cancelled */
  isCancelled: boolean;
  /** Refetch order data */
  refetch: () => void;
}

/**
 * Hook for tracking order status by order number
 *
 * @param orderNumber - Order number to track
 * @param options - Hook options
 *
 * @example
 * ```tsx
 * function OrderStatusPage({ orderNumber }: { orderNumber: string }) {
 *   const {
 *     order,
 *     status,
 *     statusDisplay,
 *     isActive,
 *     isLoading,
 *     error,
 *   } = useOrderStatus(orderNumber);
 *
 *   if (isLoading) return <Loading />;
 *   if (error) return <Error message={error.message} />;
 *
 *   return (
 *     <div>
 *       <h1>訂單 #{orderNumber}</h1>
 *       <p>狀態: {statusDisplay}</p>
 *       {isActive && <p>訂單處理中...</p>}
 *     </div>
 *   );
 * }
 * ```
 */
export function useOrderStatus(
  orderNumber: string | undefined,
  options: UseOrderStatusOptions = {}
): UseOrderStatusReturn {
  const { pollInterval = 10000, enablePolling = true } = options;

  const {
    data: order,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: orderQueryKeys.order(orderNumber || ''),
    queryFn: () => getOrderByNumber(orderNumber!),
    enabled: !!orderNumber,
    staleTime: 5000, // 5 seconds
    refetchInterval: (query) => {
      if (!enablePolling) return false;
      // Only poll for active orders
      const status = query.state.data?.status;
      if (status && ACTIVE_STATUSES.includes(status)) {
        return pollInterval;
      }
      return false;
    },
  });

  const status = order?.status;
  const statusDisplay = status ? ORDER_STATUS_DISPLAY[status] : undefined;
  const isActive = status ? ACTIVE_STATUSES.includes(status) : false;
  const isCompleted = status === 'completed';
  const isCancelled = status === 'cancelled';

  return {
    order,
    isLoading,
    error: error as Error | null,
    status,
    statusDisplay,
    isActive,
    isCompleted,
    isCancelled,
    refetch,
  };
}

/**
 * Hook for tracking order status by order ID
 *
 * @param orderId - Order ID to track
 * @param options - Hook options
 */
export function useOrderStatusById(
  orderId: string | undefined,
  options: UseOrderStatusOptions = {}
): UseOrderStatusReturn {
  const { pollInterval = 10000, enablePolling = true } = options;

  const {
    data: order,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: orderQueryKeys.orderById(orderId || ''),
    queryFn: () => getOrderById(orderId!),
    enabled: !!orderId,
    staleTime: 5000, // 5 seconds
    refetchInterval: (query) => {
      if (!enablePolling) return false;
      const status = query.state.data?.status;
      if (status && ACTIVE_STATUSES.includes(status)) {
        return pollInterval;
      }
      return false;
    },
  });

  const status = order?.status;
  const statusDisplay = status ? ORDER_STATUS_DISPLAY[status] : undefined;
  const isActive = status ? ACTIVE_STATUSES.includes(status) : false;
  const isCompleted = status === 'completed';
  const isCancelled = status === 'cancelled';

  return {
    order,
    isLoading,
    error: error as Error | null,
    status,
    statusDisplay,
    isActive,
    isCompleted,
    isCancelled,
    refetch,
  };
}

export default useOrderStatus;
