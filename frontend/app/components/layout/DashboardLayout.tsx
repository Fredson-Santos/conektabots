'use client'

import React, { useState, useRef } from 'react'
import { Sidebar } from './Sidebar'
import { Header, type Breadcrumb, type User } from './Header'
import { NavItem } from './constants'

export interface DashboardLayoutProps {
  /** Main content to render */
  children: React.ReactNode
  /** Sidebar navigation items */
  sidebarItems?: NavItem[]
  /** Page title for header */
  title?: string
  /** Page subtitle for header */
  subtitle?: string
  /** Breadcrumb navigation */
  breadcrumbs?: Breadcrumb[]
  /** Current logged-in user */
  user?: User
  /** Optional header action buttons/elements */
  actions?: React.ReactNode
  /** Callback when user logs out */
  onLogout?: () => void
}

/**
 * DashboardLayout Component
 *
 * Main layout container combining sidebar, header, and main content.
 * Handles responsive behavior (desktop sidebar, mobile drawer).
 *
 * Features:
 * - CSS Grid layout: sidebar (240px) + header (64px) + content
 * - Desktop: Sidebar always visible, header sticky
 * - Mobile: Sidebar as drawer overlay, hamburger menu in header
 * - Background: Light gray (for contrast with white cards)
 * - Responsive: 320px to 1440px+
 * - Keyboard accessible: Escape closes drawer, Tab navigation
 * - Semantic structure with proper ARIA labels
 *
 * Layout Structure:
 * ```
 * ┌──────────────────────────────────┐
 * │ SIDEBAR  │ HEADER (sticky)       │  64px
 * │ (240px)  ├──────────────────────┤
 * │          │ MAIN CONTENT (scroll │
 * │          │ independently)       │
 * └──────────────────────────────────┘
 * ```
 *
 * @example
 * ```tsx
 * export default function BotsPage() {
 *   return (
 *     <DashboardLayout
 *       sidebarItems={navigationItems}
 *       title="Bots Management"
 *       breadcrumbs={[
 *         { label: 'Dashboard', href: '/dashboard' },
 *         { label: 'Bots' },
 *       ]}
 *       user={{ name: 'John Doe', email: 'john@example.com' }}
 *       onLogout={() => router.push('/login')}
 *     >
 *       {/* Page content here *\/}
 *     </DashboardLayout>
 *   )
 * }
 * ```
 */
export const DashboardLayout = React.forwardRef<
  HTMLDivElement,
  DashboardLayoutProps
>(
  (
    {
      children,
      sidebarItems = [],
      title,
      subtitle,
      breadcrumbs,
      user,
      actions,
      onLogout,
    },
    ref
  ) => {
    const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false)
    const sidebarRef = useRef<HTMLDivElement>(null)
    const headerRef = useRef<HTMLElement>(null)

    const handleCloseMobileDrawer = () => {
      setMobileDrawerOpen(false)
    }

    return (
      <div
        ref={ref}
        className="min-h-screen bg-gray-50"
      >
        {/* Desktop Sidebar (hidden on mobile, fixed on desktop) */}
        <div className="md:block hidden fixed left-0 top-16 w-60 h-[calc(100vh-64px)] z-40">
          <Sidebar
            ref={sidebarRef}
            items={sidebarItems}
            onClose={handleCloseMobileDrawer}
          />
        </div>

        {/* Mobile Sidebar (drawer overlay) */}
        <Sidebar
          ref={sidebarRef}
          items={sidebarItems}
          isOpen={mobileDrawerOpen}
          onClose={handleCloseMobileDrawer}
        />

        {/* Header */}
        <Header
          ref={headerRef}
          title={title}
          subtitle={subtitle}
          breadcrumbs={breadcrumbs}
          user={user}
          actions={actions}
          onMobileMenuToggle={() => setMobileDrawerOpen(!mobileDrawerOpen)}
          onLogout={onLogout}
        />

        {/* Main Content Area */}
        <main
          className="pt-16 md:ml-60 h-[calc(100vh-64px)] overflow-y-auto"
          role="main"
        >
          {/* Content padding */}
          <div className="px-4 py-6 sm:px-6 md:px-8 lg:px-10 max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    )
  }
)

DashboardLayout.displayName = 'DashboardLayout'
