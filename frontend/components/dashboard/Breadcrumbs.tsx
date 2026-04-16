'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

interface BreadcrumbItem {
  label: string
  href: string
}

export default function Breadcrumbs() {
  const pathname = usePathname()

  // Generate breadcrumb items from pathname
  const generateBreadcrumbs = (): BreadcrumbItem[] => {
    const segments = pathname.split('/').filter(Boolean)

    // Remove 'dashboard' from start
    if (segments[0] === 'dashboard') {
      segments.shift()
    }

    const breadcrumbs: BreadcrumbItem[] = [
      { label: 'Dashboard', href: '/dashboard' },
    ]

    let href = '/dashboard'
    segments.forEach((segment) => {
      href += `/${segment}`
      // Convert segment to title case
      const label = segment
        .split('-')
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ')

      breadcrumbs.push({ label, href })
    })

    return breadcrumbs
  }

  const breadcrumbs = generateBreadcrumbs()

  if (breadcrumbs.length <= 1) {
    return null
  }

  return (
    <nav
      className="mb-6 flex flex-wrap items-center gap-2 text-sm"
      aria-label="Breadcrumb"
    >
      {breadcrumbs.map((crumb, index) => (
        <div key={crumb.href} className="flex items-center gap-2">
          {index > 0 && <span className="text-gray-400">/</span>}
          {index === breadcrumbs.length - 1 ? (
            // Current page (not a link)
            <span className="font-medium text-gray-900">{crumb.label}</span>
          ) : (
            // Link to previous pages
            <Link
              href={crumb.href}
              className="text-blue-600 hover:text-blue-700 hover:underline"
            >
              {crumb.label}
            </Link>
          )}
        </div>
      ))}
    </nav>
  )
}
