/**
 * Order Management Page - Admin order management with status updates
 */
import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useOrders } from '../features/order/hooks/useOrders';
import { useAuthStore } from '../features/auth/store/authStore';
import { OrderStatus, ORDER_STATUS_DISPLAY, OrderResponse } from '../shared/types/order';

const STATUS_FLOW: OrderStatus[] = ['pending', 'confirmed', 'preparing', 'ready', 'completed'];

const STATUS_COLORS: Record<OrderStatus, { bg: string; text: string }> = {
  pending: { bg: '#FFF3CD', text: '#856404' },
  confirmed: { bg: '#D1ECF1', text: '#0C5460' },
  preparing: { bg: '#D4EDDA', text: '#155724' },
  ready: { bg: '#CCE5FF', text: '#004085' },
  completed: { bg: '#E2E3E5', text: '#383D41' },
  cancelled: { bg: '#F8D7DA', text: '#721C24' },
};

function getNextStatus(current: OrderStatus): OrderStatus | null {
  const idx = STATUS_FLOW.indexOf(current);
  if (idx < 0 || idx >= STATUS_FLOW.length - 1) return null;
  return STATUS_FLOW[idx + 1];
}

export default function OrderManagementPage() {
  const { brandSlug } = useParams<{ brandSlug: string }>();
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const [filterStatus, setFilterStatus] = useState<OrderStatus | 'all'>('all');

  const {
    orders,
    isLoading,
    error,
    updateStatus,
    confirm,
    cancel,
    isUpdating,
  } = useOrders(user?.brandId || undefined, {
    status: filterStatus === 'all' ? undefined : filterStatus,
    refreshInterval: 10000,
  });

  const handleNextStatus = async (order: OrderResponse) => {
    const next = getNextStatus(order.status);
    if (!next) return;
    if (next === 'confirmed') {
      await confirm(order.id);
    } else {
      await updateStatus(order.id, next);
    }
  };

  const handleCancel = async (orderId: string) => {
    if (window.confirm('確定要取消此訂單嗎？')) {
      await cancel(orderId);
    }
  };

  const filterButtons: { label: string; value: OrderStatus | 'all' }[] = [
    { label: '全部', value: 'all' },
    { label: '待確認', value: 'pending' },
    { label: '已確認', value: 'confirmed' },
    { label: '製作中', value: 'preparing' },
    { label: '已完成', value: 'ready' },
    { label: '已取餐', value: 'completed' },
    { label: '已取消', value: 'cancelled' },
  ];

  return (
    <div style={{ maxWidth: 960, margin: '0 auto', padding: '24px 16px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 28, fontWeight: 700 }}>訂單管理</h1>
          <p style={{ margin: '4px 0 0', color: '#666' }}>{brandSlug}</p>
        </div>
        <button
          onClick={() => navigate(`/${brandSlug}/admin`)}
          style={{
            padding: '8px 16px',
            border: '1px solid #ddd',
            borderRadius: 8,
            background: '#fff',
            cursor: 'pointer',
          }}
        >
          返回後台
        </button>
      </div>

      {/* Status Filters */}
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 24 }}>
        {filterButtons.map((btn) => (
          <button
            key={btn.value}
            onClick={() => setFilterStatus(btn.value)}
            style={{
              padding: '6px 14px',
              borderRadius: 20,
              border: filterStatus === btn.value ? '2px solid #8B4513' : '1px solid #ddd',
              background: filterStatus === btn.value ? '#8B4513' : '#fff',
              color: filterStatus === btn.value ? '#fff' : '#333',
              cursor: 'pointer',
              fontWeight: filterStatus === btn.value ? 600 : 400,
              fontSize: 14,
            }}
          >
            {btn.label}
          </button>
        ))}
      </div>

      {/* Content */}
      {isLoading ? (
        <div style={{ textAlign: 'center', padding: 60, color: '#999' }}>載入中...</div>
      ) : error ? (
        <div style={{ textAlign: 'center', padding: 60, color: '#dc3545' }}>
          載入失敗: {error.message}
        </div>
      ) : orders.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 60, color: '#999' }}>
          目前沒有訂單
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {orders.map((order) => {
            const nextStatus = getNextStatus(order.status);
            const statusColor = STATUS_COLORS[order.status];
            return (
              <div
                key={order.id}
                style={{
                  border: '1px solid #e0e0e0',
                  borderRadius: 12,
                  padding: 20,
                  background: '#fff',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
                }}
              >
                {/* Order Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                  <div>
                    <span style={{ fontSize: 18, fontWeight: 700 }}>#{order.orderNumber}</span>
                    <span style={{ marginLeft: 12, color: '#888', fontSize: 14 }}>
                      {order.customerName}
                    </span>
                  </div>
                  <span
                    style={{
                      padding: '4px 12px',
                      borderRadius: 12,
                      fontSize: 13,
                      fontWeight: 600,
                      background: statusColor.bg,
                      color: statusColor.text,
                    }}
                  >
                    {ORDER_STATUS_DISPLAY[order.status]}
                  </span>
                </div>

                {/* Order Items */}
                <div style={{ marginBottom: 12 }}>
                  {order.orderItems.map((item, idx) => (
                    <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', fontSize: 14 }}>
                      <span>{item.menuItemName} x{item.quantity}</span>
                      <span style={{ color: '#666' }}>NT$ {item.subtotal}</span>
                    </div>
                  ))}
                </div>

                {/* Order Footer */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid #eee', paddingTop: 12 }}>
                  <div>
                    <span style={{ fontWeight: 600, fontSize: 16 }}>
                      總計 NT$ {order.totalAmount}
                    </span>
                    <span style={{ marginLeft: 12, color: '#999', fontSize: 13 }}>
                      {new Date(order.createdAt).toLocaleString('zh-TW')}
                    </span>
                  </div>
                  <div style={{ display: 'flex', gap: 8 }}>
                    {order.status !== 'completed' && order.status !== 'cancelled' && (
                      <button
                        onClick={() => handleCancel(order.id)}
                        disabled={isUpdating}
                        style={{
                          padding: '6px 14px',
                          borderRadius: 8,
                          border: '1px solid #dc3545',
                          background: '#fff',
                          color: '#dc3545',
                          cursor: isUpdating ? 'not-allowed' : 'pointer',
                          fontSize: 13,
                        }}
                      >
                        取消
                      </button>
                    )}
                    {nextStatus && (
                      <button
                        onClick={() => handleNextStatus(order)}
                        disabled={isUpdating}
                        style={{
                          padding: '6px 14px',
                          borderRadius: 8,
                          border: 'none',
                          background: '#8B4513',
                          color: '#fff',
                          cursor: isUpdating ? 'not-allowed' : 'pointer',
                          fontWeight: 600,
                          fontSize: 13,
                        }}
                      >
                        {ORDER_STATUS_DISPLAY[nextStatus]}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
