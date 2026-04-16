export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
export const API_BASE_PATH = process.env.NEXT_PUBLIC_API_BASE_PATH || '/api/v1'
export const API_URL = `${API_BASE_URL}${API_BASE_PATH}`

export const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME || 'ConektaBots'
export const APP_VERSION = process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0'

// Token keys
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
}

// API Endpoints
export const ENDPOINTS = {
  LOGIN: '/auth/login',
  SIGNUP: '/auth/signup',
  REFRESH: '/auth/refresh',
  LOGOUT: '/auth/logout',
  BOTS: '/bots',
  MARKETPLACES: '/marketplaces',
}
