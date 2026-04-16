'use client'

import React, { ComponentPropsWithoutRef } from 'react'

export interface InputProps extends Omit<ComponentPropsWithoutRef<'input'>, 'type' | 'size'> {
  /**
   * Input type
   * @default 'text'
   */
  type?: 'text' | 'email' | 'password' | 'number'

  /**
   * Label displayed above input
   */
  label?: string

  /**
   * Placeholder text
   */
  placeholder?: string

  /**
   * Error message displayed below input
   */
  error?: string

  /**
   * Helper text displayed below input (replaced by error if present)
   */
  helper?: string

  /**
   * Icon to display on left of input
   */
  icon?: React.ReactNode

  /**
   * Field is required
   * @default false
   */
  required?: boolean

  /**
   * Field is disabled
   * @default false
   */
  disabled?: boolean

  /**
   * Input size
   * @default 'md'
   */
  size?: 'sm' | 'md' | 'lg'

  /**
   * Current value
   */
  value: string

  /**
   * Change handler
   */
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void
}

const baseStyles =
  'w-full font-normal transition-colors duration-200 rounded-md border border-gray-300 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-0 focus:border-blue-500 focus:ring-blue-500 disabled:bg-gray-100 disabled:text-gray-500 disabled:cursor-not-allowed disabled:border-gray-200'

const sizeStyles = {
  sm: 'px-2.5 py-1.5 text-sm',
  md: 'px-3 py-2 text-base',
  lg: 'px-4 py-3 text-lg',
}


/**
 * Input component - Text input with comprehensive validation & UX states
 *
 * @example
 * ```tsx
 * <Input
 *   label="Email"
 *   type="email"
 *   placeholder="user@example.com"
 *   value={email}
 *   onChange={(e) => setEmail(e.target.value)}
 *   error={emailError}
 * />
 *
 * <Input
 *   label="Password"
 *   type="password"
 *   value={password}
 *   onChange={(e) => setPassword(e.target.value)}
 *   helper="Must be at least 8 characters"
 *   required
 * />
 * ```
 */
export const Input = React.forwardRef<
  HTMLInputElement | HTMLTextAreaElement,
  InputProps
>(
  (
    {
      type = 'text',
      label,
      placeholder,
      error,
      helper,
      icon,
      required = false,
      disabled = false,
      size = 'md',
      value,
      onChange,
      maxLength,
      className,
      id,
      ...props
    },
    ref
  ) => {
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`
    const hasError = !!error
    const showHelper = !hasError && helper
    const showSpinner = type === 'number'

    // Note: textarea variant removed — use a dedicated Textarea component if needed
    return (
      <div className="w-full">
        {label && (
          <label htmlFor={inputId} className="block text-sm font-medium text-gray-700 mb-1.5">
            {label}
            {required && <span className="text-red-600 ml-1">*</span>}
          </label>
        )}
        <div className="relative">
          {icon && (
            <div className="absolute left-0 top-0 h-full flex items-center justify-center px-2.5 text-gray-400 pointer-events-none">
              {icon}
            </div>
          )}
          <input
            ref={ref as React.Ref<HTMLInputElement>}
            type={type}
            id={inputId}
            disabled={disabled}
            aria-disabled={disabled}
            aria-invalid={hasError}
            aria-describedby={hasError || showHelper ? `${inputId}-hint` : undefined}
            placeholder={placeholder}
            value={value}
            onChange={onChange}
            maxLength={maxLength}
            className={`${baseStyles} ${sizeStyles[size]} ${icon ? 'pl-9' : ''} ${showSpinner && type === 'number' ? 'pr-8' : ''} ${hasError ? 'border-red-500 focus:ring-red-500 focus:border-red-500' : ''} ${className ?? ''}`}
            {...props}
          />
          {showSpinner && type === 'number' && (
            <div className="absolute right-0 top-0 h-full flex flex-col items-center justify-center px-1.5 pointer-events-none text-gray-400">
              <span className="text-xs leading-none">⌃</span>
              <span className="text-xs leading-none">⌄</span>
            </div>
          )}
        </div>
        {(hasError || showHelper) && (
          <div
            id={`${inputId}-hint`}
            className={`text-sm mt-1.5 ${hasError ? 'text-red-600' : 'text-gray-500'}`}
          >
            {hasError ? error : helper}
          </div>
        )}
        {maxLength && (
          <div className="text-xs text-gray-400 mt-1">
            {value.length} / {maxLength}
          </div>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'
