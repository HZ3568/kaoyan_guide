import { request } from './client'

export type GoalPriority = 'low' | 'medium' | 'high' | 'urgent'
export type GoalStatus = 'active' | 'paused' | 'completed' | 'archived'

export interface Goal {
  id: number
  user_id: number
  title: string
  goal_type?: string | null
  domain?: string | null
  target_result?: string | null
  deadline?: string | null
  priority: GoalPriority
  status: GoalStatus
  progress: number
  context_json?: Record<string, unknown> | unknown[] | null
  created_at?: string | null
  updated_at?: string | null
}

export interface GoalPayload {
  title: string
  goal_type?: string | null
  domain?: string | null
  target_result?: string | null
  deadline?: string | null
  priority?: GoalPriority
  status?: GoalStatus
  progress?: number
  context_json?: Record<string, unknown> | unknown[] | null
}

export function listGoals() {
  return request<Goal[]>({ method: 'GET', url: '/goals' })
}

export function createGoal(payload: GoalPayload) {
  return request<Goal>({ method: 'POST', url: '/goals', data: payload })
}

export function updateGoal(goalId: number, payload: Partial<GoalPayload>) {
  return request<Goal>({ method: 'PATCH', url: `/goals/${goalId}`, data: payload })
}

export function archiveGoal(goalId: number) {
  return request<Goal>({ method: 'DELETE', url: `/goals/${goalId}` })
}

export function activateGoal(goalId: number) {
  return request<Goal>({ method: 'POST', url: `/goals/${goalId}/activate` })
}
