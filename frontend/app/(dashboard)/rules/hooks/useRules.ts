'use client'

import { create } from 'zustand'
import { getApi } from '@/lib/api'
import { UUID } from '@/lib/types'
import { useState, useCallback } from 'react'

/**
 * Rule Types
 */
export interface RegraCreateData {
  nome: string
  bot_id: UUID
  marketplace_integracao_id?: UUID | null
  substituto?: string | null
  filtro_midia: string
  converter_link: boolean
  origens: string[]
  destinos: string[]
  filtros: Array<{ tipo: string; valor: string }>
  condicoes: string[]
}

export interface RegraUpdateData {
  nome?: string
  substituto?: string | null
  filtro_midia?: string
  converter_link?: boolean
  ativo?: boolean
}

export interface Regra {
  id: UUID
  tenant_id: UUID
  bot_id: UUID
  marketplace_integracao_id?: UUID | null
  nome: string
  substituto?: string | null
  filtro_midia: string
  converter_link: boolean
  ativo: boolean
  criado_em: string
  atualizado_em: string
}

export interface RegraFull extends Regra {
  origens: Array<{ id: UUID; origem: string }>
  destinos: Array<{ id: UUID; destino: string }>
  filtros: Array<{ id: UUID; tipo: string; valor: string }>
  condicoes: Array<{ id: UUID; condicao: string }>
}

/**
 * Store for Rules Management
 */
interface RulesStore {
  rules: Regra[]
  loading: boolean
  error: string | null
  setRules: (rules: Regra[]) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

export const useRulesStore = create<RulesStore>((set) => ({
  rules: [],
  loading: false,
  error: null,
  setRules: (rules) => set({ rules }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}))

/**
 * Hook for Rules Operations
 */
export const useRules = () => {
  const store = useRulesStore()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const api = getApi()

  /**
   * List all rules
   */
  const list = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await api.get<Regra[]>('/regras')
      store.setRules(response.data)
      return response.data
    } catch (err: any) {
      const errorMsg = err?.response?.data?.detail || 'Erro ao carregar regras'
      setError(errorMsg)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [api, store])

  /**
   * Get single rule with all children
   */
  const get = useCallback(
    async (regraId: UUID) => {
      setIsLoading(true)
      setError(null)
      try {
        const response = await api.get<RegraFull>(`/regras/${regraId}`)
        return response.data
      } catch (err: any) {
        const errorMsg = err?.response?.data?.detail || 'Erro ao carregar regra'
        setError(errorMsg)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    [api]
  )

  /**
   * Create new rule
   */
  const create = useCallback(
    async (data: RegraCreateData) => {
      setIsLoading(true)
      setError(null)
      try {
        const response = await api.post<RegraFull>('/regras', data)
        // Refresh list
        await list()
        return response.data
      } catch (err: any) {
        const errorMsg = err?.response?.data?.detail || 'Erro ao criar regra'
        setError(errorMsg)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    [api, list]
  )

  /**
   * Update rule metadata
   */
  const update = useCallback(
    async (regraId: UUID, data: RegraUpdateData) => {
      setIsLoading(true)
      setError(null)
      try {
        const response = await api.patch<Regra>(`/regras/${regraId}`, data)
        // Update in store
        store.setRules(
          store.rules.map((r) => (r.id === regraId ? response.data : r))
        )
        return response.data
      } catch (err: any) {
        const errorMsg = err?.response?.data?.detail || 'Erro ao atualizar regra'
        setError(errorMsg)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    [api, store]
  )

  /**
   * Delete rule
   */
  const delete_ = useCallback(
    async (regraId: UUID) => {
      setIsLoading(true)
      setError(null)
      try {
        await api.delete(`/regras/${regraId}`)
        // Update store
        store.setRules(store.rules.filter((r) => r.id !== regraId))
      } catch (err: any) {
        const errorMsg = err?.response?.data?.detail || 'Erro ao deletar regra'
        setError(errorMsg)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    [api, store]
  )

  /**
   * Toggle active status
   */
  const toggle = useCallback(
    async (regraId: UUID, currentStatus: boolean) => {
      setIsLoading(true)
      setError(null)
      try {
        const response = await api.patch<Regra>(`/regras/${regraId}`, {
          ativo: !currentStatus,
        })
        // Update in store
        store.setRules(
          store.rules.map((r) => (r.id === regraId ? response.data : r))
        )
        return response.data
      } catch (err: any) {
        const errorMsg = err?.response?.data?.detail || 'Erro ao atualizar status'
        setError(errorMsg)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    [api, store]
  )

  return {
    rules: store.rules,
    loading: isLoading || store.loading,
    error: error || store.error,
    list,
    get,
    create,
    update,
    delete: delete_,
    toggle,
  }
}
