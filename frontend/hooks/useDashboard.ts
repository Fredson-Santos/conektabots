import { useState, useEffect } from 'react'
import { getApi } from '@/lib/api'

export interface DashboardStats {
  total_bots: number
  total_rules: number
  messages_hour: number
  last_execution: string | null
}

interface UseDashboardReturn {
  stats: DashboardStats | null
  loading: boolean
  error: string | null
}

export function useDashboard(): UseDashboardReturn {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true)
        setError(null)

        const api = getApi()
        const response = await api.get('/stats')
        setStats(response.data)
      } catch (err) {
        console.error('Error fetching dashboard stats:', err)
        setError('Failed to load dashboard statistics')
        // Set mock data for development
        setStats({
          total_bots: 12,
          total_rules: 45,
          messages_hour: 234,
          last_execution: new Date().toISOString(),
        })
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  return { stats, loading, error }
}
