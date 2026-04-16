'use client'

import { Marketplace, MarketplaceType } from '../hooks/useMarketplaces'

const MARKETPLACE_OPTIONS: { value: MarketplaceType; label: string; icon: string; color: string }[] = [
  { value: 'shopee', label: 'Shopee', icon: '🛍️', color: 'bg-orange-50 border-orange-200 text-orange-700' },
  { value: 'mercadolivre', label: 'Mercado Livre', icon: '🛒', color: 'bg-yellow-50 border-yellow-200 text-yellow-700' },
  { value: 'amazon', label: 'Amazon', icon: '📦', color: 'bg-amber-50 border-amber-200 text-amber-700' },
  { value: 'magalu', label: 'Magazine Luiza', icon: '🏪', color: 'bg-blue-50 border-blue-200 text-blue-700' },
  { value: 'outro', label: 'Outro', icon: '🔗', color: 'bg-gray-50 border-gray-200 text-gray-700' },
]

const STATUS_CONFIG = {
  ativo: { label: 'Ativo', color: 'bg-green-100 text-green-700', dot: 'bg-green-500' },
  inativo: { label: 'Inativo', color: 'bg-gray-100 text-gray-600', dot: 'bg-gray-400' },
  erro: { label: 'Erro', color: 'bg-red-100 text-red-700', dot: 'bg-red-500' },
  testando: { label: 'Testando...', color: 'bg-blue-100 text-blue-700', dot: 'bg-blue-500' },
}

interface MarketplacesTableProps {
  marketplaces: Marketplace[]
  loading: boolean
  onEdit: (m: Marketplace) => void
  onDelete: (m: Marketplace) => void
  onTestConnection: (m: Marketplace) => void
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
  onTestConnection,
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
              {['Integração', 'Tipo', 'Status', 'Último Teste', 'Ações'].map(h => (
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
        <div className="text-5xl mb-4">🔗</div>
        <h3 className="text-lg font-semibold text-gray-900">Nenhuma integração configurada</h3>
        <p className="mt-2 text-sm text-gray-500">
          Conecte sua primeira plataforma de marketplace para começar.
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
              {['Integração', 'Tipo', 'Status', 'Último Teste', 'Ações'].map(h => (
                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 bg-white">
            {marketplaces.map(m => {
              const tipo = MARKETPLACE_OPTIONS.find(o => o.value === m.tipo)
              const status = STATUS_CONFIG[m.status] || STATUS_CONFIG.inativo
              return (
                <tr key={m.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3">
                    <p className="font-medium text-gray-900 text-sm">{m.nome}</p>
                    <p className="text-xs text-gray-400 font-mono">{m.id?.slice(0, 12)}...</p>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium border ${tipo?.color}`}>
                      {tipo?.icon} {tipo?.label}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium ${status.color}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${status.dot}`} />
                      {status.label}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-500">
                    {m.ultimo_teste
                      ? new Date(m.ultimo_teste).toLocaleString('pt-BR')
                      : 'Nunca testado'}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => onTestConnection(m)}
                        className="p-1.5 rounded-lg text-green-600 hover:bg-green-50 transition-colors"
                        title="Testar conexão"
                      >
                        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </button>
                      <button
                        onClick={() => onEdit(m)}
                        className="p-1.5 rounded-lg text-blue-600 hover:bg-blue-50 transition-colors"
                        title="Editar"
                      >
                        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                      <button
                        onClick={() => onDelete(m)}
                        className="p-1.5 rounded-lg text-red-500 hover:bg-red-50 transition-colors"
                        title="Excluir"
                      >
                        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
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
        {marketplaces.map(m => {
          const tipo = MARKETPLACE_OPTIONS.find(o => o.value === m.tipo)
          const status = STATUS_CONFIG[m.status] || STATUS_CONFIG.inativo
          return (
            <div key={m.id} className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-semibold text-gray-900">{m.nome}</p>
                  <span className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-lg border mt-1 ${tipo?.color}`}>
                    {tipo?.icon} {tipo?.label}
                  </span>
                </div>
                <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium ${status.color}`}>
                  <span className={`w-1.5 h-1.5 rounded-full ${status.dot}`} />
                  {status.label}
                </span>
              </div>
              <p className="text-xs text-gray-400 mt-2">
                {m.ultimo_teste ? `Testado: ${new Date(m.ultimo_teste).toLocaleString('pt-BR')}` : 'Nunca testado'}
              </p>
              <div className="mt-3 flex gap-2">
                <button onClick={() => onTestConnection(m)} className="flex-1 py-1.5 text-xs font-medium text-green-700 bg-green-50 rounded-lg hover:bg-green-100 transition-colors">
                  ✅ Testar
                </button>
                <button onClick={() => onEdit(m)} className="flex-1 py-1.5 text-xs font-medium text-blue-700 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
                  ✏️ Editar
                </button>
                <button onClick={() => onDelete(m)} className="flex-1 py-1.5 text-xs font-medium text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors">
                  🗑 Excluir
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
