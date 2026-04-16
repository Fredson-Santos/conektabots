'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/hooks/useAuth'
import { useAuthRedirect } from '@/hooks/useRouteProtection'
import { Input, Button, Alert, Card } from '@/app/components/ui'
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline'
import { validateEmail, validatePassword } from '@/lib/validation'

export default function LoginPage() {
  const router = useRouter()
  const login = useAuthStore((state) => state.login)

  // Redirect if already authenticated
  useAuthRedirect()

  const [formData, setFormData] = useState({ email: '', password: '' })
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({})
  const [apiError, setApiError] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [rememberMe, setRememberMe] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  const validateForm = (): boolean => {
    const newErrors: typeof errors = {}

    const emailValidation = validateEmail(formData.email)
    if (!emailValidation.valid) {
      newErrors.email = emailValidation.error
    }

    const passwordValidation = validatePassword(formData.password)
    if (!passwordValidation.valid) {
      newErrors.password = passwordValidation.error
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setApiError('')

    if (!validateForm()) {
      return
    }

    setLoading(true)

    try {
      await login(formData.email, formData.password)

      if (rememberMe) {
        localStorage.setItem('remembered_email', formData.email)
      } else {
        localStorage.removeItem('remembered_email')
      }

      router.push('/bots')
    } catch (error: any) {
      setLoading(false)
      const errorMessage =
        error.response?.data?.detail ||
        error.message ||
        'Login failed. Please try again.'
      setApiError(typeof errorMessage === 'string' ? errorMessage : 'Invalid credentials')
    }
  }

  return (
    <div className="space-y-lg">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900">ConektaBots</h1>
        <p className="text-sm text-gray-600 mt-md">Sign in to your account</p>
      </div>

      {/* Form Card */}
      <Card variant="default" className="p-lg">
        <form onSubmit={handleSubmit} className="space-y-lg">
          {/* Error Alert */}
          {apiError && (
            <Alert
              type="error"
              title="Sign in failed"
              description={apiError}
              dismissible
              onDismiss={() => setApiError('')}
            />
          )}

          {/* Email Input */}
          <Input
            label="Email Address"
            type="email"
            placeholder="you@example.com"
            value={formData.email}
            onChange={(e) => {
              setFormData({ ...formData, email: e.target.value })
              if (errors.email) setErrors({ ...errors, email: undefined })
            }}
            error={errors.email}
            disabled={loading}
            required
          />

          {/* Password Input with Show/Hide Toggle */}
          <div>
            <Input
              label="Password"
              type={showPassword ? 'text' : 'password'}
              placeholder="••••••••"
              value={formData.password}
              onChange={(e) => {
                setFormData({ ...formData, password: e.target.value })
                if (errors.password) setErrors({ ...errors, password: undefined })
              }}
              error={errors.password}
              disabled={loading}
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              disabled={loading}
              className="absolute right-md top-2xl text-gray-500 hover:text-gray-700 transition disabled:opacity-50"
              aria-label={showPassword ? 'Hide password' : 'Show password'}
            >
              {showPassword ? (
                <EyeSlashIcon className="w-5 h-5" />
              ) : (
                <EyeIcon className="w-5 h-5" />
              )}
            </button>
          </div>

          {/* Remember Me & Forgot Password */}
          <div className="flex items-center justify-between">
            <label className="flex items-center gap-sm">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                disabled={loading}
                className="w-4 h-4 rounded border-gray-300 accent-blue-600 cursor-pointer"
                aria-label="Remember this email"
              />
              <span className="text-sm text-gray-700">Remember me</span>
            </label>
            <Link
              href="/forgot-password"
              className="text-sm text-blue-600 hover:text-blue-700 transition"
            >
              Forgot password?
            </Link>
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
            Sign in
          </Button>
        </form>

        {/* Sign Up Link */}
        <div className="mt-lg pt-lg border-t border-gray-200 text-center">
          <p className="text-sm text-gray-600">
            Don't have an account?{' '}
            <Link href="/signup" className="text-blue-600 font-medium hover:text-blue-700 transition">
              Sign up
            </Link>
          </p>
        </div>
      </Card>

      {/* Footer */}
      <p className="text-xs text-gray-500 text-center">
        © 2026 ConektaBots. All rights reserved.
      </p>
    </div>
  )
}
