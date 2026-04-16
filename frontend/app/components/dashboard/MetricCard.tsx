'use client'

import React from 'react'
import { Card } from '@/app/components/ui'
import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/outline'

export interface MetricCardProps {
  /**
   * Metric label (e.g., "Active Bots")
   */
  label: string

  /**
   * Primary value to display
   */
  value: string | number

  /**
   * Optional subtitle/unit
   */
  unit?: string

  /**
   * Trend indicator: positive (+2), negative (-1), or undefined (neutral)
   */
  trend?: {
    value: number
    label: string
    isPositive: boolean
  }

  /**
   * Icon to display
   */
  icon?: React.ReactNode

  /**
   * Background color accent
   */
  accentColor?: 'blue' | 'green' | 'amber' | 'purple'
}

const accentColors = {
  blue: 'bg-blue-50 text-blue-600',
  green: 'bg-green-50 text-green-600',
  amber: 'bg-amber-50 text-amber-600',
  purple: 'bg-purple-50 text-purple-600',
}

const accentBorders = {
  blue: 'border-l-blue-500',
  green: 'border-l-green-500',
  amber: 'border-l-amber-500',
  purple: 'border-l-purple-500',
}

/**
 * MetricCard component - Displays KPI metrics with trend indicators
 *
 * @example
 * ```tsx
 * <MetricCard
 *   label="Active Bots"
 *   value={12}
 *   trend={{ value: 2, label: 'this week', isPositive: true }}
 *   accentColor="green"
 *   icon={<SparklesIcon className="w-6 h-6" />}
 * />
 * ```
 */
export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  unit,
  trend,
  icon,
  accentColor = 'blue',
}) => {
  return (
    <Card
      className={`border-l-4 ${accentBorders[accentColor]} overflow-hidden`}
      variant="default"
    >
      <div className="p-lg space-y-md">
        {/* Header: Icon + Label */}
        <div className="flex items-start justify-between">
          <p className="text-xs font-semibold uppercase text-gray-500 tracking-wide">
            {label}
          </p>
          {icon && <div className={`${accentColors[accentColor]} p-2 rounded-md`}>{icon}</div>}
        </div>

        {/* Main Value */}
        <div>
          <p className="text-4xl font-bold text-gray-900">{value}</p>
          {unit && <p className="text-xs text-gray-500 mt-1">{unit}</p>}
        </div>

        {/* Trend Indicator */}
        {trend && (
          <div className="flex items-center gap-1">
            <div
              className={`flex items-center gap-0.5 text-xs font-medium ${
                trend.isPositive ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {trend.isPositive ? (
                <ArrowUpIcon className="w-3 h-3" />
              ) : (
                <ArrowDownIcon className="w-3 h-3" />
              )}
              <span>
                {trend.isPositive ? '+' : '-'}
                {Math.abs(trend.value)}
              </span>
            </div>
            <span className="text-xs text-gray-500">{trend.label}</span>
          </div>
        )}
      </div>
    </Card>
  )
}

MetricCard.displayName = 'MetricCard'
