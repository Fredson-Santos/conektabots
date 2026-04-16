'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

interface NavItem {
  label: string
  href: string
  icon: string
}

const navItems: NavItem[] = [
  { label: 'Overview', href: '/', icon: '📊' },
  { label: 'Bots', href: '/bots', icon: '🤖' },
  { label: 'Regras', href: '/rules', icon: '📋' },
  { label: 'Agendamentos', href: '/schedules', icon: '⏱️' },
  { label: 'Marketplaces', href: '/marketplaces', icon: '🏪' },
  { label: 'Logs', href: '/logs', icon: '📝' },
  { label: 'Configurações', href: '/settings', icon: '⚙️' },
]

interface SidebarProps {
  isOpen?: boolean
  onClose?: () => void
}

export default function Sidebar({ isOpen = true, onClose }: SidebarProps) {
  const pathname = usePathname()

  const isActive = (href: string) => {
    if (href === '/' && pathname === '/') return true
    if (href !== '/' && pathname.startsWith(href)) return true
    return false
  }

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-16 z-50 h-[calc(100vh-4rem)] w-64 transform bg-gray-900 text-white transition-transform duration-300 ease-in-out md:relative md:top-0 md:z-0 md:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <nav className="flex h-full flex-col overflow-y-auto px-4 py-6">
          {/* Logo/Branding */}
          <div className="mb-8 flex items-center gap-2 px-2">
            <span className="text-2xl font-bold text-blue-400">KB</span>
            <span className="hidden text-sm font-semibold sm:inline">ConektaBots</span>
          </div>

          {/* Nav Links */}
          <div className="flex-1 space-y-1">
            {navItems.map((item) => {
              const active = isActive(item.href)
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium transition-all ${
                    active
                      ? 'bg-blue-600 text-white shadow-lg'
                      : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                  }`}
                  onClick={onClose}
                >
                  <span className="text-lg">{item.icon}</span>
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </div>

          {/* Footer */}
          <div className="border-t border-gray-700 pt-4">
            <p className="text-xs text-gray-500">ConektaBots v1.0</p>
          </div>
        </nav>
      </aside>
    </>
  )
}
