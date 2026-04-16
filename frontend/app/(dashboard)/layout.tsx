'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { DashboardLayout, navigationItems } from '@/app/components/layout'
import { useAuthStore } from '@/hooks/useAuth'

export default function DashboardRootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const { isAuthenticated, user } = useAuthStore()
  const [isMounted, setIsMounted] = useState(false)

  useEffect(() => {
    setIsMounted(true)
  }, [])

  useEffect(() => {
    if (isMounted && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, router, isMounted])

  if (!isMounted || !isAuthenticated) {
    return null
  }

  const handleLogout = () => {
    // TODO: Call logout API and clear auth store
    router.push('/login')
  }

  return (
    <DashboardLayout
      sidebarItems={navigationItems}
      user={
        user
          ? {
              name: user.name || user.email || 'User',
              email: user.email || '',
            }
          : undefined
      }
      onLogout={handleLogout}
    >
      {children}
    </DashboardLayout>
  )
}
