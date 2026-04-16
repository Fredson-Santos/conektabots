'use client'

import { useState } from 'react'
import Header from './Header'
import Sidebar from './Sidebar'
import Breadcrumbs from './Breadcrumbs'

interface DashboardLayoutProps {
  children: React.ReactNode
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen)
  const closeSidebar = () => setSidebarOpen(false)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <Header onMenuClick={toggleSidebar} isMenuOpen={sidebarOpen} />

      <div className="flex">
        {/* Sidebar */}
        <Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />

        {/* Main Content */}
        <main className="flex-1">
          <div className="px-4 py-8 sm:px-6 lg:px-8">
            {/* Breadcrumbs */}
            <Breadcrumbs />

            {/* Content */}
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
