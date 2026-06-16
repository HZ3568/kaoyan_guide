import { Alert, Button, Card, Collapse, Form, Input, InputNumber, Select, Space, Typography, message } from 'antd'
import type { KeyboardEvent } from 'react'
import { useEffect, useMemo, useState } from 'react'
import { listKnowledgeBases } from '../api/knowledgeBases'
import type { KnowledgeBase } from '../api/knowledgeBases'
import { askRag } from '../api/rag'
import type { RagAskResponse } from '../api/rag'
import { ErrorMessage } from '../components/ErrorMessage'
import { SourceList } from '../components/SourceList'
import { useCurrentGoal } from '../hooks/useCurrentGoal'

interface AskFormValues {
  question: string
  top_k: number
  knowledge_base_id?: number
}

export default function RagChatPage() {
  const [form] = Form.useForm<AskFormValues>()
  const { currentGoal, currentGoalId } = useCurrentGoal()
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([])
  const [selectedKbId, setSelectedKbId] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [loadingKb, setLoadingKb] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [records, setRecords] = useState<Array<{ id: number; question: string; response: RagAskResponse }>>([])

  const availableKbs = useMemo(
    () => knowledgeBases.filter((kb) => !currentGoalId || !kb.goal_id || kb.goal_id === currentGoalId),
    [knowledgeBases, currentGoalId],
  )

  async function loadKbs() {
    setLoadingKb(true)
    try {
      const items = await listKnowledgeBases()
      setKnowledgeBases(items)
      const scoped = items.filter((kb) => !currentGoalId || !kb.goal_id || kb.goal_id === currentGoalId)
      const nextKbId = selectedKbId && scoped.some((kb) => kb.id === selectedKbId) ? selectedKbId : scoped[0]?.id ?? null
      setSelectedKbId(nextKbId)
      form.setFieldValue('knowledge_base_id', nextKbId ?? undefined)
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载知识库失败')
    } finally {
      setLoadingKb(false)
    }
  }

  useEffect(() => {
    void loadKbs()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentGoalId])

  async function ask(values: AskFormValues) {
    const question = values.question.trim()
    const kbId = values.knowledge_base_id || selectedKbId
    if (!kbId) {
      message.warning('请先选择知识库')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const response = await askRag({
        question,
        top_k: values.top_k || 5,
        goal_id: currentGoalId ?? undefined,
        knowledge_base_id: kbId,
      })
      setRecords((current) => [{ id: Date.now(), question, response }, ...current])
      form.setFieldValue('question', '')
    } catch (err) {
      setError(err instanceof Error ? err.message : '问答失败')
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      form.submit()
    }
  }

  return (
    <div className="page rag-chat-page">
      <div className="page-title-row">
        <div>
          <Typography.Title level={2}>知识库 RAG 问答</Typography.Title>
          <Typography.Text type="secondary">
            当前目标：{currentGoal?.title || '未选择目标'}。回答只依据选中知识库的检索结果。
          </Typography.Text>
        </div>
      </div>
      <ErrorMessage message={error} />

      <Card>
        <Form form={form} layout="vertical" onFinish={ask} initialValues={{ top_k: 5 }}>
          <div className="form-grid compact-form-grid">
            <Form.Item
              label="知识库"
              name="knowledge_base_id"
              rules={[{ required: true, message: '请选择知识库' }]}
            >
              <Select
                loading={loadingKb}
                placeholder="选择知识库"
                value={selectedKbId ?? undefined}
                options={availableKbs.map((kb) => ({ value: kb.id, label: kb.name }))}
                onChange={(value) => {
                  setSelectedKbId(value)
                  form.setFieldValue('knowledge_base_id', value)
                }}
              />
            </Form.Item>
            <Form.Item label="TopK" name="top_k" rules={[{ required: true, type: 'number', min: 1, max: 20 }]}>
              <InputNumber min={1} max={20} style={{ width: '100%' }} />
            </Form.Item>
          </div>
          <Form.Item
            label="问题"
            name="question"
            rules={[{ required: true, message: '请输入问题' }]}
          >
            <Input.TextArea
              rows={5}
              onKeyDown={handleKeyDown}
              placeholder="例如：这份资料建议我优先实践哪些步骤？"
            />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} disabled={!selectedKbId}>
            {loading ? '正在检索知识库并生成回答' : '提问'}
          </Button>
        </Form>
      </Card>

      <div className="chat-records">
        {records.length === 0 ? (
          <Card className="block-gap">
            <Typography.Text type="secondary">
              暂无问答记录。输入问题后会在这里展示回答、来源和检索调试信息。
            </Typography.Text>
          </Card>
        ) : (
          records.map(({ id, question, response }) => (
            <Card key={id} className="block-gap" title={question}>
              {(!response.hit_source || response.sources.length === 0) && (
                <Alert
                  className="block-gap"
                  type="warning"
                  showIcon
                  message="当前知识库没有找到可靠依据"
                />
              )}
              <Typography.Paragraph className="answer-text">{response.answer}</Typography.Paragraph>
              <Space wrap>
                <Typography.Text type="secondary">命中来源：{response.hit_source ? '是' : '否'}</Typography.Text>
                {response.model_provider && (
                  <Typography.Text type="secondary">
                    模型：{response.model_provider}/{response.model_name}
                  </Typography.Text>
                )}
                {response.log_id && <Typography.Text type="secondary">日志 ID：{response.log_id}</Typography.Text>}
              </Space>
              <Card className="block-gap" size="small" title="引用来源">
                <SourceList sources={response.sources} emptyText="当前回答没有引用来源" />
              </Card>
              <Collapse
                className="block-gap"
                items={[
                  {
                    key: 'debug',
                    label: 'retrieval_debug',
                    children: <pre className="json-block">{JSON.stringify(response.retrieval_debug, null, 2)}</pre>,
                  },
                  {
                    key: 'chunks',
                    label: '检索到的 chunks',
                    children: <SourceList sources={response.sources} emptyText="暂无 chunks" />,
                  },
                ]}
              />
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
