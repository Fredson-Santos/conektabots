'use client'

import React, { useEffect, useRef } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  HomeIcon,
  SparklesIcon,
  ShoppingCartIcon,
  Cog6ToothIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline'

import { NavItem } from './constants'

export interface SidebarProps {
  /** Navigation items to display */
  items: NavItem[]
  /** Current active route (if not using usePathname) */
  activeRoute?: string
  /** Callback when nav item is clicked */
  onItemClick?: (item: NavItem) => void
  /** Mobile: whether drawer is open */
  isOpen?: boolean
  /** Callback to close drawer (mobile) */
  onClose?: () => void
}

/**
 * Icon mapping: string identifier to Heroicon component
 */
const iconMap: Record<string, React.ReactNode> = {
  home: <HomeIcon className="w-5 h-5" />,
  sparkles: <SparklesIcon className="w-5 h-5" />,
  'shopping-cart': <ShoppingCartIcon className="w-5 h-5" />,
  'cog-6-tooth': <Cog6ToothIcon className="w-5 h-5" />,
}

/**
 * Sidebar Component
 *
 * Responsive navigation sidebar with desktop fixed layout and mobile drawer overlay.
 * Features:
 * - Desktop: 240px fixed left sidebar
 * - Mobile: Drawer overlay with backdrop
 * - Active state highlighting with blue accent
 * - Badge support for counts (notifications, etc)
 * - Keyboard accessible (Escape to close, Tab navigation)
 * - Semantic HTML with nav element
 *
 * @example
 * ```tsx
 * <Sidebar
 *   items={navigationItems}
 *   isOpen={mobileMenuOpen}
 *   onClose={() => setMobileMenuOpen(false)}
 * />
 * ```
 */
export const Sidebar = React.forwardRef<HTMLDivElement, SidebarProps>(
  ({ items, activeRoute, onItemClick, isOpen = false, onClose }, ref) => {
    const pathname = usePathname()
    const currentRoute = activeRoute || pathname
    const drawerRef = useRef<HTMLDivElement>(null)

    // Close drawer on escape key
    useEffect(() => {
      const handleEscape = (e: KeyboardEvent) => {
        if (e.key === 'Escape' && isOpen) {
          onClose?.()
        }
      }

      window.addEventListener('keydown', handleEscape)
      return () => window.removeEventListener('keydown', handleEscape)
    }, [isOpen, onClose])

    // Close drawer when clicking outside
    useEffect(() => {
      const handleClickOutside = (e: MouseEvent) => {
        if (
          isOpen &&
          drawerRef.current &&
          !drawerRef.current.contains(e.target as Node)
        ) {
          // Only close if click is on the backdrop, not inside drawer
          const rect = drawerRef.current.getBoundingClientRect()
          if (e.clientX > rect.right || e.clientX < rect.left) {
            onClose?.()
          }
        }
      }

      window.addEventListener('click', handleClickOutside)
      return () => window.removeEventListener('click', handleClickOutside)
    }, [isOpen, onClose])

    const handleItemClick = (item: NavItem) => {
      onItemClick?.(item)
      // Close drawer on mobile after clicking
      if (isOpen) {
        onClose?.()
      }
    }

    /**
     * Render a single navigation item with active state and badge
     */
    const renderNavItem = (item: NavItem) => {
      const isActive = currentRoute === item.href || currentRoute?.startsWith(item.href + '/')
      const icon = iconMap[item.icon] || null

      return (
        <Link key={item.id} href={item.href}>
          <button
            onClick={() => handleItemClick(item)}
            className={`
              w-full flex items-center justify-between px-3 py-3 rounded-md text-sm font-medium
              transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
              ${
                isActive
                  ? 'bg-blue-50 text-blue-600 border-l-4 border-blue-500'
                  : 'text-gray-700 hover:bg-gray-100 border-l-4 border-transparent'
              }
            `}
            aria-current={isActive ? 'page' : undefined}
          >
            <span className="flex items-center gap-2">
              {icon && <span className="text-gray-500">{icon}</span>}
              <span>{item.label}</span>
            </span>
            {item.badge !== undefined && item.badge > 0 && (
              <span className="ml-auto text-xs font-medium bg-gray-200 text-gray-700 rounded-full px-2 py-0.5">
                {item.badge}
              </span>
            )}
          </button>
        </Link>
      )
    }

    // Desktop Sidebar (always visible)
    const desktopSidebar = (
      <aside
        ref={ref}
        className="hidden md:flex flex-col w-60 bg-white border-r border-gray-200 fixed left-0 top-0 h-screen z-40"
      >
        {/* Logo / Brand */}
        <div className="px-4 py-5 border-b border-gray-200">
          <h1 className="text-base font-bold text-gray-900">ConektaBots</h1>
        </div>

        {/* Navigation Items */}
        <nav
          className="flex-1 overflow-y-auto px-2 py-4 space-y-1"
          aria-label="Main navigation"
        >
          {items.map(renderNavItem)}
        </nav>

        {/* Footer (optional: user info, etc) */}
        <div className="border-t border-gray-200 px-4 py-4 text-xs text-gray-500">
          Version 1.0
        </div>
      </aside>
    )

    // Mobile Drawer (overlay)
    const mobileSidebar = (
      <>
        {/* Backdrop overlay */}
        {isOpen && (
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-30 md:hidden"
            onClick={onClose}
          />
        )}

        {/* Drawer */}
        <aside
          ref={drawerRef}
          className={`
            fixed top-0 left-0 h-screen w-60 bg-white z-40 md:hidden
            transition-transform duration-300 ease-in-out transform
            ${isOpen ? 'translate-x-0' : '-translate-x-full'}
          `}
        >
          {/* Header with close button */}
          <div className="flex items-center justify-between px-4 py-5 border-b border-gray-200">
            <h1 className="text-base font-bold text-gray-900">ConektaBots</h1>
            <button
              onClick={onClose}
              className="p-1.5 text-gray-500 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md"
              aria-label="Close navigation"
            >
              <XMarkIcon className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation Items */}
          <nav
            className="overflow-y-auto px-2 py-4 space-y-1"
            aria-label="Mobile navigation"
          >
            {items.map(renderNavItem)}
          </nav>
        </aside>
      </>
    )

    return (
      <>
        {desktopSidebar}
        {mobileSidebar}
      </>
    )
  }
)

Sidebar.displayName = 'Sidebar'
