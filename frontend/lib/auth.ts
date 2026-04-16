import { STORAGE_KEYS } from './constants'

export interface TokenData {
  access_token: string
  refresh_token: string
  user_id: string
  tenant_id: string
  role: string
  expires_in: number
}

export const auth = {
  // Store tokens
  setTokens: (data: TokenData) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, data.access_token)
      localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, data.refresh_token)
      // Store user info in memory (for quick access)
      sessionStorage.setItem('user_id', data.user_id)
      sessionStorage.setItem('tenant_id', data.tenant_id)
      sessionStorage.setItem('role', data.role)
    }
  },

  // Get access token
  getAccessToken: () => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)
    }
    return null
  },

  // Get refresh token
  getRefreshToken: () => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN)
    }
    return null
  },

  // Clear all tokens
  clearTokens: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN)
      localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN)
      sessionStorage.removeItem('user_id')
      sessionStorage.removeItem('tenant_id')
      sessionStorage.removeItem('role')
    }
  },

  // Check if authenticated
  isAuthenticated: () => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)
      return !!token
    }
    return false
  },

  // Get stored user data
  getUserData: (): { user_id: string; tenant_id: string; role: string; name?: string; email?: string } | null => {
    if (typeof window !== 'undefined') {
      const user_id = sessionStorage.getItem('user_id')
      if (!user_id) return null
      return {
        user_id,
        tenant_id: sessionStorage.getItem('tenant_id') || '',
        role: sessionStorage.getItem('role') || '',
        name: sessionStorage.getItem('user_name') || undefined,
        email: sessionStorage.getItem('user_email') || undefined,
      }
    }
    return null
  },
}
