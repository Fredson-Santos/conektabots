import axios, { AxiosError, AxiosInstance } from 'axios'
import { API_URL, ENDPOINTS } from './constants'
import { auth } from './auth'

let api: AxiosInstance | null = null
let isRefreshing = false
let failedQueue: Array<(token: string) => void> = []

const processQueue = (token: string) => {
  failedQueue.forEach(cb => cb(token))
  failedQueue = []
}

export const createApiInstance = (): AxiosInstance => {
  const instance = axios.create({
    baseURL: API_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  })

  // Request interceptor: Add token
  instance.interceptors.request.use(
    (config) => {
      const token = auth.getAccessToken()
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    },
    (error) => Promise.reject(error)
  )

  // Response interceptor: Handle 401 + refresh
  instance.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const originalRequest = error.config

      if (error.response?.status === 401 && originalRequest) {
        if (isRefreshing) {
          return new Promise((resolve) => {
            failedQueue.push((token) => {
              originalRequest.headers.Authorization = `Bearer ${token}`
              resolve(instance(originalRequest))
            })
          })
        }

        isRefreshing = true

        try {
          const refreshToken = auth.getRefreshToken()
          if (!refreshToken) {
            auth.clearTokens()
            if (typeof window !== 'undefined') {
              window.location.href = '/login'
            }
            return Promise.reject(error)
          }

          const response = await axios.post(`${API_URL}${ENDPOINTS.REFRESH}`, {
            refresh_token: refreshToken,
          })

          const { access_token, refresh_token } = response.data
          auth.setTokens({
            access_token,
            refresh_token,
            user_id: '',
            tenant_id: '',
            role: '',
            expires_in: response.data.expires_in,
          })

          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`
          }
          processQueue(access_token)

          return instance(originalRequest)
        } catch (refreshError) {
          auth.clearTokens()
          if (typeof window !== 'undefined') {
            window.location.href = '/login'
          }
          return Promise.reject(refreshError)
        } finally {
          isRefreshing = false
        }
      }

      return Promise.reject(error)
    }
  )

  return instance
}

// Lazy load API instance
export const getApi = (): AxiosInstance => {
  if (!api) {
    api = createApiInstance()
  }
  return api
}
