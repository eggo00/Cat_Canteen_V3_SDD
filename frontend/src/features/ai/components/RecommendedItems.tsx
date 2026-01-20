/**
 * Recommended Items Component
 * Displays AI-powered menu item recommendations
 */

import React from 'react';
import { useRecommendations } from '../hooks/useRecommendations';
import { RecommendationItem } from '../../../shared/types/ai';

/**
 * Component styles
 */
const styles = {
  container: {
    marginBottom: '2rem',
  } as React.CSSProperties,
  header: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    marginBottom: '1rem',
  } as React.CSSProperties,
  title: {
    fontSize: '1.25rem',
    fontWeight: '600',
    color: 'var(--color-text, #333)',
    margin: 0,
  } as React.CSSProperties,
  badge: {
    backgroundColor: 'var(--color-primary, #3498db)',
    color: 'white',
    fontSize: '0.75rem',
    padding: '0.25rem 0.5rem',
    borderRadius: '12px',
  } as React.CSSProperties,
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '1rem',
  } as React.CSSProperties,
  card: {
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
    overflow: 'hidden',
    transition: 'transform 0.2s, box-shadow 0.2s',
    cursor: 'pointer',
  } as React.CSSProperties,
  cardHover: {
    transform: 'translateY(-2px)',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.12)',
  } as React.CSSProperties,
  imageContainer: {
    position: 'relative' as const,
    paddingTop: '56.25%', // 16:9 aspect ratio
    backgroundColor: '#f5f5f5',
    overflow: 'hidden',
  } as React.CSSProperties,
  image: {
    position: 'absolute' as const,
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    objectFit: 'cover' as const,
  } as React.CSSProperties,
  placeholder: {
    position: 'absolute' as const,
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    fontSize: '3rem',
  } as React.CSSProperties,
  scoreBadge: {
    position: 'absolute' as const,
    top: '0.5rem',
    right: '0.5rem',
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    color: 'white',
    fontSize: '0.75rem',
    padding: '0.25rem 0.5rem',
    borderRadius: '4px',
  } as React.CSSProperties,
  content: {
    padding: '1rem',
  } as React.CSSProperties,
  itemName: {
    fontSize: '1rem',
    fontWeight: '600',
    margin: '0 0 0.25rem 0',
    color: 'var(--color-text, #333)',
  } as React.CSSProperties,
  category: {
    fontSize: '0.875rem',
    color: '#666',
    margin: '0 0 0.5rem 0',
  } as React.CSSProperties,
  reason: {
    fontSize: '0.875rem',
    color: 'var(--color-primary, #3498db)',
    margin: '0 0 0.5rem 0',
    display: 'flex',
    alignItems: 'center',
    gap: '0.25rem',
  } as React.CSSProperties,
  price: {
    fontSize: '1.125rem',
    fontWeight: '600',
    color: 'var(--color-primary, #3498db)',
    margin: 0,
  } as React.CSSProperties,
  loading: {
    textAlign: 'center' as const,
    padding: '2rem',
    color: '#666',
  } as React.CSSProperties,
  error: {
    textAlign: 'center' as const,
    padding: '2rem',
    color: '#e74c3c',
  } as React.CSSProperties,
  empty: {
    textAlign: 'center' as const,
    padding: '2rem',
    color: '#999',
  } as React.CSSProperties,
};

/**
 * Single recommendation card component
 */
interface RecommendationCardProps {
  item: RecommendationItem;
  onClick?: (item: RecommendationItem) => void;
}

function RecommendationCard({ item, onClick }: RecommendationCardProps) {
  const [isHovered, setIsHovered] = React.useState(false);

  const handleClick = () => {
    if (onClick) {
      onClick(item);
    }
  };

  return (
    <div
      style={{
        ...styles.card,
        ...(isHovered ? styles.cardHover : {}),
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleClick}
    >
      {/* Image */}
      <div style={styles.imageContainer}>
        {item.imageUrl ? (
          <img
            src={item.imageUrl}
            alt={item.itemName}
            style={styles.image}
            loading="lazy"
          />
        ) : (
          <span style={styles.placeholder}>🍽️</span>
        )}
        <span style={styles.scoreBadge}>
          {Math.round(item.score * 100)}% 推薦
        </span>
      </div>

      {/* Content */}
      <div style={styles.content}>
        <h3 style={styles.itemName}>{item.itemName}</h3>
        {item.categoryName && (
          <p style={styles.category}>{item.categoryName}</p>
        )}
        <p style={styles.reason}>
          <span>✨</span>
          {item.reason}
        </p>
        {item.price !== null && (
          <p style={styles.price}>NT$ {item.price}</p>
        )}
      </div>
    </div>
  );
}

/**
 * Main recommended items component
 */
interface RecommendedItemsProps {
  brandSlug: string;
  limit?: number;
  userId?: string;
  onItemClick?: (item: RecommendationItem) => void;
  showTitle?: boolean;
  className?: string;
}

export function RecommendedItems({
  brandSlug,
  limit = 5,
  userId,
  onItemClick,
  showTitle = true,
  className,
}: RecommendedItemsProps) {
  const { data, isLoading, isError, error } = useRecommendations(brandSlug, {
    userId,
    limit,
  });

  if (isLoading) {
    return (
      <div style={styles.loading}>
        <span>正在載入推薦...</span>
      </div>
    );
  }

  if (isError) {
    return (
      <div style={styles.error}>
        <span>無法載入推薦: {error?.message || '未知錯誤'}</span>
      </div>
    );
  }

  if (!data || data.recommendations.length === 0) {
    return (
      <div style={styles.empty}>
        <span>目前沒有推薦項目</span>
      </div>
    );
  }

  return (
    <div style={styles.container} className={className}>
      {showTitle && (
        <div style={styles.header}>
          <h2 style={styles.title}>為您推薦</h2>
          <span style={styles.badge}>AI</span>
        </div>
      )}

      <div style={styles.grid}>
        {data.recommendations.map((item) => (
          <RecommendationCard
            key={item.itemId}
            item={item}
            onClick={onItemClick}
          />
        ))}
      </div>
    </div>
  );
}

export default RecommendedItems;
