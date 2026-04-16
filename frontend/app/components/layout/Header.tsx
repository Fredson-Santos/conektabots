'use client'

import React, { useEffect, useRef, useState } from 'react'
import Link from 'next/link'
import {
  Bars3Icon,
  ChevronDownIcon,
  ArrowRightOnRectangleIcon,
} from '@heroicons/react/24/outline'

export interface Breadcrumb {
  /** Display label */
  label: string
  /** Optional link href */
  href?: string
}

export interface User {
  /** User display name */
  name: string
  /** User email */
  email: string
  /** Optional avatar URL */
  avatar?: string
}

export interface HeaderProps {
  /** Page title */
  title?: string
  /** Optional subtitle */
  subtitle?: string
  /** Breadcrumb navigation */
  breadcrumbs?: Breadcrumb[]
  /** Current logged-in user */
  user?: User
  /** Callback for mobile hamburger menu toggle */
  onMobileMenuToggle?: () => void
  /** Callback when user clicks logout */
  onLogout?: () => void
  /** Optional action buttons/elements on the right */
  actions?: React.ReactNode
}

/**
 * Header Component
 *
 * Top navigation bar with breadcrumbs, page title, and user menu.
 * Features:
 * - Sticky positioning at top
 * - Breadcrumb navigation (responsive: hidden on mobile)
 * - User menu dropdown (keyboard accessible)
 * - Mobile hamburger menu toggle
 * - 64px fixed height
 * - Semantic HTML with proper ARIA labels
 *
 * @example
 * ```tsx
 * <Header
 *   title="Bots Management"
 *   breadcrumbs={[
 *     { label: 'Dashboard', href: '/dashboard' },
 *     { label: 'Bots' },
 *   ]}
 *   user={{ name: 'John Doe', email: 'john@example.com' }}
 *   onMobileMenuToggle={() => setMenuOpen(!menuOpen)}
 *   onLogout={() => handleLogout()}
 * />
 * ```
 */
export const Header = React.forwardRef<HTMLElement, HeaderProps>(
  (
    {
      title,
      subtitle,
      breadcrumbs,
      user,
      onMobileMenuToggle,
      onLogout,
      actions,
    },
    ref
  ) => {
    const [userMenuOpen, setUserMenuOpen] = useState(false)
    const userMenuRef = useRef<HTMLDivElement>(null)

    // Close menu when clicking outside
    useEffect(() => {
      const handleClickOutside = (e: MouseEvent) => {
        if (
          userMenuOpen &&
          userMenuRef.current &&
          !userMenuRef.current.contains(e.target as Node)
        ) {
          setUserMenuOpen(false)
        }
      }

      window.addEventListener('click', handleClickOutside)
      return () => window.removeEventListener('click', handleClickOutside)
    }, [userMenuOpen])

    // Handle keyboard navigation in dropdown
    const handleUserMenuKeyDown = (e: React.KeyboardEvent) => {
      if (e.key === 'Escape') {
        setUserMenuOpen(false)
      }
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        const logoutBtn = userMenuRef.current?.querySelector(
          '[data-logout-btn]'
        ) as HTMLButtonElement
        logoutBtn?.focus()
      }
    }

    const handleLogoutClick = () => {
      setUserMenuOpen(false)
      onLogout?.()
    }

    return (
      <header
        ref={ref}
        className="fixed top-0 left-0 right-0 h-16 bg-white border-b border-gray-200 z-30 md:z-20"
      >
        <div className="h-full px-4 md:px-6 flex items-center justify-between gap-4">
          {/* Left side: Hamburger + Breadcrumbs + Title */}
          <div className="flex items-center gap-4 min-w-0 flex-1">
            {/* Mobile hamburger menu */}
            <button
              onClick={onMobileMenuToggle}
              className="md:hidden p-1.5 text-gray-500 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md"
              aria-label="Toggle navigation menu"
            >
              <Bars3Icon className="w-5 h-5" />
            </button>

            {/* Breadcrumbs */}
            {breadcrumbs && breadcrumbs.length > 0 && (
              <nav className="hidden sm:flex items-center text-sm" aria-label="Breadcrumb">
                {breadcrumbs.map((crumb, index) => (
                  <React.Fragment key={index}>
                    {index > 0 && (
                      <span className="mx-2 text-gray-400">/</span>
                    )}
                    {crumb.href ? (
                      <Link
                        href={crumb.href}
                        className="text-gray-600 hover:text-blue-600 transition-colors duration-200"
                      >
                        {crumb.label}
                      </Link>
                    ) : (
                      <span className="text-gray-900 font-medium">
                        {crumb.label}
                      </span>
                    )}
                  </React.Fragment>
                ))}
              </nav>
            )}

            {/* Title */}
            {title && (
              <div className="min-w-0">
                <h1 className="text-lg font-semibold text-gray-900 truncate">
                  {title}
                </h1>
                {subtitle && (
                  <p className="text-sm text-gray-500 truncate">{subtitle}</p>
                )}
              </div>
            )}
          </div>

          {/* Right side: Actions + User Menu */}
          <div className="flex items-center gap-4">
            {/* Custom actions (search, notifications, etc) */}
            {actions}

            {/* User Menu Dropdown */}
            {user && (
              <div className="relative" ref={userMenuRef}>
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  onKeyDown={handleUserMenuKeyDown}
                  className="flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors duration-200"
                  aria-haspopup="true"
                  aria-expanded={userMenuOpen}
                >
                  {user.avatar ? (
                    <img
                      src={user.avatar}
                      alt={user.name}
                      className="w-6 h-6 rounded-full"
                    />
                  ) : (
                    <div className="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center text-white text-xs font-bold">
                      {user.name?.charAt(0)?.toUpperCase() || 'U'}
                    </div>
                  )}
                  <span className="hidden sm:inline text-gray-900">
                    {user.name}
                  </span>
                  <ChevronDownIcon
                    className={`w-4 h-4 text-gray-500 transition-transform duration-200 ${
                      userMenuOpen ? 'rotate-180' : ''
                    }`}
                  />
                </button>

                {/* Dropdown Menu */}
                {userMenuOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 py-1 z-50">
                    {/* User Info */}
                    <div className="px-4 py-2 border-b border-gray-200">
                      <p className="text-sm font-medium text-gray-900">
                        {user.name}
                      </p>
                      <p className="text-xs text-gray-500">{user.email}</p>
                    </div>

                    {/* Menu Items */}
                    <Link
                      href="/dashboard/settings"
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      Settings
                    </Link>

                    {/* Logout */}
                    <button
                      data-logout-btn
                      onClick={handleLogoutClick}
                      className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors flex items-center gap-2 border-t border-gray-200 mt-1"
                    >
                      <ArrowRightOnRectangleIcon className="w-4 h-4" />
                      Logout
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </header>
    )
  }
)

Header.displayName = 'Header'
