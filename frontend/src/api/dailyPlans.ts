import { request } from './client'
import { listTasks, normalizeTask } from './tasks'
import type { TaskItem } from './tasks'
import { taskToPlanTask, tasksToDailyPlan } from './calendarTasks'

export type DailyPlanStatus = 'suggested' | 'confirmed' | 'finished'
export type DailyPlanTaskStatus =
  | 'pending'
  | 'scheduled'
  | 'in_progress'
  | 'completed'
  | 'delayed'
  | 'skipped'
  | 'cancelled'
  | 'archived'
  | 'removed'

export interface TaskFeedbackCreate {
  actual_minutes?: number
  difficulty_feedback?: string
  completion_note?: string
}

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
  started_at?: string | null
  completed_at?: string | null
  actual_seconds?: number | null
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

export function getTodayPlan() {
  const today = new Date().toISOString().slice(0, 10)
  return listTasks({ date: today }).then((tasks) => tasksToDailyPlan(today, tasks))
}

export function getDailyPlanByDate(date: string) {
  return listTasks({ date }).then((tasks) => tasksToDailyPlan(date, tasks))
}

export function startDailyPlanTask(_dailyPlanId: number, dailyPlanTaskId: number) {
  return request<any>({ method: 'POST', url: `/tasks/${dailyPlanTaskId}/start` }).then((session): DailyPlanTask => ({
    id: dailyPlanTaskId,
    daily_plan_id: 0,
    task_id: dailyPlanTaskId,
    order_index: 0,
    planned_minutes: 0,
    status: 'in_progress',
    started_at: session.started_at,
    actual_seconds: null,
  }))
}

export function completeDailyPlanTask(
  _dailyPlanId: number,
  dailyPlanTaskId: number,
  payload: { actual_seconds?: number } = {},
) {
  return request<any>({
    method: 'POST',
    url: `/tasks/${dailyPlanTaskId}/complete`,
    data: { actual_minutes: payload.actual_seconds == null ? undefined : Math.ceil(payload.actual_seconds / 60) },
  }).then((raw): DailyPlanTask => taskToPlanTask(normalizeTask(raw)))
}

export function postponeDailyPlanTask(_dailyPlanId: number, dailyPlanTaskId: number) {
  return request<any>({ method: 'POST', url: `/tasks/${dailyPlanTaskId}/postpone` }).then((raw): DailyPlanTask =>
    taskToPlanTask(normalizeTask(raw)),
  )
}

export function updateDailyPlanTaskStatus(_dailyPlanId: number, dailyPlanTaskId: number, status: DailyPlanTaskStatus) {
  return request<any>({ method: 'PATCH', url: `/tasks/${dailyPlanTaskId}/status`, data: { status } }).then((raw): DailyPlanTask =>
    taskToPlanTask(normalizeTask(raw)),
  )
}

export function generateDailyPlan() {
  throw new Error('This legacy planning API has been replaced by date-based task scheduling.')
}

export function confirmDailyPlan() {
  throw new Error('This legacy planning API has been replaced by date-based task scheduling.')
}

export function submitDailyPlanTaskFeedback() {
  throw new Error('feedback has been replaced by task completion timing.')
}

export function adjustDailyPlans() {
  throw new Error('This legacy planning API has been replaced by daily reviews and task supplement suggestions.')
}
