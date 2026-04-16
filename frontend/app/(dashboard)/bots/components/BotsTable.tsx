'use client'

import React, { useState } from 'react'
import {
  CheckCircleIcon,
  XCircleIcon,
  PencilIcon,
  TrashIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline'
import { Bot } from '../hooks/useBots'

interface BotsTableProps {
  bots: Bot[]
  loading?: boolean
  onEdit: (bot: Bot) => void
  onDelete: (bot: Bot) => void
  onToggleStatus: (bot: Bot) => Promise<void>
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
}

export default function BotsTable({
  bots,
  loading = false,
  onEdit,
  onDelete,
  onToggleStatus,
  currentPage,
  totalPages,
  onPageChange,
}: BotsTableProps) {
  const [togglingId, setTogglingId] = useState<string | null>(null)

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('pt-BR', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    } catch {
      return 'Invalid date'
    }
  }

  const handleToggleStatus = async (bot: Bot) => {
    setTogglingId(bot.id)
    try {
      await onToggleStatus(bot)
    } finally {
      setTogglingId(null)
    }
  }

  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="rounded-lg border border-gray-200 bg-white p-4 h-16 opacity-60 animate-pulse"
          >
            <div className="flex gap-4">
              <div className="h-4 w-32 bg-gray-300 rounded" />
              <div className="h-4 w-32 bg-gray-300 rounded" />
              <div className="h-4 w-16 bg-gray-300 rounded" />
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (bots.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-gray-50 p-12 text-center">
        <div className="flex justify-center mb-4">
          <SparklesIcon className="h-12 w-12 text-gray-400" />
        </div>
        <p className="text-lg font-semibold text-gray-900">No bots yet</p>
        <p className="mt-2 text-sm text-gray-600">
          Create your first bot to get started
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Table - Desktop View */}
      <div className="hidden md:block overflow-x-auto rounded-lg border border-gray-200 bg-white">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50">
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase tracking-wide">
                Bot Name
              </th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase tracking-wide">
                API ID
              </th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase tracking-wide">
                Status
              </th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase tracking-wide">
                Created
              </th>
              <th className="px-6 py-4 text-right text-xs font-medium text-gray-600 uppercase tracking-wide">
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            {bots.map((bot) => (
              <tr
                key={bot.id}
                className="border-b border-gray-200 hover:bg-gray-50 transition-colors"
              >
                {/* Bot Name */}
                <td className="px-6 py-4 text-sm font-medium text-gray-900">
                  {bot.nome}
                </td>

                {/* API ID */}
                <td className="px-6 py-4 text-sm text-gray-600 font-mono">
                  {bot.api_id}
                </td>

                {/* Status */}
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    {bot.ativo ? (
                      <>
                        <CheckCircleIcon className="h-5 w-5 text-green-600" />
                        <span className="text-sm font-medium text-green-600">
                          Active
                        </span>
                      </>
                    ) : (
                      <>
                        <XCircleIcon className="h-5 w-5 text-gray-400" />
                        <span className="text-sm font-medium text-gray-600">
                          Inactive
                        </span>
                      </>
                    )}
                  </div>
                </td>

                {/* Created Date */}
                <td className="px-6 py-4 text-sm text-gray-600">
                  {formatDate(bot.criado_em)}
                </td>

                {/* Actions */}
                <td className="px-6 py-4">
                  <div className="flex items-center justify-end gap-1">
                    <button
                      onClick={() => onEdit(bot)}
                      className="inline-flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-100 transition-colors"
                      title="Edit bot"
                    >
                      <PencilIcon className="h-4 w-4" />
                      <span className="hidden sm:inline">Edit</span>
                    </button>
                    <button
                      onClick={() => onDelete(bot)}
                      className="inline-flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
                      title="Delete bot"
                    >
                      <TrashIcon className="h-4 w-4" />
                      <span className="hidden sm:inline">Delete</span>
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Card View - Mobile */}
      <div className="md:hidden space-y-3">
        {bots.map((bot) => (
          <div
            key={bot.id}
            className="rounded-lg border border-gray-200 bg-white p-4"
          >
            <div className="flex items-start justify-between gap-4 mb-3">
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-gray-900 truncate">
                  {bot.nome}
                </h3>
                <p className="text-sm text-gray-600 font-mono mt-1 truncate">
                  {bot.api_id}
                </p>
              </div>
              {bot.ativo ? (
                <CheckCircleIcon className="h-5 w-5 text-green-600 flex-shrink-0" />
              ) : (
                <XCircleIcon className="h-5 w-5 text-gray-400 flex-shrink-0" />
              )}
            </div>

            <div className="mb-3 text-xs text-gray-500">
              Created {formatDate(bot.criado_em)}
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => onEdit(bot)}
                className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
              >
                <PencilIcon className="h-4 w-4" />
                Edit
              </button>
              <button
                onClick={() => onDelete(bot)}
                className="flex-1 rounded-lg border border-red-300 px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50 transition-colors flex items-center justify-center gap-2"
              >
                <TrashIcon className="h-4 w-4" />
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-6 border-t border-gray-200">
          <div className="text-sm text-gray-600">
            Page {currentPage} of {totalPages} • {bots.length} items shown
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => onPageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="px-4 py-2 rounded-lg border border-gray-300 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Previous
            </button>
            <button
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage >= totalPages}
              className="px-4 py-2 rounded-lg border border-gray-300 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
