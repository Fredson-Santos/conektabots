'use client'

import React from 'react'
import { Bot } from '../hooks/useBots'

interface DeleteConfirmationModalProps {
  isOpen: boolean
  bot: Bot | null
  isLoading?: boolean
  onConfirm: () => Promise<void>
  onCancel: () => void
}

export default function DeleteConfirmationModal({
  isOpen,
  bot,
  isLoading = false,
  onConfirm,
  onCancel,
}: DeleteConfirmationModalProps) {
  if (!isOpen || !bot) return null

  const handleConfirm = async () => {
    await onConfirm()
    onCancel()
  }

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-black bg-opacity-50 backdrop-blur-sm transition-opacity"
        onClick={onCancel}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="w-full max-w-sm rounded-lg bg-white shadow-xl">
          {/* Header */}
          <div className="border-b border-gray-200 bg-white px-6 py-4">
            <h2 className="text-lg font-bold text-gray-900">Delete Bot</h2>
          </div>

          {/* Content */}
          <div className="px-6 py-4 space-y-4">
            <div className="rounded-lg bg-red-50 p-3 border border-red-200">
              <p className="text-sm text-red-800">
                <span className="font-semibold">Warning:</span> This action
                cannot be undone. All associated data will be permanently deleted.
              </p>
            </div>

            <p className="text-gray-700">
              Are you sure you want to delete the bot{' '}
              <span className="font-semibold text-gray-900">&quot;{bot.nome}&quot;</span>?
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-3 border-t border-gray-200 bg-gray-50 px-6 py-4">
            <button
              type="button"
              onClick={onCancel}
              disabled={isLoading}
              className="flex-1 px-4 py-2 rounded-lg font-semibold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed bg-gray-200 text-gray-800 hover:bg-gray-300 active:bg-gray-400"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleConfirm}
              disabled={isLoading}
              className="flex-1 px-4 py-2 rounded-lg font-semibold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed bg-red-600 text-white hover:bg-red-700 active:bg-red-800"
            >
              {isLoading ? (
                <span className="flex items-center justify-center">
                  <svg
                    className="animate-spin -ml-1 mr-2 h-4 w-4 text-current"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Deleting...
                </span>
              ) : (
                'Delete Bot'
              )}
            </button>
          </div>
        </div>
      </div>
    </>
  )
}
