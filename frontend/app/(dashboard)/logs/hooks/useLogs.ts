'use client'

import { useState, useCallback, useRef } from 'react'
import { getApi } from '@/lib/api'

export interface Log {
  id: string
  bot_id: string
  bot_nome?: string
  chat_origem: string
  chat_destino: string
  status: 'sucesso' | 'erro' | 'bloqueado' | 'pendente'
  mensagem?: string
  erro?: string
  tipo_midia?: string
  criado_em: string
  tenant_id: string
}

export interface LogFilters {
  status?: string
  bot_id?: string
  data_inicio?: string
  data_fim?: string
  search?: string
}

interface UseLogsReturn {
  logs: Log[]
  loading: boolean
  error: string | null
  totalPages: number
  currentPage: number
  totalLogs: number
  autoRefresh: boolean

  fetchLogs: (page?: number, filters?: LogFilters) => Promise<void>
  setAutoRefresh: (val: boolean) => void
  exportCsv: () => void
}

export function useLogs(): UseLogsReturn {
  const [logs, setLogs] = useState<Log[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)
  const [totalLogs, setTotalLogs] = useState(0)
  const [autoRefresh, setAutoRefreshState] = useState(false)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const filtersRef = useRef<LogFilters>({})

  const fetchLogs = useCallback(
    async (page: number = currentPage, filters: LogFilters = filtersRef.current) => {
      try {
        setLoading(true)
        setError(null)
        filtersRef.current = filters

        const api = getApi()
        const params: Record<string, unknown> = { page, page_size: 50 }
        if (filters.status) params.status = filters.status
        if (filters.bot_id) params.bot_id = filters.bot_id
        if (filters.data_inicio) params.data_inicio = filters.data_inicio
        if (filters.data_fim) params.data_fim = filters.data_fim
        if (filters.search) params.q = filters.search

        const response = await api.get('/logs', { params })
        const data = response.data

        let list: Log[] = []
        let total = 0

        if (Array.isArray(data)) {
          list = data
          total = data.length
          setTotalPages(Math.ceil(total / 50))
        } else if (data.items) {
          list = data.items
          total = data.total || data.items.length
          setTotalPages(data.total_pages || Math.ceil(total / 50))
        } else if (data.data) {
          list = data.data
          total = list.length
        }

        setLogs(list)
        setCurrentPage(page)
        setTotalLogs(total)
      } catch (err) {
        console.error('Error fetching logs:', err)
        setError(err instanceof Error ? err.message : 'Failed to load logs.')
      } finally {
        setLoading(false)
      }
    },
    [currentPage]
  )

  const setAutoRefresh = useCallback((val: boolean) => {
    setAutoRefreshState(val)
    if (val) {
      intervalRef.current = setInterval(() => {
        fetchLogs(1, filtersRef.current)
      }, 5000)
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [fetchLogs])

  const exportCsv = useCallback(() => {
    const headers = ['Data/Hora', 'Bot', 'Origem', 'Destino', 'Status', 'Tipo Mídia', 'Mensagem', 'Erro']
    const rows = logs.map(log => [
      new Date(log.criado_em).toLocaleString('pt-BR'),
      log.bot_nome || log.bot_id,
      log.chat_origem,
      log.chat_destino,
      log.status,
      log.tipo_midia || '',
      (log.mensagem || '').replace(/,/g, ';'),
      (log.erro || '').replace(/,/g, ';'),
    ])
    const csv = [headers, ...rows].map(r => r.join(',')).join('\n')
    const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `logs_${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }, [logs])

  return {
    logs, loading, error, totalPages, currentPage, totalLogs, autoRefresh,
    fetchLogs, setAutoRefresh, exportCsv,
  }
}
