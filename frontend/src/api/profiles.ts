import { request } from './client'
import type { Goal, GoalPayload } from './goals'

export interface UserProfile {
  id: number
  user_id: number
  persona_type?: string | null
  current_stage?: string | null
  domain?: string | null
  background_summary?: string | null
  ability_level?: string | null
  daily_available_minutes?: number | null
  weekly_available_days?: number | null
  preference_json?: Record<string, unknown> | unknown[] | null
  constraint_json?: Record<string, unknown> | unknown[] | null
  created_at?: string | null
  updated_at?: string | null
}

export interface UserProfilePayload {
  persona_type?: string | null
  current_stage?: string | null
  domain?: string | null
  background_summary?: string | null
  ability_level?: string | null
  daily_available_minutes?: number | null
  weekly_available_days?: number | null
  preference_json?: Record<string, unknown> | unknown[] | null
  constraint_json?: Record<string, unknown> | unknown[] | null
}

export interface OnboardingPayload {
  profile: UserProfilePayload
  goal?: GoalPayload | null
}

export interface OnboardingResponse {
  profile: UserProfile
  goal?: Goal | null
}

export function getMyProfile() {
  return request<UserProfile>({ method: 'GET', url: '/profiles/me' })
}

export function updateMyProfile(payload: UserProfilePayload) {
  return request<UserProfile>({ method: 'PUT', url: '/profiles/me', data: payload })
}

export function submitOnboarding(payload: OnboardingPayload) {
  return request<OnboardingResponse>({ method: 'POST', url: '/profiles/onboarding', data: payload })
}
