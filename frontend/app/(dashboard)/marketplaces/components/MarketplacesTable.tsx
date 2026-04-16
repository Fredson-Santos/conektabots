'use client'

import { Marketplace, MarketplaceType } from '../hooks/useMarketplaces'

import {
  BuildingStorefrontIcon,
  CubeIcon,
  LinkIcon,
  PencilIcon,
  PlusIcon,
  PowerIcon,
  ShoppingBagIcon,
  ShieldCheckIcon,
  TrashIcon,
} from '@heroicons/react/24/outline'

const MARKETPLACE_OPTIONS: { value: MarketplaceType; label: string; icon: typeof ShoppingBagIcon; color: string }[] = [
  { value: 'shopee', label: 'Shopee', icon: ShoppingBagIcon, color: 'bg-orange-50 border-orange-200 text-orange-700' },
  { value: 'mercado_livre', label: 'Mercado Livre', icon: BuildingStorefrontIcon, color: 'bg-yellow-50 border-yellow-200 text-yellow-700' },
  { value: 'amazon', label: 'Amazon', icon: CubeIcon, color: 'bg-amber-50 border-amber-200 text-amber-700' },
  { value: 'magalu', label: 'Magazine Luiza', icon: ShieldCheckIcon, color: 'bg-blue-50 border-blue-200 text-blue-700' },
  { value: 'americanas', label: 'Americanas', icon: LinkIcon, color: 'bg-indigo-50 border-indigo-200 text-indigo-700' },
  { value: 'aliexpress', label: 'AliExpress', icon: LinkIcon, color: 'bg-red-50 border-red-200 text-red-700' },
  { value: 'shein', label: 'Shein', icon: LinkIcon, color: 'bg-pink-50 border-pink-200 text-pink-700' },
  { value: 'outro', label: 'Outro', icon: LinkIcon, color: 'bg-gray-50 border-gray-200 text-gray-700' },
]

const STATUS_CONFIG = {
  active: { label: 'Ativo', color: 'bg-green-50 text-green-700 border-green-200', dot: 'bg-green-500' },
  inactive: { label: 'Inativo', color: 'bg-gray-50 text-gray-700 border-gray-200', dot: 'bg-gray-400' },
  configured: { label: 'Configurado', color: 'bg-blue-50 text-blue-700 border-blue-200', dot: 'bg-blue-500' },
  missing: { label: 'Sem credenciais', color: 'bg-amber-50 text-amber-700 border-amber-200', dot: 'bg-amber-500' },
}

interface MarketplacesTableProps {
  marketplaces: Marketplace[]
  loading: boolean
  onEdit: (m: Marketplace) => void
  onDelete: (m: Marketplace) => void
  onToggleActive: (m: Marketplace) => Promise<void>
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
}

function SkeletonRow() {
  return (
    <tr className="animate-pulse">
      {[...Array(5)].map((_, i) => (
        <td key={i} className="px-4 py-3">
          <div className="h-4 bg-gray-200 rounded w-3/4" />
        </td>
      ))}
    </tr>
  )
}

export default function MarketplacesTable({
  marketplaces,
  loading,
  onEdit,
  onDelete,
  onToggleActive,
  currentPage,
  totalPages,
  onPageChange,
}: MarketplacesTableProps) {
  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {['Integração', 'Tipo', 'Estado', 'Atualizado', 'Ações'].map((h) => (
                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {[...Array(4)].map((_, i) => <SkeletonRow key={i} />)}
          </tbody>
        </table>
      </div>
    )
  }

  if (marketplaces.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-12 text-center shadow-sm">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-gray-100">
          <PlusIcon className="h-6 w-6 text-gray-400" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900">Nenhuma integração configurada</h3>
        <p className="mt-2 text-sm text-gray-500">
          Crie a primeira integração para começar a conectar pedidos e regras.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Desktop */}
      <div className="hidden md:block bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {['Integração', 'Tipo', 'Estado', 'Atualizado', 'Ações'].map((h) => (
                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 bg-white">
            {marketplaces.map((m) => {
              const tipo = MARKETPLACE_OPTIONS.find((o) => o.value === m.tipo)
              const status = m.ativo ? STATUS_CONFIG.active : STATUS_CONFIG.inactive
              const configState = m.is_configured ? STATUS_CONFIG.configured : STATUS_CONFIG.missing
              return (
                <tr key={m.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3">
                    <p className="font-medium text-gray-900 text-sm">{m.nome}</p>
                    <p className="text-xs text-gray-400 font-mono">{m.id?.slice(0, 12)}...</p>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium border ${tipo?.color}`}>
                      {tipo ? <tipo.icon className="h-3.5 w-3.5" /> : null}
                      {tipo?.label || m.tipo}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="space-y-2">
                      <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium border ${status.color}`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${status.dot}`} />
                        {status.label}
                      </span>
                      <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium border ${configState.color}`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${configState.dot}`} />
                        {configState.label}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-500">
                    {m.atualizado_em
                      ? new Date(m.atualizado_em).toLocaleString('pt-BR')
                      : new Date(m.criado_em).toLocaleString('pt-BR')}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => onToggleActive(m)}
                        className={`p-1.5 rounded-lg transition-colors ${m.ativo ? 'text-amber-600 hover:bg-amber-50' : 'text-green-600 hover:bg-green-50'}`}
                        title={m.ativo ? 'Desativar' : 'Ativar'}
                      >
                        <PowerIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => onEdit(m)}
                        className="p-1.5 rounded-lg text-blue-600 hover:bg-blue-50 transition-colors"
                        title="Editar"
                      >
                        <PencilIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => onDelete(m)}
                        className="p-1.5 rounded-lg text-red-500 hover:bg-red-50 transition-colors"
                        title="Excluir"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Mobile Cards */}
      <div className="md:hidden space-y-3">
        {marketplaces.map((m) => {
          const tipo = MARKETPLACE_OPTIONS.find((o) => o.value === m.tipo)
          const status = m.ativo ? STATUS_CONFIG.active : STATUS_CONFIG.inactive
          const configState = m.is_configured ? STATUS_CONFIG.configured : STATUS_CONFIG.missing
          return (
            <div key={m.id} className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-semibold text-gray-900">{m.nome}</p>
                  <span className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-lg border mt-1 ${tipo?.color}`}>
                    {tipo ? <tipo.icon className="h-3.5 w-3.5" /> : null}
                    {tipo?.label || m.tipo}
                  </span>
                </div>
                <div className="flex flex-col items-end gap-1">
                  <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium border ${status.color}`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${status.dot}`} />
                    {status.label}
                  </span>
                  <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium border ${configState.color}`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${configState.dot}`} />
                    {configState.label}
                  </span>
                </div>
              </div>
              <p className="text-xs text-gray-400 mt-2">
                Atualizado em {new Date(m.atualizado_em || m.criado_em).toLocaleString('pt-BR')}
              </p>
              <div className="mt-3 flex gap-2">
                <button onClick={() => onToggleActive(m)} className={`flex-1 py-1.5 text-xs font-medium rounded-lg transition-colors ${m.ativo ? 'text-amber-700 bg-amber-50 hover:bg-amber-100' : 'text-green-700 bg-green-50 hover:bg-green-100'}`}>
                  {m.ativo ? 'Desativar' : 'Ativar'}
                </button>
                <button onClick={() => onEdit(m)} className="flex-1 py-1.5 text-xs font-medium text-blue-700 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
                  Editar
                </button>
                <button onClick={() => onDelete(m)} className="flex-1 py-1.5 text-xs font-medium text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors">
                  Excluir
                </button>
              </div>
            </div>
          )
        })}
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between px-1">
          <p className="text-sm text-gray-500">Página {currentPage} de {totalPages}</p>
          <div className="flex gap-2">
            <button onClick={() => onPageChange(currentPage - 1)} disabled={currentPage <= 1}
              className="px-3 py-1.5 text-sm font-medium rounded-lg border border-gray-200 text-gray-700 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors">
              ← Anterior
            </button>
            <button onClick={() => onPageChange(currentPage + 1)} disabled={currentPage >= totalPages}
              className="px-3 py-1.5 text-sm font-medium rounded-lg border border-gray-200 text-gray-700 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors">
              Próximo →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
