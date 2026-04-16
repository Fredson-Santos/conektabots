'use client'

import { useState } from 'react'
import { Marketplace, MarketplaceCreateInput, MarketplaceType, MARKETPLACE_FIELD_SCHEMAS } from '../hooks/useMarketplaces'
import {
  BuildingStorefrontIcon,
  CubeIcon,
  EyeIcon,
  EyeSlashIcon,
  LinkIcon,
  ShoppingBagIcon,
} from '@heroicons/react/24/outline'

const MARKETPLACE_OPTIONS = [
  { value: 'shopee' as MarketplaceType, label: 'Shopee', desc: 'Integração com Shopee via API Parceiro' },
  { value: 'mercado_livre' as MarketplaceType, label: 'Mercado Livre', desc: 'Conecte sua conta do Mercado Livre' },
  { value: 'amazon' as MarketplaceType, label: 'Amazon', desc: 'Amazon Seller Central API' },
  { value: 'magalu' as MarketplaceType, label: 'Magazine Luiza', desc: 'Integração Magalu via API' },
  { value: 'americanas' as MarketplaceType, label: 'Americanas', desc: 'Conexão com a API da Americanas' },
  { value: 'aliexpress' as MarketplaceType, label: 'AliExpress', desc: 'Integração com AliExpress' },
  { value: 'shein' as MarketplaceType, label: 'Shein', desc: 'Integração com Shein' },
  { value: 'outro' as MarketplaceType, label: 'Outro', desc: 'Outro marketplace via API genérica' },
]

type MarketplaceFormData = MarketplaceCreateInput

interface MarketplaceFormProps {
  onSubmit: (data: MarketplaceFormData) => Promise<void>
  onCancel: () => void
  initialData?: Marketplace | null
  isLoading: boolean
}

export default function MarketplaceForm({ onSubmit, onCancel, initialData, isLoading }: MarketplaceFormProps) {
  const [step, setStep] = useState(initialData ? 1 : 0)
  const [error, setError] = useState<string | null>(null)
  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({})

  const [formData, setFormData] = useState<MarketplaceFormData>({
    nome: initialData?.nome || '',
    tipo: initialData?.tipo || 'shopee',
    credenciais: {},
  })

  const fields = MARKETPLACE_FIELD_SCHEMAS[formData.tipo] || []
  const hasCredentials = Object.values(formData.credenciais || {}).some((value) => Boolean(value && value.trim()))

  const trimCredentialValues = (values: Record<string, string>) => {
    return Object.fromEntries(
      Object.entries(values)
        .map(([key, value]) => [key, value.trim()])
        .filter(([, value]) => Boolean(value))
    ) as Record<string, string>
  }

  const handleSubmit = async () => {
    setError(null)
    if (!formData.nome.trim()) {
      setError('Nome é obrigatório')
      return
    }

    const isCredentialEditing = hasCredentials
    if (isCredentialEditing) {
      const missing = fields.filter((field) => field.required && !formData.credenciais?.[field.key])
      if (missing.length > 0) {
        setError(`Campos obrigatórios: ${missing.map((field) => field.label).join(', ')}`)
        return
      }
    }

    const payload: MarketplaceFormData = {
      nome: formData.nome.trim(),
      tipo: formData.tipo,
    }

    if (hasCredentials && formData.credenciais) {
      payload.credenciais = trimCredentialValues(formData.credenciais)
    }

    if (!payload.nome) {
      setError('Nome é obrigatório')
      return
    }

    try {
      await onSubmit(payload)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao salvar.')
    }
  }

  return (
    <div className="space-y-6">
      {step === 0 && !initialData && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Nome da integração *</label>
            <input
              type="text"
              value={formData.nome}
              onChange={(event) => setFormData((previous) => ({ ...previous, nome: event.target.value }))}
              placeholder="Ex: Loja principal"
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Tipo de marketplace *</label>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {MARKETPLACE_OPTIONS.map((option) => {
                const Icon = MARKETPLACE_ICONS[option.value]
                const selected = formData.tipo === option.value

                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setFormData((previous) => ({ ...previous, tipo: option.value, credenciais: {} }))}
                    className={`flex items-start gap-3 rounded-xl border p-4 text-left transition-colors ${
                      selected
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    <span className={`flex h-10 w-10 items-center justify-center rounded-lg ${selected ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-500'}`}>
                      <Icon className="h-5 w-5" />
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block text-sm font-semibold text-gray-900">{option.label}</span>
                      <span className="mt-1 block text-xs text-gray-500">{option.desc}</span>
                    </span>
                  </button>
                )
              })}
            </div>
          </div>

          <div className="flex items-center justify-end pt-2">
            <button
              type="button"
              onClick={() => setStep(1)}
              disabled={!formData.nome.trim()}
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2 text-sm font-semibold text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Configurar credenciais
            </button>
          </div>
        </div>
      )}

      {step === 1 && (
        <div className="space-y-6">
          <div className="rounded-xl border border-blue-100 bg-blue-50 p-4">
            <div className="flex items-start gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white text-blue-600 shadow-sm">
                <MarketplaceFormIcon type={formData.tipo} />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold text-blue-900">{formData.nome || 'Nova integração'}</p>
                <p className="text-xs text-blue-700">{MARKETPLACE_OPTIONS.find((option) => option.value === formData.tipo)?.label}</p>
              </div>
              {!initialData && (
                <button
                  type="button"
                  onClick={() => setStep(0)}
                  className="text-xs font-medium text-blue-700 hover:text-blue-800"
                >
                  Alterar tipo
                </button>
              )}
            </div>
          </div>

          <div className="rounded-xl border border-gray-200 bg-gray-50 p-4 text-sm text-gray-600">
            Credenciais são criptografadas antes de serem armazenadas. Deixe os campos vazios para manter os valores atuais ao editar.
          </div>

          <div className="grid grid-cols-1 gap-4">
            {fields.map((field) => (
              <div key={field.key}>
                <label className="mb-1.5 block text-sm font-medium text-gray-700">
                  {field.label} {field.required ? <span className="text-red-500">*</span> : null}
                </label>
                <div className="relative">
                  <input
                    type={field.secret && !showSecrets[field.key] ? 'password' : 'text'}
                    value={formData.credenciais?.[field.key] || ''}
                    onChange={(event) =>
                      setFormData((previous) => ({
                        ...previous,
                        credenciais: {
                          ...previous.credenciais,
                          [field.key]: event.target.value,
                        },
                      }))
                    }
                    placeholder={field.placeholder}
                    className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 pr-10"
                  />
                  {field.secret && (
                    <button
                      type="button"
                      onClick={() => setShowSecrets((previous) => ({ ...previous, [field.key]: !previous[field.key] }))}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 transition hover:text-gray-600"
                      aria-label={showSecrets[field.key] ? 'Ocultar credencial' : 'Mostrar credencial'}
                    >
                      {showSecrets[field.key] ? <EyeSlashIcon className="h-4 w-4" /> : <EyeIcon className="h-4 w-4" />}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          {error && (
            <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <div className="flex flex-col-reverse gap-3 border-t border-gray-100 pt-4 sm:flex-row sm:items-center">
            <button
              type="button"
              onClick={onCancel}
              className="inline-flex items-center justify-center rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
            >
              Cancelar
            </button>
            <div className="flex-1" />
            {!initialData && (
              <button
                type="button"
                onClick={() => setStep(0)}
                className="inline-flex items-center justify-center rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
              >
                Voltar
              </button>
            )}
            <button
              type="button"
              onClick={handleSubmit}
              disabled={isLoading}
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-5 py-2 text-sm font-semibold text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isLoading ? <SpinnerIcon /> : null}
              {initialData ? 'Salvar alterações' : 'Criar integração'}
            </button>
          </div>
        </div>
      )}

      {step === 0 && initialData && (
        <div className="space-y-6">
          <div className="rounded-xl border border-gray-200 bg-gray-50 p-4 text-sm text-gray-600">
            Atualize o nome ou substitua as credenciais existentes. Se não preencher nenhum campo secreto, as credenciais atuais são mantidas.
          </div>

          <div className="space-y-4">
            <div>
              <label className="mb-1.5 block text-sm font-medium text-gray-700">Nome da integração *</label>
              <input
                type="text"
                value={formData.nome}
                onChange={(event) => setFormData((previous) => ({ ...previous, nome: event.target.value }))}
                className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium text-gray-700">Tipo de marketplace *</label>
              <select
                value={formData.tipo}
                onChange={(event) => setFormData((previous) => ({ ...previous, tipo: event.target.value as MarketplaceType, credenciais: {} }))}
                className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              >
                {MARKETPLACE_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function MarketplaceFormIcon({ type }: { type: MarketplaceType }) {
  const iconClass = 'h-5 w-5'

  switch (type) {
    case 'shopee':
      return <ShoppingBagIcon className={iconClass} />
    case 'mercado_livre':
      return <BuildingStorefrontIcon className={iconClass} />
    case 'amazon':
      return <CubeIcon className={iconClass} />
    default:
      return <LinkIcon className={iconClass} />
  }
}

function SpinnerIcon() {
  return (
    <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  )
}
