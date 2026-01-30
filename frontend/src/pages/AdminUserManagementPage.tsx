/**
 * User Management Page - Admin user list, add, and delete
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../features/auth/store/authStore';
import { getUsers, registerUser, deleteUser } from '../features/auth/api/authApi';
import { User, UserRole } from '../shared/types/auth';

const ROLE_LABELS: Record<UserRole, string> = {
  customer: '顧客',
  staff: '員工',
  admin: '管理員',
  super_admin: '超級管理員',
};

const ROLE_COLORS: Record<UserRole, { bg: string; text: string }> = {
  customer: { bg: '#E0F2FE', text: '#0369A1' },
  staff: { bg: '#FEF3C7', text: '#92400E' },
  admin: { bg: '#D1FAE5', text: '#065F46' },
  super_admin: { bg: '#EDE9FE', text: '#5B21B6' },
};

const styles = {
  container: {
    maxWidth: 960,
    margin: '0 auto',
    padding: '24px 16px',
  } as React.CSSProperties,
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  } as React.CSSProperties,
  backButton: {
    padding: '8px 16px',
    border: '1px solid #ddd',
    borderRadius: 8,
    background: '#fff',
    cursor: 'pointer',
    fontSize: 14,
  } as React.CSSProperties,
  toolbar: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  } as React.CSSProperties,
  count: {
    color: '#666',
    fontSize: 14,
  } as React.CSSProperties,
  addButton: {
    padding: '8px 20px',
    border: 'none',
    borderRadius: 8,
    background: '#8B4513',
    color: '#fff',
    cursor: 'pointer',
    fontWeight: 600,
    fontSize: 14,
  } as React.CSSProperties,
  userCard: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    background: '#fff',
    border: '1px solid #e0e0e0',
    borderRadius: 12,
    marginBottom: 12,
  } as React.CSSProperties,
  userInfo: {
    flex: 1,
  } as React.CSSProperties,
  userName: {
    fontSize: 16,
    fontWeight: 600,
    color: '#333',
  } as React.CSSProperties,
  userEmail: {
    fontSize: 13,
    color: '#888',
    marginTop: 2,
  } as React.CSSProperties,
  badges: {
    display: 'flex',
    gap: 8,
    alignItems: 'center',
    marginRight: 16,
  } as React.CSSProperties,
  roleBadge: {
    padding: '3px 10px',
    borderRadius: 12,
    fontSize: 12,
    fontWeight: 600,
  } as React.CSSProperties,
  statusBadge: {
    padding: '3px 10px',
    borderRadius: 12,
    fontSize: 12,
    fontWeight: 600,
  } as React.CSSProperties,
  deleteButton: {
    padding: '6px 14px',
    border: '1px solid #dc3545',
    borderRadius: 8,
    background: '#fff',
    color: '#dc3545',
    cursor: 'pointer',
    fontSize: 13,
  } as React.CSSProperties,
  loading: {
    textAlign: 'center' as const,
    padding: 60,
    color: '#999',
  } as React.CSSProperties,
  error: {
    padding: 12,
    background: '#fef2f2',
    color: '#b91c1c',
    borderRadius: 8,
    marginBottom: 16,
    fontSize: 14,
  } as React.CSSProperties,
  success: {
    padding: 12,
    background: '#f0fdf4',
    color: '#166534',
    borderRadius: 8,
    marginBottom: 16,
    fontSize: 14,
  } as React.CSSProperties,
  emptyState: {
    textAlign: 'center' as const,
    padding: 60,
    color: '#999',
  } as React.CSSProperties,
  modalOverlay: {
    position: 'fixed' as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(0,0,0,0.5)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  } as React.CSSProperties,
  modalContent: {
    background: '#fff',
    borderRadius: 12,
    padding: 24,
    width: 420,
    maxWidth: '90vw',
  } as React.CSSProperties,
  modalTitle: {
    fontSize: 18,
    fontWeight: 700,
    marginBottom: 20,
    color: '#333',
  } as React.CSSProperties,
  formGroup: {
    marginBottom: 16,
  } as React.CSSProperties,
  label: {
    display: 'block',
    fontSize: 13,
    fontWeight: 600,
    color: '#555',
    marginBottom: 4,
  } as React.CSSProperties,
  input: {
    width: '100%',
    padding: '8px 12px',
    border: '1px solid #ddd',
    borderRadius: 6,
    fontSize: 14,
    boxSizing: 'border-box' as const,
  } as React.CSSProperties,
  select: {
    width: '100%',
    padding: '8px 12px',
    border: '1px solid #ddd',
    borderRadius: 6,
    fontSize: 14,
    boxSizing: 'border-box' as const,
    background: '#fff',
  } as React.CSSProperties,
  modalActions: {
    display: 'flex',
    justifyContent: 'flex-end',
    gap: 8,
    marginTop: 20,
  } as React.CSSProperties,
  cancelButton: {
    padding: '8px 16px',
    border: '1px solid #ddd',
    borderRadius: 8,
    background: '#fff',
    cursor: 'pointer',
    fontSize: 14,
  } as React.CSSProperties,
  submitButton: {
    padding: '8px 20px',
    border: 'none',
    borderRadius: 8,
    background: '#8B4513',
    color: '#fff',
    cursor: 'pointer',
    fontWeight: 600,
    fontSize: 14,
  } as React.CSSProperties,
};

export default function AdminUserManagementPage() {
  const { brandSlug } = useParams<{ brandSlug: string }>();
  const navigate = useNavigate();
  const currentUser = useAuthStore((s) => s.user);

  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Add user form
  const [newEmail, setNewEmail] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [newName, setNewName] = useState('');
  const [newRole, setNewRole] = useState<UserRole>('staff');

  const loadUsers = useCallback(async () => {
    if (!currentUser?.brandId) return;
    try {
      setIsLoading(true);
      const data = await getUsers({ brandId: currentUser.brandId });
      setUsers(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : '載入使用者失敗');
    } finally {
      setIsLoading(false);
    }
  }, [currentUser?.brandId]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  const handleAddUser = async () => {
    if (!newEmail || !newPassword) {
      setError('Email 和密碼為必填');
      return;
    }
    try {
      setIsSubmitting(true);
      setError(null);
      await registerUser({
        email: newEmail,
        password: newPassword,
        name: newName || undefined,
        role: newRole,
        brandId: currentUser?.brandId || undefined,
      });
      setSuccess('使用者已新增');
      setShowAddModal(false);
      setNewEmail('');
      setNewPassword('');
      setNewName('');
      setNewRole('staff');
      await loadUsers();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : '新增使用者失敗');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteUser = async (userId: string) => {
    if (userId === currentUser?.id) {
      setError('無法刪除自己的帳號');
      return;
    }
    if (!window.confirm('確定要刪除此使用者嗎？')) return;
    try {
      setError(null);
      await deleteUser(userId);
      setSuccess('使用者已刪除');
      await loadUsers();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : '刪除使用者失敗');
    }
  };

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div>
          <h1 style={{ margin: 0, fontSize: 28, fontWeight: 700 }}>使用者管理</h1>
          <p style={{ margin: '4px 0 0', color: '#666' }}>{brandSlug}</p>
        </div>
        <button style={styles.backButton} onClick={() => navigate(`/${brandSlug}/admin`)}>
          返回後台
        </button>
      </div>

      {/* Messages */}
      {error && <div style={styles.error}>{error}</div>}
      {success && <div style={styles.success}>{success}</div>}

      {/* Toolbar */}
      <div style={styles.toolbar}>
        <span style={styles.count}>共 {users.length} 位使用者</span>
        <button style={styles.addButton} onClick={() => setShowAddModal(true)}>
          新增使用者
        </button>
      </div>

      {/* User List */}
      {isLoading ? (
        <div style={styles.loading}>載入中...</div>
      ) : users.length === 0 ? (
        <div style={styles.emptyState}>目前沒有使用者</div>
      ) : (
        users.map((u) => (
          <div key={u.id} style={styles.userCard}>
            <div style={styles.userInfo}>
              <div style={styles.userName}>{u.name || '(未命名)'}</div>
              <div style={styles.userEmail}>{u.email}</div>
            </div>
            <div style={styles.badges}>
              <span
                style={{
                  ...styles.roleBadge,
                  backgroundColor: ROLE_COLORS[u.role].bg,
                  color: ROLE_COLORS[u.role].text,
                }}
              >
                {ROLE_LABELS[u.role]}
              </span>
              <span
                style={{
                  ...styles.statusBadge,
                  backgroundColor: u.isActive ? '#D1FAE5' : '#FEE2E2',
                  color: u.isActive ? '#065F46' : '#991B1B',
                }}
              >
                {u.isActive ? '啟用' : '停用'}
              </span>
            </div>
            {u.id !== currentUser?.id && (
              <button style={styles.deleteButton} onClick={() => handleDeleteUser(u.id)}>
                刪除
              </button>
            )}
          </div>
        ))
      )}

      {/* Add User Modal */}
      {showAddModal && (
        <div style={styles.modalOverlay} onClick={() => setShowAddModal(false)}>
          <div style={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <h3 style={styles.modalTitle}>新增使用者</h3>
            <div style={styles.formGroup}>
              <label style={styles.label}>Email *</label>
              <input
                style={styles.input}
                type="email"
                value={newEmail}
                onChange={(e) => setNewEmail(e.target.value)}
                placeholder="user@example.com"
              />
            </div>
            <div style={styles.formGroup}>
              <label style={styles.label}>密碼 *</label>
              <input
                style={styles.input}
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="至少 8 個字元"
              />
            </div>
            <div style={styles.formGroup}>
              <label style={styles.label}>姓名</label>
              <input
                style={styles.input}
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="選填"
              />
            </div>
            <div style={styles.formGroup}>
              <label style={styles.label}>角色</label>
              <select
                style={styles.select}
                value={newRole}
                onChange={(e) => setNewRole(e.target.value as UserRole)}
              >
                <option value="staff">員工</option>
                <option value="admin">管理員</option>
                <option value="customer">顧客</option>
              </select>
            </div>
            <div style={styles.modalActions}>
              <button style={styles.cancelButton} onClick={() => setShowAddModal(false)}>
                取消
              </button>
              <button
                style={{
                  ...styles.submitButton,
                  opacity: isSubmitting ? 0.6 : 1,
                }}
                onClick={handleAddUser}
                disabled={isSubmitting}
              >
                {isSubmitting ? '新增中...' : '新增'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
