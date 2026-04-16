'use client'

import React, { useState } from 'react'
import {
  InformationCircleIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline'

export interface AlertProps {
  /**
   * Alert type
   */
  type: 'info' | 'success' | 'warning' | 'error'

  /**
   * Alert title
   */
  title: string

  /**
   * Optional description text
   */
  description?: string

  /**
   * Show dismiss button
   * @default true
   */
  dismissible?: boolean

  /**
   * Called when alert is dismissed
   */
  onDismiss?: () => void

  /**
   * Optional action button
   */
  action?: {
    label: string
    onClick: () => void
  }
}

const typeConfig = {
  info: {
    icon: InformationCircleIcon,
    bgColor: 'bg-blue-50',
    textColor: 'text-blue-900',
    iconColor: 'text-blue-600',
    dismissColor: 'hover:text-blue-600',
  },
  success: {
    icon: CheckCircleIcon,
    bgColor: 'bg-green-50',
    textColor: 'text-green-900',
    iconColor: 'text-green-600',
    dismissColor: 'hover:text-green-600',
  },
  warning: {
    icon: ExclamationTriangleIcon,
    bgColor: 'bg-amber-50',
    textColor: 'text-amber-900',
    iconColor: 'text-amber-600',
    dismissColor: 'hover:text-amber-600',
  },
  error: {
    icon: XCircleIcon,
    bgColor: 'bg-red-50',
    textColor: 'text-red-900',
    iconColor: 'text-red-600',
    dismissColor: 'hover:text-red-600',
  },
}

/**
 * Alert component - Notification/alert messages
 *
 * @example
 * ```tsx
 * <Alert
 *   type="success"
 *   title="Bot created successfully"
 *   description="Your bot is now running and ready to use."
 *   dismissible
 * />
 *
 * <Alert
 *   type="error"
 *   title="Connection failed"
 *   action={{ label: 'Retry', onClick: () => handleRetry() }}
 * />
 * ```
 */
export const Alert: React.FC<AlertProps> = ({
  type,
  title,
  description,
  dismissible = true,
  onDismiss,
  action,
}) => {
  const [isVisible, setIsVisible] = useState(true)
  const config = typeConfig[type]
  const IconComponent = config.icon

  const handleDismiss = () => {
    setIsVisible(false)
    onDismiss?.()
  }

  if (!isVisible) {
    return null
  }

  return (
    <div
      className={`w-full ${config.bgColor} ${config.textColor} rounded-lg p-4 flex items-start gap-3`}
      role="alert"
    >
      <IconComponent className={`${config.iconColor} w-5 h-5 flex-shrink-0 mt-0.5`} />

      <div className="flex-1 min-w-0">
        <h3 className="font-semibold text-sm">{title}</h3>
        {description && <p className="text-sm mt-1 opacity-90">{description}</p>}

        {action && (
          <button
            onClick={action.onClick}
            className={`text-sm font-medium mt-2 opacity-90 hover:opacity-100 transition-opacity ${config.textColor}`}
          >
            {action.label}
          </button>
        )}
      </div>

      {dismissible && (
        <button
          onClick={handleDismiss}
          className={`flex-shrink-0 ${config.iconColor} ${config.dismissColor} transition-colors duration-200 opacity-70 hover:opacity-100 p-1`}
          aria-label="Dismiss alert"
          type="button"
        >
          <XMarkIcon className="w-5 h-5" />
        </button>
      )}
    </div>
  )
}

Alert.displayName = 'Alert'
