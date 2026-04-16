'use client'

import { useState, useCallback } from 'react'
import { getApi } from '@/lib/api'

export interface Schedule {
  id: string
  nome: string
  bot_id: string
  bot_nome?: string
  chats_origem: string[]
  chats_destino: string[]
  horarios: string[]
  tipo_envio: 'sequencial' | 'pontual'
  tipo_midia: string[]
  filtros: ScheduleFilter[]
  ativo: boolean
  criado_em: string
  tenant_id: string
}

export interface ScheduleFilter {
  tipo: 'whitelist' | 'blacklist'
  valor: string
}

export interface ScheduleCreateInput {
  nome: string
  bot_id: string
  chats_origem: string[]
  chats_destino: string[]
  horarios: string[]
  tipo_envio: 'sequencial' | 'pontual'
  tipo_midia: string[]
  filtros: ScheduleFilter[]
}

interface UseSchedulesReturn {
  schedules: Schedule[]
  loading: boolean
  error: string | null
  totalPages: number
  currentPage: number
  pageSize: number

  fetchSchedules: (page?: number, pageSize?: number) => Promise<void>
  createSchedule: (data: ScheduleCreateInput) => Promise<Schedule>
  updateSchedule: (id: string, data: Partial<ScheduleCreateInput>) => Promise<Schedule>
  deleteSchedule: (id: string) => Promise<void>
  toggleScheduleStatus: (id: string, ativo: boolean) => Promise<Schedule>
  triggerManualSend: (id: string) => Promise<void>
  refetch: () => Promise<void>
}

export function useSchedules(): UseSchedulesReturn {
  const [schedules, setSchedules] = useState<Schedule[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [totalPages, setTotalPages] = useState(0)

  const fetchSchedules = useCallback(
    async (page: number = currentPage, size: number = pageSize) => {
      try {
        setLoading(true)
        setError(null)

        const api = getApi()
        const response = await api.get('/agendamentos', {
          params: { page, page_size: size },
        })

        const data = response.data
        let list: Schedule[] = []

        if (Array.isArray(data)) {
          list = data
          setTotalPages(Math.ceil(data.length / size))
        } else if (data.items) {
          list = data.items
          setTotalPages(data.total_pages || Math.ceil(data.total / size))
        } else if (data.data) {
          list = data.data
          setTotalPages(Math.ceil(list.length / size))
        }

        setSchedules(list)
        setCurrentPage(page)
        setPageSize(size)
      } catch (err) {
        console.error('Error fetching schedules:', err)
        setError(err instanceof Error ? err.message : 'Failed to load schedules.')
        setSchedules([])
      } finally {
        setLoading(false)
      }
    },
    [currentPage, pageSize]
  )

  const createSchedule = useCallback(async (data: ScheduleCreateInput): Promise<Schedule> => {
    try {
      setError(null)
      const api = getApi()
      const response = await api.post('/agendamentos', data)
      const newSchedule = response.data
      setSchedules(prev => [newSchedule, ...prev])
      return newSchedule
    } catch (err) {
      console.error('Error creating schedule:', err)
      const msg = err instanceof Error ? err.message : 'Failed to create schedule.'
      setError(msg)
      throw err
    }
  }, [])

  const updateSchedule = useCallback(
    async (id: string, data: Partial<ScheduleCreateInput>): Promise<Schedule> => {
      try {
        setError(null)
        const api = getApi()
        const response = await api.patch(`/agendamentos/${id}`, data)
        const updated = response.data
        setSchedules(prev => prev.map(s => (s.id === id ? updated : s)))
        return updated
      } catch (err) {
        console.error('Error updating schedule:', err)
        const msg = err instanceof Error ? err.message : 'Failed to update schedule.'
        setError(msg)
        throw err
      }
    },
    []
  )

  const deleteSchedule = useCallback(async (id: string): Promise<void> => {
    try {
      setError(null)
      const api = getApi()
      await api.delete(`/agendamentos/${id}`)
      setSchedules(prev => prev.filter(s => s.id !== id))
    } catch (err) {
      console.error('Error deleting schedule:', err)
      const msg = err instanceof Error ? err.message : 'Failed to delete schedule.'
      setError(msg)
      throw err
    }
  }, [])

  const toggleScheduleStatus = useCallback(
    async (id: string, ativo: boolean): Promise<Schedule> => {
      try {
        setError(null)
        const api = getApi()
        const response = await api.patch(`/agendamentos/${id}`, { ativo: !ativo })
        const updated = response.data
        setSchedules(prev => prev.map(s => (s.id === id ? updated : s)))
        return updated
      } catch (err) {
        console.error('Error toggling status:', err)
        const msg = err instanceof Error ? err.message : 'Failed to toggle status.'
        setError(msg)
        throw err
      }
    },
    []
  )

  const triggerManualSend = useCallback(async (id: string): Promise<void> => {
    try {
      const api = getApi()
      await api.post(`/agendamentos/${id}/enviar`)
    } catch (err) {
      console.error('Error triggering manual send:', err)
      throw err
    }
  }, [])

  const refetch = useCallback(async () => {
    await fetchSchedules(currentPage, pageSize)
  }, [fetchSchedules, currentPage, pageSize])

  return {
    schedules,
    loading,
    error,
    totalPages,
    currentPage,
    pageSize,
    fetchSchedules,
    createSchedule,
    updateSchedule,
    deleteSchedule,
    toggleScheduleStatus,
    triggerManualSend,
    refetch,
  }
}
