import { create } from 'zustand'
import { auth } from '@/lib/auth'
import { User } from '@/lib/types'

interface AuthState {
  isAuthenticated: boolean
  user: Partial<User> | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  setUser: (user: Partial<User>) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: auth.isAuthenticated(),
  user: null,

  login: async (_email: string, _password: string) => {
    // Will be used in Task B1 (auth pages)
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    set({ isAuthenticated: true })
  },

  logout: () => {
    auth.clearTokens()
    set({ isAuthenticated: false, user: null })
  },

  setUser: (user) => {
    set({ user })
  },
}))
