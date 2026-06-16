import { request } from './client'

export type KnowledgeBaseVisibility = 'private' | 'shared' | 'public'

export interface KnowledgeBase {
  id: number
  user_id: number
  goal_id?: number | null
  name: string
  description?: string | null
  domain?: string | null
  visibility: KnowledgeBaseVisibility
  created_at?: string | null
  updated_at?: string | null
}

export interface KnowledgeBasePayload {
  name: string
  description?: string | null
  domain?: string | null
  visibility?: KnowledgeBaseVisibility
  goal_id?: number | null
}

export function listKnowledgeBases() {
  return request<KnowledgeBase[]>({ method: 'GET', url: '/knowledge-bases' })
}

export function createKnowledgeBase(payload: KnowledgeBasePayload) {
  return request<KnowledgeBase>({ method: 'POST', url: '/knowledge-bases', data: payload })
}

export function updateKnowledgeBase(kbId: number, payload: Partial<KnowledgeBasePayload>) {
  return request<KnowledgeBase>({ method: 'PATCH', url: `/knowledge-bases/${kbId}`, data: payload })
}

export function deleteKnowledgeBase(kbId: number) {
  return request<KnowledgeBase>({ method: 'DELETE', url: `/knowledge-bases/${kbId}` })
}

export function bindKnowledgeBaseGoal(kbId: number, goalId: number) {
  return request<KnowledgeBase>({ method: 'POST', url: `/knowledge-bases/${kbId}/bind-goal/${goalId}` })
}
