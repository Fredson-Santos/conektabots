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

      // Redirect to dashboard
      router.push('/dashboard')
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
    <FormContainer
      title="Welcome Back"
      subtitle="Sign in to your account to continue"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {apiError && (
          <ErrorAlert
            message={apiError}
            onDismiss={() => setApiError('')}
          />
        )}

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

        <InputField
          label="Password"
          name="password"
          type="password"
          placeholder="••••••••"
          value={formData.password}
          onChange={(e) => {
            setFormData({ ...formData, password: e.target.value })
            if (errors.password) setErrors({ ...errors, password: undefined })
          }}
          error={errors.password}
          disabled={loading}
          autoComplete="current-password"
        />

        <div className="flex items-center">
          <input
            id="rememberMe"
            type="checkbox"
            checked={rememberMe}
            onChange={(e) => setRememberMe(e.target.checked)}
            disabled={loading}
            className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
          />
          <label htmlFor="rememberMe" className="ml-2 text-sm text-gray-700 cursor-pointer">
            Remember this email
          </label>
        </div>

        <FormButton type="submit" loading={loading} disabled={loading}>
          Sign In
        </FormButton>
      </form>

      <FormLink
        text="Don't have an account?"
        linkText="Create one"
        href="/signup"
      />
    </FormContainer>
  )
}
