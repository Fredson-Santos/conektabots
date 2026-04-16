'use client'

import Link from 'next/link'
import UserProfile from './UserProfile'

interface HeaderProps {
  onMenuClick?: () => void
  isMenuOpen?: boolean
}

export default function Header({ onMenuClick, isMenuOpen = false }: HeaderProps) {
  return (
    <header className="sticky top-0 z-40 border-b border-gray-200 bg-white shadow-sm">
      <div className="flex items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        {/* Left: Logo + Menu Button */}
        <div className="flex items-center gap-4">
          {/* Mobile Menu Button */}
          <button
            onClick={onMenuClick}
            className="inline-flex items-center justify-center rounded-md p-2 text-gray-600 hover:bg-gray-100 md:hidden"
            aria-label="Toggle menu"
          >
            <svg
              className={`h-6 w-6 transform transition-transform ${isMenuOpen ? 'rotate-90' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>

          {/* Logo */}
          <Link href="/dashboard" className="flex items-center gap-2">
            <span className="text-2xl font-bold text-blue-600">KB</span>
            <span className="hidden font-semibold text-gray-900 sm:inline">ConektaBots</span>
          </Link>
        </div>

        {/* Right: User Profile */}
        <UserProfile />
      </div>
    </header>
  )
}
