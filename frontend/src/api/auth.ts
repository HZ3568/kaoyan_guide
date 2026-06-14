import { http } from './http'

export interface LoginPayload {
  username: string
  password: string
}

export async function login(payload: LoginPayload) {
  const { data } = await http.post('/auth/login', payload)
  return data as { access_token: string; token_type: string }
}

export async function register(payload: LoginPayload & { email?: string }) {
  const { data } = await http.post('/auth/register', payload)
  return data
}
