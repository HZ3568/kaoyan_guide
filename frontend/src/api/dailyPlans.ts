import { request } from './client'
import type { TaskDifficulty, TaskItem } from './tasks'

export type DailyPlanStatus = 'suggested' | 'confirmed' | 'finished'
export type DailyPlanTaskStatus =
  | 'suggested'
  | 'accepted'
  | 'pending'
  | 'in_progress'
  | 'completed'
  | 'delayed'
  | 'skipped'
  | 'removed'

export interface DailyPlanTask {
  id: number
  daily_plan_id: number
  task_id: number
  order_index: number
  planned_minutes: number
  planned_start_time?: string | null
  planned_end_time?: string | null
  reason?: string | null
  status: DailyPlanTaskStatus
  task?: TaskItem | null
  created_at?: string | null
  updated_at?: string | null
}

export interface DailyPlan {
  id: number
  user_id: number
  plan_date: string
  available_minutes: number
  summary?: string | null
  status: DailyPlanStatus
  created_by: 'user' | 'ai'
  tasks: DailyPlanTask[]
  created_at?: string | null
  updated_at?: string | null
}

export interface DailyPlanGeneratePayload {
  date: string
  available_minutes: number
  preferences?: {
    max_tasks?: number
    prefer_mixed_categories?: boolean
    include_overdue?: boolean
  }
}

export interface DailyPlanGenerateResponse {
  daily_plan_id: number
  status: DailyPlanStatus
  suggested_tasks: DailyPlanTask[]
  total_planned_minutes: number
  reason: string
}

export interface TaskFeedbackCreate {
  actual_minutes?: number
  difficulty_feedback?: TaskDifficulty
  completion_note?: string
}

export interface TaskFeedback {
  id: number
  task_id: number
  daily_plan_task_id?: number | null
  user_id: number
  actual_minutes?: number | null
  difficulty_feedback?: string | null
  completion_note?: string | null
  created_at?: string | null
}

export interface DailyPlanAdjustResponse {
  adjusted_task_ids: number[]
  suggestion_ids: number[]
  message: string
}

export function generateDailyPlan(payload: DailyPlanGeneratePayload) {
  return request<DailyPlanGenerateResponse>({
    method: 'POST',
    url: '/daily-plans/generate',
    data: payload,
  })
}

export function confirmDailyPlan(dailyPlanId: number) {
  return request<DailyPlan>({ method: 'POST', url: `/daily-plans/${dailyPlanId}/confirm` })
}

export function getTodayPlan() {
  return request<DailyPlan | null>({ method: 'GET', url: '/daily-plans/today' })
}

export function getDailyPlanByDate(date: string) {
  return request<DailyPlan | null>({ method: 'GET', url: '/daily-plans', params: { date } })
}

export function updateDailyPlanTaskStatus(dailyPlanId: number, dailyPlanTaskId: number, status: DailyPlanTaskStatus) {
  return request<DailyPlanTask>({
    method: 'PATCH',
    url: `/daily-plans/${dailyPlanId}/tasks/${dailyPlanTaskId}/status`,
    data: { status },
  })
}

export function submitDailyPlanTaskFeedback(dailyPlanId: number, dailyPlanTaskId: number, payload: TaskFeedbackCreate) {
  return request<TaskFeedback>({
    method: 'POST',
    url: `/daily-plans/${dailyPlanId}/tasks/${dailyPlanTaskId}/feedback`,
    data: payload,
  })
}

export function adjustDailyPlans(payload: { from_date?: string; days?: number } = {}) {
  return request<DailyPlanAdjustResponse>({
    method: 'POST',
    url: '/daily-plans/adjust',
    data: { days: 7, ...payload },
  })
}
