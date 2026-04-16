'use client'

import { useState } from 'react'
import { Marketplace, MarketplaceCreateInput, MarketplaceType, MARKETPLACE_FIELD_SCHEMAS } from '../hooks/useMarketplaces'

const MARKETPLACE_OPTIONS = [
  { value: 'shopee' as MarketplaceType, label: 'Shopee', icon: '🛍️', desc: 'Integração com Shopee via API Parceiro' },
  { value: 'mercadolivre' as MarketplaceType, label: 'Mercado Livre', icon: '🛒', desc: 'Conecte sua conta ML' },
  { value: 'amazon' as MarketplaceType, label: 'Amazon', icon: '📦', desc: 'Amazon Seller Central API' },
  { value: 'magalu' as MarketplaceType, label: 'Magazine Luiza', icon: '🏪', desc: 'Integração Magalu via API' },
  { value: 'outro' as MarketplaceType, label: 'Outro', icon: '🔗', desc: 'Outro marketplace via API genérica' },
]

interface MarketplaceFormProps {
  onSubmit: (data: MarketplaceCreateInput) => Promise<void>
  onCancel: () => void
  initialData?: Marketplace | null
  isLoading: boolean
}

export default function MarketplaceForm({ onSubmit, onCancel, initialData, isLoading }: MarketplaceFormProps) {
  const [step, setStep] = useState(initialData ? 1 : 0)
  const [error, setError] = useState<string | null>(null)
  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({})

  const [formData, setFormData] = useState<MarketplaceCreateInput>({
    nome: initialData?.nome || '',
    tipo: initialData?.tipo || 'shopee',
    credenciais: {},
  })

  const fields = MARKETPLACE_FIELD_SCHEMAS[formData.tipo] || []

  const handlesubmit = async () => {
    setError(null)
    if (!formData.nome.trim()) { setError('Nome é obrigatório'); return }
    const missing = fields.filter(f => f.required && !formData.credenciais[f.key])
    if (missing.length > 0) {
      setError(`Campos obrigatórios: ${missing.map(f => f.label).join(', ')}`)
      return
    }
    try {
      await onSubmit(formData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao salvar.')
    }
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Step 0: Select type (only for new) */}
      {step === 0 && !initialData && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">Nome da Integração *</label>
            <input
              type="text"
              value={formData.nome}
              onChange={e => setFormData(p => ({ ...p, nome: e.target.value }))}
              placeholder="Ex: Minha loja Shopee"
              className="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Tipo de Marketplace *</label>
            <div className="grid grid-cols-1 gap-2">
              {MARKETPLACE_OPTIONS.map(opt => (
                <button
                  key={opt.value}
                  onClick={() => setFormData(p => ({ ...p, tipo: opt.value, credenciais: {} }))}
                  className={`flex items-center gap-3 p-3 rounded-xl border-2 text-left transition-all ${
                    formData.tipo === opt.value ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  <span className="text-2xl">{opt.icon}</span>
                  <div>
                    <p className="font-semibold text-sm text-gray-900">{opt.label}</p>
                    <p className="text-xs text-gray-500">{opt.desc}</p>
                  </div>
                  {formData.tipo === opt.value && (
                    <span className="ml-auto text-blue-600">✓</span>
                  )}
                </button>
              ))}
            </div>
          </div>
          <div className="flex justify-end pt-2">
            <button
              onClick={() => setStep(1)}
              disabled={!formData.nome.trim()}
              className="px-5 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              Configurar Credenciais →
            </button>
          </div>
        </div>
      )}

      {/* Step 1: Credentials */}
      {step === 1 && (
        <div className="space-y-4">
          <div className="flex items-center gap-2 p-3 bg-blue-50 rounded-xl border border-blue-200">
            <span className="text-xl">{MARKETPLACE_OPTIONS.find(o => o.value === formData.tipo)?.icon}</span>
            <div>
              <p className="text-sm font-semibold text-blue-900">{formData.nome}</p>
              <p className="text-xs text-blue-600">{MARKETPLACE_OPTIONS.find(o => o.value === formData.tipo)?.label}</p>
            </div>
            {!initialData && (
              <button onClick={() => setStep(0)} className="ml-auto text-xs text-blue-600 hover:underline">Alterar</button>
            )}
          </div>

          <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl">
            <p className="text-xs text-amber-800">
              🔒 Suas credenciais são criptografadas com AES-256 antes de serem armazenadas. Nunca são expostas em texto claro.
            </p>
          </div>

          {fields.map(field => (
            <div key={field.key}>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {field.label} {field.required && <span className="text-red-500">*</span>}
              </label>
              <div className="relative">
                <input
                  type={field.secret && !showSecrets[field.key] ? 'password' : 'text'}
                  value={formData.credenciais[field.key] || ''}
                  onChange={e => setFormData(p => ({ ...p, credenciais: { ...p.credenciais, [field.key]: e.target.value } }))}
                  placeholder={field.placeholder}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 pr-10"
                />
                {field.secret && (
                  <button
                    type="button"
                    onClick={() => setShowSecrets(p => ({ ...p, [field.key]: !p[field.key] }))}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showSecrets[field.key] ? (
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                      </svg>
                    ) : (
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    )}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{error}</div>
      )}

      {/* Footer */}
      {step === 1 && (
        <div className="flex gap-3 pt-2 border-t border-gray-100">
          <button onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            Cancelar
          </button>
          <div className="flex-1" />
          <button
            onClick={handlesubmit}
            disabled={isLoading}
            className="px-5 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center gap-2"
          >
            {isLoading && (
              <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            )}
            {initialData ? 'Salvar Alterações' : 'Criar Integração'}
          </button>
        </div>
      )}
    </div>
  )
}
