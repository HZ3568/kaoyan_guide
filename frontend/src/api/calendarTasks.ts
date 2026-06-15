import { request } from './client'
import type { DailyPlan } from './dailyPlans'
import type { TaskItem, TaskItemCreate, TaskPriority } from './tasks'

export interface CalendarDaySummary {
  date: string
  task_count: number
  completed_count: number
  unfinished_count: number
  estimated_minutes: number
  completion_rate: number
  has_delayed: boolean
  titles: string[]
}

export interface CalendarMonthSummary {
  year: number
  month: number
  days: CalendarDaySummary[]
}

export interface CalendarSupplementPayload {
  date: string
  available_minutes: number
  max_new_tasks?: number
  preferences?: {
    prefer_mixed_categories?: boolean
    include_delayed?: boolean
  }
}

export interface CalendarTaskSuggestion {
  title: string
  description?: string | null
  category?: string | null
  subject?: string | null
  estimated_minutes: number
  priority: TaskPriority
  reason: string
  source_type: 'ai_supplement'
  confidence?: number | null
  risk_level?: 'low' | 'medium' | 'high' | null
}

export interface CalendarSupplementResponse {
  suggestions: CalendarTaskSuggestion[]
  message: string
}

export function getCalendarMonthSummary(year: number, month: number) {
  return request<CalendarMonthSummary>({ method: 'GET', url: '/calendar-tasks/month', params: { year, month } })
}

export function getCalendarTasksByDate(date: string) {
  return request<DailyPlan | null>({ method: 'GET', url: '/calendar-tasks', params: { date } })
}

export function supplementCalendarTasks(payload: CalendarSupplementPayload) {
  return request<CalendarSupplementResponse>({
    method: 'POST',
    url: '/calendar-tasks/ai/supplement',
    data: {
      max_new_tasks: 3,
      preferences: { prefer_mixed_categories: true, include_delayed: true },
      ...payload,
    },
  })
}

export function acceptCalendarTaskSuggestion(payload: TaskItemCreate) {
  return request<TaskItem>({ method: 'POST', url: '/calendar-tasks/accept-suggestion', data: payload })
}
