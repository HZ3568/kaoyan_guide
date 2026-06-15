import { request } from './client'

export interface RetrievalFilter {
  subject?: string
  school?: string
  major?: string
  year?: number
}

export interface RagSearchRequest {
  query: string
  top_k?: number
  filters?: RetrievalFilter
}

export interface RagSearchResult {
  chunk_id: number
  document_id: number
  score: number
  content: string
  source: Record<string, unknown>
  page_number?: number | null
  location: Record<string, unknown>
  metadata: Record<string, unknown>
}

export interface RagSource {
  chunk_id: number
  document_id: number
  score: number
  title?: string | null
  source?: string | null
  source_type?: string | null
  source_url?: string | null
  file_name?: string | null
  page_number?: number | null
  location: Record<string, unknown>
  content_preview: string
  metadata: Record<string, unknown>
}

export interface RagAskRequest {
  question: string
  top_k?: number
  filters?: RetrievalFilter
  session_id?: number
  stream?: boolean
}

export interface RagAskResponse {
  answer: string
  sources: RagSource[]
  hit_source: boolean
  model_provider?: string | null
  model_name?: string | null
  log_id?: number | null
  retrieval_debug: Record<string, unknown>
}

export function searchRag(payload: RagSearchRequest) {
  return request<RagSearchResult[]>({
    method: 'POST',
    url: '/rag/search',
    data: {
      top_k: 5,
      ...payload,
    },
  })
}

export function askRag(payload: RagAskRequest) {
  return request<RagAskResponse>({
    method: 'POST',
    url: '/rag/ask',
    data: {
      top_k: 5,
      stream: false,
      ...payload,
    },
  })
}

export function ragChat(question: string) {
  return askRag({ question })
}

