import { request, upload } from './client'

export interface DocumentRecord {
  id: number
  title: string
  file_name: string
  file_type: string
  source?: string | null
  source_type: string
  source_url?: string | null
  subject?: string | null
  school?: string | null
  major?: string | null
  tags_json?: string[] | null
  exam_year?: number | null
  parse_status: string
  created_at?: string | null
}

export interface DocumentChunk {
  id: number
  document_id: number
  chunk_index: number
  content: string
  chunk_type: string
  page_number?: number | null
  position_start?: number | null
  position_end?: number | null
  token_count: number
  metadata_json?: Record<string, unknown> | null
  embedding_status: string
  is_vectorized: boolean
}

export interface DocumentUploadMetadata {
  title?: string
  source?: string
  source_url?: string
  subject?: string
  school?: string
  major?: string
  tags?: string
  exam_year?: number
  description?: string
}

export interface VectorIndexRequest {
  document_id?: number
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
}

export interface VectorIndexStatus {
  total_chunks: number
  indexed_chunks: number
  pending_chunks: number
  failed_chunks: number
  redis: Record<string, unknown>
}

function appendIfPresent(formData: FormData, key: string, value: unknown) {
  if (value === undefined || value === null || value === '') return
  formData.append(key, String(value))
}

export function uploadDocument(file: File, metadata: DocumentUploadMetadata = {}) {
  const formData = new FormData()
  formData.append('file', file)
  Object.entries(metadata).forEach(([key, value]) => appendIfPresent(formData, key, value))
  return upload<DocumentRecord>('/documents/upload', formData)
}

export function listDocuments() {
  return request<DocumentRecord[]>({
    method: 'GET',
    url: '/documents',
  })
}

export function listDocumentChunks(documentId: number) {
  return request<DocumentChunk[]>({
    method: 'GET',
    url: `/documents/${documentId}/chunks`,
  })
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
    },
  })
}

export function getVectorIndexStatus() {
  return request<VectorIndexStatus>({
    method: 'GET',
    url: '/rag/index/status',
  })
}

