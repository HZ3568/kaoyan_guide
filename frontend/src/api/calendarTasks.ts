import { request } from './client'
import type { DailyPlan, DailyPlanTask } from './dailyPlans'
import type { TaskItem, TaskItemCreate, TaskPriority } from './tasks'
import { createTask, listTasks, normalizeTask } from './tasks'

export interface CalendarDaySummary {
  date: string
  task_count: number
  completed_count: number
  unfinished_count: number
  estimated_minutes: number
  actual_minutes?: number
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
  preferences?: Record<string, unknown>
}

export interface CalendarTaskSuggestion {
  title: string
  content?: string
  description?: string | null
  category?: string | null
  task_type?: string | null
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

export function taskToPlanTask(task: TaskItem): DailyPlanTask {
  return {
    id: task.id,
    daily_plan_id: 0,
    task_id: task.id,
    order_index: 0,
    planned_minutes: task.estimated_minutes,
    status: task.status as any,
    started_at: task.actual_start_time ?? null,
    completed_at: task.actual_end_time ?? null,
    actual_seconds: task.actual_minutes == null ? null : task.actual_minutes * 60,
    reason: task.ai_reason ?? null,
    task,
    created_at: task.created_at,
    updated_at: task.updated_at,
  }
}

export function tasksToDailyPlan(date: string, tasks: TaskItem[]): DailyPlan {
  return {
    id: 0,
    user_id: tasks[0]?.user_id ?? 0,
    plan_date: date,
    available_minutes: tasks.reduce((sum, task) => sum + (task.estimated_minutes || 0), 0),
    status: 'confirmed',
    created_by: 'user',
    tasks: tasks.map(taskToPlanTask),
  }
}

export function getCalendarMonthSummary(year: number, month: number) {
  return request<CalendarMonthSummary>({ method: 'GET', url: '/tasks/month', params: { year, month } })
}

export function getCalendarTasksByDate(date: string) {
  return listTasks({ date }).then((tasks) => tasksToDailyPlan(date, tasks))
}

export function supplementCalendarTasks(payload: CalendarSupplementPayload) {
  return request<any>({
    method: 'POST',
    url: '/tasks/ai/supplement',
    data: {
      planned_date: payload.date,
      available_minutes: payload.available_minutes,
      max_new_tasks: payload.max_new_tasks ?? 3,
      preferences: payload.preferences ?? {},
    },
  }).then((response): CalendarSupplementResponse => ({
    message: response.message,
    suggestions: (response.suggestions || []).map((item: any) => ({
      ...item,
      title: item.title ?? item.content,
      content: item.content ?? item.title,
      description: item.description ?? item.reason,
    })),
  }))
}

export function acceptCalendarTaskSuggestion(payload: TaskItemCreate) {
  return createTask(payload)
}
