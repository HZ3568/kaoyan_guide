import { http } from './http'

export async function ragChat(question: string) {
  const { data } = await http.post('/rag/chat', { question })
  return data
}

export async function uploadDocument(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await http.post('/documents/upload', formData)
  return data
}

export async function listDocuments() {
  const { data } = await http.get('/documents')
  return data
}
