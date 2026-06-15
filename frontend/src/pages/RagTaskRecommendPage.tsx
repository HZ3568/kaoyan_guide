import { Button, Card, Checkbox, Form, Input, InputNumber, Space, Tag, Typography, message } from 'antd'
import { useMemo, useState } from 'react'
import { askRag } from '../api/rag'
import type { RagAskResponse } from '../api/rag'
import { bulkCreateTasks, recommendTasksFromRag } from '../api/tasks'
import type { TaskAiSuggestion, TaskItemCreate, TaskPriority } from '../api/tasks'
import { ErrorMessage } from '../components/ErrorMessage'
import { SourceList } from '../components/SourceList'

interface RecommendFormValues {
  query: string
  top_k: number
  max_tasks: number
}

function asObject(value: TaskAiSuggestion['suggestion_content']): Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value) ? value : { text: value }
}

function suggestionToTask(suggestion: TaskAiSuggestion): TaskItemCreate | null {
  const content = asObject(suggestion.suggestion_content)
  if (!content.title) return null
  const priority = String(content.priority || 'medium')
  return {
    title: String(content.title),
    description: String(content.description || content.reason || ''),
    category: String(content.category || '考研复习'),
    subject: typeof content.subject === 'string' ? content.subject : null,
    project: null,
    priority: ['low', 'medium', 'high', 'urgent'].includes(priority) ? (priority as TaskPriority) : 'medium',
    difficulty: 'normal',
    estimated_minutes: Number(content.estimated_minutes) || 60,
    status: 'backlog',
    is_splittable: true,
    is_ai_generated: true,
    source_type: 'rag_recommendation',
    source_ref: {
      suggestion_id: suggestion.id,
      source_ref: content.source_ref,
      rag_sources: content.rag_sources,
      reason: content.reason,
    },
  }
}

export default function RagTaskRecommendPage() {
  const [form] = Form.useForm<RecommendFormValues>()
  const [answer, setAnswer] = useState<RagAskResponse | null>(null)
  const [suggestions, setSuggestions] = useState<TaskAiSuggestion[]>([])
  const [selectedSuggestionIds, setSelectedSuggestionIds] = useState<number[]>([])
  const [loading, setLoading] = useState(false)
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const candidates = useMemo(() => (
    suggestions
      .map((suggestion) => ({ suggestion, task: suggestionToTask(suggestion) }))
      .filter((item): item is { suggestion: TaskAiSuggestion; task: TaskItemCreate } => Boolean(item.task))
  ), [suggestions])

  async function handleRecommend(values: RecommendFormValues) {
    setLoading(true)
    setError(null)
    setAnswer(null)
    setSuggestions([])
    setSelectedSuggestionIds([])
    const query = values.query.trim()
    try {
      const [ragResult, recommendResult] = await Promise.allSettled([
        askRag({ question: query, top_k: values.top_k }),
        recommendTasksFromRag({ query, top_k: values.top_k, max_tasks: values.max_tasks }),
      ])
      if (ragResult.status === 'fulfilled') {
        setAnswer(ragResult.value)
      } else {
        setError(ragResult.reason instanceof Error ? ragResult.reason.message : 'RAG 问答失败')
      }
      if (recommendResult.status === 'fulfilled') {
        setSuggestions(recommendResult.value.suggestions)
        setSelectedSuggestionIds(recommendResult.value.suggestions.map((item) => item.id))
        message.success(recommendResult.value.message)
      } else {
        setError(recommendResult.reason instanceof Error ? recommendResult.reason.message : '生成候选任务失败')
      }
    } finally {
      setLoading(false)
    }
  }

  async function addSelectedTasks() {
    const selectedTasks = candidates
      .filter((item) => selectedSuggestionIds.includes(item.suggestion.id))
      .map((item) => item.task)
    if (selectedTasks.length === 0) {
      message.warning('请选择要加入任务池的候选任务')
      return
    }
    setCreating(true)
    try {
      await bulkCreateTasks(selectedTasks)
      message.success(`已加入 ${selectedTasks.length} 个候选任务`)
      setSelectedSuggestionIds([])
    } catch (err) {
      message.error(err instanceof Error ? err.message : '加入任务池失败')
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="page">
      <div className="page-title-row">
        <div>
          <Typography.Title level={2}>RAG 推荐任务</Typography.Title>
          <Typography.Text type="secondary">从知识库依据中提炼候选复习任务，用户确认后再进入任务池。</Typography.Text>
        </div>
      </div>
      <ErrorMessage message={error} />

      <Card title="输入目标或问题">
        <Form form={form} layout="vertical" onFinish={handleRecommend} initialValues={{ top_k: 5, max_tasks: 5 }}>
          <Form.Item label="问题" name="query" rules={[{ required: true, message: '请输入目标或复习问题' }]}>
            <Input.TextArea rows={4} placeholder="例如：根据数据结构考试内容推荐本周任务" />
          </Form.Item>
          <div className="form-grid compact-form-grid">
            <Form.Item label="TopK" name="top_k" rules={[{ required: true, type: 'number', min: 1, max: 10 }]}>
              <InputNumber min={1} max={10} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item label="候选任务数" name="max_tasks" rules={[{ required: true, type: 'number', min: 1, max: 10 }]}>
              <InputNumber min={1} max={10} style={{ width: '100%' }} />
            </Form.Item>
          </div>
          <Button type="primary" htmlType="submit" loading={loading}>生成候选任务</Button>
        </Form>
      </Card>

      {answer && (
        <Card className="block-gap" title="RAG 回答与依据">
          <Typography.Paragraph className="answer-text">{answer.answer}</Typography.Paragraph>
          <SourceList sources={answer.sources} emptyText="当前回答没有引用来源" />
        </Card>
      )}

      <Card
        className="block-gap"
        title="候选任务"
        extra={<Button type="primary" disabled={candidates.length === 0} loading={creating} onClick={addSelectedTasks}>加入任务池</Button>}
      >
        {candidates.length === 0 ? (
          <Typography.Text type="secondary">暂无候选任务。请先输入问题并生成。</Typography.Text>
        ) : (
          <div className="suggestion-grid">
            {candidates.map(({ suggestion, task }) => {
              const checked = selectedSuggestionIds.includes(suggestion.id)
              return (
                <Card key={suggestion.id} size="small" className="suggestion-card">
                  <Space align="start">
                    <Checkbox
                      checked={checked}
                      onChange={(event) => {
                        setSelectedSuggestionIds((current) => (
                          event.target.checked
                            ? [...current, suggestion.id]
                            : current.filter((id) => id !== suggestion.id)
                        ))
                      }}
                    />
                    <div>
                      <Space wrap>
                        <Typography.Text strong>{task.title}</Typography.Text>
                        <Tag color="blue">{task.priority}</Tag>
                        <Tag>{task.estimated_minutes} 分钟</Tag>
                        {task.subject && <Tag>{task.subject}</Tag>}
                      </Space>
                      <Typography.Paragraph className="compact-paragraph">{task.description}</Typography.Paragraph>
                      <pre className="json-block compact">{JSON.stringify(suggestion.suggestion_content, null, 2)}</pre>
                    </div>
                  </Space>
                </Card>
              )
            })}
          </div>
        )}
      </Card>
    </div>
  )
}
