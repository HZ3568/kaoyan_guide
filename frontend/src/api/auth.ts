import { request } from './client'

export interface LoginPayload {
  username: string
  password: string
}

export async function login(payload: LoginPayload) {
  return request<{ access_token: string; token_type: string }>({
    method: 'POST',
    url: '/auth/login',
    data: payload,
  })
}

export async function register(payload: LoginPayload & { email?: string }) {
  return request({
    method: 'POST',
    url: '/auth/register',
    data: payload,
  })
}
