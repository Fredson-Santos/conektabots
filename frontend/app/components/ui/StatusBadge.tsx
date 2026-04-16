'use client'

import React from 'react'
import {
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'
import { SpinnerIcon } from './icons.tsx'

export interface StatusBadgeProps {
  /**
   * Status type
   */
  status: 'active' | 'inactive' | 'processing' | 'error' | 'warning' | 'success'

  /**
   * Label text (defaults to status name if not provided)
   */
  label?: string

  /**
   * Badge size
   * @default 'md'
   */
  size?: 'xs' | 'sm' | 'md'

  /**
   * Display variant
   * @default 'pill'
   */
  variant?: 'dot' | 'pill'
}

const statusConfig = {
  active: {
    icon: CheckCircleIcon,
    colors: 'text-green-600 bg-green-50',
    dotColors: 'bg-green-600',
    label: 'Active',
  },
  inactive: {
    icon: XCircleIcon,
    colors: 'text-gray-500 bg-gray-50',
    dotColors: 'bg-gray-500',
    label: 'Inactive',
  },
  processing: {
    icon: SpinnerIcon,
    colors: 'text-blue-600 bg-blue-50',
    dotColors: 'bg-blue-600',
    label: 'Processing',
    spinning: true,
  },
  error: {
    icon: XCircleIcon,
    colors: 'text-red-600 bg-red-50',
    dotColors: 'bg-red-600',
    label: 'Error',
  },
  warning: {
    icon: ExclamationTriangleIcon,
    colors: 'text-amber-600 bg-amber-50',
    dotColors: 'bg-amber-600',
    label: 'Warning',
  },
  success: {
    icon: CheckCircleIcon,
    colors: 'text-green-600 bg-green-50',
    dotColors: 'bg-green-600',
    label: 'Success',
  },
}

const sizeConfig = {
  xs: {
    icon: 'w-3 h-3',
    dot: 'w-1.5 h-1.5',
    padding: 'px-1.5 py-0.5',
    text: 'text-xs',
  },
  sm: {
    icon: 'w-4 h-4',
    dot: 'w-2 h-2',
    padding: 'px-2 py-1',
    text: 'text-xs',
  },
  md: {
    icon: 'w-5 h-5',
    dot: 'w-2 h-2',
    padding: 'px-3 py-1.5',
    text: 'text-sm',
  },
}

/**
 * StatusBadge component - Visual status indicator
 *
 * @example
 * ```tsx
 * <StatusBadge status="active" label="Active" />
 * <StatusBadge status="processing" size="sm" />
 * <StatusBadge status="error" variant="dot" />
 * ```
 */
export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  label,
  size = 'md',
  variant = 'pill',
}) => {
  const config = statusConfig[status]
  const sizeStyle = sizeConfig[size]
  const displayLabel = label || config.label
  const IconComponent = config.icon as React.ComponentType<{ className: string }>
  const isSpinning = (config as { spinning?: boolean }).spinning

  if (variant === 'dot') {
    return (
      <div className="flex items-center gap-1.5">
        <div className={`rounded-full flex-shrink-0 ${sizeStyle.dot} ${config.dotColors}`} />
        <span className={`${sizeStyle.text} font-medium text-gray-700`}>{displayLabel}</span>
      </div>
    )
  }

  return (
    <div className={`inline-flex items-center gap-1.5 rounded-full ${sizeStyle.padding} ${config.colors}`}>
      {isSpinning ? (
        <SpinnerIcon className={sizeStyle.icon} />
      ) : (
        <IconComponent className={sizeStyle.icon} />
      )}
      <span className={`${sizeStyle.text} font-medium`}>{displayLabel}</span>
    </div>
  )
}

StatusBadge.displayName = 'StatusBadge'
