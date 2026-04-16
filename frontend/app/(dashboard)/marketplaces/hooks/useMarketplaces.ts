'use client'

import { useState, useCallback } from 'react'
import { getApi } from '@/lib/api'

export type MarketplaceType = 'shopee' | 'mercadolivre' | 'amazon' | 'magalu' | 'outro'

export interface Marketplace {
  id: string
  nome: string
  tipo: MarketplaceType
  ativo: boolean
  status: 'ativo' | 'inativo' | 'erro' | 'testando'
  ultimo_teste?: string
  criado_em: string
  tenant_id: string
}

export interface MarketplaceCreateInput {
  nome: string
  tipo: MarketplaceType
  credenciais: Record<string, string>
}

export const MARKETPLACE_FIELD_SCHEMAS: Record<MarketplaceType, { key: string; label: string; placeholder: string; required: boolean; secret?: boolean }[]> = {
  shopee: [
    { key: 'partner_id', label: 'Partner ID', placeholder: 'Ex: 1234567', required: true },
    { key: 'partner_key', label: 'Partner Key', placeholder: 'Chave secreta da API', required: true, secret: true },
    { key: 'shop_id', label: 'Shop ID', placeholder: 'ID da sua loja', required: true },
  ],
  mercadolivre: [
    { key: 'client_id', label: 'Client ID', placeholder: 'App ID do ML', required: true },
    { key: 'client_secret', label: 'Client Secret', placeholder: 'Secret da aplicação', required: true, secret: true },
    { key: 'seller_id', label: 'Seller ID', placeholder: 'Seu ID de vendedor', required: false },
  ],
  amazon: [
    { key: 'access_key', label: 'Access Key ID', placeholder: 'AKIA...', required: true },
    { key: 'secret_key', label: 'Secret Access Key', placeholder: 'Chave secreta AWS', required: true, secret: true },
    { key: 'seller_id', label: 'Seller ID', placeholder: 'Merchant token', required: true },
    { key: 'marketplace_id', label: 'Marketplace ID', placeholder: 'Ex: A2Q3Y263D00KWC', required: true },
  ],
  magalu: [
    { key: 'client_id', label: 'Client ID', placeholder: 'ID da integração', required: true },
    { key: 'client_secret', label: 'Client Secret', placeholder: 'Secret da API', required: true, secret: true },
  ],
  outro: [
    { key: 'api_key', label: 'API Key', placeholder: 'Chave da API', required: true, secret: true },
    { key: 'endpoint', label: 'Endpoint URL', placeholder: 'https://api.exemplo.com', required: false },
  ],
}

interface UseMarketplacesReturn {
  marketplaces: Marketplace[]
  loading: boolean
  error: string | null
  totalPages: number
  currentPage: number

  fetchMarketplaces: (page?: number, pageSize?: number) => Promise<void>
  createMarketplace: (data: MarketplaceCreateInput) => Promise<Marketplace>
  updateMarketplace: (id: string, data: Partial<MarketplaceCreateInput>) => Promise<Marketplace>
  deleteMarketplace: (id: string) => Promise<void>
  testConnection: (id: string) => Promise<{ success: boolean; message: string }>
  refetch: () => Promise<void>
}

export function useMarketplaces(): UseMarketplacesReturn {
  const [marketplaces, setMarketplaces] = useState<Marketplace[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)

  const fetchMarketplaces = useCallback(
    async (page: number = currentPage, size: number = 20) => {
      try {
        setLoading(true)
        setError(null)
        const api = getApi()
        const response = await api.get('/marketplaces', {
          params: { page, page_size: size },
        })

        const data = response.data
        let list: Marketplace[] = []

        if (Array.isArray(data)) {
          list = data
          setTotalPages(Math.ceil(data.length / size))
        } else if (data.items) {
          list = data.items
          setTotalPages(data.total_pages || 1)
        } else if (data.data) {
          list = data.data
        }

        setMarketplaces(list)
        setCurrentPage(page)
      } catch (err) {
        console.error('Error fetching marketplaces:', err)
        setError(err instanceof Error ? err.message : 'Failed to load marketplaces.')
        setMarketplaces([])
      } finally {
        setLoading(false)
      }
    },
    [currentPage]
  )

  const createMarketplace = useCallback(async (data: MarketplaceCreateInput): Promise<Marketplace> => {
    try {
      setError(null)
      const api = getApi()
      const response = await api.post('/marketplaces', data)
      const created = response.data
      setMarketplaces(prev => [created, ...prev])
      return created
    } catch (err) {
      console.error('Error creating marketplace:', err)
      const msg = err instanceof Error ? err.message : 'Failed to create marketplace.'
      setError(msg)
      throw err
    }
  }, [])

  const updateMarketplace = useCallback(
    async (id: string, data: Partial<MarketplaceCreateInput>): Promise<Marketplace> => {
      try {
        setError(null)
        const api = getApi()
        const response = await api.patch(`/marketplaces/${id}`, data)
        const updated = response.data
        setMarketplaces(prev => prev.map(m => (m.id === id ? updated : m)))
        return updated
      } catch (err) {
        console.error('Error updating marketplace:', err)
        const msg = err instanceof Error ? err.message : 'Failed to update marketplace.'
        setError(msg)
        throw err
      }
    },
    []
  )

  const deleteMarketplace = useCallback(async (id: string): Promise<void> => {
    try {
      setError(null)
      const api = getApi()
      await api.delete(`/marketplaces/${id}`)
      setMarketplaces(prev => prev.filter(m => m.id !== id))
    } catch (err) {
      console.error('Error deleting marketplace:', err)
      const msg = err instanceof Error ? err.message : 'Failed to delete marketplace.'
      setError(msg)
      throw err
    }
  }, [])

  const testConnection = useCallback(async (id: string): Promise<{ success: boolean; message: string }> => {
    try {
      const api = getApi()
      const response = await api.post(`/marketplaces/${id}/test`)
      setMarketplaces(prev =>
        prev.map(m => m.id === id ? { ...m, status: response.data.success ? 'ativo' : 'erro', ultimo_teste: new Date().toISOString() } : m)
      )
      return response.data
    } catch (err) {
      console.error('Error testing connection:', err)
      setMarketplaces(prev =>
        prev.map(m => m.id === id ? { ...m, status: 'erro', ultimo_teste: new Date().toISOString() } : m)
      )
      return { success: false, message: err instanceof Error ? err.message : 'Connection test failed.' }
    }
  }, [])

  const refetch = useCallback(async () => {
    await fetchMarketplaces(currentPage)
  }, [fetchMarketplaces, currentPage])

  return {
    marketplaces,
    loading,
    error,
    totalPages,
    currentPage,
    fetchMarketplaces,
    createMarketplace,
    updateMarketplace,
    deleteMarketplace,
    testConnection,
    refetch,
  }
}
