import { request } from './client'

export type TaskItemStatus = 'pending' | 'scheduled' | 'in_progress' | 'completed' | 'delayed' | 'cancelled' | 'archived'
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent'
export type TaskSourceType = 'manual' | 'ai_optimized' | 'ai_supplement' | 'imported' | 'planner'
export type TaskSessionStatus = 'running' | 'paused' | 'completed'

export interface TaskItemPayload {
  content?: string
  title?: string
  goal_id?: number | null
  domain?: string | null
  category?: string | null
  task_type?: string | null
  planned_date?: string | null
  date?: string | null
  status?: TaskItemStatus
  priority?: TaskPriority
  estimated_minutes?: number
  actual_minutes?: number | null
  source_type?: TaskSourceType
  ai_reason?: string | null
  context_json?: Record<string, unknown> | unknown[] | null
}

export interface TaskItem {
  id: number
  user_id: number
  goal_id?: number | null
  content: string
  domain?: string | null
  category?: string | null
  task_type?: string | null
  planned_date?: string | null
  status: TaskItemStatus
  priority: TaskPriority
  estimated_minutes: number
  actual_minutes?: number | null
  actual_start_time?: string | null
  actual_end_time?: string | null
  source_type: TaskSourceType
  ai_reason?: string | null
  context_json?: Record<string, unknown> | unknown[] | null
  created_at?: string | null
  updated_at?: string | null
}

export interface TaskExecutionSession {
  id: number
  user_id: number
  task_id: number
  started_at: string
  ended_at?: string | null
  duration_minutes?: number | null
  status: TaskSessionStatus
  created_at?: string | null
  updated_at?: string | null
}

export interface TaskListParams {
  goal_id?: number
  date?: string
  planned_date?: string
  status?: TaskItemStatus
  category?: string
}

export interface TaskOptimizeRequest {
  raw_content?: string
  raw_title?: string
  raw_description?: string | null
  date?: string | null
  category?: string | null
  estimated_minutes?: number | null
  priority?: TaskPriority
  context?: Record<string, unknown> | string | null
}

export interface TaskOptimizeResponse {
  suggested_content: string
  suggested_category?: string | null
  suggested_estimated_minutes: number
  suggested_priority: TaskPriority
  reason: string
  warnings: string[]
}

export interface TaskSuggestion {
  content: string
  category?: string | null
  task_type?: string | null
  estimated_minutes: number
  priority: TaskPriority
  reason: string
  source_type: 'ai_supplement'
  confidence?: number | null
  risk_level?: 'low' | 'medium' | 'high' | null
}

export interface TaskSupplementRequest {
  planned_date?: string
  date?: string
  goal_id?: number | null
  available_minutes: number
  max_new_tasks?: number
  preferences?: Record<string, unknown>
}

export interface TaskSupplementResponse {
  suggestions: TaskSuggestion[]
  message: string
}

export interface CalendarDaySummary {
  date: string
  task_count: number
  completed_count: number
  unfinished_count: number
  estimated_minutes: number
  actual_minutes: number
  completion_rate: number
  has_delayed: boolean
  titles: string[]
}

export interface CalendarMonthSummaryResponse {
  year: number
  month: number
  days: CalendarDaySummary[]
}

function normalizePayload(payload: Partial<TaskItemPayload>) {
  const content = payload.content ?? payload.title
  return {
    ...payload,
    content,
    planned_date: payload.planned_date ?? payload.date ?? null,
  }
}

export function createTask(payload: TaskItemPayload) {
  return request<TaskItem>({ method: 'POST', url: '/tasks', data: normalizePayload(payload) })
}

export function listTasks(params: TaskListParams = {}) {
  return request<TaskItem[]>({
    method: 'GET',
    url: '/tasks',
    params: {
      ...params,
      date: params.date ?? params.planned_date,
    },
  })
}

export function getTask(taskId: number) {
  return request<TaskItem>({ method: 'GET', url: `/tasks/${taskId}` })
}

export function updateTask(taskId: number, payload: Partial<TaskItemPayload>) {
  return request<TaskItem>({ method: 'PATCH', url: `/tasks/${taskId}`, data: normalizePayload(payload) })
}

export function deleteTask(taskId: number) {
  return request<TaskItem>({ method: 'DELETE', url: `/tasks/${taskId}` })
}

export function updateTaskStatus(taskId: number, status: TaskItemStatus) {
  return request<TaskItem>({ method: 'PATCH', url: `/tasks/${taskId}/status`, data: { status } })
}

export function postponeTask(taskId: number) {
  return request<TaskItem>({ method: 'POST', url: `/tasks/${taskId}/postpone` })
}

export function startTask(taskId: number) {
  return request<TaskExecutionSession>({ method: 'POST', url: `/tasks/${taskId}/start` })
}

export function pauseTask(taskId: number) {
  return request<TaskExecutionSession>({ method: 'POST', url: `/tasks/${taskId}/pause` })
}

export function completeTask(taskId: number, payload: { actual_minutes?: number } = {}) {
  return request<TaskItem>({ method: 'POST', url: `/tasks/${taskId}/complete`, data: payload })
}

export function optimizeTask(payload: TaskOptimizeRequest) {
  return request<TaskOptimizeResponse>({
    method: 'POST',
    url: '/tasks/ai/optimize',
    data: {
      ...payload,
      raw_content: payload.raw_content ?? payload.raw_title,
    },
  })
}

export function supplementTasks(payload: TaskSupplementRequest) {
  return request<TaskSupplementResponse>({
    method: 'POST',
    url: '/tasks/ai/supplement',
    data: {
      ...payload,
      planned_date: payload.planned_date ?? payload.date,
      max_new_tasks: payload.max_new_tasks ?? 3,
      preferences: payload.preferences ?? {},
    },
  })
}

export function getTaskMonthSummary(year: number, month: number, goalId?: number | null) {
  return request<CalendarMonthSummaryResponse>({
    method: 'GET',
    url: '/tasks/month',
    params: {
      year,
      month,
      goal_id: goalId ?? undefined,
    },
  })
}
