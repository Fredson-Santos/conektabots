'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/hooks/useAuth'
import { useAuthRedirect } from '@/hooks/useRouteProtection'
import { Input, Button, Alert, Card } from '@/app/components/ui'
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline'
import { validateEmail, validatePassword, validateName } from '@/lib/validation'

export default function SignupPage() {
  const router = useRouter()
  const signup = useAuthStore((state) => state.signup)

  // Redirect if already authenticated
  useAuthRedirect()

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
  })
  const [errors, setErrors] = useState<{
    name?: string
    email?: string
    password?: string
  }>({})
  const [apiError, setApiError] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [agreeToTerms, setAgreeToTerms] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  const validateForm = (): boolean => {
    const newErrors: typeof errors = {}

    const nameValidation = validateName(formData.name)
    if (!nameValidation.valid) {
      newErrors.name = nameValidation.error
    }

    const emailValidation = validateEmail(formData.email)
    if (!emailValidation.valid) {
      newErrors.email = emailValidation.error
    }

    const passwordValidation = validatePassword(formData.password)
    if (!passwordValidation.valid) {
      newErrors.password = passwordValidation.error
    }

    if (!agreeToTerms) {
      setApiError('You must agree to the Terms & Conditions to continue.')
      return false
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
      await signup(formData.name, formData.email, formData.password)
      router.push('/bots')
    } catch (error: any) {
      setLoading(false)
      const errorMessage =
        error.response?.data?.detail ||
        error.message ||
        'Signup failed. Please try again.'
      setApiError(typeof errorMessage === 'string' ? errorMessage : 'Signup failed')
    }
  }

  const passwordStrength = React.useMemo(() => {
    const pwd = formData.password
    if (!pwd) return null
    let strength = 0
    if (pwd.length >= 8) strength++
    if (/[A-Z]/.test(pwd)) strength++
    if (/[0-9]/.test(pwd)) strength++
    if (/[!@#$%^&*]/.test(pwd)) strength++

    const levels = [
      { label: 'Weak', color: 'bg-red-500', text: 'text-red-600' },
      { label: 'Fair', color: 'bg-amber-500', text: 'text-amber-600' },
      { label: 'Good', color: 'bg-yellow-500', text: 'text-yellow-600' },
      { label: 'Strong', color: 'bg-green-500', text: 'text-green-600' },
    ]
    const level = Math.max(0, strength - 1)
    return { level: strength, ...levels[level] }
  }, [formData.password])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900">ConektaBots</h1>
        <p className="text-sm text-gray-600 mt-2">Create your account</p>
      </div>

      {/* Form Card */}
      <Card variant="default" className="p-8">
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Error Alert */}
          {apiError && (
            <Alert
              type="error"
              title="Signup failed"
              description={apiError}
              dismissible
              onDismiss={() => setApiError('')}
            />
          )}

          {/* Full Name */}
          <Input
            label="Full Name"
            type="text"
            placeholder="João Silva"
            value={formData.name}
            onChange={(e) => {
              setFormData({ ...formData, name: e.target.value })
              if (errors.name) setErrors({ ...errors, name: undefined })
            }}
            error={errors.name}
            disabled={loading}
            autoComplete="name"
            required
          />

          {/* Email */}
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
            autoComplete="email"
            required
          />

          {/* Password with show/hide + strength indicator */}
          <div>
            <div className="relative">
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
                autoComplete="new-password"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                disabled={loading}
                className="absolute right-3 top-8 text-gray-400 hover:text-gray-600 transition disabled:opacity-50"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? (
                  <EyeSlashIcon className="w-5 h-5" />
                ) : (
                  <EyeIcon className="w-5 h-5" />
                )}
              </button>
            </div>

            {/* Password Strength */}
            {passwordStrength && (
              <div className="mt-2 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">Password strength</span>
                  <span className={`text-xs font-semibold ${passwordStrength.text}`}>
                    {passwordStrength.label}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-1.5">
                  <div
                    className={`h-1.5 rounded-full transition-all duration-300 ${passwordStrength.color}`}
                    style={{ width: `${(passwordStrength.level / 4) * 100}%` }}
                  />
                </div>
                <p className="text-xs text-gray-400">
                  Min. 8 chars, uppercase, number & special character (!@#$%^&*)
                </p>
              </div>
            )}
          </div>

          {/* Terms Agreement */}
          <label className="flex items-start gap-3 cursor-pointer">
            <input
              id="agreeToTerms"
              type="checkbox"
              checked={agreeToTerms}
              onChange={(e) => {
                setAgreeToTerms(e.target.checked)
                if (e.target.checked && apiError.includes('Terms')) setApiError('')
              }}
              disabled={loading}
              className="mt-0.5 h-4 w-4 rounded border-gray-300 accent-blue-600 cursor-pointer"
            />
            <span className="text-sm text-gray-700 leading-snug">
              I agree to the{' '}
              <a
                href="#"
                className="text-blue-600 hover:text-blue-700 font-medium underline-offset-2 hover:underline"
                onClick={(e) => e.preventDefault()}
              >
                Terms of Service
              </a>{' '}
              and{' '}
              <a
                href="#"
                className="text-blue-600 hover:text-blue-700 font-medium underline-offset-2 hover:underline"
                onClick={(e) => e.preventDefault()}
              >
                Privacy Policy
              </a>
            </span>
          </label>

          {/* Submit Button */}
          <Button
            variant="primary"
            size="md"
            fullWidth
            disabled={loading}
            loading={loading}
            type="submit"
          >
            Create account
          </Button>
        </form>

        {/* Sign In Link */}
        <div className="mt-6 pt-6 border-t border-gray-200 text-center">
          <p className="text-sm text-gray-600">
            Already have an account?{' '}
            <Link href="/login" className="text-blue-600 font-medium hover:text-blue-700 transition">
              Sign in
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
