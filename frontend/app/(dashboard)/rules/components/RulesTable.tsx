'use client'

import React, { useState } from 'react'
import { Regra, useRules } from '../hooks/useRules'
import { UUID } from '@/lib/types'

interface RulesTableProps {
  onEdit: (rule: Regra) => void
  onRefresh: () => void
}

/**
 * Paginated Rules Table Component
 *
 * Features:
 * - Display rules in paginated table (20 items/page)
 * - Enable/disable toggle
 * - Delete with confirmation
 * - Status indicator (active/inactive)
 * - Responsive design (mobile-friendly)
 * - Accessibility (ARIA labels, keyboard navigation)
 */
export function RulesTable({ onEdit, onRefresh }: RulesTableProps) {
  const { rules, loading, error, toggle, delete: deleteRule } = useRules()
  const ITEMS_PER_PAGE = 20

  const [currentPage, setCurrentPage] = useState(1)
  const [searchTerm, setSearchTerm] = useState('')
  const [deleteConfirm, setDeleteConfirm] = useState<UUID | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)

  const filteredRules = rules.filter((rule) =>
    rule.nome.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const totalPages = Math.ceil(filteredRules.length / ITEMS_PER_PAGE)
  const paginatedRules = filteredRules.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  )

  const handleDelete = async (ruleId: UUID) => {
    setIsDeleting(true)
    try {
      await deleteRule(ruleId)
      setDeleteConfirm(null)
      onRefresh()
    } catch (err) {
      console.error('Failed to delete rule:', err)
    } finally {
      setIsDeleting(false)
    }
  }

  const handleToggle = async (rule: Regra) => {
    try {
      await toggle(rule.id, rule.ativo)
      onRefresh()
    } catch (err) {
      console.error('Failed to toggle rule:', err)
    }
  }

  if (loading && rules.length === 0) {
    return (
      <div className="space-y-4">
        <div className="animate-pulse space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-16 bg-gray-200 rounded-lg" />
          ))}
        </div>
      </div>
    )
  }

  if (error && rules.length === 0) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4">
        <p className="text-sm text-red-700">Erro ao carregar regras: {error}</p>
      </div>
    )
  }

  if (rules.length === 0) {
    return (
      <div className="rounded-lg border-2 border-dashed border-gray-300 bg-gray-50 p-12 text-center">
        <p className="text-lg text-gray-600">Nenhuma regra criada ainda</p>
        <p className="mt-1 text-sm text-gray-500">
          Clique em "Nova Regra" para começar
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Search */}
      <div className="flex gap-3">
        <input
          type="text"
          placeholder="Buscar regras..."
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value)
            setCurrentPage(1)
          }}
          className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          aria-label="Buscar regras"
        />
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
        <table className="w-full text-sm">
          <thead className="border-b border-gray-200 bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left font-medium text-gray-700">
                Nome
              </th>
              <th className="px-6 py-3 text-left font-medium text-gray-700">
                Bot
              </th>
              <th className="px-6 py-3 text-left font-medium text-gray-700">
                Status
              </th>
              <th className="px-6 py-3 text-right font-medium text-gray-700">
                Ações
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {paginatedRules.map((rule) => (
              <tr
                key={rule.id}
                className="hover:bg-gray-50 transition-colors"
              >
                <td className="px-6 py-4">
                  <p className="font-medium text-gray-900">{rule.nome}</p>
                  <p className="mt-0.5 text-xs text-gray-500">
                    ID: {String(rule.id).substring(0, 8)}
                  </p>
                </td>
                <td className="px-6 py-4 text-gray-600">
                  {String(rule.bot_id).substring(0, 8)}
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleToggle(rule)}
                      className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                        rule.ativo
                          ? 'bg-green-100 text-green-700 hover:bg-green-200'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                      aria-label={`${rule.ativo ? 'Desativar' : 'Ativar'} regra ${rule.nome}`}
                    >
                      {rule.ativo ? 'Ativa' : 'Inativa'}
                    </button>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex justify-end gap-2">
                    <button
                      onClick={() => onEdit(rule)}
                      className="inline-flex items-center gap-2 rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                      aria-label={`Editar regra ${rule.nome}`}
                    >
                      ✎ Editar
                    </button>
                    <button
                      onClick={() => setDeleteConfirm(rule.id)}
                      className="inline-flex items-center gap-2 rounded-lg border border-red-200 px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
                      aria-label={`Deletar regra ${rule.nome}`}
                    >
                      🗑 Deletar
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-600">
            Exibindo {(currentPage - 1) * ITEMS_PER_PAGE + 1}-
            {Math.min(currentPage * ITEMS_PER_PAGE, filteredRules.length)} de{' '}
            {filteredRules.length}
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
              aria-label="Página anterior"
            >
              ← Anterior
            </button>
            <div className="flex items-center gap-1">
              {Array.from({ length: Math.min(totalPages, 5) }).map((_, i) => {
                const pageNum = totalPages > 5 ? Math.max(1, currentPage - 2) + i : i + 1
                if (pageNum > totalPages) return null
                return (
                  <button
                    key={pageNum}
                    onClick={() => setCurrentPage(pageNum)}
                    className={`rounded px-2 py-1 text-sm font-medium ${
                      currentPage === pageNum
                        ? 'bg-blue-500 text-white'
                        : 'border border-gray-300 text-gray-700 hover:bg-gray-50'
                    }`}
                    aria-label={`Ir para página ${pageNum}`}
                  >
                    {pageNum}
                  </button>
                )
              })}
            </div>
            <button
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
              aria-label="Próxima página"
            >
              Próximo →
            </button>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-lg">
            <h3 className="text-lg font-bold text-gray-900">
              Confirmar exclusão
            </h3>
            <p className="mt-2 text-sm text-gray-600">
              Tem certeza que deseja deletar esta regra? Esta ação não pode ser
              desfeita.
            </p>
            <div className="mt-6 flex gap-3 justify-end">
              <button
                onClick={() => setDeleteConfirm(null)}
                disabled={isDeleting}
                className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                onClick={() => deleteConfirm && handleDelete(deleteConfirm)}
                disabled={isDeleting}
                className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
              >
                {isDeleting ? 'Deletando...' : 'Deletar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
