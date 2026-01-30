/**
 * Menu Management Page - Admin category and item CRUD
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../features/auth/store/authStore';
import {
  getCategories,
  createCategory,
  updateCategory,
  deleteCategory,
  uploadMenu,
} from '../features/menu/api/menuApi';
import { Category, MenuItem, UploadMenuRequest } from '../shared/types/menu';

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
  saveBar: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px 16px',
    background: '#FEF3C7',
    border: '1px solid #F59E0B',
    borderRadius: 8,
    marginBottom: 20,
  } as React.CSSProperties,
  saveBarText: {
    color: '#92400E',
    fontSize: 14,
    fontWeight: 600,
  } as React.CSSProperties,
  saveButton: {
    padding: '8px 20px',
    border: 'none',
    borderRadius: 8,
    background: '#8B4513',
    color: '#fff',
    cursor: 'pointer',
    fontWeight: 600,
    fontSize: 14,
  } as React.CSSProperties,
  toolbar: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  } as React.CSSProperties,
  addCategoryButton: {
    padding: '8px 20px',
    border: 'none',
    borderRadius: 8,
    background: '#8B4513',
    color: '#fff',
    cursor: 'pointer',
    fontWeight: 600,
    fontSize: 14,
  } as React.CSSProperties,
  categoryCard: {
    background: '#fff',
    border: '1px solid #e0e0e0',
    borderRadius: 12,
    marginBottom: 20,
    overflow: 'hidden',
  } as React.CSSProperties,
  categoryHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '14px 20px',
    background: '#f9f9f9',
    borderBottom: '1px solid #e0e0e0',
  } as React.CSSProperties,
  categoryName: {
    fontSize: 16,
    fontWeight: 700,
    color: '#333',
  } as React.CSSProperties,
  categoryDesc: {
    fontSize: 13,
    color: '#888',
    marginLeft: 12,
  } as React.CSSProperties,
  categoryActions: {
    display: 'flex',
    gap: 8,
  } as React.CSSProperties,
  smallButton: {
    padding: '4px 12px',
    border: '1px solid #ddd',
    borderRadius: 6,
    background: '#fff',
    cursor: 'pointer',
    fontSize: 12,
    color: '#555',
  } as React.CSSProperties,
  smallButtonDanger: {
    padding: '4px 12px',
    border: '1px solid #dc3545',
    borderRadius: 6,
    background: '#fff',
    cursor: 'pointer',
    fontSize: 12,
    color: '#dc3545',
  } as React.CSSProperties,
  itemRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '10px 20px',
    borderBottom: '1px solid #f0f0f0',
  } as React.CSSProperties,
  itemInfo: {
    flex: 1,
  } as React.CSSProperties,
  itemName: {
    fontSize: 14,
    fontWeight: 600,
    color: '#333',
  } as React.CSSProperties,
  itemDesc: {
    fontSize: 12,
    color: '#888',
    marginTop: 2,
  } as React.CSSProperties,
  itemPrice: {
    fontSize: 14,
    fontWeight: 600,
    color: '#8B4513',
    marginRight: 16,
    minWidth: 80,
    textAlign: 'right' as const,
  } as React.CSSProperties,
  itemActions: {
    display: 'flex',
    gap: 6,
  } as React.CSSProperties,
  addItemRow: {
    padding: '10px 20px',
    textAlign: 'center' as const,
  } as React.CSSProperties,
  addItemButton: {
    padding: '6px 16px',
    border: '1px dashed #aaa',
    borderRadius: 6,
    background: '#fff',
    cursor: 'pointer',
    fontSize: 13,
    color: '#666',
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

interface EditingItem {
  categoryIndex: number;
  itemIndex: number | null; // null = add new
  name: string;
  price: string;
  description: string;
}

interface EditingCategory {
  id: string | null; // null = add new
  name: string;
  description: string;
}

export default function AdminMenuManagementPage() {
  const { brandSlug } = useParams<{ brandSlug: string }>();
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);

  const [categories, setCategories] = useState<Category[]>([]);
  const [editedCategories, setEditedCategories] = useState<Category[]>([]);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Modal state
  const [editingCategory, setEditingCategory] = useState<EditingCategory | null>(null);
  const [editingItem, setEditingItem] = useState<EditingItem | null>(null);

  const brandId = user?.brandId;

  const loadCategories = useCallback(async () => {
    if (!brandId) return;
    try {
      setIsLoading(true);
      const data = await getCategories(brandId, true);
      setCategories(data);
      setEditedCategories(JSON.parse(JSON.stringify(data)));
      setHasUnsavedChanges(false);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : '載入菜單失敗');
    } finally {
      setIsLoading(false);
    }
  }, [brandId]);

  useEffect(() => {
    loadCategories();
  }, [loadCategories]);

  // Warn on unsaved changes
  useEffect(() => {
    const handler = (e: BeforeUnloadEvent) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = '';
      }
    };
    window.addEventListener('beforeunload', handler);
    return () => window.removeEventListener('beforeunload', handler);
  }, [hasUnsavedChanges]);

  // === Category Operations ===

  const handleAddCategory = () => {
    setEditingCategory({ id: null, name: '', description: '' });
  };

  const handleEditCategory = (cat: Category) => {
    setEditingCategory({ id: cat.id, name: cat.name, description: cat.description || '' });
  };

  const handleSaveCategory = async () => {
    if (!editingCategory || !brandId) return;
    if (!editingCategory.name.trim()) {
      setError('分類名稱為必填');
      return;
    }

    try {
      setError(null);
      if (editingCategory.id) {
        await updateCategory(brandId, editingCategory.id, {
          name: editingCategory.name,
          description: editingCategory.description || undefined,
        });
        setSuccess('分類已更新');
      } else {
        await createCategory(brandId, {
          name: editingCategory.name,
          description: editingCategory.description || undefined,
        });
        setSuccess('分類已新增');
      }
      setEditingCategory(null);
      await loadCategories();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : '儲存分類失敗');
    }
  };

  const handleDeleteCategory = async (catId: string) => {
    if (!brandId) return;
    if (!window.confirm('確定要刪除此分類嗎？分類下的所有品項也會被刪除。')) return;
    try {
      setError(null);
      await deleteCategory(brandId, catId);
      setSuccess('分類已刪除');
      await loadCategories();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : '刪除分類失敗');
    }
  };

  // === Item Operations (local edits) ===

  const handleAddItem = (categoryIndex: number) => {
    setEditingItem({ categoryIndex, itemIndex: null, name: '', price: '', description: '' });
  };

  const handleEditItem = (categoryIndex: number, itemIndex: number) => {
    const item = editedCategories[categoryIndex].menuItems?.[itemIndex];
    if (!item) return;
    setEditingItem({
      categoryIndex,
      itemIndex,
      name: item.name,
      price: String(item.price),
      description: item.description || '',
    });
  };

  const handleSaveItem = () => {
    if (!editingItem) return;
    const { categoryIndex, itemIndex, name, price, description } = editingItem;

    if (!name.trim()) {
      setError('品項名稱為必填');
      return;
    }
    const priceNum = parseFloat(price);
    if (isNaN(priceNum) || priceNum < 0) {
      setError('請輸入有效價格');
      return;
    }

    setError(null);
    const updated = JSON.parse(JSON.stringify(editedCategories)) as Category[];
    const items = updated[categoryIndex].menuItems || [];

    if (itemIndex !== null) {
      // Edit existing
      items[itemIndex] = { ...items[itemIndex], name: name.trim(), price: priceNum, description: description.trim() || undefined };
    } else {
      // Add new
      items.push({
        id: crypto.randomUUID(),
        categoryId: updated[categoryIndex].id,
        name: name.trim(),
        price: priceNum,
        description: description.trim() || undefined,
        displayOrder: items.length,
        isAvailable: true,
      });
    }
    updated[categoryIndex].menuItems = items;
    setEditedCategories(updated);
    setHasUnsavedChanges(true);
    setEditingItem(null);
  };

  const handleDeleteItem = (categoryIndex: number, itemIndex: number) => {
    if (!window.confirm('確定要刪除此品項嗎？')) return;
    const updated = JSON.parse(JSON.stringify(editedCategories)) as Category[];
    updated[categoryIndex].menuItems?.splice(itemIndex, 1);
    setEditedCategories(updated);
    setHasUnsavedChanges(true);
  };

  // === Save All ===

  const handleSaveAll = async () => {
    if (!brandId) return;
    try {
      setIsSaving(true);
      setError(null);
      const uploadData: UploadMenuRequest = {
        categories: editedCategories.map((cat, catIdx) => ({
          name: cat.name,
          description: cat.description,
          displayOrder: cat.displayOrder ?? catIdx,
          menuItems: (cat.menuItems || []).map((item, itemIdx) => ({
            name: item.name,
            description: item.description,
            price: item.price,
            imageUrl: item.imageUrl,
            displayOrder: item.displayOrder ?? itemIdx,
            customizationOptions: item.customizationOptions?.map((opt) => ({
              optionType: opt.optionType,
              name: opt.name,
              priceAdjustment: opt.priceAdjustment,
            })),
          })),
        })),
      };
      await uploadMenu(brandId, uploadData);
      setSuccess('菜單已儲存');
      await loadCategories();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : '儲存菜單失敗');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div>
          <h1 style={{ margin: 0, fontSize: 28, fontWeight: 700 }}>菜單管理</h1>
          <p style={{ margin: '4px 0 0', color: '#666' }}>{brandSlug}</p>
        </div>
        <button style={styles.backButton} onClick={() => navigate(`/${brandSlug}/admin`)}>
          返回後台
        </button>
      </div>

      {/* Messages */}
      {error && <div style={styles.error}>{error}</div>}
      {success && <div style={styles.success}>{success}</div>}

      {/* Unsaved changes bar */}
      {hasUnsavedChanges && (
        <div style={styles.saveBar}>
          <span style={styles.saveBarText}>有未儲存的品項變更</span>
          <button
            style={{ ...styles.saveButton, opacity: isSaving ? 0.6 : 1 }}
            onClick={handleSaveAll}
            disabled={isSaving}
          >
            {isSaving ? '儲存中...' : '儲存全部品項'}
          </button>
        </div>
      )}

      {/* Toolbar */}
      <div style={styles.toolbar}>
        <span style={{ color: '#666', fontSize: 14 }}>
          共 {editedCategories.length} 個分類，
          {editedCategories.reduce((sum, c) => sum + (c.menuItems?.length || 0), 0)} 個品項
        </span>
        <button style={styles.addCategoryButton} onClick={handleAddCategory}>
          新增分類
        </button>
      </div>

      {/* Content */}
      {isLoading ? (
        <div style={styles.loading}>載入中...</div>
      ) : editedCategories.length === 0 ? (
        <div style={styles.emptyState}>尚無菜單分類，點擊「新增分類」開始建立</div>
      ) : (
        editedCategories.map((cat, catIdx) => (
          <div key={cat.id} style={styles.categoryCard}>
            {/* Category Header */}
            <div style={styles.categoryHeader}>
              <div>
                <span style={styles.categoryName}>{cat.name}</span>
                {cat.description && <span style={styles.categoryDesc}>{cat.description}</span>}
                <span style={{ ...styles.categoryDesc, marginLeft: 8 }}>
                  ({cat.menuItems?.length || 0} 項)
                </span>
              </div>
              <div style={styles.categoryActions}>
                <button style={styles.smallButton} onClick={() => handleEditCategory(cat)}>
                  編輯
                </button>
                <button style={styles.smallButtonDanger} onClick={() => handleDeleteCategory(cat.id)}>
                  刪除
                </button>
              </div>
            </div>

            {/* Items */}
            {(cat.menuItems || []).map((item, itemIdx) => (
              <div key={item.id} style={styles.itemRow}>
                <div style={styles.itemInfo}>
                  <div style={styles.itemName}>{item.name}</div>
                  {item.description && <div style={styles.itemDesc}>{item.description}</div>}
                </div>
                <div style={styles.itemPrice}>NT$ {item.price}</div>
                <div style={styles.itemActions}>
                  <button style={styles.smallButton} onClick={() => handleEditItem(catIdx, itemIdx)}>
                    編輯
                  </button>
                  <button style={styles.smallButtonDanger} onClick={() => handleDeleteItem(catIdx, itemIdx)}>
                    刪除
                  </button>
                </div>
              </div>
            ))}

            {/* Add Item */}
            <div style={styles.addItemRow}>
              <button style={styles.addItemButton} onClick={() => handleAddItem(catIdx)}>
                + 新增品項
              </button>
            </div>
          </div>
        ))
      )}

      {/* Category Modal */}
      {editingCategory && (
        <div style={styles.modalOverlay} onClick={() => setEditingCategory(null)}>
          <div style={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <h3 style={styles.modalTitle}>
              {editingCategory.id ? '編輯分類' : '新增分類'}
            </h3>
            <div style={styles.formGroup}>
              <label style={styles.label}>分類名稱 *</label>
              <input
                style={styles.input}
                type="text"
                value={editingCategory.name}
                onChange={(e) => setEditingCategory({ ...editingCategory, name: e.target.value })}
                placeholder="例：飲品"
              />
            </div>
            <div style={styles.formGroup}>
              <label style={styles.label}>描述</label>
              <input
                style={styles.input}
                type="text"
                value={editingCategory.description}
                onChange={(e) => setEditingCategory({ ...editingCategory, description: e.target.value })}
                placeholder="選填"
              />
            </div>
            <div style={styles.modalActions}>
              <button style={styles.cancelButton} onClick={() => setEditingCategory(null)}>
                取消
              </button>
              <button style={styles.submitButton} onClick={handleSaveCategory}>
                {editingCategory.id ? '更新' : '新增'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Item Modal */}
      {editingItem && (
        <div style={styles.modalOverlay} onClick={() => setEditingItem(null)}>
          <div style={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <h3 style={styles.modalTitle}>
              {editingItem.itemIndex !== null ? '編輯品項' : '新增品項'}
            </h3>
            <div style={styles.formGroup}>
              <label style={styles.label}>品項名稱 *</label>
              <input
                style={styles.input}
                type="text"
                value={editingItem.name}
                onChange={(e) => setEditingItem({ ...editingItem, name: e.target.value })}
                placeholder="例：美式咖啡"
              />
            </div>
            <div style={styles.formGroup}>
              <label style={styles.label}>價格 (NT$) *</label>
              <input
                style={styles.input}
                type="number"
                min="0"
                step="1"
                value={editingItem.price}
                onChange={(e) => setEditingItem({ ...editingItem, price: e.target.value })}
                placeholder="例：80"
              />
            </div>
            <div style={styles.formGroup}>
              <label style={styles.label}>描述</label>
              <input
                style={styles.input}
                type="text"
                value={editingItem.description}
                onChange={(e) => setEditingItem({ ...editingItem, description: e.target.value })}
                placeholder="選填"
              />
            </div>
            <div style={styles.modalActions}>
              <button style={styles.cancelButton} onClick={() => setEditingItem(null)}>
                取消
              </button>
              <button style={styles.submitButton} onClick={handleSaveItem}>
                {editingItem.itemIndex !== null ? '更新' : '新增'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
