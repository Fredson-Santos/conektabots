'use client'

import React from 'react'

export interface EmptyStateProps {
  /**
   * Large icon to display (e.g., Heroicon 48x48)
   */
  icon: React.ReactNode

  /**
   * Main title text
   */
  title: string

  /**
   * Optional description
   */
  description?: string

  /**
   * Primary action button
   */
  action?: {
    label: string
    onClick: () => void
    icon?: React.ReactNode
  }

  /**
   * Secondary action (text link)
   */
  secondaryAction?: {
    label: string
    onClick: () => void
  }
}

/**
 * EmptyState component - Centered no-data visualization
 *
 * @example
 * ```tsx
 * <EmptyState
 *   icon={<PlusIcon className="w-12 h-12" />}
 *   title="No bots yet"
 *   description="Create your first bot to get started"
 *   action={{
 *     label: 'Create Bot',
 *     onClick: () => handleCreate(),
 *     icon: <PlusIcon className="w-4 h-4" />,
 *   }}
 *   secondaryAction={{
 *     label: 'Learn More',
 *     onClick: () => handleLearnMore(),
 *   }}
 * />
 * ```
 */
export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action,
  secondaryAction,
}) => {
  return (
    <div className="flex items-center justify-center min-h-96 px-4">
      <div className="text-center">
        <div className="flex justify-center mb-4">
          <div className="text-gray-400 w-12 h-12">{icon}</div>
        </div>

        <h2 className="text-xl font-semibold text-gray-900 mb-2">{title}</h2>

        {description && (
          <p className="text-sm text-gray-500 mb-6 max-w-sm mx-auto">{description}</p>
        )}

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          {action && (
            <button
              onClick={action.onClick}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-0"
            >
              {action.icon && <span className="flex items-center justify-center">{action.icon}</span>}
              {action.label}
            </button>
          )}

          {secondaryAction && (
            <button
              onClick={secondaryAction.onClick}
              className="text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-0 rounded px-3 py-2"
            >
              {secondaryAction.label}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

EmptyState.displayName = 'EmptyState'
