'use client'

import React, { useEffect, useRef } from 'react'
import { XMarkIcon } from '@heroicons/react/24/outline'
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
  const modalRef = useRef<HTMLDivElement>(null)
  const firstInputRef = useRef<HTMLInputElement>(null)

  // Focus management
  useEffect(() => {
    if (isOpen) {
      // Focus first input when modal opens
      setTimeout(() => {
        const input = modalRef.current?.querySelector('input[type="text"]')
        if (input instanceof HTMLInputElement) {
          input.focus()
        }
      }, 0)

      // Trap focus within modal and handle ESC key
      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
          onClose()
        }
      }

      document.addEventListener('keydown', handleKeyDown)
      document.body.style.overflow = 'hidden'

      return () => {
        document.removeEventListener('keydown', handleKeyDown)
        document.body.style.overflow = 'unset'
      }
    }
  }, [isOpen, onClose])

  if (!isOpen) return null

  const handleSubmit = async (data: BotCreateInput) => {
    await onSubmit(data)
    onClose()
  }

  const handleBackdropClick = (
    e: React.MouseEvent<HTMLDivElement>
  ) => {
    if (e.target === e.currentTarget) {
      onClose()
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
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <div
          ref={modalRef}
          className="w-full max-w-md rounded-lg bg-white shadow-lg max-h-[90vh] overflow-y-auto"
        >
          {/* Modal Header */}
          <div className="sticky top-0 border-b border-gray-200 bg-white px-6 py-4 flex items-center justify-between">
            <h2 id="modal-title" className="text-lg font-semibold text-gray-900">
              {bot ? `Edit Bot: ${bot.nome}` : 'Create New Bot'}
            </h2>
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors disabled:opacity-50"
              aria-label="Close modal"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          {/* Modal Body */}
          <div className="px-6 py-6">
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
