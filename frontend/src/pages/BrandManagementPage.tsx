/**
 * Brand Management Page
 * Allows admins to customize brand settings and theme
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../features/auth/hooks/useAuth';
import { getBrandById, updateBrand, updateBrandTheme } from '../features/brand/api/brandApi';
import { BrandResponse, ThemeConfig } from '../shared/types/brand';
import { useThemeContext } from '../theme/ThemeProvider';
import { isValidHexColor, defaultTheme } from '../theme/themeConfig';

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
    maxWidth: '1200px',
    margin: '0 auto',
    display: 'grid',
    gridTemplateColumns: '1fr 400px',
    gap: '2rem',
  } as React.CSSProperties,
  mainMobile: {
    gridTemplateColumns: '1fr',
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
  settingsColumn: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '1.5rem',
  } as React.CSSProperties,
  section: {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '1.5rem',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
  } as React.CSSProperties,
  sectionTitle: {
    fontSize: '1.125rem',
    fontWeight: '600',
    color: '#333',
    marginBottom: '1rem',
    paddingBottom: '0.75rem',
    borderBottom: '1px solid #e5e5e5',
  } as React.CSSProperties,
  formGroup: {
    marginBottom: '1.25rem',
  } as React.CSSProperties,
  label: {
    display: 'block',
    fontSize: '0.875rem',
    fontWeight: '500',
    color: '#444',
    marginBottom: '0.5rem',
  } as React.CSSProperties,
  input: {
    width: '100%',
    padding: '0.75rem 1rem',
    fontSize: '1rem',
    border: '1px solid #ddd',
    borderRadius: '8px',
    outline: 'none',
    transition: 'border-color 0.2s',
    boxSizing: 'border-box' as const,
  } as React.CSSProperties,
  textarea: {
    width: '100%',
    padding: '0.75rem 1rem',
    fontSize: '1rem',
    border: '1px solid #ddd',
    borderRadius: '8px',
    outline: 'none',
    minHeight: '100px',
    resize: 'vertical' as const,
    boxSizing: 'border-box' as const,
  } as React.CSSProperties,
  colorInputGroup: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
  } as React.CSSProperties,
  colorInput: {
    width: '50px',
    height: '40px',
    padding: '0',
    border: '1px solid #ddd',
    borderRadius: '8px',
    cursor: 'pointer',
  } as React.CSSProperties,
  colorTextInput: {
    flex: 1,
    padding: '0.75rem 1rem',
    fontSize: '1rem',
    border: '1px solid #ddd',
    borderRadius: '8px',
    outline: 'none',
    fontFamily: 'monospace',
  } as React.CSSProperties,
  select: {
    width: '100%',
    padding: '0.75rem 1rem',
    fontSize: '1rem',
    border: '1px solid #ddd',
    borderRadius: '8px',
    outline: 'none',
    backgroundColor: 'white',
    cursor: 'pointer',
  } as React.CSSProperties,
  previewColumn: {
    position: 'sticky' as const,
    top: '2rem',
    height: 'fit-content',
  } as React.CSSProperties,
  previewCard: {
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
    overflow: 'hidden',
  } as React.CSSProperties,
  previewHeader: {
    padding: '1rem 1.5rem',
    borderBottom: '1px solid #e5e5e5',
  } as React.CSSProperties,
  previewTitle: {
    fontSize: '1rem',
    fontWeight: '600',
    color: '#333',
  } as React.CSSProperties,
  previewContent: {
    padding: '1.5rem',
    minHeight: '300px',
  } as React.CSSProperties,
  previewBrand: {
    textAlign: 'center' as const,
    marginBottom: '1.5rem',
  } as React.CSSProperties,
  previewLogo: {
    width: '80px',
    height: '80px',
    borderRadius: '12px',
    objectFit: 'cover' as const,
    marginBottom: '0.75rem',
    backgroundColor: '#f5f5f5',
  } as React.CSSProperties,
  previewBrandName: {
    fontSize: '1.25rem',
    fontWeight: '600',
    marginBottom: '0.25rem',
  } as React.CSSProperties,
  previewBrandDesc: {
    fontSize: '0.875rem',
    color: '#666',
  } as React.CSSProperties,
  previewButtons: {
    display: 'flex',
    gap: '0.75rem',
    marginBottom: '1rem',
  } as React.CSSProperties,
  previewPrimaryBtn: {
    flex: 1,
    padding: '0.75rem',
    border: 'none',
    borderRadius: '8px',
    fontWeight: '600',
    color: 'white',
    cursor: 'pointer',
  } as React.CSSProperties,
  previewSecondaryBtn: {
    flex: 1,
    padding: '0.75rem',
    border: 'none',
    borderRadius: '8px',
    fontWeight: '600',
    color: 'white',
    cursor: 'pointer',
  } as React.CSSProperties,
  previewAccentBtn: {
    padding: '0.5rem 1rem',
    border: 'none',
    borderRadius: '6px',
    fontSize: '0.875rem',
    cursor: 'pointer',
  } as React.CSSProperties,
  previewCard2: {
    padding: '1rem',
    borderRadius: '8px',
    border: '1px solid #e5e5e5',
  } as React.CSSProperties,
  actions: {
    display: 'flex',
    gap: '1rem',
    marginTop: '1rem',
  } as React.CSSProperties,
  saveButton: {
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
  saveButtonDisabled: {
    backgroundColor: '#9ca3af',
    cursor: 'not-allowed',
  } as React.CSSProperties,
  resetButton: {
    padding: '1rem 1.5rem',
    fontSize: '1rem',
    fontWeight: '500',
    color: '#666',
    backgroundColor: 'white',
    border: '1px solid #ddd',
    borderRadius: '8px',
    cursor: 'pointer',
  } as React.CSSProperties,
  error: {
    padding: '1rem',
    backgroundColor: '#fef2f2',
    border: '1px solid #fecaca',
    borderRadius: '8px',
    color: '#b91c1c',
    marginBottom: '1rem',
  } as React.CSSProperties,
  success: {
    padding: '1rem',
    backgroundColor: '#f0fdf4',
    border: '1px solid #bbf7d0',
    borderRadius: '8px',
    color: '#166534',
    marginBottom: '1rem',
  } as React.CSSProperties,
  loading: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '400px',
  } as React.CSSProperties,
  spinner: {
    width: '40px',
    height: '40px',
    border: '4px solid #e5e5e5',
    borderTop: '4px solid #3b82f6',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  } as React.CSSProperties,
};

/**
 * Font family options
 */
const fontFamilyOptions = [
  { value: 'Inter, system-ui, sans-serif', label: 'Inter (Default)' },
  { value: 'system-ui, sans-serif', label: 'System UI' },
  { value: '"Noto Sans TC", sans-serif', label: 'Noto Sans TC' },
  { value: '"Roboto", sans-serif', label: 'Roboto' },
  { value: '"Open Sans", sans-serif', label: 'Open Sans' },
  { value: '"Lato", sans-serif', label: 'Lato' },
  { value: '"Poppins", sans-serif', label: 'Poppins' },
  { value: 'Georgia, serif', label: 'Georgia (Serif)' },
];

/**
 * Brand Management Page component
 */
export default function BrandManagementPage(): JSX.Element {
  const { brandSlug } = useParams<{ brandSlug: string }>();
  const { user } = useAuth();
  const { setTheme } = useThemeContext();

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [brand, setBrand] = useState<BrandResponse | null>(null);

  // Form state
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [logoUrl, setLogoUrl] = useState('');
  const [themeConfig, setThemeConfig] = useState<ThemeConfig>({ ...defaultTheme });

  // Load brand data
  useEffect(() => {
    async function loadBrand() {
      if (!user?.brandId) {
        setError('No brand associated with this account');
        setIsLoading(false);
        return;
      }

      try {
        const brandData = await getBrandById(user.brandId);
        setBrand(brandData);
        setName(brandData.name);
        setDescription(brandData.description || '');
        setLogoUrl(brandData.logoUrl || '');
        setThemeConfig({
          ...defaultTheme,
          ...brandData.themeConfig,
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load brand');
      } finally {
        setIsLoading(false);
      }
    }

    loadBrand();
  }, [user?.brandId]);

  // Update live preview when theme changes
  useEffect(() => {
    setTheme(themeConfig);
  }, [themeConfig, setTheme]);

  // Handle color change
  const handleColorChange = useCallback((key: keyof ThemeConfig, value: string) => {
    setThemeConfig(prev => ({ ...prev, [key]: value }));
    setSuccess(null);
  }, []);

  // Handle text color input (with validation)
  const handleColorTextChange = useCallback((key: keyof ThemeConfig, value: string) => {
    // Allow typing without immediate validation
    setThemeConfig(prev => ({ ...prev, [key]: value }));
    setSuccess(null);
  }, []);

  // Handle font family change
  const handleFontChange = useCallback((value: string) => {
    setThemeConfig(prev => ({ ...prev, fontFamily: value }));
    setSuccess(null);
  }, []);

  // Reset to defaults
  const handleReset = useCallback(() => {
    if (brand) {
      setName(brand.name);
      setDescription(brand.description || '');
      setLogoUrl(brand.logoUrl || '');
      setThemeConfig({
        ...defaultTheme,
        ...brand.themeConfig,
      });
    }
    setSuccess(null);
    setError(null);
  }, [brand]);

  // Save changes
  const handleSave = useCallback(async () => {
    if (!brand) return;

    // Validate colors
    const colorFields: (keyof ThemeConfig)[] = ['primaryColor', 'secondaryColor', 'accentColor', 'backgroundColor', 'textColor'];
    for (const field of colorFields) {
      const value = themeConfig[field];
      if (value && !isValidHexColor(value)) {
        setError(`Invalid color format for ${field}. Please use hex format (e.g., #FF6B6B)`);
        return;
      }
    }

    setIsSaving(true);
    setError(null);
    setSuccess(null);

    try {
      // Update brand info
      await updateBrand(brand.id, {
        name,
        description: description || undefined,
        logoUrl: logoUrl || undefined,
      });

      // Update theme
      await updateBrandTheme(brand.id, {
        themeConfig,
      });

      setSuccess('Brand settings saved successfully!');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save changes');
    } finally {
      setIsSaving(false);
    }
  }, [brand, name, description, logoUrl, themeConfig]);

  if (isLoading) {
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
        <div style={styles.loading}>
          <div style={styles.spinner} />
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
          input[type="color"]::-webkit-color-swatch-wrapper {
            padding: 0;
          }
          input[type="color"]::-webkit-color-swatch {
            border: none;
            border-radius: 6px;
          }
        `}
      </style>

      {/* Header */}
      <header style={styles.header}>
        <Link to={`/${brandSlug}/admin`} style={styles.backLink}>
          ← Back to Dashboard
        </Link>
        <span style={styles.headerTitle}>Brand Settings</span>
        <div />
      </header>

      {/* Main content */}
      <main style={styles.main}>
        {/* Settings Column */}
        <div style={styles.settingsColumn}>
          <div>
            <h1 style={styles.title}>Brand Settings</h1>
            <p style={styles.subtitle}>
              Customize your brand's appearance and identity
            </p>
          </div>

          {error && <div style={styles.error}>{error}</div>}
          {success && <div style={styles.success}>{success}</div>}

          {/* Brand Info Section */}
          <div style={styles.section}>
            <h2 style={styles.sectionTitle}>Brand Information</h2>

            <div style={styles.formGroup}>
              <label style={styles.label}>Brand Name</label>
              <input
                type="text"
                style={styles.input}
                value={name}
                onChange={(e) => { setName(e.target.value); setSuccess(null); }}
                placeholder="Enter brand name"
              />
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Description</label>
              <textarea
                style={styles.textarea}
                value={description}
                onChange={(e) => { setDescription(e.target.value); setSuccess(null); }}
                placeholder="Enter brand description"
              />
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Logo URL</label>
              <input
                type="url"
                style={styles.input}
                value={logoUrl}
                onChange={(e) => { setLogoUrl(e.target.value); setSuccess(null); }}
                placeholder="https://example.com/logo.png"
              />
            </div>
          </div>

          {/* Theme Colors Section */}
          <div style={styles.section}>
            <h2 style={styles.sectionTitle}>Theme Colors</h2>

            <div style={styles.formGroup}>
              <label style={styles.label}>Primary Color</label>
              <div style={styles.colorInputGroup}>
                <input
                  type="color"
                  style={styles.colorInput}
                  value={themeConfig.primaryColor}
                  onChange={(e) => handleColorChange('primaryColor', e.target.value)}
                />
                <input
                  type="text"
                  style={styles.colorTextInput}
                  value={themeConfig.primaryColor}
                  onChange={(e) => handleColorTextChange('primaryColor', e.target.value)}
                  placeholder="#FF6B6B"
                />
              </div>
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Secondary Color</label>
              <div style={styles.colorInputGroup}>
                <input
                  type="color"
                  style={styles.colorInput}
                  value={themeConfig.secondaryColor}
                  onChange={(e) => handleColorChange('secondaryColor', e.target.value)}
                />
                <input
                  type="text"
                  style={styles.colorTextInput}
                  value={themeConfig.secondaryColor}
                  onChange={(e) => handleColorTextChange('secondaryColor', e.target.value)}
                  placeholder="#4ECDC4"
                />
              </div>
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Accent Color</label>
              <div style={styles.colorInputGroup}>
                <input
                  type="color"
                  style={styles.colorInput}
                  value={themeConfig.accentColor || '#FFE66D'}
                  onChange={(e) => handleColorChange('accentColor', e.target.value)}
                />
                <input
                  type="text"
                  style={styles.colorTextInput}
                  value={themeConfig.accentColor || ''}
                  onChange={(e) => handleColorTextChange('accentColor', e.target.value)}
                  placeholder="#FFE66D"
                />
              </div>
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Background Color</label>
              <div style={styles.colorInputGroup}>
                <input
                  type="color"
                  style={styles.colorInput}
                  value={themeConfig.backgroundColor || '#FFFFFF'}
                  onChange={(e) => handleColorChange('backgroundColor', e.target.value)}
                />
                <input
                  type="text"
                  style={styles.colorTextInput}
                  value={themeConfig.backgroundColor || ''}
                  onChange={(e) => handleColorTextChange('backgroundColor', e.target.value)}
                  placeholder="#FFFFFF"
                />
              </div>
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Text Color</label>
              <div style={styles.colorInputGroup}>
                <input
                  type="color"
                  style={styles.colorInput}
                  value={themeConfig.textColor || '#2C3E50'}
                  onChange={(e) => handleColorChange('textColor', e.target.value)}
                />
                <input
                  type="text"
                  style={styles.colorTextInput}
                  value={themeConfig.textColor || ''}
                  onChange={(e) => handleColorTextChange('textColor', e.target.value)}
                  placeholder="#2C3E50"
                />
              </div>
            </div>
          </div>

          {/* Typography Section */}
          <div style={styles.section}>
            <h2 style={styles.sectionTitle}>Typography</h2>

            <div style={styles.formGroup}>
              <label style={styles.label}>Font Family</label>
              <select
                style={styles.select}
                value={themeConfig.fontFamily || 'Inter, system-ui, sans-serif'}
                onChange={(e) => handleFontChange(e.target.value)}
              >
                {fontFamilyOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Actions */}
          <div style={styles.actions}>
            <button style={styles.resetButton} onClick={handleReset}>
              Reset Changes
            </button>
            <button
              style={{
                ...styles.saveButton,
                ...(isSaving ? styles.saveButtonDisabled : {}),
              }}
              onClick={handleSave}
              disabled={isSaving}
            >
              {isSaving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>

        {/* Preview Column */}
        <div style={styles.previewColumn}>
          <div style={styles.previewCard}>
            <div style={styles.previewHeader}>
              <h3 style={styles.previewTitle}>Live Preview</h3>
            </div>
            <div
              style={{
                ...styles.previewContent,
                backgroundColor: themeConfig.backgroundColor || '#FFFFFF',
                fontFamily: themeConfig.fontFamily || 'Inter, system-ui, sans-serif',
              }}
            >
              {/* Brand Preview */}
              <div style={styles.previewBrand}>
                {logoUrl ? (
                  <img
                    src={logoUrl}
                    alt="Logo"
                    style={styles.previewLogo}
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none';
                    }}
                  />
                ) : (
                  <div
                    style={{
                      ...styles.previewLogo,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '2rem',
                    }}
                  >
                    🏪
                  </div>
                )}
                <div
                  style={{
                    ...styles.previewBrandName,
                    color: themeConfig.textColor || '#2C3E50',
                  }}
                >
                  {name || 'Brand Name'}
                </div>
                <div style={styles.previewBrandDesc}>
                  {description || 'Brand description goes here'}
                </div>
              </div>

              {/* Buttons Preview */}
              <div style={styles.previewButtons}>
                <button
                  style={{
                    ...styles.previewPrimaryBtn,
                    backgroundColor: themeConfig.primaryColor,
                  }}
                >
                  Primary
                </button>
                <button
                  style={{
                    ...styles.previewSecondaryBtn,
                    backgroundColor: themeConfig.secondaryColor,
                  }}
                >
                  Secondary
                </button>
              </div>

              <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
                <button
                  style={{
                    ...styles.previewAccentBtn,
                    backgroundColor: themeConfig.accentColor || '#FFE66D',
                    color: '#333',
                  }}
                >
                  Accent Button
                </button>
              </div>

              {/* Card Preview */}
              <div style={styles.previewCard2}>
                <div
                  style={{
                    fontWeight: '600',
                    marginBottom: '0.5rem',
                    color: themeConfig.textColor || '#2C3E50',
                  }}
                >
                  Sample Menu Item
                </div>
                <div style={{ fontSize: '0.875rem', color: '#666', marginBottom: '0.5rem' }}>
                  Delicious item description
                </div>
                <div
                  style={{
                    fontWeight: '600',
                    color: themeConfig.primaryColor,
                  }}
                >
                  $120
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
