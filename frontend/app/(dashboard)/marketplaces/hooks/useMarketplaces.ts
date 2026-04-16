'use client'

import { useState, useCallback } from 'react'
import { getApi } from '@/lib/api'

export type MarketplaceType =
  | 'shopee'
  | 'mercado_livre'
  | 'amazon'
  | 'magalu'
  | 'americanas'
  | 'aliexpress'
  | 'shein'
  | 'outro'

export interface Marketplace {
  id: string
  tenant_id: string
  nome: string
  tipo: MarketplaceType
  ativo: boolean
  is_configured: boolean
  criado_em: string
  atualizado_em: string
  deletado_em?: string | null
}

export interface MarketplaceCreateInput {
  nome: string
  tipo: MarketplaceType
  credenciais?: Record<string, string>
}

export interface MarketplaceUpdateInput {
  nome?: string
  tipo?: MarketplaceType
  credenciais?: Record<string, string>
  ativo?: boolean
}

export const MARKETPLACE_FIELD_SCHEMAS: Record<MarketplaceType, { key: string; label: string; placeholder: string; required: boolean; secret?: boolean }[]> = {
  shopee: [
    { key: 'shop_id', label: 'Shop ID', placeholder: 'Ex: 123456', required: true },
    { key: 'app_id', label: 'App ID', placeholder: 'Identificador da aplicação', required: true },
    { key: 'app_secret', label: 'App Secret', placeholder: 'Chave secreta da integração', required: true, secret: true },
    { key: 'access_token', label: 'Access Token', placeholder: 'Token de acesso atual', required: false, secret: true },
  ],
  mercado_livre: [
    { key: 'app_id', label: 'App ID', placeholder: 'App ID do Mercado Livre', required: true },
    { key: 'app_secret', label: 'App Secret', placeholder: 'Secret da aplicação', required: true, secret: true },
    { key: 'access_token', label: 'Access Token', placeholder: 'Token de acesso', required: true, secret: true },
    { key: 'user_id', label: 'User ID', placeholder: 'Identificador do vendedor', required: true },
  ],
  amazon: [
    { key: 'aws_access_key', label: 'AWS Access Key', placeholder: 'AKIA...', required: true },
    { key: 'aws_secret_key', label: 'AWS Secret Key', placeholder: 'Chave secreta AWS', required: true, secret: true },
    { key: 'seller_id', label: 'Seller ID', placeholder: 'Merchant token', required: true },
    { key: 'region', label: 'Region', placeholder: 'us-east-1', required: false },
  ],
  magalu: [
    { key: 'client_id', label: 'Client ID', placeholder: 'ID da integração', required: true },
    { key: 'client_secret', label: 'Client Secret', placeholder: 'Secret da API', required: true, secret: true },
  ],
  outro: [
    { key: 'api_key', label: 'API Key', placeholder: 'Chave da API', required: true, secret: true },
    { key: 'endpoint', label: 'Endpoint URL', placeholder: 'https://api.exemplo.com', required: false },
  ],
  americanas: [
    { key: 'app_id', label: 'App ID', placeholder: 'ID da aplicação', required: true },
    { key: 'app_secret', label: 'App Secret', placeholder: 'Secret da aplicação', required: true, secret: true },
  ],
  aliexpress: [
    { key: 'app_key', label: 'App Key', placeholder: 'Chave da aplicação', required: true },
    { key: 'app_secret', label: 'App Secret', placeholder: 'Secret da aplicação', required: true, secret: true },
    { key: 'api_gateway', label: 'API Gateway', placeholder: 'https://api.example.com', required: true },
  ],
  shein: [
    { key: 'app_key', label: 'App Key', placeholder: 'Chave da integração', required: true },
    { key: 'app_secret', label: 'App Secret', placeholder: 'Secret da integração', required: true, secret: true },
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
  updateMarketplace: (id: string, data: MarketplaceUpdateInput) => Promise<Marketplace>
  deleteMarketplace: (id: string) => Promise<void>
  setMarketplaceActive: (id: string, ativo: boolean) => Promise<Marketplace>
  refetch: () => Promise<void>
}

const normalizeMarketplace = (marketplace: unknown): Marketplace => {
  const raw = marketplace as Record<string, unknown>
  const tipo = raw.tipo === 'mercadolivre' ? 'mercado_livre' : String(raw.tipo || 'outro') as MarketplaceType

  return {
    id: String(raw.id || ''),
    tenant_id: String(raw.tenant_id || ''),
    nome: String(raw.nome || ''),
    tipo,
    ativo: Boolean(raw.ativo),
    is_configured: Boolean(raw.is_configured),
    criado_em: String(raw.criado_em || ''),
    atualizado_em: String(raw.atualizado_em || raw.criado_em || ''),
    deletado_em: raw.deletado_em ? String(raw.deletado_em) : null,
  }
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
          list = data.map(normalizeMarketplace)
          setTotalPages(Math.ceil(data.length / size))
        } else if (data.items) {
          list = data.items.map(normalizeMarketplace)
          setTotalPages(data.total_pages || 1)
        } else if (data.data) {
          list = Array.isArray(data.data) ? data.data.map(normalizeMarketplace) : []
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
      const normalized = normalizeMarketplace(created)
      setMarketplaces(prev => [normalized, ...prev])
      return normalized
    } catch (err) {
      console.error('Error creating marketplace:', err)
      const msg = err instanceof Error ? err.message : 'Failed to create marketplace.'
      setError(msg)
      throw err
    }
  }, [])

  const updateMarketplace = useCallback(
    async (id: string, data: MarketplaceUpdateInput): Promise<Marketplace> => {
      try {
        setError(null)
        const api = getApi()
        const response = await api.patch(`/marketplaces/${id}`, data)
        const updated = normalizeMarketplace(response.data)
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

  const setMarketplaceActive = useCallback(
    async (id: string, ativo: boolean): Promise<Marketplace> => {
      const updated = await updateMarketplace(id, { ativo })
      return updated
    },
    [updateMarketplace]
  )

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
    setMarketplaceActive,
    refetch,
  }
}
