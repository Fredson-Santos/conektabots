'use client'

import { useEffect, useState } from 'react'
import { useMarketplaces, Marketplace, MarketplaceCreateInput } from './hooks/useMarketplaces'
import MarketplacesTable from './components/MarketplacesTable'
import CreateMarketplaceModal from './components/CreateMarketplaceModal'

function DeleteMarketplaceModal({ isOpen, marketplace, isLoading, onConfirm, onCancel }: {
  isOpen: boolean; marketplace: Marketplace | null; isLoading: boolean
  onConfirm: () => void; onCancel: () => void
}) {
  if (!isOpen || !marketplace) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onCancel} />
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 text-center">
        <div className="w-14 h-14 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
          <svg className="h-7 w-7 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </div>
        <h3 className="text-lg font-bold text-gray-900">Remover Integração</h3>
        <p className="mt-2 text-sm text-gray-600">
          Remover <strong>{marketplace.nome}</strong>? As credenciais serão apagadas permanentemente.
        </p>
        <div className="flex gap-3 mt-6">
          <button onClick={onCancel} className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors">Cancelar</button>
          <button onClick={onConfirm} disabled={isLoading}
            className="flex-1 px-4 py-2 text-sm font-semibold text-white bg-red-600 rounded-xl hover:bg-red-700 disabled:opacity-50 transition-colors flex items-center justify-center gap-2">
            {isLoading && <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>}
            Remover
          </button>
        </div>
      </div>
    </div>
  )
}

export default function MarketplacesPage() {
  const {
    marketplaces, loading, error,
    totalPages, currentPage,
    fetchMarketplaces, createMarketplace, updateMarketplace,
    deleteMarketplace, testConnection,
  } = useMarketplaces()

  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingMarketplace, setEditingMarketplace] = useState<Marketplace | null>(null)
  const [deletingMarketplace, setDeletingMarketplace] = useState<Marketplace | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null)

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { fetchMarketplaces(1) }, [])

  const showToast = (type: 'success' | 'error', message: string) => {
    setToast({ type, message })
    setTimeout(() => setToast(null), 3500)
  }

  const handleCreate = async (data: MarketplaceCreateInput) => {
    setIsSubmitting(true)
    try {
      await createMarketplace(data)
      setIsModalOpen(false)
      showToast('success', 'Integração criada com sucesso!')
    } catch { showToast('error', 'Erro ao criar integração.') }
    finally { setIsSubmitting(false) }
  }

  const handleUpdate = async (data: MarketplaceCreateInput) => {
    if (!editingMarketplace) return
    setIsSubmitting(true)
    try {
      await updateMarketplace(editingMarketplace.id, data)
      setEditingMarketplace(null)
      setIsModalOpen(false)
      showToast('success', 'Integração atualizada!')
    } catch { showToast('error', 'Erro ao atualizar integração.') }
    finally { setIsSubmitting(false) }
  }

  const handleDelete = async () => {
    if (!deletingMarketplace) return
    setIsDeleting(true)
    try {
      await deleteMarketplace(deletingMarketplace.id)
      setDeletingMarketplace(null)
      showToast('success', 'Integração removida.')
    } catch { showToast('error', 'Erro ao remover.') }
    finally { setIsDeleting(false) }
  }

  const handleTest = async (m: Marketplace) => {
    showToast('success', `Testando conexão com ${m.nome}...`)
    const result = await testConnection(m.id)
    showToast(result.success ? 'success' : 'error', result.message || (result.success ? 'Conexão OK!' : 'Teste falhou.'))
  }

  return (
    <div className="space-y-6">
      {/* Toast */}
      {toast && (
        <div className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-xl shadow-lg text-sm font-medium ${
          toast.type === 'success' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
        }`}>
          {toast.type === 'success' ? '✅ ' : '❌ '}{toast.message}
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Marketplaces</h1>
          <p className="mt-1 text-gray-600">Conecte e gerencie integrações com plataformas de venda.</p>
        </div>
        <button
          onClick={() => { setEditingMarketplace(null); setIsModalOpen(true) }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700 transition w-full sm:w-auto justify-center"
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Adicionar Integração
        </button>
      </div>

      {error && !loading && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
          <h3 className="font-semibold">Erro</h3>
          <p className="mt-1 text-sm">{error}</p>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Total', value: marketplaces.length, icon: '🔗' },
          { label: 'Ativos', value: marketplaces.filter(m => m.status === 'ativo').length, icon: '✅' },
          { label: 'Com erro', value: marketplaces.filter(m => m.status === 'erro').length, icon: '❌' },
          { label: 'Inativos', value: marketplaces.filter(m => m.status === 'inativo').length, icon: '⚪' },
        ].map(stat => (
          <div key={stat.label} className="bg-white rounded-xl border border-gray-200 p-3 shadow-sm">
            <p className="text-2xl">{stat.icon}</p>
            <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
            <p className="text-xs text-gray-500">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Table */}
      <MarketplacesTable
        marketplaces={marketplaces}
        loading={loading && marketplaces.length === 0}
        onEdit={m => { setEditingMarketplace(m); setIsModalOpen(true) }}
        onDelete={m => setDeletingMarketplace(m)}
        onTestConnection={handleTest}
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={p => fetchMarketplaces(p)}
      />

      <CreateMarketplaceModal
        isOpen={isModalOpen}
        onClose={() => { setIsModalOpen(false); setEditingMarketplace(null) }}
        onSubmit={editingMarketplace ? handleUpdate : handleCreate}
        marketplace={editingMarketplace}
        isLoading={isSubmitting}
      />

      <DeleteMarketplaceModal
        isOpen={deletingMarketplace !== null}
        marketplace={deletingMarketplace}
        isLoading={isDeleting}
        onConfirm={handleDelete}
        onCancel={() => setDeletingMarketplace(null)}
      />
    </div>
  )
}
