'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/hooks/useAuth'
import { useAuthRedirect } from '@/hooks/useRouteProtection'
import {
  InputField,
  FormButton,
  FormContainer,
  ErrorAlert,
  FormLink,
} from '@/app/components/AuthForm'
import {
  validateEmail,
  validatePassword,
  validateName,
  validatePasswordMatch,
} from '@/lib/validation'

export default function SignupPage() {
  const router = useRouter()
  const signup = useAuthStore((state) => state.signup)

  // Redirect if already authenticated
  useAuthRedirect()

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  })
  const [errors, setErrors] = useState<{
    name?: string
    email?: string
    password?: string
    confirmPassword?: string
  }>({})
  const [apiError, setApiError] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [agreeToTerms, setAgreeToTerms] = useState(false)

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

    const matchValidation = validatePasswordMatch(
      formData.password,
      formData.confirmPassword
    )
    if (!matchValidation.valid) {
      newErrors.confirmPassword = matchValidation.error
    }

    if (!agreeToTerms) {
      setApiError('You must agree to the Terms & Conditions')
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
      // Redirect to dashboard
      router.push('/dashboard')
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
    let strength = 0
    if (pwd.length >= 8) strength++
    if (/[A-Z]/.test(pwd)) strength++
    if (/[0-9]/.test(pwd)) strength++
    if (/[!@#$%^&*]/.test(pwd)) strength++

    return {
      level: strength,
      label: strength === 0 ? 'Weak' : strength < 2 ? 'Fair' : strength < 4 ? 'Good' : 'Strong',
      color:
        strength === 0
          ? 'bg-gray-300'
          : strength < 2
            ? 'bg-red-500'
            : strength < 4
              ? 'bg-yellow-500'
              : 'bg-green-500',
    }
  }, [formData.password])

  return (
    <FormContainer title="Create Account" subtitle="Join ConektaBots today">
      <form onSubmit={handleSubmit} className="space-y-4">
        {apiError && (
          <ErrorAlert
            message={apiError}
            onDismiss={() => setApiError('')}
          />
        )}

        <InputField
          label="Full Name"
          name="name"
          type="text"
          placeholder="John Doe"
          value={formData.name}
          onChange={(e) => {
            setFormData({ ...formData, name: e.target.value })
            if (errors.name) setErrors({ ...errors, name: undefined })
          }}
          error={errors.name}
          disabled={loading}
          autoComplete="name"
        />

        <InputField
          label="Email Address"
          name="email"
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
        />

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
            Password
          </label>
          <input
            id="password"
            name="password"
            type="password"
            placeholder="••••••••"
            value={formData.password}
            onChange={(e) => {
              setFormData({ ...formData, password: e.target.value })
              if (errors.password) setErrors({ ...errors, password: undefined })
            }}
            disabled={loading}
            autoComplete="new-password"
            className={`w-full px-4 py-2 border rounded-lg font-medium text-gray-900 placeholder-gray-400 transition focus:outline-none focus:ring-2 focus:ring-offset-0 ${
              errors.password
                ? 'border-red-500 focus:ring-red-500 bg-red-50'
                : 'border-gray-300 focus:ring-blue-500 focus:border-transparent'
            } ${loading ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}`}
            required
          />

          {formData.password && (
            <div className="mt-2">
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-gray-600">Password Strength</span>
                <span className={`font-semibold ${passwordStrength.color === 'bg-green-500' ? 'text-green-600' : passwordStrength.color === 'bg-yellow-500' ? 'text-yellow-600' : 'text-red-600'}`}>
                  {passwordStrength.label}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all ${passwordStrength.color}`}
                  style={{ width: `${(passwordStrength.level / 4) * 100}%` }}
                ></div>
              </div>
            </div>
          )}

          {errors.password && <p className="mt-1 text-sm text-red-600">{errors.password}</p>}
          <p className="mt-2 text-xs text-gray-500">
            Must contain: 8+ characters, uppercase letter, number, and special character (!@#$%^&*)
          </p>
        </div>

        <InputField
          label="Confirm Password"
          name="confirmPassword"
          type="password"
          placeholder="••••••••"
          value={formData.confirmPassword}
          onChange={(e) => {
            setFormData({ ...formData, confirmPassword: e.target.value })
            if (errors.confirmPassword) setErrors({ ...errors, confirmPassword: undefined })
          }}
          error={errors.confirmPassword}
          disabled={loading}
          autoComplete="new-password"
        />

        <div className="flex items-start">
          <input
            id="agreeToTerms"
            type="checkbox"
            checked={agreeToTerms}
            onChange={(e) => setAgreeToTerms(e.target.checked)}
            disabled={loading}
            className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer mt-0.5"
          />
          <label htmlFor="agreeToTerms" className="ml-2 text-sm text-gray-700 cursor-pointer">
            I agree to the{' '}
            <a href="#" className="font-semibold text-blue-600 hover:text-blue-700">
              Terms & Conditions
            </a>
          </label>
        </div>

        <FormButton type="submit" loading={loading} disabled={loading}>
          Create Account
        </FormButton>
      </form>

      <FormLink
        text="Already have an account?"
        linkText="Sign in"
        href="/login"
      />
    </FormContainer>
  )
}
