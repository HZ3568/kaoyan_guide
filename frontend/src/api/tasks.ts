import { request } from './client'

export type TaskItemStatus = 'backlog' | 'pending' | 'in_progress' | 'completed' | 'delayed' | 'skipped' | 'archived'
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent'
export type TaskDifficulty = 'easy' | 'normal' | 'hard' | 'very_hard'
export type TaskSourceType = 'manual' | 'ai_split' | 'rag_recommendation' | 'imported' | 'planner'

export interface TaskItemCreate {
  title: string
  description?: string | null
  category?: string | null
  subject?: string | null
  project?: string | null
  priority?: TaskPriority
  difficulty?: TaskDifficulty | null
  estimated_minutes?: number
  deadline?: string | null
  status?: TaskItemStatus
  parent_task_id?: number | null
  is_splittable?: boolean
  is_ai_generated?: boolean
  source_type?: TaskSourceType
  source_ref?: Record<string, unknown> | unknown[] | string | null
}

export interface TaskItem extends TaskItemCreate {
  id: number
  user_id: number
  title: string
  priority: TaskPriority
  estimated_minutes: number
  status: TaskItemStatus
  is_splittable: boolean
  is_ai_generated: boolean
  source_type: TaskSourceType
  created_at?: string | null
  updated_at?: string | null
}

export interface TaskAiSuggestion {
  id: number
  user_id: number
  task_id?: number | null
  suggestion_type: string
  suggestion_content: Record<string, unknown> | unknown[] | string
  accepted: boolean
  created_at?: string | null
}

export interface TaskListParams {
  status?: TaskItemStatus
  category?: string
  subject?: string
  priority?: TaskPriority
  deadline_before?: string
}

export interface TaskOrganizeRequest {
  status?: TaskItemStatus[]
  limit?: number
}

export interface RagTaskRecommendationRequest {
  query: string
  top_k?: number
  max_tasks?: number
}

export interface RagTaskRecommendationResponse {
  suggestions: TaskAiSuggestion[]
  message: string
}

export function createTask(payload: TaskItemCreate) {
  return request<TaskItem>({ method: 'POST', url: '/tasks', data: payload })
}

export function bulkCreateTasks(tasks: TaskItemCreate[]) {
  return request<{ tasks: TaskItem[] }>({ method: 'POST', url: '/tasks/bulk', data: { tasks } })
}

export function listTasks(params: TaskListParams = {}) {
  return request<TaskItem[]>({ method: 'GET', url: '/tasks', params })
}

export function updateTask(taskId: number, payload: Partial<TaskItemCreate>) {
  return request<TaskItem>({ method: 'PATCH', url: `/tasks/${taskId}`, data: payload })
}

export function deleteTask(taskId: number) {
  return request<TaskItem>({ method: 'DELETE', url: `/tasks/${taskId}` })
}

export function archiveTask(taskId: number) {
  return request<TaskItem>({ method: 'PATCH', url: `/tasks/${taskId}/archive` })
}

export function splitTask(taskId: number) {
  return request<{ task: TaskItem; suggestions: TaskAiSuggestion[]; message: string }>({
    method: 'POST',
    url: `/tasks/${taskId}/split`,
  })
}

export function organizeTasks(payload: TaskOrganizeRequest = {}) {
  return request<{ suggestions: TaskAiSuggestion[]; message: string }>({
    method: 'POST',
    url: '/tasks/ai/organize',
    data: { limit: 50, ...payload },
  })
}

export function recommendTasksFromRag(payload: RagTaskRecommendationRequest) {
  return request<RagTaskRecommendationResponse>({
    method: 'POST',
    url: '/tasks/ai/recommend-from-rag',
    data: {
      top_k: 5,
      max_tasks: 5,
      ...payload,
    },
  })
}
