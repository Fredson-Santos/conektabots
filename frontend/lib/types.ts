export interface User {
  id: string
  email: string
  name: string
  role: 'owner' | 'admin' | 'editor' | 'viewer'
  tenant_id: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user_id: string
  tenant_id: string
  role: string
}

export interface ApiError {
  detail: string | { [key: string]: string[] }
  status: number
}
