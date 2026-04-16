'use client'

import { useEffect, useState } from 'react'
import { DashboardLayout, navigationItems } from '@/app/components/layout'
import { Card, Button, Alert } from '@/app/components/ui'
import { MetricCard } from '@/app/components/dashboard/MetricCard'
import {
  SparklesIcon,
  ChartBarIcon,
  RocketLaunchIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline'

interface DashboardMetrics {
  activeBots: number
  activeBotsTrend: { value: number; isPositive: boolean }
  totalMessages: number
  messagesTrend: { value: number; isPositive: boolean }
  uptime: number
  uptimeTrend: { value: number; isPositive: boolean }
}

interface ActivityItem {
  id: string
  action: string
  timestamp: Date
  details?: string
}

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [activities, setActivities] = useState<ActivityItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Simulate fetching dashboard metrics
    // In production, this would call an API endpoint
    const loadMetrics = async () => {
      try {
        setLoading(true)
        // Mock data for demonstration
        await new Promise((resolve) => setTimeout(resolve, 800))

        setMetrics({
          activeBots: 12,
          activeBotsTrend: { value: 2, isPositive: true },
          totalMessages: 45234,
          messagesTrend: { value: 1200, isPositive: true },
          uptime: 99.8,
          uptimeTrend: { value: 0.1, isPositive: false },
        })

        setActivities([
          {
            id: '1',
            action: 'Bot "MyBot" processed 523 messages',
            timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
            details: '2h ago',
          },
          {
            id: '2',
            action: 'New marketplace added (Shopee)',
            timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
            details: '4h ago',
          },
          {
            id: '3',
            action: 'Settings updated',
            timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000),
            details: '1d ago',
          },
        ])

        setError(null)
      } catch (err) {
        setError('Failed to load dashboard metrics')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    loadMetrics()
  }, [])

  const handleRefresh = () => {
    setLoading(true)
    // Trigger refresh logic here
  }

  return (
    <DashboardLayout
      sidebarItems={navigationItems}
      title="Dashboard"
      breadcrumbs={[{ label: 'Dashboard' }]}
      actions={
        <button
          onClick={handleRefresh}
          className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition"
          title="Refresh dashboard"
        >
          <ArrowPathIcon className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
        </button>
      }
    >
      <div className="space-y-lg">
        {/* Page Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-1 text-sm text-gray-600">
            Welcome back! Here&apos;s your overview of bots and activity.
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert
            type="error"
            title="Could not load dashboard"
            description={error}
            action={{ label: 'Retry', onClick: handleRefresh }}
          />
        )}

        {/* Metrics Cards - Loading State */}
        {loading && !metrics ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-lg">
            {[1, 2, 3].map((i) => (
              <Card key={i}>
                <div className="p-lg space-y-md">
                  <div className="h-4 w-20 bg-gray-200 rounded animate-pulse" />
                  <div className="h-8 w-16 bg-gray-200 rounded animate-pulse" />
                  <div className="h-3 w-24 bg-gray-100 rounded animate-pulse" />
                </div>
              </Card>
            ))}
          </div>
        ) : metrics ? (
          <>
            {/* Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-lg">
              <MetricCard
                label="Active Bots"
                value={metrics.activeBots}
                trend={{
                  value: metrics.activeBotsTrend.value,
                  label: 'this week',
                  isPositive: metrics.activeBotsTrend.isPositive,
                }}
                icon={<SparklesIcon className="w-6 h-6" />}
                accentColor="blue"
              />

              <MetricCard
                label="Total Messages"
                value={metrics.totalMessages.toLocaleString()}
                unit="in last 30 days"
                trend={{
                  value: metrics.messagesTrend.value,
                  label: '/day average',
                  isPositive: metrics.messagesTrend.isPositive,
                }}
                icon={<ChartBarIcon className="w-6 h-6" />}
                accentColor="green"
              />

              <MetricCard
                label="System Uptime"
                value={`${metrics.uptime}%`}
                unit="last 30 days"
                trend={{
                  value: metrics.uptimeTrend.value,
                  label: 'vs last month',
                  isPositive: metrics.uptimeTrend.isPositive,
                }}
                icon={<RocketLaunchIcon className="w-6 h-6" />}
                accentColor={metrics.uptime >= 99 ? 'green' : 'amber'}
              />
            </div>

            {/* Recent Activity Section */}
            <Card>
              <Card.Header title="Recent Activity" />
              <Card.Body className="space-y-md">
                {activities.length > 0 ? (
                  <div className="space-y-md">
                    {activities.map((activity) => (
                      <div
                        key={activity.id}
                        className="flex items-start gap-md pb-md border-b border-gray-100 last:border-0 last:pb-0"
                      >
                        <div className="flex-shrink-0 w-2 h-2 rounded-full bg-blue-500 mt-2" />
                        <div className="flex-1">
                          <p className="text-sm text-gray-900">{activity.action}</p>
                          <p className="text-xs text-gray-500 mt-0.5">{activity.details}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No recent activity</p>
                )}
              </Card.Body>
            </Card>

            {/* Quick Actions Section */}
            <Card>
              <Card.Header title="Quick Actions" />
              <Card.Body>
                <div className="flex flex-col sm:flex-row gap-md">
                  <Button
                    variant="primary"
                    size="md"
                    icon={<SparklesIcon className="w-5 h-5" />}
                    fullWidth
                  >
                    Create Bot
                  </Button>
                  <Button
                    variant="secondary"
                    size="md"
                    fullWidth
                  >
                    Add Marketplace
                  </Button>
                  <Button
                    variant="tertiary"
                    size="md"
                    fullWidth
                  >
                    View Settings
                  </Button>
                </div>
              </Card.Body>
            </Card>
          </>
        ) : null}
      </div>
    </DashboardLayout>
  )
}
