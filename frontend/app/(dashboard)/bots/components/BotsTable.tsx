'use client'

import React, { useState } from 'react'
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
            className="rounded-lg border border-gray-200 bg-white p-4 h-16 animate-pulse"
          >
            <div className="flex gap-4">
              <div className="h-4 w-32 bg-gray-200 rounded" />
              <div className="h-4 w-32 bg-gray-200 rounded" />
              <div className="h-4 w-16 bg-gray-200 rounded" />
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (bots.length === 0) {
    return (
      <div className="rounded-lg border-2 border-dashed border-gray-300 bg-gray-50 p-12 text-center">
        <p className="text-lg text-gray-600 font-medium">No bots yet</p>
        <p className="mt-1 text-sm text-gray-500">
          Create your first bot to get started
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Table - Desktop View */}
      <div className="hidden md:block overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50">
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                Bot Name
              </th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                API ID
              </th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                Status
              </th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                Created
              </th>
              <th className="px-6 py-3 text-right text-sm font-semibold text-gray-900">
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            {bots.map((bot, index) => (
              <tr
                key={bot.id}
                className={`border-b border-gray-200 transition hover:bg-blue-50 ${
                  index % 2 === 0 ? 'bg-white' : 'bg-gray-50'
                }`}
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
                <td className="px-6 py-4 text-sm">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleToggleStatus(bot)}
                      disabled={togglingId === bot.id}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors disabled:opacity-50 ${
                        bot.ativo
                          ? 'bg-green-500 hover:bg-green-600'
                          : 'bg-gray-300 hover:bg-gray-400'
                      }`}
                      aria-label="Toggle bot status"
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          bot.ativo ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                    <span
                      className={`text-xs font-medium ${
                        bot.ativo ? 'text-green-600' : 'text-gray-600'
                      }`}
                    >
                      {bot.ativo ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </td>

                {/* Created Date */}
                <td className="px-6 py-4 text-sm text-gray-600">
                  {formatDate(bot.criado_em)}
                </td>

                {/* Actions */}
                <td className="px-6 py-4">
                  <div className="flex items-center justify-end gap-2">
                    <button
                      onClick={() => onEdit(bot)}
                      className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium text-blue-600 hover:bg-blue-50 transition"
                      title="Edit bot"
                    >
                      <svg
                        className="h-4 w-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                        />
                      </svg>
                      Edit
                    </button>
                    <button
                      onClick={() => onDelete(bot)}
                      className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 transition"
                      title="Delete bot"
                    >
                      <svg
                        className="h-4 w-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                        />
                      </svg>
                      Delete
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
            className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
          >
            <div className="flex items-start justify-between gap-4 mb-3">
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900">{bot.nome}</h3>
                <p className="text-sm text-gray-600 font-mono mt-1">
                  {bot.api_id}
                </p>
              </div>
              <button
                onClick={() => handleToggleStatus(bot)}
                disabled={togglingId === bot.id}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors disabled:opacity-50 ${
                  bot.ativo
                    ? 'bg-green-500 hover:bg-green-600'
                    : 'bg-gray-300 hover:bg-gray-400'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    bot.ativo ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            <div className="mb-3 text-xs text-gray-500">
              Created {formatDate(bot.criado_em)}
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => onEdit(bot)}
                className="flex-1 rounded-lg bg-blue-100 px-3 py-2 text-sm font-medium text-blue-600 hover:bg-blue-200 transition"
              >
                Edit
              </button>
              <button
                onClick={() => onDelete(bot)}
                className="flex-1 rounded-lg bg-red-100 px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-200 transition"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-4">
          <div className="text-sm text-gray-600">
            Page {currentPage} of {totalPages} • {bots.length} items shown
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => onPageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="px-3 py-2 rounded-lg border border-gray-300 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              ← Previous
            </button>
            <button
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage >= totalPages}
              className="px-3 py-2 rounded-lg border border-gray-300 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              Next →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
