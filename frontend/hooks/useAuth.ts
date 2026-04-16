import { create } from 'zustand'
import { auth } from '@/lib/auth'
import { User, AuthResponse } from '@/lib/types'
import { getApi } from '@/lib/api'
import { ENDPOINTS } from '@/lib/constants'

interface AuthState {
  isAuthenticated: boolean
  user: Partial<User> | null
  login: (email: string, password: string) => Promise<void>
  signup: (name: string, email: string, password: string) => Promise<void>
  logout: () => void
  setUser: (user: Partial<User>) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: auth.isAuthenticated(),
  user: null,

  login: async (email: string, password: string) => {
    try {
      const api = getApi()
      const response = await api.post<AuthResponse>(ENDPOINTS.LOGIN, {
        email,
        password,
      })

      const { access_token, refresh_token, user_id, tenant_id, expires_in, role } = response.data

      // Store tokens and user info
      auth.setTokens({
        access_token,
        refresh_token,
        user_id,
        tenant_id,
        role,
        expires_in,
      })

      // Set authenticated state
      set({
        isAuthenticated: true,
        user: {
          id: user_id,
          email,
          role: role as 'owner' | 'admin' | 'editor' | 'viewer',
          tenant_id,
        },
      })
    } catch (error) {
      // Re-throw to be handled by the component
      throw error
    }
  },

  signup: async (name: string, email: string, password: string) => {
    try {
      const api = getApi()
      // Split name into first/last for backend schema
      const nameParts = name.trim().split(' ')
      const first_name = nameParts[0] || name
      const last_name = nameParts.slice(1).join(' ') || '.'

      const response = await api.post<AuthResponse>(ENDPOINTS.SIGNUP, {
        email,
        password,
        password_confirm: password,
        first_name,
        last_name,
      })

      const { access_token, refresh_token, user_id, tenant_id, expires_in, role } = response.data

      // Store tokens and user info
      auth.setTokens({
        access_token,
        refresh_token,
        user_id,
        tenant_id,
        role,
        expires_in,
      })

      // Set authenticated state
      set({
        isAuthenticated: true,
        user: {
          id: user_id,
          name,
          email,
          role: role as 'owner' | 'admin' | 'editor' | 'viewer',
          tenant_id,
        },
      })
    } catch (error) {
      // Re-throw to be handled by the component
      throw error
    }
  },

  logout: () => {
    auth.clearTokens()
    set({ isAuthenticated: false, user: null })
  },

  setUser: (user) => {
    set({ user })
  },
}))
