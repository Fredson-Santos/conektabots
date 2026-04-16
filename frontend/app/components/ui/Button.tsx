'use client'

import React, { ComponentPropsWithoutRef } from 'react'
import { SpinnerIcon } from './icons'

export interface ButtonProps extends ComponentPropsWithoutRef<'button'> {
  /**
   * Visual style variant
   * @default 'primary'
   */
  variant?: 'primary' | 'secondary' | 'tertiary' | 'ghost' | 'danger'

  /**
   * Button size
   * @default 'md'
   */
  size?: 'sm' | 'md' | 'lg'

  /**
   * Fill full available width
   * @default false
   */
  fullWidth?: boolean

  /**
   * Show loading spinner and disable interaction
   * @default false
   */
  loading?: boolean

  /**
   * Icon to display on the left of text
   */
  icon?: React.ReactNode

  /**
   * Icon to display on the right of text
   */
  iconRight?: React.ReactNode

  /**
   * Button content
   */
  children: React.ReactNode
}

const baseStyles =
  'inline-flex items-center justify-center font-medium transition-all duration-200 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-0 disabled:opacity-50 disabled:cursor-not-allowed'

const sizeStyles = {
  sm: 'h-8 px-3 text-sm gap-1.5',
  md: 'h-10 px-4 text-base gap-2',
  lg: 'h-12 px-6 text-lg gap-2.5',
}

const variantStyles = {
  primary:
    'bg-blue-500 text-white hover:bg-blue-600 active:bg-blue-700 focus:ring-blue-500 disabled:hover:bg-blue-500',
  secondary:
    'bg-gray-200 text-gray-900 hover:bg-gray-300 active:bg-gray-400 focus:ring-gray-400 disabled:hover:bg-gray-200',
  tertiary:
    'text-blue-600 hover:bg-blue-50 active:bg-blue-100 focus:ring-blue-300 disabled:text-gray-400 disabled:hover:bg-transparent',
  ghost:
    'text-gray-700 hover:bg-gray-100 active:bg-gray-200 focus:ring-gray-300 disabled:text-gray-400 disabled:hover:bg-transparent',
  danger:
    'bg-red-600 text-white hover:bg-red-700 active:bg-red-800 focus:ring-red-500 disabled:hover:bg-red-600',
}

/**
 * Button component - Primary action component with full state coverage
 *
 * @example
 * ```tsx
 * <Button variant="primary" size="md">Click me</Button>
 * <Button variant="danger" size="lg" icon={<TrashIcon />}>Delete</Button>
 * <Button variant="tertiary" loading>Saving...</Button>
 * ```
 */
export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      fullWidth = false,
      loading = false,
      disabled = false,
      icon,
      iconRight,
      children,
      className,
      ...props
    },
    ref
  ) => {
    const isDisabled = disabled || loading

    return (
      <button
        ref={ref}
        disabled={isDisabled}
        aria-disabled={isDisabled}
        className={`${baseStyles} ${sizeStyles[size]} ${variantStyles[variant]} ${fullWidth ? 'w-full' : ''} ${className ?? ''}`}
        {...props}
      >
        {loading ? (
          <>
            <SpinnerIcon className={size === 'sm' ? 'w-3 h-3' : size === 'md' ? 'w-4 h-4' : 'w-5 h-5'} />
            {children}
          </>
        ) : (
          <>
            {icon && <span className="flex items-center justify-center">{icon}</span>}
            {children}
            {iconRight && <span className="flex items-center justify-center">{iconRight}</span>}
          </>
        )}
      </button>
    )
  }
)

Button.displayName = 'Button'
