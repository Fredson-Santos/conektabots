'use client'

import { DashboardLayout, navigationItems } from '@/app/components/layout'
import { Card, Button } from '@/app/components/ui'
import {
  UserCircleIcon,
  BellIcon,
  CreditCardIcon,
} from '@heroicons/react/24/outline'

export default function SettingsPage() {
  return (
    <DashboardLayout
      sidebarItems={navigationItems}
      title="Settings"
      breadcrumbs={[
        { label: 'Dashboard', href: '/dashboard' },
        { label: 'Settings' },
      ]}
    >
      <div className="space-y-lg max-w-2xl">
        {/* Page Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage your account preferences and application settings.
          </p>
        </div>

        {/* Account Settings */}
        <Card>
          <Card.Header
            title="Account Settings"
            action={<UserCircleIcon className="w-6 h-6 text-gray-400" />}
          />
          <Card.Body className="space-y-md">
            <p className="text-sm text-gray-600">
              Update your profile information, email address, and password.
            </p>
          </Card.Body>
          <Card.Footer align="right">
            <Button variant="secondary" size="md">
              Edit Account
            </Button>
          </Card.Footer>
        </Card>

        {/* Notifications */}
        <Card>
          <Card.Header
            title="Notifications"
            action={<BellIcon className="w-6 h-6 text-gray-400" />}
          />
          <Card.Body className="space-y-md">
            <p className="text-sm text-gray-600">
              Configure email alerts and notification preferences for your bots and activity.
            </p>
          </Card.Body>
          <Card.Footer align="right">
            <Button variant="secondary" size="md">
              Edit Notifications
            </Button>
          </Card.Footer>
        </Card>

        {/* Billing */}
        <Card>
          <Card.Header
            title="Billing & Subscription"
            action={<CreditCardIcon className="w-6 h-6 text-gray-400" />}
          />
          <Card.Body className="space-y-md">
            <p className="text-sm text-gray-600">
              Manage payment methods, view invoices, and upgrade your subscription plan.
            </p>
          </Card.Body>
          <Card.Footer align="right">
            <Button variant="secondary" size="md">
              View Billing
            </Button>
          </Card.Footer>
        </Card>
      </div>
    </DashboardLayout>
  )
}
