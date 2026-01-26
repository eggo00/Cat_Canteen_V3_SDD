/**
 * Admin Dashboard Page
 * Main entry point for brand administrators
 */

import React from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../features/auth/hooks/useAuth';

/**
 * Dashboard card styles
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
  headerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
  } as React.CSSProperties,
  logo: {
    fontSize: '1.5rem',
    fontWeight: '600',
    color: '#333',
  } as React.CSSProperties,
  brandBadge: {
    backgroundColor: '#e0f2fe',
    color: '#0369a1',
    padding: '0.25rem 0.75rem',
    borderRadius: '9999px',
    fontSize: '0.875rem',
    fontWeight: '500',
  } as React.CSSProperties,
  userInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
  } as React.CSSProperties,
  userName: {
    fontSize: '0.875rem',
    color: '#666',
  } as React.CSSProperties,
  logoutButton: {
    padding: '0.5rem 1rem',
    fontSize: '0.875rem',
    color: '#666',
    backgroundColor: 'white',
    border: '1px solid #ddd',
    borderRadius: '6px',
    cursor: 'pointer',
  } as React.CSSProperties,
  main: {
    padding: '2rem',
    maxWidth: '1200px',
    margin: '0 auto',
  } as React.CSSProperties,
  title: {
    fontSize: '1.75rem',
    fontWeight: '600',
    color: '#333',
    marginBottom: '0.5rem',
  } as React.CSSProperties,
  subtitle: {
    fontSize: '1rem',
    color: '#666',
    marginBottom: '2rem',
  } as React.CSSProperties,
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '1.5rem',
  } as React.CSSProperties,
  card: {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '1.5rem',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
    border: '1px solid #e5e5e5',
    textDecoration: 'none',
    color: 'inherit',
    display: 'block',
    transition: 'box-shadow 0.2s, transform 0.2s',
  } as React.CSSProperties,
  cardHover: {
    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
    transform: 'translateY(-2px)',
  } as React.CSSProperties,
  cardIcon: {
    fontSize: '2rem',
    marginBottom: '1rem',
  } as React.CSSProperties,
  cardTitle: {
    fontSize: '1.125rem',
    fontWeight: '600',
    color: '#333',
    marginBottom: '0.5rem',
  } as React.CSSProperties,
  cardDescription: {
    fontSize: '0.875rem',
    color: '#666',
    lineHeight: '1.5',
  } as React.CSSProperties,
  cardDisabled: {
    opacity: 0.5,
    cursor: 'not-allowed',
  } as React.CSSProperties,
  comingSoon: {
    display: 'inline-block',
    backgroundColor: '#fef3c7',
    color: '#92400e',
    padding: '0.125rem 0.5rem',
    borderRadius: '4px',
    fontSize: '0.75rem',
    marginLeft: '0.5rem',
  } as React.CSSProperties,
};

/**
 * Dashboard card component
 */
interface DashboardCardProps {
  to: string;
  icon: string;
  title: string;
  description: string;
  disabled?: boolean;
  comingSoon?: boolean;
}

function DashboardCard({ to, icon, title, description, disabled, comingSoon }: DashboardCardProps) {
  const [isHovered, setIsHovered] = React.useState(false);

  if (disabled) {
    return (
      <div
        style={{
          ...styles.card,
          ...styles.cardDisabled,
        }}
      >
        <div style={styles.cardIcon}>{icon}</div>
        <div style={styles.cardTitle}>
          {title}
          {comingSoon && <span style={styles.comingSoon}>Coming Soon</span>}
        </div>
        <div style={styles.cardDescription}>{description}</div>
      </div>
    );
  }

  return (
    <Link
      to={to}
      style={{
        ...styles.card,
        ...(isHovered ? styles.cardHover : {}),
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div style={styles.cardIcon}>{icon}</div>
      <div style={styles.cardTitle}>{title}</div>
      <div style={styles.cardDescription}>{description}</div>
    </Link>
  );
}

/**
 * Admin Dashboard Page component
 */
export default function AdminDashboardPage(): JSX.Element {
  const { brandSlug } = useParams<{ brandSlug: string }>();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerLeft}>
          <span style={styles.logo}>Cat Canteen Admin</span>
          {brandSlug && <span style={styles.brandBadge}>{brandSlug}</span>}
        </div>
        <div style={styles.userInfo}>
          <span style={styles.userName}>
            {user?.name || user?.email || 'Admin'}
          </span>
          <button style={styles.logoutButton} onClick={handleLogout}>
            Logout
          </button>
        </div>
      </header>

      {/* Main content */}
      <main style={styles.main}>
        <h1 style={styles.title}>Dashboard</h1>
        <p style={styles.subtitle}>
          Manage your restaurant's menu, orders, and settings
        </p>

        <div style={styles.grid}>
          {/* Menu Upload - Phase I AI Recognition */}
          <DashboardCard
            to={`/${brandSlug}/admin/menu/upload`}
            icon="📷"
            title="AI Menu Upload"
            description="Upload menu images and let AI automatically extract menu items. Review and edit before publishing."
          />

          {/* Menu Management */}
          <DashboardCard
            to={`/${brandSlug}/admin/menu`}
            icon="📋"
            title="Menu Management"
            description="View and edit your current menu items, categories, and prices."
            disabled
            comingSoon
          />

          {/* Brand Settings */}
          <DashboardCard
            to={`/${brandSlug}/admin/brand`}
            icon="🎨"
            title="Brand Settings"
            description="Customize your brand's appearance including logo, colors, and theme."
          />

          {/* Analytics */}
          <DashboardCard
            to={`/${brandSlug}/analytics`}
            icon="📊"
            title="Analytics"
            description="View sales reports, popular items, and demand forecasts."
          />

          {/* Orders */}
          <DashboardCard
            to={`/${brandSlug}/admin/orders`}
            icon="🛒"
            title="Order Management"
            description="View and manage incoming orders."
            disabled
            comingSoon
          />

          {/* Users */}
          <DashboardCard
            to={`/${brandSlug}/admin/users`}
            icon="👥"
            title="User Management"
            description="Manage staff accounts and permissions."
            disabled
            comingSoon
          />
        </div>
      </main>
    </div>
  );
}
