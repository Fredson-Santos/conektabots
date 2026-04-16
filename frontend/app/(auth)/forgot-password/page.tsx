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
    <div className="flex flex-col gap-4">
      {/* Header */}
      <div className="text-center mb-2">
        <Link
          href="/login"
          className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 font-medium transition mb-3"
        >
          ← Back to sign in
        </Link>
        <h1 className="text-2xl font-semibold text-gray-900">Reset password</h1>
      </div>

      {/* Form Card */}
      <Card variant="default" className="px-8 py-12">
        {success ? (
          // Success State
          <div className="space-y-6 text-center">
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
              <h2 className="text-lg font-semibold text-gray-900">Check your inbox</h2>
              <p className="text-sm text-gray-600 mt-2">
                We've sent a password reset link to{' '}
                <span className="font-medium text-gray-900">{email}</span>
              </p>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
              <p className="text-sm text-blue-900">
                Didn't receive the email? Check your spam folder or{' '}
                <button
                  onClick={() => {
                    setSuccess(false)
                    setEmail('')
                  }}
                  className="underline font-medium hover:text-blue-800 transition"
                >
                  try again
                </button>
              </p>
            </div>

            <Link
              href="/login"
              className="inline-block text-sm text-blue-600 hover:text-blue-700 font-medium transition"
            >
              Back to sign in
            </Link>
          </div>
        ) : (
          // Form State
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <Alert
                type="error"
                title="Error"
                description={error}
                dismissible
                onDismiss={() => setError('')}
              />
            )}

            <p className="text-sm text-gray-600">
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
            <div className="text-center pt-4 border-t border-gray-200">
              <Link href="/login" className="text-sm text-gray-600 hover:text-gray-900 transition">
                Remember your password?{' '}
                <span className="text-blue-600 font-medium hover:text-blue-700">Sign in</span>
              </Link>
            </div>
          </form>
        )}
      </Card>
    </div>
  )
}
