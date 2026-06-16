import { Alert, Button, Card, Form, Input, Modal, Popconfirm, Select, Space, Table, Tag, Typography, Upload, message } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useEffect, useMemo, useState } from 'react'
import {
  checkEmbeddingHealth,
  getVectorIndexStatus,
  indexChunks,
  listDocumentChunks,
  listDocuments,
  uploadDocument,
} from '../api/documents'
import type { DocumentChunk, DocumentRecord, EmbeddingHealthResponse, VectorIndexStatus } from '../api/documents'
import {
  createKnowledgeBase,
  deleteKnowledgeBase,
  listKnowledgeBases,
  updateKnowledgeBase,
} from '../api/knowledgeBases'
import type { KnowledgeBase, KnowledgeBasePayload } from '../api/knowledgeBases'
import { ChunkList } from '../components/ChunkList'
import { EmptyState } from '../components/EmptyState'
import { ErrorMessage } from '../components/ErrorMessage'
import { Loading } from '../components/Loading'
import { useCurrentGoal } from '../hooks/useCurrentGoal'

interface UploadValues {
  category?: string
  tags?: string
  description?: string
}

export default function KnowledgeBasePage() {
  const [kbForm] = Form.useForm<KnowledgeBasePayload>()
  const [uploadForm] = Form.useForm<UploadValues>()
  const { currentGoal, currentGoalId, activeGoals } = useCurrentGoal()
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([])
  const [selectedKbId, setSelectedKbId] = useState<number | null>(null)
  const [editingKb, setEditingKb] = useState<KnowledgeBase | null>(null)
  const [kbModalOpen, setKbModalOpen] = useState(false)
  const [documents, setDocuments] = useState<DocumentRecord[]>([])
  const [chunksByDocument, setChunksByDocument] = useState<Record<number, DocumentChunk[]>>({})
  const [selectedDocumentId, setSelectedDocumentId] = useState<number | null>(null)
  const [uploadFile, setUploadFile] = useState<File | null>(null)
  const [indexStatus, setIndexStatus] = useState<VectorIndexStatus | null>(null)
  const [embeddingHealth, setEmbeddingHealth] = useState<EmbeddingHealthResponse | null>(null)
  const [loadingKb, setLoadingKb] = useState(false)
  const [loadingDocs, setLoadingDocs] = useState(false)
  const [savingKb, setSavingKb] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [indexing, setIndexing] = useState(false)
  const [checkingEmbedding, setCheckingEmbedding] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const selectedKb = useMemo(
    () => knowledgeBases.find((item) => item.id === selectedKbId) || null,
    [knowledgeBases, selectedKbId],
  )

  async function refreshKnowledgeBases() {
    setLoadingKb(true)
    setError(null)
    try {
      const items = await listKnowledgeBases()
      const filtered = currentGoalId ? items.filter((kb) => !kb.goal_id || kb.goal_id === currentGoalId) : items
      setKnowledgeBases(filtered)
      setSelectedKbId((current) => {
        if (current && filtered.some((kb) => kb.id === current)) return current
        return filtered[0]?.id ?? null
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载知识库失败')
    } finally {
      setLoadingKb(false)
    }
  }

  async function refreshDocuments(kbId = selectedKbId) {
    if (!kbId) {
      setDocuments([])
      setChunksByDocument({})
      return
    }
    setLoadingDocs(true)
    setError(null)
    try {
      const docs = await listDocuments({ knowledge_base_id: kbId, goal_id: currentGoalId ?? undefined })
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
      setError(err instanceof Error ? err.message : '加载文档失败')
    } finally {
      setLoadingDocs(false)
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
    void refreshKnowledgeBases()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentGoalId])

  useEffect(() => {
    void refreshDocuments(selectedKbId)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedKbId])

  function openCreateKb() {
    setEditingKb(null)
    kbForm.setFieldsValue({
      name: '',
      description: '',
      domain: currentGoal?.domain || '',
      visibility: 'private',
      goal_id: currentGoalId,
    })
    setKbModalOpen(true)
  }

  function openEditKb(kb: KnowledgeBase) {
    setEditingKb(kb)
    kbForm.setFieldsValue({
      name: kb.name,
      description: kb.description || '',
      domain: kb.domain || '',
      visibility: kb.visibility,
      goal_id: kb.goal_id ?? currentGoalId,
    })
    setKbModalOpen(true)
  }

  async function saveKnowledgeBase(values: KnowledgeBasePayload) {
    setSavingKb(true)
    try {
      const payload = {
        ...values,
        goal_id: values.goal_id ?? currentGoalId,
        visibility: values.visibility || 'private',
      }
      const saved = editingKb
        ? await updateKnowledgeBase(editingKb.id, payload)
        : await createKnowledgeBase(payload)
      setSelectedKbId(saved.id)
      message.success(editingKb ? '知识库已更新' : '知识库已创建')
      setKbModalOpen(false)
      await refreshKnowledgeBases()
    } catch (err) {
      message.error(err instanceof Error ? err.message : '保存知识库失败')
    } finally {
      setSavingKb(false)
    }
  }

  async function removeKnowledgeBase(kb: KnowledgeBase) {
    try {
      await deleteKnowledgeBase(kb.id)
      if (selectedKbId === kb.id) setSelectedKbId(null)
      message.success('知识库已删除')
      await refreshKnowledgeBases()
    } catch (err) {
      message.error(err instanceof Error ? err.message : '删除知识库失败')
    }
  }

  async function handleUpload(values: UploadValues) {
    if (!selectedKb) {
      message.warning('请先选择知识库')
      return
    }
    if (!currentGoalId) {
      message.warning('请先选择当前目标')
      return
    }
    if (!uploadFile) {
      message.warning('请选择要上传的文件')
      return
    }
    setUploading(true)
    try {
      await uploadDocument(uploadFile, {
        knowledge_base_id: selectedKb.id,
        goal_id: currentGoalId,
        domain: selectedKb.domain || currentGoal?.domain || undefined,
        category: values.category,
        tags: values.tags,
        description: values.description,
      })
      message.success('上传并切片完成')
      uploadForm.resetFields()
      setUploadFile(null)
      await refreshDocuments(selectedKb.id)
    } catch (err) {
      setError(err instanceof Error ? err.message : '上传失败')
    } finally {
      setUploading(false)
    }
  }

  async function handleIndex(documentId?: number, forceReindex = false) {
    if (!selectedKb) {
      message.warning('请先选择知识库')
      return
    }
    setIndexing(true)
    setError(null)
    try {
      const result = await indexChunks({
        document_id: documentId,
        knowledge_base_id: selectedKb.id,
        goal_id: currentGoalId ?? undefined,
        force_reindex: forceReindex,
        limit: 1000,
      })
      if (result.failed > 0 || result.errors.length > 0) {
        setError([`向量化失败 ${result.failed} 个 chunk，成功 ${result.indexed} 个。`, ...result.errors].join('\n'))
      } else {
        message.success(`向量化完成：成功 ${result.indexed}，跳过 ${result.skipped}`)
      }
      await refreshDocuments(selectedKb.id)
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
        setError([result.message, ...(result.hints || []), result.error_body || ''].filter(Boolean).join('\n'))
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Embedding 连通性测试失败')
    } finally {
      setCheckingEmbedding(false)
    }
  }

  const rows = documents.map((doc) => {
    const chunks = chunksByDocument[doc.id] || []
    return {
      ...doc,
      vectorized_count: chunks.filter((chunk) => chunk.is_vectorized).length,
      chunk_count: chunks.length || doc.chunk_count,
    }
  })

  const columns: ColumnsType<(typeof rows)[number]> = [
    {
      title: '文档',
      dataIndex: 'title',
      render: (_, record) => (
        <div>
          <Typography.Text strong>{record.original_filename || record.filename}</Typography.Text>
          <div className="muted-text">{record.filename}</div>
        </div>
      ),
    },
    { title: '类型', dataIndex: 'file_type', width: 90 },
    { title: '分类', dataIndex: 'category', render: (value?: string | null) => value || '-' },
    {
      title: '状态',
      width: 160,
      render: (_, record) => (
        <Space wrap>
          <Tag>{record.parse_status}</Tag>
          <Tag color={record.embedding_status === 'indexed' ? 'green' : 'orange'}>{record.embedding_status}</Tag>
        </Space>
      ),
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
        <div>
          <Typography.Title level={2}>知识库管理</Typography.Title>
          <Typography.Text type="secondary">
            当前目标：{currentGoal?.title || '未选择目标'}。知识库用于限定 RAG 检索范围。
          </Typography.Text>
        </div>
        <Space wrap>
          <Button onClick={() => void refreshKnowledgeBases()} loading={loadingKb}>刷新</Button>
          <Button onClick={handleCheckEmbedding} loading={checkingEmbedding}>测试 Embedding</Button>
          <Button type="primary" onClick={openCreateKb}>新建知识库</Button>
        </Space>
      </div>
      <ErrorMessage message={error} />

      <div className="knowledge-layout">
        <Card className="kb-list-card" title="知识库">
          {loadingKb ? (
            <Loading tip="正在加载知识库" />
          ) : knowledgeBases.length === 0 ? (
            <EmptyState
              title="暂无知识库"
              description="先为当前目标创建一个知识库，再上传文档。"
              extra={<Button type="primary" onClick={openCreateKb}>创建知识库</Button>}
            />
          ) : (
            <Space direction="vertical" className="full-width">
              {knowledgeBases.map((kb) => (
                <button
                  key={kb.id}
                  type="button"
                  className={`kb-list-item ${selectedKbId === kb.id ? 'active' : ''}`}
                  onClick={() => setSelectedKbId(kb.id)}
                >
                  <span>
                    <strong>{kb.name}</strong>
                    <small>{kb.domain || '未设置领域'}</small>
                  </span>
                  <Space>
                    <Button size="small" onClick={(event) => { event.stopPropagation(); openEditKb(kb) }}>编辑</Button>
                    <Popconfirm title="确认删除知识库？" onConfirm={(event) => { event?.stopPropagation(); void removeKnowledgeBase(kb) }}>
                      <Button size="small" danger onClick={(event) => event.stopPropagation()}>删除</Button>
                    </Popconfirm>
                  </Space>
                </button>
              ))}
            </Space>
          )}
        </Card>

        <div className="kb-detail">
          <Card
            title={selectedKb ? selectedKb.name : '选择知识库'}
            extra={
              <Space wrap>
                <Button onClick={() => void refreshDocuments()} loading={loadingDocs}>刷新文档</Button>
                <Button type="primary" onClick={() => handleIndex()} loading={indexing} disabled={!selectedKb}>增量向量化</Button>
                <Button onClick={() => handleIndex(undefined, true)} loading={indexing} disabled={!selectedKb}>重建索引</Button>
              </Space>
            }
          >
            {!selectedKb ? (
              <EmptyState title="请选择知识库" description="从左侧选择一个知识库后查看文档。" />
            ) : (
              <>
                <Form form={uploadForm} layout="vertical" onFinish={handleUpload}>
                  <div className="form-grid compact-form-grid">
                    <Form.Item label="分类" name="category">
                      <Input placeholder="例如：论文、项目笔记、课程材料" />
                    </Form.Item>
                    <Form.Item label="标签" name="tags">
                      <Input placeholder="用逗号分隔" />
                    </Form.Item>
                    <Form.Item label="说明" name="description">
                      <Input />
                    </Form.Item>
                  </div>
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
              </>
            )}
          </Card>

          <Card className="block-gap" title="Redis Vector 索引状态">
            {indexStatus ? (
              <Space wrap>
                <Tag>索引：{String(indexStatus.redis.index_name || '-')}</Tag>
                <Tag>模型：{String(indexStatus.embedding?.model || '-')}</Tag>
                <Tag>维度：{String(indexStatus.embedding?.dimension || '-')}</Tag>
                <Tag color="blue">总 chunk：{indexStatus.total_chunks}</Tag>
                <Tag color="green">已向量化：{indexStatus.indexed_chunks}</Tag>
                <Tag color="orange">待向量化：{indexStatus.pending_chunks}</Tag>
                <Tag color={indexStatus.failed_chunks > 0 ? 'red' : 'default'}>失败：{indexStatus.failed_chunks}</Tag>
              </Space>
            ) : (
              <Typography.Text type="secondary">暂无索引状态</Typography.Text>
            )}
            {embeddingHealth && (
              <Alert
                className="block-gap"
                type={embeddingHealth.ok ? 'success' : 'error'}
                showIcon
                message={embeddingHealth.ok ? 'Embedding 连通性正常' : 'Embedding 连通性失败'}
                description={[embeddingHealth.message, ...(embeddingHealth.hints || [])].join('\n')}
              />
            )}
          </Card>

          <Card className="block-gap" title="文档列表">
            <Table
              rowKey="id"
              columns={columns}
              dataSource={rows}
              loading={loadingDocs}
              locale={{ emptyText: '当前知识库暂无文档' }}
              pagination={{ pageSize: 8 }}
            />
          </Card>

          <Card className="block-gap" title={selectedDocumentId ? `文档 ${selectedDocumentId} 的 chunks` : 'Chunk 展示'}>
            <ChunkList chunks={selectedChunks} />
          </Card>
        </div>
      </div>

      <Modal
        title={editingKb ? '编辑知识库' : '新建知识库'}
        open={kbModalOpen}
        onCancel={() => setKbModalOpen(false)}
        footer={null}
        destroyOnHidden
      >
        <Form form={kbForm} layout="vertical" onFinish={saveKnowledgeBase}>
          <Form.Item label="名称" name="name" rules={[{ required: true, message: '请输入知识库名称' }]}>
            <Input />
          </Form.Item>
          <Form.Item label="说明" name="description">
            <Input.TextArea rows={3} />
          </Form.Item>
          <Form.Item label="领域" name="domain">
            <Input placeholder="例如 AI 工程、写作、语言学习" />
          </Form.Item>
          <Form.Item label="绑定目标" name="goal_id">
            <Select
              allowClear
              options={activeGoals.map((goal) => ({ value: goal.id, label: goal.title }))}
            />
          </Form.Item>
          <Form.Item label="可见性" name="visibility">
            <Select
              options={[
                { value: 'private', label: '私有' },
                { value: 'shared', label: '共享' },
                { value: 'public', label: '公开' },
              ]}
            />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={savingKb}>保存</Button>
        </Form>
      </Modal>
    </div>
  )
}
