/**
 * Menu Upload Page
 * AI-powered menu extraction from images (Phase I)
 */

import React, { useState, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../features/auth/hooks/useAuth';
import { extractMenuFromImage, getExtractionQuota } from '../features/ai/api/aiApi';
import { MenuDraft, MenuDraftCategory, MenuDraftItem, ExtractionQuota } from '../shared/types/menuExtract';

/**
 * Page styles
 */
const styles = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
  } as React.CSSProperties,
  header: {
    backgroundColor: 'white',
    borderBottom: '1px solid #e5e5e5',
    padding: '1rem 2rem',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  } as React.CSSProperties,
  backLink: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    color: '#666',
    textDecoration: 'none',
    fontSize: '0.875rem',
  } as React.CSSProperties,
  headerTitle: {
    fontSize: '1.25rem',
    fontWeight: '600',
    color: '#333',
  } as React.CSSProperties,
  main: {
    padding: '2rem',
    maxWidth: '1000px',
    margin: '0 auto',
  } as React.CSSProperties,
  title: {
    fontSize: '1.5rem',
    fontWeight: '600',
    color: '#333',
    marginBottom: '0.5rem',
  } as React.CSSProperties,
  subtitle: {
    fontSize: '1rem',
    color: '#666',
    marginBottom: '2rem',
  } as React.CSSProperties,
  uploadSection: {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '2rem',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
    marginBottom: '2rem',
  } as React.CSSProperties,
  dropzone: {
    border: '2px dashed #ddd',
    borderRadius: '8px',
    padding: '3rem 2rem',
    textAlign: 'center' as const,
    cursor: 'pointer',
    transition: 'border-color 0.2s, background-color 0.2s',
  } as React.CSSProperties,
  dropzoneActive: {
    borderColor: '#3b82f6',
    backgroundColor: '#eff6ff',
  } as React.CSSProperties,
  dropzoneIcon: {
    fontSize: '3rem',
    marginBottom: '1rem',
  } as React.CSSProperties,
  dropzoneText: {
    fontSize: '1rem',
    color: '#666',
    marginBottom: '0.5rem',
  } as React.CSSProperties,
  dropzoneSubtext: {
    fontSize: '0.875rem',
    color: '#999',
  } as React.CSSProperties,
  fileInput: {
    display: 'none',
  } as React.CSSProperties,
  previewSection: {
    marginTop: '1.5rem',
    padding: '1rem',
    backgroundColor: '#f9fafb',
    borderRadius: '8px',
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
  } as React.CSSProperties,
  previewImage: {
    width: '80px',
    height: '80px',
    objectFit: 'cover' as const,
    borderRadius: '8px',
  } as React.CSSProperties,
  previewInfo: {
    flex: 1,
  } as React.CSSProperties,
  previewName: {
    fontWeight: '500',
    color: '#333',
    marginBottom: '0.25rem',
  } as React.CSSProperties,
  previewSize: {
    fontSize: '0.875rem',
    color: '#666',
  } as React.CSSProperties,
  removeButton: {
    padding: '0.5rem',
    color: '#ef4444',
    backgroundColor: 'transparent',
    border: 'none',
    cursor: 'pointer',
    fontSize: '1.25rem',
  } as React.CSSProperties,
  extractButton: {
    width: '100%',
    padding: '1rem',
    fontSize: '1rem',
    fontWeight: '600',
    color: 'white',
    backgroundColor: '#3b82f6',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    marginTop: '1.5rem',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '0.5rem',
  } as React.CSSProperties,
  extractButtonDisabled: {
    backgroundColor: '#9ca3af',
    cursor: 'not-allowed',
  } as React.CSSProperties,
  quotaInfo: {
    marginTop: '1rem',
    padding: '0.75rem 1rem',
    backgroundColor: '#f0f9ff',
    borderRadius: '6px',
    fontSize: '0.875rem',
    color: '#0369a1',
  } as React.CSSProperties,
  error: {
    marginTop: '1rem',
    padding: '1rem',
    backgroundColor: '#fef2f2',
    border: '1px solid #fecaca',
    borderRadius: '8px',
    color: '#b91c1c',
  } as React.CSSProperties,
  resultSection: {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '2rem',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
  } as React.CSSProperties,
  resultHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1.5rem',
    paddingBottom: '1rem',
    borderBottom: '1px solid #e5e5e5',
  } as React.CSSProperties,
  resultTitle: {
    fontSize: '1.25rem',
    fontWeight: '600',
    color: '#333',
  } as React.CSSProperties,
  resultStats: {
    display: 'flex',
    gap: '1rem',
    fontSize: '0.875rem',
  } as React.CSSProperties,
  statBadge: {
    padding: '0.25rem 0.75rem',
    borderRadius: '9999px',
    backgroundColor: '#e0f2fe',
    color: '#0369a1',
  } as React.CSSProperties,
  statBadgeWarning: {
    backgroundColor: '#fef3c7',
    color: '#92400e',
  } as React.CSSProperties,
  warnings: {
    marginBottom: '1.5rem',
    padding: '1rem',
    backgroundColor: '#fffbeb',
    border: '1px solid #fde68a',
    borderRadius: '8px',
  } as React.CSSProperties,
  warningTitle: {
    fontWeight: '600',
    color: '#92400e',
    marginBottom: '0.5rem',
  } as React.CSSProperties,
  warningList: {
    margin: 0,
    paddingLeft: '1.25rem',
    color: '#92400e',
    fontSize: '0.875rem',
  } as React.CSSProperties,
  category: {
    marginBottom: '1.5rem',
  } as React.CSSProperties,
  categoryHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    marginBottom: '1rem',
  } as React.CSSProperties,
  categoryName: {
    fontSize: '1.125rem',
    fontWeight: '600',
    color: '#333',
  } as React.CSSProperties,
  categoryCount: {
    fontSize: '0.875rem',
    color: '#666',
  } as React.CSSProperties,
  itemsGrid: {
    display: 'grid',
    gap: '0.75rem',
  } as React.CSSProperties,
  item: {
    display: 'flex',
    alignItems: 'center',
    padding: '1rem',
    backgroundColor: '#f9fafb',
    borderRadius: '8px',
    border: '1px solid #e5e5e5',
  } as React.CSSProperties,
  itemNeedsReview: {
    borderColor: '#fde68a',
    backgroundColor: '#fffbeb',
  } as React.CSSProperties,
  itemInfo: {
    flex: 1,
  } as React.CSSProperties,
  itemName: {
    fontWeight: '500',
    color: '#333',
    marginBottom: '0.25rem',
  } as React.CSSProperties,
  itemDescription: {
    fontSize: '0.875rem',
    color: '#666',
  } as React.CSSProperties,
  itemPrice: {
    fontWeight: '600',
    color: '#333',
    fontSize: '1.125rem',
  } as React.CSSProperties,
  reviewBadge: {
    marginLeft: '0.5rem',
    padding: '0.125rem 0.5rem',
    backgroundColor: '#fef3c7',
    color: '#92400e',
    borderRadius: '4px',
    fontSize: '0.75rem',
  } as React.CSSProperties,
  actions: {
    display: 'flex',
    gap: '1rem',
    marginTop: '2rem',
    paddingTop: '1.5rem',
    borderTop: '1px solid #e5e5e5',
  } as React.CSSProperties,
  primaryButton: {
    flex: 1,
    padding: '1rem',
    fontSize: '1rem',
    fontWeight: '600',
    color: 'white',
    backgroundColor: '#22c55e',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
  } as React.CSSProperties,
  secondaryButton: {
    padding: '1rem 1.5rem',
    fontSize: '1rem',
    fontWeight: '500',
    color: '#666',
    backgroundColor: 'white',
    border: '1px solid #ddd',
    borderRadius: '8px',
    cursor: 'pointer',
  } as React.CSSProperties,
  loading: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    gap: '1rem',
    padding: '3rem',
  } as React.CSSProperties,
  spinner: {
    width: '48px',
    height: '48px',
    border: '4px solid #e5e5e5',
    borderTop: '4px solid #3b82f6',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  } as React.CSSProperties,
  loadingText: {
    color: '#666',
    fontSize: '1rem',
  } as React.CSSProperties,
};

/**
 * Menu Upload Page component
 */
export default function MenuUploadPage(): JSX.Element {
  const { brandSlug } = useParams<{ brandSlug: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [quota, setQuota] = useState<ExtractionQuota | null>(null);
  const [menuDraft, setMenuDraft] = useState<MenuDraft | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  // File selection handler
  const handleFileSelect = useCallback((file: File) => {
    if (!file.type.startsWith('image/')) {
      setError('Please select an image file (JPEG, PNG, or WebP)');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError('Image size must be less than 10MB');
      return;
    }

    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setError(null);
    setMenuDraft(null);
  }, []);

  // Drag and drop handlers
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  }, [handleFileSelect]);

  // File input change handler
  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  }, [handleFileSelect]);

  // Remove selected file
  const handleRemoveFile = useCallback(() => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setMenuDraft(null);
    setError(null);
  }, []);

  // Extract menu from image
  const handleExtract = useCallback(async () => {
    if (!selectedFile || !user?.brandId || !user?.id) {
      setError('Missing required information');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const draft = await extractMenuFromImage(selectedFile, user.brandId, user.id);
      setMenuDraft(draft);

      // Refresh quota
      const newQuota = await getExtractionQuota(user.brandId, user.id);
      setQuota(newQuota);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to extract menu';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [selectedFile, user]);

  // Confirm and save menu
  const handleConfirm = useCallback(() => {
    // TODO: Implement menu save logic
    alert('Menu saving will be implemented in the next phase. For now, the extraction is complete.');
    navigate(`/${brandSlug}/admin`);
  }, [brandSlug, navigate]);

  // Format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div style={styles.container}>
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>

      {/* Header */}
      <header style={styles.header}>
        <Link to={`/${brandSlug}/admin`} style={styles.backLink}>
          ← Back to Dashboard
        </Link>
        <span style={styles.headerTitle}>AI Menu Upload</span>
        <div />
      </header>

      {/* Main content */}
      <main style={styles.main}>
        <h1 style={styles.title}>Upload Menu Image</h1>
        <p style={styles.subtitle}>
          Upload a photo of your menu and our AI will automatically extract all items with prices.
        </p>

        {/* Upload Section */}
        <div style={styles.uploadSection}>
          {!menuDraft ? (
            <>
              {/* Dropzone */}
              <div
                style={{
                  ...styles.dropzone,
                  ...(isDragOver ? styles.dropzoneActive : {}),
                }}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => document.getElementById('fileInput')?.click()}
              >
                <div style={styles.dropzoneIcon}>📷</div>
                <div style={styles.dropzoneText}>
                  Drag and drop your menu image here, or click to browse
                </div>
                <div style={styles.dropzoneSubtext}>
                  Supports JPEG, PNG, WebP (max 10MB)
                </div>
                <input
                  id="fileInput"
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  style={styles.fileInput}
                  onChange={handleInputChange}
                />
              </div>

              {/* Preview */}
              {selectedFile && previewUrl && (
                <div style={styles.previewSection}>
                  <img
                    src={previewUrl}
                    alt="Preview"
                    style={styles.previewImage}
                  />
                  <div style={styles.previewInfo}>
                    <div style={styles.previewName}>{selectedFile.name}</div>
                    <div style={styles.previewSize}>
                      {formatFileSize(selectedFile.size)}
                    </div>
                  </div>
                  <button
                    style={styles.removeButton}
                    onClick={handleRemoveFile}
                    title="Remove"
                  >
                    ×
                  </button>
                </div>
              )}

              {/* Error */}
              {error && <div style={styles.error}>{error}</div>}

              {/* Quota info */}
              {quota && (
                <div style={styles.quotaInfo}>
                  Daily remaining: {quota.brandDailyRemaining} |
                  Hourly remaining: {quota.userHourlyRemaining}
                </div>
              )}

              {/* Extract button */}
              <button
                style={{
                  ...styles.extractButton,
                  ...((!selectedFile || isLoading) ? styles.extractButtonDisabled : {}),
                }}
                onClick={handleExtract}
                disabled={!selectedFile || isLoading}
              >
                {isLoading ? (
                  <>
                    <div style={{ ...styles.spinner, width: '20px', height: '20px', borderWidth: '2px' }} />
                    Analyzing...
                  </>
                ) : (
                  <>
                    🤖 Extract Menu with AI
                  </>
                )}
              </button>
            </>
          ) : (
            /* Loading state */
            isLoading && (
              <div style={styles.loading}>
                <div style={styles.spinner} />
                <div style={styles.loadingText}>
                  AI is analyzing your menu image...
                </div>
              </div>
            )
          )}
        </div>

        {/* Results Section */}
        {menuDraft && !isLoading && (
          <div style={styles.resultSection}>
            <div style={styles.resultHeader}>
              <h2 style={styles.resultTitle}>Extraction Results</h2>
              <div style={styles.resultStats}>
                <span style={styles.statBadge}>
                  {menuDraft.stats.totalItems} items found
                </span>
                {menuDraft.stats.itemsNeedReview > 0 && (
                  <span style={{ ...styles.statBadge, ...styles.statBadgeWarning }}>
                    {menuDraft.stats.itemsNeedReview} need review
                  </span>
                )}
              </div>
            </div>

            {/* Warnings */}
            {menuDraft.warnings.length > 0 && (
              <div style={styles.warnings}>
                <div style={styles.warningTitle}>Items need attention:</div>
                <ul style={styles.warningList}>
                  {menuDraft.warnings.map((warning, index) => (
                    <li key={index}>{warning}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Categories and Items */}
            {menuDraft.categories.map((category) => (
              <div key={category.tempId} style={styles.category}>
                <div style={styles.categoryHeader}>
                  <span style={styles.categoryName}>{category.name}</span>
                  <span style={styles.categoryCount}>
                    ({category.items.length} items)
                  </span>
                </div>
                <div style={styles.itemsGrid}>
                  {category.items.map((item) => (
                    <div
                      key={item.tempId}
                      style={{
                        ...styles.item,
                        ...(item.needsReview ? styles.itemNeedsReview : {}),
                      }}
                    >
                      <div style={styles.itemInfo}>
                        <div style={styles.itemName}>
                          {item.name}
                          {item.needsReview && (
                            <span style={styles.reviewBadge}>Needs Review</span>
                          )}
                        </div>
                        {item.description && (
                          <div style={styles.itemDescription}>
                            {item.description}
                          </div>
                        )}
                      </div>
                      <div style={styles.itemPrice}>
                        ${item.price.toFixed(0)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}

            {/* Actions */}
            <div style={styles.actions}>
              <button style={styles.secondaryButton} onClick={handleRemoveFile}>
                Upload Different Image
              </button>
              <button style={styles.primaryButton} onClick={handleConfirm}>
                Confirm & Save Menu
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
