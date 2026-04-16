'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { auth } from '@/lib/auth'

/**
 * Hook to protect routes - redirects to login if not authenticated
 * Use in protected pages like /dashboard
 */
export function useProtectedRoute() {
  const router = useRouter()

  useEffect(() => {
    if (!auth.isAuthenticated()) {
      router.push('/login')
    }
  }, [router])
}

/**
 * Hook to redirect authenticated users away from auth pages
 * Use in /login and /signup pages
 */
export function useAuthRedirect() {
  const router = useRouter()

  useEffect(() => {
    if (auth.isAuthenticated()) {
      router.push('/dashboard')
    }
  }, [router])
}
