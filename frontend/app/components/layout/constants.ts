/**
 * Navigation Items for Dashboard
 * Defines sidebar menu structure and routes
 */

export interface NavItem {
  /** Unique identifier for the nav item */
  id: string
  /** Display label */
  label: string
  /** Route href */
  href: string
  /** Heroicon component (outline style) */
  icon: string // 'home' | 'sparkles' | 'shopping-cart' | 'cog-6-tooth'
  /** Optional badge count (e.g., notifications) */
  badge?: number
  /** Submenu items (future support) */
  children?: NavItem[]
}

/**
 * Main navigation items for the dashboard sidebar
 * These are rendered in order in the Sidebar component
 */
export const navigationItems: NavItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    href: '/dashboard',
    icon: 'home',
    badge: undefined,
  },
  {
    id: 'bots',
    label: 'Bots',
    href: '/dashboard/bots',
    icon: 'sparkles',
    badge: undefined,
  },
  {
    id: 'marketplaces',
    label: 'Marketplaces',
    href: '/dashboard/marketplaces',
    icon: 'shopping-cart',
    badge: undefined,
  },
  {
    id: 'settings',
    label: 'Settings',
    href: '/dashboard/settings',
    icon: 'cog-6-tooth',
    badge: undefined,
  },
]
