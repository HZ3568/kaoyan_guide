import axios from 'axios'
import type { AxiosError, AxiosRequestConfig } from 'axios'
import { useAuthStore } from '../stores/authStore'

const DEFAULT_BASE_URL = '/api/v1'

export class ApiError extends Error {
  status?: number

  constructor(message: string, status?: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

function resolveBaseUrl() {
  return import.meta.env.VITE_API_BASE_URL || DEFAULT_BASE_URL
}

function resolveErrorMessage(error: unknown) {
  const axiosError = error as AxiosError<{ detail?: string | { msg?: string }[]; message?: string }>
  if (axiosError.response?.data) {
    const detail = axiosError.response.data.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail) && detail.length > 0) {
      return detail.map((item) => item.msg).filter(Boolean).join('；') || '请求参数不正确'
    }
    if (axiosError.response.data.message) return axiosError.response.data.message
  }
  if (axiosError.message) return axiosError.message
  return '网络请求失败，请稍后重试'
}

export const apiClient = axios.create({
  baseURL: resolveBaseUrl(),
  timeout: 30000,
  headers: {
    Accept: 'application/json',
  },
})

apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const axiosError = error as AxiosError
    return Promise.reject(new ApiError(resolveErrorMessage(error), axiosError.response?.status))
  },
)

export async function request<T>(config: AxiosRequestConfig) {
  const { data } = await apiClient.request<T>(config)
  return data
}

export async function upload<T>(url: string, formData: FormData, config: AxiosRequestConfig = {}) {
  const { data } = await apiClient.post<T>(url, formData, {
    ...config,
    headers: {
      ...config.headers,
      'Content-Type': 'multipart/form-data',
    },
  })
  return data
}

export function getApiBaseUrl() {
  return resolveBaseUrl()
}
