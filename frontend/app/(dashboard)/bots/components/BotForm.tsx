'use client'

import React, { useState, useEffect } from 'react'
import { Bot, BotCreateInput } from '../hooks/useBots'

interface BotFormProps {
  bot?: Bot | null
  onSubmit: (data: BotCreateInput) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
}

interface FormErrors {
  nome?: string
  api_id?: string
  api_hash?: string
  telefone?: string
}

export default function BotForm({
  bot,
  onSubmit,
  onCancel,
  isLoading = false,
}: BotFormProps) {
  const [formData, setFormData] = useState<BotCreateInput>({
    nome: '',
    api_id: '',
    api_hash: '',
    telefone: '',
  })

  const [errors, setErrors] = useState<FormErrors>({})
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [touched, setTouched] = useState<Record<string, boolean>>({})

  // Populate form with bot data when editing
  useEffect(() => {
    if (bot) {
      setFormData({
        nome: bot.nome || '',
        api_id: bot.api_id || '',
        api_hash: bot.api_hash || '',
        telefone: bot.telefone || '',
      })
    }
  }, [bot])

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {}

    // Validate nome
    if (!formData.nome.trim()) {
      newErrors.nome = 'Bot name is required'
    } else if (formData.nome.trim().length < 2) {
      newErrors.nome = 'Bot name must be at least 2 characters'
    } else if (formData.nome.trim().length > 50) {
      newErrors.nome = 'Bot name must not exceed 50 characters'
    }

    // Validate api_id
    if (!formData.api_id.trim()) {
      newErrors.api_id = 'API ID is required'
    }

    // Validate api_hash
    if (!formData.api_hash.trim()) {
      newErrors.api_hash = 'API Hash is required'
    }

    // Validate telefone
    if (!formData.telefone.trim()) {
      newErrors.telefone = 'Phone number is required'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
    // Clear error for this field when user starts typing
    if (errors[name as keyof FormErrors]) {
      setErrors((prev) => ({
        ...prev,
        [name]: undefined,
      }))
    }
  }

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>): void => {
    const { name } = e.target
    setTouched((prev) => ({
      ...prev,
      [name]: true,
    }))
  }

  const handleSubmit = async (
    e: React.FormEvent<HTMLFormElement>
  ): Promise<void> => {
    e.preventDefault()
    setSubmitError(null)

    if (!validateForm()) {
      return
    }

    try {
      await onSubmit(formData)
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to save bot'
      setSubmitError(message)
    }
  }

  const isFormValid = Object.keys(errors).length === 0
  const hasError = (field: keyof FormErrors) =>
    errors[field] && (touched[field] || submitError)

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Submit Error Alert */}
      {submitError && (
        <div className="rounded-lg border border-red-300 bg-red-50 p-4">
          <p className="text-sm font-medium text-red-800">Error saving bot</p>
          <p className="mt-1 text-sm text-red-700">{submitError}</p>
        </div>
      )}

      {/* Bot Name */}
      <div className="space-y-2">
        <label
          htmlFor="nome"
          className="block text-sm font-medium text-gray-900"
        >
          Bot Name <span className="text-red-600">*</span>
        </label>
        <input
          id="nome"
          name="nome"
          type="text"
          placeholder="MyAwesomeBot"
          value={formData.nome}
          onChange={handleChange}
          onBlur={handleBlur}
          disabled={isLoading}
          className={`w-full px-4 py-2 rounded-lg border text-sm font-medium text-gray-900 placeholder-gray-500 transition focus:outline-none focus:ring-2 focus:ring-offset-0 ${
            hasError('nome')
              ? 'border-red-300 bg-red-50 focus:ring-red-400'
              : 'border-gray-300 bg-white focus:ring-blue-400 focus:border-transparent'
          } ${isLoading ? 'bg-gray-100 cursor-not-allowed' : ''}`}
        />
        {hasError('nome') && (
          <p className="text-sm font-medium text-red-600">{errors.nome}</p>
        )}
        <p className="text-xs text-gray-600">
          Enter a unique name for your bot (2-50 characters)
        </p>
      </div>

      {/* API ID */}
      <div className="space-y-2">
        <label
          htmlFor="api_id"
          className="block text-sm font-medium text-gray-900"
        >
          API ID <span className="text-red-600">*</span>
        </label>
        <input
          id="api_id"
          name="api_id"
          type="text"
          placeholder="1234567890"
          value={formData.api_id}
          onChange={handleChange}
          onBlur={handleBlur}
          disabled={isLoading}
          className={`w-full px-4 py-2 rounded-lg border text-sm font-medium text-gray-900 placeholder-gray-500 transition focus:outline-none focus:ring-2 focus:ring-offset-0 ${
            hasError('api_id')
              ? 'border-red-300 bg-red-50 focus:ring-red-400'
              : 'border-gray-300 bg-white focus:ring-blue-400 focus:border-transparent'
          } ${isLoading ? 'bg-gray-100 cursor-not-allowed' : ''}`}
        />
        {hasError('api_id') && (
          <p className="text-sm font-medium text-red-600">{errors.api_id}</p>
        )}
        <p className="text-xs text-gray-600">
          Your Telegram API ID from{' '}
          <a
            href="https://my.telegram.org"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline"
          >
            https://my.telegram.org
          </a>
        </p>
      </div>

      {/* API Hash */}
      <div className="space-y-2">
        <label
          htmlFor="api_hash"
          className="block text-sm font-medium text-gray-900"
        >
          API Hash <span className="text-red-600">*</span>
        </label>
        <input
          id="api_hash"
          name="api_hash"
          type="text"
          placeholder="abcdef1234567890"
          value={formData.api_hash}
          onChange={handleChange}
          onBlur={handleBlur}
          disabled={isLoading}
          className={`w-full px-4 py-2 rounded-lg border text-sm font-medium text-gray-900 placeholder-gray-500 transition focus:outline-none focus:ring-2 focus:ring-offset-0 ${
            hasError('api_hash')
              ? 'border-red-300 bg-red-50 focus:ring-red-400'
              : 'border-gray-300 bg-white focus:ring-blue-400 focus:border-transparent'
          } ${isLoading ? 'bg-gray-100 cursor-not-allowed' : ''}`}
        />
        {hasError('api_hash') && (
          <p className="text-sm font-medium text-red-600">{errors.api_hash}</p>
        )}
        <p className="text-xs text-gray-600">
          Your Telegram API Hash from{' '}
          <a
            href="https://my.telegram.org"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline"
          >
            https://my.telegram.org
          </a>
        </p>
      </div>

      {/* Phone Number */}
      <div className="space-y-2">
        <label
          htmlFor="telefone"
          className="block text-sm font-medium text-gray-900"
        >
          Phone Number <span className="text-red-600">*</span>
        </label>
        <input
          id="telefone"
          name="telefone"
          type="tel"
          placeholder="+55 11 99999-9999"
          value={formData.telefone}
          onChange={handleChange}
          onBlur={handleBlur}
          disabled={isLoading}
          className={`w-full px-4 py-2 rounded-lg border text-sm font-medium text-gray-900 placeholder-gray-500 transition focus:outline-none focus:ring-2 focus:ring-offset-0 ${
            hasError('telefone')
              ? 'border-red-300 bg-red-50 focus:ring-red-400'
              : 'border-gray-300 bg-white focus:ring-blue-400 focus:border-transparent'
          } ${isLoading ? 'bg-gray-100 cursor-not-allowed' : ''}`}
        />
        {hasError('telefone') && (
          <p className="text-sm font-medium text-red-600">{errors.telefone}</p>
        )}
        <p className="text-xs text-gray-600">
          Phone number associated with this Telegram account
        </p>
      </div>

      {/* Form Actions */}
      <div className="flex gap-3 pt-2">
        <button
          type="submit"
          disabled={isLoading || !isFormValid}
          className="flex-1 px-4 py-2 rounded-lg font-semibold text-sm text-white bg-blue-600 hover:bg-blue-700 active:bg-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
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
              Saving...
            </span>
          ) : bot ? (
            'Update Bot'
          ) : (
            'Create Bot'
          )}
        </button>
        <button
          type="button"
          onClick={onCancel}
          disabled={isLoading}
          className="flex-1 px-4 py-2 rounded-lg font-semibold text-sm text-gray-700 bg-gray-200 hover:bg-gray-300 active:bg-gray-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Cancel
        </button>
      </div>
    </form>
  )
}
