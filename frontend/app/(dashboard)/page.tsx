'use client'

import { useDashboard } from '@/hooks/useDashboard'
import StatCard from '@/components/dashboard/StatCard'
import LoadingSkeleton from '@/components/dashboard/LoadingSkeleton'

export default function DashboardPage() {
  const { stats, loading, error } = useDashboard()

  if (loading) {
    return <LoadingSkeleton />
  }

  if (error && !stats) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
        <h3 className="font-semibold">Error Loading Dashboard</h3>
        <p className="mt-1 text-sm">{error}</p>
      </div>
    )
  }

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never'
    try {
      const date = new Date(dateString)
      return date.toLocaleString()
    } catch {
      return 'Invalid date'
    }
  }

  return (
    <div className="space-y-8">
      {/* Page Title */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-gray-600">Welcome back! Here&apos;s an overview of your activity.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Bots"
          value={stats?.total_bots || 0}
          icon="🤖"
          isLoading={loading}
        />
        <StatCard
          title="Total Rules"
          value={stats?.total_rules || 0}
          icon="📋"
          isLoading={loading}
        />
        <StatCard
          title="Messages This Hour"
          value={stats?.messages_hour || 0}
          icon="💬"
          isLoading={loading}
        />
        <StatCard
          title="Last Execution"
          value={formatDate(stats?.last_execution || null)}
          icon="⏱️"
          isLoading={loading}
        />
      </div>

      {/* Quick Actions */}
      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">Quick Actions</h2>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          <a
            href="/dashboard/bots"
            className="rounded-lg bg-blue-50 p-4 text-center transition-all hover:bg-blue-100"
          >
            <div className="text-2xl">🤖</div>
            <div className="mt-2 text-sm font-medium text-blue-900">Manage Bots</div>
          </a>
          <a
            href="/dashboard/rules"
            className="rounded-lg bg-green-50 p-4 text-center transition-all hover:bg-green-100"
          >
            <div className="text-2xl">📋</div>
            <div className="mt-2 text-sm font-medium text-green-900">Create Rules</div>
          </a>
          <a
            href="/dashboard/schedules"
            className="rounded-lg bg-purple-50 p-4 text-center transition-all hover:bg-purple-100"
          >
            <div className="text-2xl">⏱️</div>
            <div className="mt-2 text-sm font-medium text-purple-900">Set Schedules</div>
          </a>
          <a
            href="/dashboard/marketplaces"
            className="rounded-lg bg-orange-50 p-4 text-center transition-all hover:bg-orange-100"
          >
            <div className="text-2xl">🏪</div>
            <div className="mt-2 text-sm font-medium text-orange-900">Connect Marketplaces</div>
          </a>
        </div>
      </div>
    </div>
  )
}
