'use client'

import { useState, useCallback } from 'react'
import { getApi } from '@/lib/api'

export interface Bot {
  id: string
  nome: string
  api_id: string
  api_hash?: string
  telefone?: string
  ativo: boolean
  criado_em: string
  tenant_id: string
}

export interface BotCreateInput {
  nome: string
  api_id: string
  api_hash: string
  telefone: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

interface UseBotsReturn {
  bots: Bot[]
  loading: boolean
  error: string | null
  totalPages: number
  currentPage: number
  pageSize: number
  
  // Operations
  fetchBots: (page: number, pageSize: number) => Promise<void>
  createBot: (data: BotCreateInput) => Promise<Bot>
  updateBot: (id: string, data: Partial<BotCreateInput>) => Promise<Bot>
  deleteBot: (id: string) => Promise<void>
  toggleBotStatus: (id: string, ativo: boolean) => Promise<Bot>
  refetch: () => Promise<void>
}

export function useBots(): UseBotsReturn {
  const [bots, setBots] = useState<Bot[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [totalPages, setTotalPages] = useState(0)

  const fetchBots = useCallback(
    async (page: number = currentPage, size: number = pageSize) => {
      try {
        setLoading(true)
        setError(null)

        const api = getApi()
        const response = await api.get('/bots', {
          params: {
            page,
            page_size: size,
          },
        })

        // Handle different response formats
        const data = response.data
        let botsList: Bot[] = []
        let total = 0

        if (Array.isArray(data)) {
          // Direct array response
          botsList = data
          total = data.length
        } else if (data.items) {
          // Paginated response
          botsList = data.items
          total = data.total
          setTotalPages(data.total_pages || Math.ceil(total / size))
        } else if (data.data) {
          // Alternative format
          botsList = data.data
          total = botsList.length
        }

        setBots(botsList)
        setCurrentPage(page)
        setPageSize(size)
      } catch (err) {
        console.error('Error fetching bots:', err)
        const errorMsg =
          err instanceof Error
            ? err.message
            : 'Failed to load bots. Please try again.'
        setError(errorMsg)
        setBots([])
      } finally {
        setLoading(false)
      }
    },
    [currentPage, pageSize]
  )

  const createBot = useCallback(
    async (data: BotCreateInput): Promise<Bot> => {
      try {
        setError(null)
        const api = getApi()

        const response = await api.post('/bots', {
          nome: data.nome,
          api_id: data.api_id,
          api_hash: data.api_hash,
          telefone: data.telefone,
        })

        const newBot = response.data
        setBots((prev) => [...prev, newBot])

        return newBot
      } catch (err) {
        console.error('Error creating bot:', err)
        const errorMsg =
          err instanceof Error
            ? err.message
            : 'Failed to create bot. Please try again.'
        setError(errorMsg)
        throw err
      }
    },
    []
  )

  const updateBot = useCallback(
    async (id: string, data: Partial<BotCreateInput>): Promise<Bot> => {
      try {
        setError(null)
        const api = getApi()

        const response = await api.patch(`/bots/${id}`, data)

        const updatedBot = response.data
        setBots((prev) =>
          prev.map((bot) => (bot.id === id ? updatedBot : bot))
        )

        return updatedBot
      } catch (err) {
        console.error('Error updating bot:', err)
        const errorMsg =
          err instanceof Error
            ? err.message
            : 'Failed to update bot. Please try again.'
        setError(errorMsg)
        throw err
      }
    },
    []
  )

  const deleteBot = useCallback(async (id: string): Promise<void> => {
    try {
      setError(null)
      const api = getApi()

      await api.delete(`/bots/${id}`)

      setBots((prev) => prev.filter((bot) => bot.id !== id))
    } catch (err) {
      console.error('Error deleting bot:', err)
      const errorMsg =
        err instanceof Error
          ? err.message
          : 'Failed to delete bot. Please try again.'
      setError(errorMsg)
      throw err
    }
  }, [])

  const toggleBotStatus = useCallback(
    async (id: string, ativo: boolean): Promise<Bot> => {
      try {
        setError(null)
        const api = getApi()

        const response = await api.patch(`/bots/${id}`, {
          ativo: !ativo,
        })

        const updatedBot = response.data
        setBots((prev) =>
          prev.map((bot) => (bot.id === id ? updatedBot : bot))
        )

        return updatedBot
      } catch (err) {
        console.error('Error toggling bot status:', err)
        const errorMsg =
          err instanceof Error
            ? err.message
            : 'Failed to toggle bot status. Please try again.'
        setError(errorMsg)
        throw err
      }
    },
    []
  )

  const refetch = useCallback(
    async () => {
      await fetchBots(currentPage, pageSize)
    },
    [fetchBots, currentPage, pageSize]
  )

  return {
    bots,
    loading,
    error,
    totalPages,
    currentPage,
    pageSize,
    fetchBots,
    createBot,
    updateBot,
    deleteBot,
    toggleBotStatus,
    refetch,
  }
}
