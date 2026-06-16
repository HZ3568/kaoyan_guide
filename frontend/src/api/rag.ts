import { request } from './client'

export interface RetrievalFilter {
  goal_id?: number
  knowledge_base_id?: number
  domain?: string
  category?: string
}

export interface RagSearchRequest {
  question?: string
  query?: string
  knowledge_base_id?: number
  goal_id?: number
  top_k?: number
  filters?: RetrievalFilter
}

export interface RagSource {
  chunk_id: number
  document_id: number
  knowledge_base_id?: number | null
  goal_id?: number | null
  score: number
  filename?: string | null
  original_filename?: string | null
  domain?: string | null
  category?: string | null
  content_preview: string
  metadata: Record<string, unknown>
}

export interface RagSearchResult extends RagSource {
  content: string
  source: Record<string, unknown>
  page_number?: number | null
  location?: Record<string, unknown>
}

export interface RagAskRequest {
  question: string
  knowledge_base_id?: number
  goal_id?: number
  top_k?: number
  filters?: RetrievalFilter
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
      question: payload.question ?? payload.query,
    },
  }).then((items) =>
    items.map((item) => ({
      ...item,
      source: item.source ?? {
        title: item.original_filename ?? item.filename,
        source: item.category ?? item.domain,
        file_name: item.filename,
      },
    })),
  )
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
