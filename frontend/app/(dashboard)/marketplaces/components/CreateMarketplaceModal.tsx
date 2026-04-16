'use client'

import { Marketplace, MarketplaceCreateInput } from '../hooks/useMarketplaces'
import MarketplaceForm from './MarketplaceForm'
import { ShoppingBagIcon, XMarkIcon } from '@heroicons/react/24/outline'

interface CreateMarketplaceModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (data: MarketplaceCreateInput) => Promise<void>
  marketplace?: Marketplace | null
  isLoading: boolean
}

export default function CreateMarketplaceModal({ isOpen, onClose, onSubmit, marketplace, isLoading }: CreateMarketplaceModalProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      <div className="relative flex w-full max-w-2xl flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-2xl max-h-[90vh]">
        {/* Header */}
        <div className="flex items-start justify-between gap-4 border-b border-gray-100 px-6 py-5">
          <div className="flex items-start gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
              <ShoppingBagIcon className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                {marketplace ? `Editar integração` : 'Nova integração'}
              </h2>
              <p className="mt-0.5 text-sm text-gray-500">
                {marketplace ? marketplace.nome : 'Conecte um marketplace ao ConektaBots'}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-2 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
            aria-label="Fechar modal"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6">
          <MarketplaceForm
            onSubmit={onSubmit}
            onCancel={onClose}
            initialData={marketplace}
            isLoading={isLoading}
          />
        </div>
      </div>
    </div>
  )
}
