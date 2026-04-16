'use client'

import React from 'react'
import BotForm from './BotForm'
import { Bot, BotCreateInput } from '../hooks/useBots'

interface CreateBotModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (data: BotCreateInput) => Promise<void>
  bot?: Bot | null
  isLoading?: boolean
}

export default function CreateBotModal({
  isOpen,
  onClose,
  onSubmit,
  bot,
  isLoading = false,
}: CreateBotModalProps) {
  if (!isOpen) return null

  const handleSubmit = async (data: BotCreateInput) => {
    await onSubmit(data)
    onClose()
  }

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-black bg-opacity-50 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="w-full max-w-md rounded-lg bg-white shadow-xl max-h-[90vh] overflow-y-auto">
          {/* Modal Header */}
          <div className="sticky top-0 border-b border-gray-200 bg-white px-6 py-4 flex items-center justify-between">
            <h2 className="text-lg font-bold text-gray-900">
              {bot ? `Edit Bot: ${bot.nome}` : 'Create New Bot'}
            </h2>
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              className="text-gray-400 hover:text-gray-600 transition disabled:opacity-50"
              aria-label="Close modal"
            >
              <svg
                className="h-6 w-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          {/* Modal Body */}
          <div className="px-6 py-4">
            <BotForm
              bot={bot}
              onSubmit={handleSubmit}
              onCancel={onClose}
              isLoading={isLoading}
            />
          </div>
        </div>
      </div>
    </>
  )
}
