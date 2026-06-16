import { request, upload } from './client'

export interface DocumentRecord {
  id: number
  user_id: number
  knowledge_base_id?: number | null
  goal_id?: number | null
  filename: string
  title?: string
  file_name?: string
  original_filename?: string | null
  file_type: string
  file_path: string
  domain?: string | null
  category?: string | null
  source?: string | null
  tags_json?: string[] | null
  parse_status: string
  chunk_status: string
  embedding_status: string
  chunk_count: number
  description?: string | null
  created_at?: string | null
}

export interface DocumentChunk {
  id: number
  document_id: number
  user_id: number
  knowledge_base_id?: number | null
  goal_id?: number | null
  chunk_index: number
  content: string
  content_hash: string
  chunk_type?: string
  page_number?: number | null
  token_count?: number
  is_vectorized?: boolean
  domain?: string | null
  category?: string | null
  metadata_json?: Record<string, unknown> | null
  embedding_id?: string | null
  embedding_status: string
}

export interface DocumentUploadMetadata {
  knowledge_base_id?: number
  goal_id?: number
  domain?: string
  category?: string
  tags?: string
  description?: string
}

export interface VectorIndexRequest {
  document_id?: number
  knowledge_base_id?: number
  goal_id?: number
  limit?: number
  batch_size?: number
  force_reindex?: boolean
}

export interface VectorIndexResponse {
  indexed: number
  skipped: number
  failed: number
  errors: string[]
  index_name: string
  embedding_dim: number
  dimension_notice?: string | null
}

export interface VectorIndexStatus {
  total_chunks: number
  indexed_chunks: number
  pending_chunks: number
  failed_chunks: number
  redis: Record<string, unknown>
  embedding?: Record<string, unknown>
  dimension_notice?: string | null
}

export interface EmbeddingHealthResponse {
  ok: boolean
  provider: string
  base_url?: string | null
  model: string
  dimension: number
  status_code?: number | null
  message: string
  error_body?: string | null
  hints: string[]
  dimension_notice?: string | null
}

function appendIfPresent(formData: FormData, key: string, value: unknown) {
  if (value === undefined || value === null || value === '') return
  formData.append(key, String(value))
}

export function uploadDocument(file: File, metadata: DocumentUploadMetadata = {}) {
  const formData = new FormData()
  formData.append('file', file)
  Object.entries(metadata).forEach(([key, value]) => appendIfPresent(formData, key, value))
  return upload<any>('/documents/upload', formData).then(normalizeDocument)
}

export function listDocuments(params: Partial<DocumentUploadMetadata> = {}) {
  return request<any[]>({ method: 'GET', url: '/documents', params }).then((items) => items.map(normalizeDocument))
}

export function listDocumentChunks(documentId: number) {
  return request<any[]>({ method: 'GET', url: `/documents/${documentId}/chunks` }).then((items) => items.map(normalizeChunk))
}

export function indexChunks(payload: VectorIndexRequest = {}) {
  return request<VectorIndexResponse>({
    method: 'POST',
    url: '/rag/index',
    data: {
      limit: payload.limit ?? 100,
      batch_size: payload.batch_size ?? 32,
      force_reindex: payload.force_reindex ?? false,
      document_id: payload.document_id,
      knowledge_base_id: payload.knowledge_base_id,
      goal_id: payload.goal_id,
    },
  })
}

export function getVectorIndexStatus() {
  return request<VectorIndexStatus>({ method: 'GET', url: '/rag/index/status' })
}

export function checkEmbeddingHealth() {
  return request<EmbeddingHealthResponse>({ method: 'GET', url: '/rag/embedding/health' })
}

function normalizeDocument(raw: any): DocumentRecord {
  return {
    ...raw,
    title: raw.title ?? raw.original_filename ?? raw.filename,
    file_name: raw.file_name ?? raw.original_filename ?? raw.filename,
    source: raw.source ?? raw.category,
  }
}

function normalizeChunk(raw: any): DocumentChunk {
  const metadata = raw.metadata_json || {}
  return {
    ...raw,
    chunk_type: raw.chunk_type ?? metadata.chunk_type ?? 'text',
    page_number: raw.page_number ?? metadata.page_number ?? null,
    token_count: raw.token_count ?? metadata.token_count ?? 0,
    is_vectorized: raw.is_vectorized ?? raw.embedding_status === 'indexed',
  }
}
