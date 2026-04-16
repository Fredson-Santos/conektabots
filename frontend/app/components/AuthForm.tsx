'use client'

import React from 'react'

interface InputFieldProps {
  label: string
  name: string
  type?: 'text' | 'email' | 'password'
  placeholder?: string
  value: string
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void
  error?: string
  disabled?: boolean
  autoComplete?: string
}

export function InputField({
  label,
  name,
  type = 'text',
  placeholder,
  value,
  onChange,
  error,
  disabled = false,
  autoComplete,
}: InputFieldProps) {
  return (
    <div className="mb-4">
      <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>
      <input
        id={name}
        name={name}
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        disabled={disabled}
        autoComplete={autoComplete}
        className={`w-full px-4 py-2 border rounded-lg font-medium text-gray-900 placeholder-gray-400 transition focus:outline-none focus:ring-2 focus:ring-offset-0 ${
          error
            ? 'border-red-500 focus:ring-red-500 bg-red-50'
            : 'border-gray-300 focus:ring-blue-500 focus:border-transparent'
        } ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}`}
        required
      />
      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
    </div>
  )
}

interface FormButtonProps {
  type?: 'button' | 'submit' | 'reset'
  onClick?: () => void
  disabled?: boolean
  loading?: boolean
  children: React.ReactNode
  variant?: 'primary' | 'secondary'
}

export function FormButton({
  type = 'button',
  onClick,
  disabled = false,
  loading = false,
  children,
  variant = 'primary',
}: FormButtonProps) {
  const baseStyles =
    'w-full px-4 py-2 rounded-lg font-semibold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed'
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300 active:bg-gray-400',
  }

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`${baseStyles} ${variants[variant]}`}
    >
      {loading ? (
        <span className="flex items-center justify-center">
          <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {children}
        </span>
      ) : (
        children
      )}
    </button>
  )
}

interface FormContainerProps {
  title: string
  subtitle?: string
  children: React.ReactNode
}

export function FormContainer({ title, subtitle, children }: FormContainerProps) {
  return (
    <div className="bg-white rounded-xl shadow-lg p-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">{title}</h1>
      {subtitle && <p className="text-gray-600 mb-6">{subtitle}</p>}
      {children}
    </div>
  )
}

interface ErrorAlertProps {
  message: string
  onDismiss?: () => void
}

export function ErrorAlert({ message, onDismiss }: ErrorAlertProps) {
  return (
    <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start justify-between">
      <div className="flex items-start gap-3">
        <svg className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
        </svg>
        <p className="text-red-800 text-sm">{message}</p>
      </div>
      {onDismiss && (
        <button onClick={onDismiss} className="text-red-600 hover:text-red-800 flex-shrink-0">
          <svg className="w-5 h-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M18 6L6 18M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  )
}

interface FormLinkProps {
  text: string
  linkText: string
  href: string
}

export function FormLink({ text, linkText, href }: FormLinkProps) {
  return (
    <p className="mt-6 text-center text-gray-600 text-sm">
      {text}{' '}
      <a href={href} className="font-semibold text-blue-600 hover:text-blue-700 transition">
        {linkText}
      </a>
    </p>
  )
}
