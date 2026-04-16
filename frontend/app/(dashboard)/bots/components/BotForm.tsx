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

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Submit Error Alert */}
      {submitError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {submitError}
        </div>
      )}

      {/* Bot Name */}
      <div>
        <label
          htmlFor="nome"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Bot Name <span className="text-red-500">*</span>
        </label>
        <input
          id="nome"
          name="nome"
          type="text"
          placeholder="Enter bot name (e.g., MyAwesomeBot)"
          value={formData.nome}
          onChange={handleChange}
          disabled={isLoading}
          className={`w-full px-3 py-2 border rounded-lg font-medium text-gray-900 placeholder-gray-400 transition focus:outline-none focus:ring-2 focus:ring-offset-0 ${
            errors.nome
              ? 'border-red-500 focus:ring-red-500 bg-red-50'
              : 'border-gray-300 focus:ring-blue-500 focus:border-transparent'
          } ${isLoading ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}`}
        />
        {errors.nome && (
          <p className="mt-1 text-sm text-red-600">{errors.nome}</p>
        )}
      </div>

      {/* API ID */}
      <div>
        <label
          htmlFor="api_id"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          API ID <span className="text-red-500">*</span>
        </label>
        <input
          id="api_id"
          name="api_id"
          type="text"
          placeholder="Enter your Telegram API ID"
          value={formData.api_id}
          onChange={handleChange}
          disabled={isLoading}
          className={`w-full px-3 py-2 border rounded-lg font-medium text-gray-900 placeholder-gray-400 transition focus:outline-none focus:ring-2 focus:ring-offset-0 ${
            errors.api_id
              ? 'border-red-500 focus:ring-red-500 bg-red-50'
              : 'border-gray-300 focus:ring-blue-500 focus:border-transparent'
          } ${isLoading ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}`}
        />
        {errors.api_id && (
          <p className="mt-1 text-sm text-red-600">{errors.api_id}</p>
        )}
      </div>

      {/* API Hash */}
      <div>
        <label
          htmlFor="api_hash"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          API Hash <span className="text-red-500">*</span>
        </label>
        <input
          id="api_hash"
          name="api_hash"
          type="text"
          placeholder="Enter your Telegram API Hash"
          value={formData.api_hash}
          onChange={handleChange}
          disabled={isLoading}
          className={`w-full px-3 py-2 border rounded-lg font-medium text-gray-900 placeholder-gray-400 transition focus:outline-none focus:ring-2 focus:ring-offset-0 ${
            errors.api_hash
              ? 'border-red-500 focus:ring-red-500 bg-red-50'
              : 'border-gray-300 focus:ring-blue-500 focus:border-transparent'
          } ${isLoading ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}`}
        />
        {errors.api_hash && (
          <p className="mt-1 text-sm text-red-600">{errors.api_hash}</p>
        )}
      </div>

      {/* Phone Number */}
      <div>
        <label
          htmlFor="telefone"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Phone Number <span className="text-red-500">*</span>
        </label>
        <input
          id="telefone"
          name="telefone"
          type="tel"
          placeholder="Enter phone number (e.g., +55 11 99999-9999)"
          value={formData.telefone}
          onChange={handleChange}
          disabled={isLoading}
          className={`w-full px-3 py-2 border rounded-lg font-medium text-gray-900 placeholder-gray-400 transition focus:outline-none focus:ring-2 focus:ring-offset-0 ${
            errors.telefone
              ? 'border-red-500 focus:ring-red-500 bg-red-50'
              : 'border-gray-300 focus:ring-blue-500 focus:border-transparent'
          } ${isLoading ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}`}
        />
        {errors.telefone && (
          <p className="mt-1 text-sm text-red-600">{errors.telefone}</p>
        )}
      </div>

      {/* Form Actions */}
      <div className="flex gap-3 pt-4">
        <button
          type="submit"
          disabled={isLoading || !isFormValid}
          className="flex-1 px-4 py-2 rounded-lg font-semibold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800"
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
          className="flex-1 px-4 py-2 rounded-lg font-semibold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed bg-gray-200 text-gray-800 hover:bg-gray-300 active:bg-gray-400"
        >
          Cancel
        </button>
      </div>
    </form>
  )
}
