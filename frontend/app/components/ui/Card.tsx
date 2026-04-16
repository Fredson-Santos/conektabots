'use client'

import React, { ComponentPropsWithoutRef } from 'react'

export interface CardProps extends ComponentPropsWithoutRef<'div'> {
  /**
   * Card variant
   * @default 'default'
   */
  variant?: 'default' | 'elevated'

  /**
   * Show hover effects
   * @default false
   */
  interactive?: boolean

  /**
   * Card content
   */
  children: React.ReactNode
}

export interface CardHeaderProps {
  /**
   * Header title
   */
  title?: string

  /**
   * Subtitle text
   */
  subtitle?: string

  /**
   * Right-aligned action (button, icon, etc.)
   */
  action?: React.ReactNode

  /**
   * Custom header content
   */
  children?: React.ReactNode
}

export interface CardBodyProps extends ComponentPropsWithoutRef<'div'> {
  /**
   * Body content
   */
  children: React.ReactNode
}

export interface CardFooterProps {
  /**
   * Content alignment
   * @default 'right'
   */
  align?: 'left' | 'center' | 'right'

  /**
   * Footer content
   */
  children: React.ReactNode
}

/**
 * Card component - Flexible container for data display
 *
 * @example
 * ```tsx
 * <Card variant="default" interactive>
 *   <Card.Header
 *     title="Bot Configuration"
 *     subtitle="Manage bot settings"
 *     action={<MoreButton />}
 *   />
 *   <Card.Body>
 *     {/* Main content *\/}
 *   </Card.Body>
 *   <Card.Footer>
 *     <Button>Save</Button>
 *   </Card.Footer>
 * </Card>
 * ```
 */
export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  (
    { variant = 'default', interactive = false, children, className, ...props },
    ref
  ) => {
    const baseStyles = 'w-full rounded-lg bg-white overflow-hidden'
    const variantStyles =
      variant === 'elevated'
        ? 'border border-gray-200 hover:shadow-md transition-shadow duration-200'
        : 'border border-gray-200'
    const interactiveStyles = interactive ? 'cursor-pointer' : ''

    return (
      <div
        ref={ref}
        className={`${baseStyles} ${variantStyles} ${interactiveStyles} ${className ?? ''}`}
        {...props}
      >
        {children}
      </div>
    )
  }
)

Card.displayName = 'Card'

const CardHeader = ({ title, subtitle, action, children }: CardHeaderProps) => {
  return (
    <>
      <div className="px-4 py-3 border-b border-gray-200 flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          {children ? (
            children
          ) : (
            <>
              {title && (
                <h3 className="text-base font-semibold text-gray-900 truncate">{title}</h3>
              )}
              {subtitle && (
                <p className="text-sm text-gray-500 truncate mt-0.5">{subtitle}</p>
              )}
            </>
          )}
        </div>
        {action && <div className="flex-shrink-0">{action}</div>}
      </div>
    </>
  )
}

CardHeader.displayName = 'Card.Header'

const CardBody = React.forwardRef<HTMLDivElement, CardBodyProps>(
  ({ children, className, ...props }, ref) => (
    <div ref={ref} className={`px-4 py-4 ${className ?? ''}`} {...props}>
      {children}
    </div>
  )
)

CardBody.displayName = 'Card.Body'

const CardFooter = ({ align = 'right', children }: CardFooterProps) => {
  const alignStyles = {
    left: 'justify-start',
    center: 'justify-center',
    right: 'justify-end',
  }

  return (
    <div
      className={`px-4 py-3 border-t border-gray-100 bg-gray-50 flex items-center gap-3 flex-wrap ${alignStyles[align]}`}
    >
      {children}
    </div>
  )
}

CardFooter.displayName = 'Card.Footer'

// Compound component type
type CardComponent = React.ForwardRefExoticComponent<CardProps & React.RefAttributes<HTMLDivElement>> & {
  Header: typeof CardHeader
  Body: typeof CardBody
  Footer: typeof CardFooter
}

;(Card as CardComponent).Header = CardHeader
;(Card as CardComponent).Body = CardBody
;(Card as CardComponent).Footer = CardFooter

export { Card as default }
export const CardWithSubs = Card as CardComponent
