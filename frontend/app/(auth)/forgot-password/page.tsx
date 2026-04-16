'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { Input, Button, Alert, Card } from '@/app/components/ui'
import { validateEmail } from '@/lib/validation'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [error, setError] = useState<string>('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)

  const validateForm = (): boolean => {
    const emailValidation = validateEmail(email)
    if (!emailValidation.valid) {
      setError(emailValidation.error ?? 'Invalid email address')
      return false
    }
    return true
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!validateForm()) {
      return
    }

    setLoading(true)

    try {
      // Call password reset API endpoint
      const response = await fetch('/api/v1/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to send reset email')
      }

      setSuccess(true)
    } catch (err: any) {
      const message = err.message || 'Failed to send reset email. Please try again.'
      setError(typeof message === 'string' ? message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-lg">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900">ConektaBots</h1>
        <p className="text-sm text-gray-600 mt-md">Reset your password</p>
      </div>

      {/* Form Card */}
      <Card variant="default" className="p-lg">
        {success ? (
          // Success State
          <div className="space-y-lg text-center">
            <div className="flex justify-center">
              <div className="w-12 h-12 bg-green-50 rounded-full flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
            </div>

            <div>
              <h2 className="text-lg font-semibold text-gray-900">Check your email</h2>
              <p className="text-sm text-gray-600 mt-md">
                We've sent a password reset link to <span className="font-medium">{email}</span>
              </p>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-md p-md">
              <p className="text-sm text-blue-800">
                Didn't receive the email? Check your spam folder or{' '}
                <button
                  onClick={() => {
                    setSuccess(false)
                    setEmail('')
                  }}
                  className="underline font-medium hover:text-blue-900 transition"
                >
                  try again
                </button>
              </p>
            </div>

            <Link
              href="/login"
              className="text-sm text-blue-600 hover:text-blue-700 transition font-medium"
            >
              Back to sign in
            </Link>
          </div>
        ) : (
          // Form State
          <form onSubmit={handleSubmit} className="space-y-lg">
            {error && (
              <Alert
                type="error"
                title="Error"
                description={error}
                dismissible
                onDismiss={() => setError('')}
              />
            )}

            <div>
              <p className="text-sm text-gray-600 mb-lg">
                Enter your email address and we'll send you a link to reset your password.
              </p>

              <Input
                label="Email Address"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value)
                  if (error) setError('')
                }}
                disabled={loading}
                required
              />
            </div>

            {/* Submit Button */}
            <Button
              variant="primary"
              size="md"
              fullWidth
              disabled={loading}
              loading={loading}
              type="submit"
            >
              Send reset link
            </Button>

            {/* Back to Login */}
            <div className="text-center pt-md border-t border-gray-200">
              <Link href="/login" className="text-sm text-gray-600 hover:text-gray-900 transition">
                Remember your password?{' '}
                <span className="text-blue-600 font-medium hover:text-blue-700">Sign in</span>
              </Link>
            </div>
          </form>
        )}
      </Card>

      {/* Footer */}
      <p className="text-xs text-gray-500 text-center">
        © 2026 ConektaBots. All rights reserved.
      </p>
    </div>
  )
}
