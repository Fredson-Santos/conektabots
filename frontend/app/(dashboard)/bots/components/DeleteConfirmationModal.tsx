'use client'

import React, { useEffect } from 'react'
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline'
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
  // Focus management and ESC key handling
  useEffect(() => {
    if (isOpen) {
      // Handle ESC key
      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
          onCancel()
        }
      }

      document.addEventListener('keydown', handleKeyDown)
      document.body.style.overflow = 'hidden'

      return () => {
        document.removeEventListener('keydown', handleKeyDown)
        document.body.style.overflow = 'unset'
      }
    }
  }, [isOpen, onCancel])

  if (!isOpen || !bot) return null

  const handleConfirm = async () => {
    await onConfirm()
  }

  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onCancel()
    }
  }

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-black bg-opacity-50 transition-opacity"
        onClick={handleBackdropClick}
        aria-hidden="true"
      />

      {/* Modal */}
      <div
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="delete-title"
        aria-describedby="delete-description"
      >
        <div className="w-full max-w-sm rounded-lg bg-white shadow-lg">
          {/* Header with Warning Icon */}
          <div className="border-b border-gray-200 bg-red-50 px-6 py-6 flex flex-col items-center text-center">
            <div className="rounded-lg bg-red-100 p-3 mb-4">
              <ExclamationTriangleIcon className="h-6 w-6 text-red-600" />
            </div>
            <h2 id="delete-title" className="text-lg font-semibold text-gray-900">
              Delete Bot?
            </h2>
          </div>

          {/* Content */}
          <div className="px-6 py-6">
            <p
              id="delete-description"
              className="text-sm text-gray-700 mb-4"
            >
              This action cannot be undone. The bot{' '}
              <span className="font-semibold text-gray-900">&quot;{bot.nome}&quot;</span> and
              all associated data will be permanently deleted.
            </p>
            <div className="rounded-lg bg-red-50 border border-red-200 p-3">
              <p className="text-xs font-medium text-red-800">
                Warning: This is irreversible
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 border-t border-gray-200 bg-gray-50 px-6 py-4">
            <button
              type="button"
              onClick={onCancel}
              disabled={isLoading}
              className="flex-1 px-4 py-2 rounded-lg font-semibold text-sm text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 active:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleConfirm}
              disabled={isLoading}
              className="flex-1 px-4 py-2 rounded-lg font-semibold text-sm text-white bg-red-600 hover:bg-red-700 active:bg-red-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg
                    className="animate-spin h-4 w-4"
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
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
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
