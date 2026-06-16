import { Alert, Button, Card, Form, Input, Space, Table, Tag, Typography, Upload, message } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useEffect, useMemo, useState } from 'react'
import {
  getVectorIndexStatus,
  indexChunks,
  listDocumentChunks,
  listDocuments,
  uploadDocument,
  checkEmbeddingHealth,
} from '../api/documents'
import type {
  DocumentChunk,
  DocumentRecord,
  DocumentUploadMetadata,
  EmbeddingHealthResponse,
  VectorIndexResponse,
  VectorIndexStatus,
} from '../api/documents'
import { ChunkList } from '../components/ChunkList'
import { ErrorMessage } from '../components/ErrorMessage'
import { Loading } from '../components/Loading'

interface DocumentRow extends DocumentRecord {
  chunk_count: number
  vectorized_count: number
}

function formatIndexFailure(result: VectorIndexResponse) {
  const lines = [
    `向量化失败 ${result.failed} 个 chunk，成功 ${result.indexed} 个。`,
    ...result.errors,
  ]
  if (result.dimension_notice) {
    lines.push(result.dimension_notice)
  }
  return lines.filter(Boolean).join('\n')
}

function formatEmbeddingHealth(result: EmbeddingHealthResponse) {
  const lines = [
    result.message,
    result.status_code ? `HTTP 状态码：${result.status_code}` : '',
    result.hints?.length ? `可能原因：${result.hints.join('；')}` : '',
    result.error_body ? `服务商返回：${result.error_body}` : '',
    result.dimension_notice || '',
  ]
  return lines.filter(Boolean).join('\n')
}

export default function KnowledgeBasePage() {
  const [form] = Form.useForm<DocumentUploadMetadata>()
  const [uploadFile, setUploadFile] = useState<File | null>(null)
  const [documents, setDocuments] = useState<DocumentRecord[]>([])
  const [chunksByDocument, setChunksByDocument] = useState<Record<number, DocumentChunk[]>>({})
  const [selectedDocumentId, setSelectedDocumentId] = useState<number | null>(null)
  const [indexStatus, setIndexStatus] = useState<VectorIndexStatus | null>(null)
  const [embeddingHealth, setEmbeddingHealth] = useState<EmbeddingHealthResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [indexing, setIndexing] = useState(false)
  const [checkingEmbedding, setCheckingEmbedding] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function refresh() {
    setLoading(true)
    setError(null)
    try {
      const docs = await listDocuments()
      const chunkPairs = await Promise.all(
        docs.map(async (doc) => {
          try {
            return [doc.id, await listDocumentChunks(doc.id)] as const
          } catch {
            return [doc.id, []] as const
          }
        }),
      )
      setDocuments(docs)
      setChunksByDocument(Object.fromEntries(chunkPairs))
      await refreshIndexStatus()
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载知识库失败')
    } finally {
      setLoading(false)
    }
  }

  async function refreshIndexStatus() {
    try {
      setIndexStatus(await getVectorIndexStatus())
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载索引状态失败')
    }
  }

  useEffect(() => {
    void refresh()
  }, [])

  const rows = useMemo<DocumentRow[]>(() => (
    documents.map((doc) => {
      const chunks = chunksByDocument[doc.id] || []
      return {
        ...doc,
        chunk_count: chunks.length,
        vectorized_count: chunks.filter((chunk) => chunk.is_vectorized).length,
      }
    })
  ), [documents, chunksByDocument])

  async function handleUpload(values: DocumentUploadMetadata) {
    if (!uploadFile) {
      message.warning('请选择要上传的文件')
      return
    }
    setUploading(true)
    setError(null)
    try {
      await uploadDocument(uploadFile, values)
      message.success('上传并切片完成')
      form.resetFields()
      setUploadFile(null)
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : '上传失败')
    } finally {
      setUploading(false)
    }
  }

  async function handleIndex(documentId?: number, forceReindex = false) {
    setIndexing(true)
    setError(null)
    try {
      const result = await indexChunks({ document_id: documentId, force_reindex: forceReindex, limit: 1000 })
      if (result.failed > 0 || result.errors.length > 0) {
        const detail = formatIndexFailure(result)
        setError(detail)
        message.warning(`向量化完成但存在失败：成功 ${result.indexed}，失败 ${result.failed}`)
      } else {
        message.success(`向量化完成：成功 ${result.indexed}，跳过 ${result.skipped}，失败 ${result.failed}`)
      }
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : '向量化失败')
    } finally {
      setIndexing(false)
    }
  }

  async function handleCheckEmbedding() {
    setCheckingEmbedding(true)
    setError(null)
    try {
      const result = await checkEmbeddingHealth()
      setEmbeddingHealth(result)
      if (result.ok) {
        message.success(`Embedding 连通性正常：${result.model} / ${result.dimension}`)
      } else {
        setError(formatEmbeddingHealth(result))
        message.error('Embedding 连通性失败')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Embedding 连通性测试失败')
    } finally {
      setCheckingEmbedding(false)
    }
  }

  const columns: ColumnsType<DocumentRow> = [
    {
      title: '标题',
      dataIndex: 'title',
      render: (value: string, record) => (
        <div>
          <Typography.Text strong>{value}</Typography.Text>
          <div className="muted-text">{record.file_name}</div>
        </div>
      ),
    },
    { title: '类型', dataIndex: 'file_type', width: 90 },
    { title: '来源', dataIndex: 'source', render: (value?: string | null) => value || '-' },
    {
      title: '标签',
      render: (_, record) => (
        <Space wrap>
          {record.domain && <Tag>{record.domain}</Tag>}
          {record.category && <Tag>{record.category}</Tag>}
          {(record.tags_json || []).map((tag) => <Tag key={tag}>{tag}</Tag>)}
        </Space>
      ),
    },
    {
      title: '处理状态',
      dataIndex: 'parse_status',
      width: 120,
      render: (value: string) => <Tag color={value === 'completed' ? 'green' : 'orange'}>{value}</Tag>,
    },
    {
      title: 'Chunk',
      width: 140,
      render: (_, record) => `${record.vectorized_count}/${record.chunk_count} 已向量化`,
    },
    {
      title: '操作',
      width: 220,
      render: (_, record) => (
        <Space wrap>
          <Button size="small" onClick={() => setSelectedDocumentId(record.id)}>查看 chunks</Button>
          <Button size="small" loading={indexing} onClick={() => handleIndex(record.id)}>向量化</Button>
          <Button size="small" loading={indexing} onClick={() => handleIndex(record.id, true)}>重建</Button>
        </Space>
      ),
    },
  ]

  const selectedChunks = selectedDocumentId ? chunksByDocument[selectedDocumentId] || [] : []

  return (
    <div className="page">
      <div className="page-title-row">
        <Typography.Title level={2}>知识库管理</Typography.Title>
        <Space>
          <Button onClick={refresh} loading={loading}>刷新</Button>
          <Button onClick={handleCheckEmbedding} loading={checkingEmbedding}>测试 Embedding</Button>
          <Button type="primary" onClick={() => handleIndex()} loading={indexing}>增量向量化</Button>
          <Button onClick={() => handleIndex(undefined, true)} loading={indexing}>重建索引</Button>
        </Space>
      </div>

      <ErrorMessage message={error} />

      <Card title="上传资料">
        <Form form={form} layout="vertical" onFinish={handleUpload}>
          <div className="form-grid">
            <Form.Item label="标题" name="title">
              <Input placeholder="默认使用文件名" />
            </Form.Item>
            <Form.Item label="领域" name="domain">
              <Input placeholder="例如：软件工程、写作训练、产品设计" />
            </Form.Item>
            <Form.Item label="分类" name="category">
              <Input placeholder="例如：后端、阅读、项目、复盘" />
            </Form.Item>
            <Form.Item label="标签" name="tags">
              <Input placeholder="用逗号分隔" />
            </Form.Item>
          </div>
          <Form.Item label="说明" name="description">
            <Input.TextArea rows={2} maxLength={500} />
          </Form.Item>
          <Space wrap>
            <Upload
              beforeUpload={(file) => {
                setUploadFile(file)
                return false
              }}
              maxCount={1}
              onRemove={() => setUploadFile(null)}
              accept=".txt,.md,.pdf,.json"
            >
              <Button>选择 txt / md / pdf / json</Button>
            </Upload>
            <Button type="primary" htmlType="submit" loading={uploading}>上传并生成 chunk</Button>
          </Space>
        </Form>
      </Card>

      <Card className="block-gap" title="Redis Vector 索引状态">
        {indexStatus ? (
          <>
            <Space wrap>
              <Tag>索引名：{String(indexStatus.redis.index_name || '-')}</Tag>
              <Tag>Provider：{String(indexStatus.embedding?.provider || '-')}</Tag>
              <Tag>模型：{String(indexStatus.embedding?.model || '-')}</Tag>
              <Tag>维度：{String(indexStatus.embedding?.dimension || indexStatus.redis.embedding_dim || '-')}</Tag>
              <Tag color="blue">总 chunk：{indexStatus.total_chunks}</Tag>
              <Tag color="green">已向量化：{indexStatus.indexed_chunks}</Tag>
              <Tag color="orange">待向量化：{indexStatus.pending_chunks}</Tag>
              <Tag color={indexStatus.failed_chunks > 0 ? 'red' : 'default'}>失败：{indexStatus.failed_chunks}</Tag>
            </Space>
            {indexStatus.dimension_notice && (
              <Alert
                className="block-gap"
                type="warning"
                showIcon
                message="Embedding 维度变更提示"
                description={indexStatus.dimension_notice}
              />
            )}
            {embeddingHealth && (
              <Alert
                className="block-gap"
                type={embeddingHealth.ok ? 'success' : 'error'}
                showIcon
                message={embeddingHealth.ok ? 'Embedding 连通性正常' : 'Embedding 连通性失败'}
                description={formatEmbeddingHealth(embeddingHealth)}
              />
            )}
          </>
        ) : (
          <Typography.Text type="secondary">暂无索引状态</Typography.Text>
        )}
      </Card>

      {loading ? (
        <Loading tip="正在加载文档和 chunk" />
      ) : (
        <Card className="block-gap" title="文档列表">
          <Table rowKey="id" columns={columns} dataSource={rows} pagination={{ pageSize: 8 }} />
        </Card>
      )}

      <Card className="block-gap" title={selectedDocumentId ? `文档 ${selectedDocumentId} 的 chunks` : 'Chunk 展示'}>
        <ChunkList chunks={selectedChunks} />
      </Card>
    </div>
  )
}
