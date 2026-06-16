import { request } from './client'

export type TaskItemStatus = 'pending' | 'scheduled' | 'in_progress' | 'completed' | 'delayed' | 'cancelled' | 'archived'
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent'
export type TaskDifficulty = 'easy' | 'normal' | 'hard' | 'very_hard'
export type TaskSourceType = 'manual' | 'ai_optimized' | 'ai_supplement' | 'imported' | 'planner'

export interface TaskItemCreate {
  content?: string
  title?: string
  description?: string | null
  goal_id?: number | null
  domain?: string | null
  category?: string | null
  task_type?: string | null
  project?: string | null
  deadline?: string | null
  is_splittable?: boolean
  is_ai_generated?: boolean
  priority?: TaskPriority
  difficulty?: TaskDifficulty | null
  estimated_minutes?: number
  status?: TaskItemStatus
  source_type?: TaskSourceType
  ai_reason?: string | null
  source_ref?: Record<string, unknown> | unknown[] | string | null
  context_json?: Record<string, unknown> | unknown[] | null
  date?: string | null
  planned_date?: string | null
}

export interface TaskItem extends TaskItemCreate {
  id: number
  user_id: number
  content: string
  title: string
  category?: string | null
  project?: string | null
  deadline?: string | null
  is_splittable?: boolean
  is_ai_generated?: boolean
  priority: TaskPriority
  estimated_minutes: number
  actual_minutes?: number | null
  status: TaskItemStatus
  source_type: TaskSourceType
  actual_start_time?: string | null
  actual_end_time?: string | null
  created_at?: string | null
  updated_at?: string | null
}

export interface TaskListParams {
  status?: TaskItemStatus
  category?: string
  priority?: TaskPriority
  date?: string
  planned_date?: string
  goal_id?: number
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
  suggested_title: string
  suggested_category?: string | null
  suggested_description?: string | null
  suggested_estimated_minutes: number
  suggested_priority: TaskPriority
  reason: string
  warnings: string[]
}

function normalizeOutgoing(payload: Partial<TaskItemCreate>) {
  const content = payload.content ?? payload.title
  return {
    ...payload,
    content,
    category: payload.category ?? null,
    planned_date: payload.planned_date ?? payload.date ?? null,
  }
}

export function normalizeTask(raw: any): TaskItem {
  return {
    ...raw,
    title: raw.title ?? raw.content,
    description: raw.description ?? raw.ai_reason ?? null,
    project: raw.project ?? raw.domain,
    deadline: raw.deadline ?? null,
    is_splittable: raw.is_splittable ?? true,
    is_ai_generated: raw.is_ai_generated ?? Boolean(raw.source_type?.startsWith('ai_')),
  }
}

export function createTask(payload: TaskItemCreate) {
  return request<any>({ method: 'POST', url: '/tasks', data: normalizeOutgoing(payload) }).then(normalizeTask)
}

export function listTasks(params: TaskListParams = {}) {
  const normalizedParams = {
    ...params,
    date: params.date ?? params.planned_date,
  }
  return request<any[]>({ method: 'GET', url: '/tasks', params: normalizedParams }).then((items) => items.map(normalizeTask))
}

export function updateTask(taskId: number, payload: Partial<TaskItemCreate>) {
  return request<any>({ method: 'PATCH', url: `/tasks/${taskId}`, data: normalizeOutgoing(payload) }).then(normalizeTask)
}

export function deleteTask(taskId: number) {
  return request<any>({ method: 'DELETE', url: `/tasks/${taskId}` }).then(normalizeTask)
}

export function archiveTask(taskId: number) {
  return deleteTask(taskId)
}

export function optimizeTask(payload: TaskOptimizeRequest) {
  return request<any>({
    method: 'POST',
    url: '/tasks/ai/optimize',
    data: {
      ...payload,
      raw_content: payload.raw_content ?? payload.raw_title,
      category: payload.category,
    },
  }).then((item): TaskOptimizeResponse => ({
    ...item,
    suggested_title: item.suggested_title ?? item.suggested_content,
    suggested_content: item.suggested_content ?? item.suggested_title,
    suggested_description: item.suggested_description ?? item.suggested_content,
  }))
}

export function updateTaskStatus(taskId: number, status: TaskItemStatus) {
  return request<any>({ method: 'PATCH', url: `/tasks/${taskId}/status`, data: { status } }).then(normalizeTask)
}

export function submitTaskFeedback(taskId: number, payload: { actual_minutes?: number }) {
  return request<any>({
    method: 'POST',
    url: `/tasks/${taskId}/complete`,
    data: { actual_minutes: payload.actual_minutes ?? 0 },
  }).then(normalizeTask)
}
