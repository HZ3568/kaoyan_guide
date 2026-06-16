import { request } from './client'

export interface DailyReviewPayload {
  goal_id?: number | null
  review_date: string
  completion_rate?: number
  total_estimated_minutes?: number
  total_actual_minutes?: number
  summary?: string | null
  problems?: string | null
  adjustment_suggestion?: string | null
  metadata_json?: Record<string, unknown> | unknown[] | null
}

export interface DailyReview extends DailyReviewPayload {
  id: number
  user_id: number
  completion_rate: number
  total_estimated_minutes: number
  total_actual_minutes: number
  created_at?: string | null
  updated_at?: string | null
}

export interface ReviewStats {
  goal_id?: number | null
  total_tasks: number
  completed_tasks: number
  delayed_tasks: number
  completion_rate: number
  delay_rate: number
  estimated_minutes: number
  actual_minutes: number
  actual_estimated_delta_minutes: number
}

export function listReviews(params: { goal_id?: number; review_date?: string } = {}) {
  return request<DailyReview[]>({ method: 'GET', url: '/reviews', params })
}

export function createReview(payload: DailyReviewPayload) {
  return request<DailyReview>({ method: 'POST', url: '/reviews', data: payload })
}

export function updateReview(reviewId: number, payload: Partial<DailyReviewPayload>) {
  return request<DailyReview>({ method: 'PATCH', url: `/reviews/${reviewId}`, data: payload })
}

export function getReviewStats(goalId?: number | null) {
  return request<ReviewStats>({
    method: 'GET',
    url: '/reviews/stats',
    params: { goal_id: goalId ?? undefined },
  })
}
