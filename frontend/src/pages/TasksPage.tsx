import { Button, Card, Form, Input, Modal, Select, Space, Table, Tag, Typography, message } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useEffect, useMemo, useState } from 'react'
import {
  bulkCreateTasks,
  createTask,
  listTasks,
  organizeTasks,
  splitTask,
  updateTask,
  archiveTask,
} from '../api/tasks'
import type {
  TaskAiSuggestion,
  TaskItem,
  TaskItemCreate,
  TaskItemStatus,
  TaskListParams,
  TaskPriority,
} from '../api/tasks'
import { EmptyState } from '../components/EmptyState'
import { ErrorMessage } from '../components/ErrorMessage'
import { Loading } from '../components/Loading'
import { TaskForm } from '../components/TaskForm'
import { TaskStatusBadge } from '../components/TaskStatusBadge'

const PRIORITY_LABEL: Record<TaskPriority, string> = {
  low: '低',
  medium: '中',
  high: '高',
  urgent: '紧急',
}

interface TaskFilterValues {
  status?: TaskItemStatus
  category?: string
  subject?: string
  priority?: TaskPriority
  deadline_before?: string
}

function asObject(value: TaskAiSuggestion['suggestion_content']): Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value) ? value : { text: value }
}

function buildSubtasks(suggestion: TaskAiSuggestion): TaskItemCreate[] {
  const content = asObject(suggestion.suggestion_content)
  const subtasks = Array.isArray(content.subtasks) ? content.subtasks : []
  return subtasks
    .filter((item): item is Record<string, unknown> => typeof item === 'object' && item !== null)
    .map((item) => ({
      title: String(item.title || 'AI 拆分子任务'),
      description: String(item.description || item.reason || ''),
      category: String(item.category || 'AI 拆分'),
      subject: typeof item.subject === 'string' ? item.subject : null,
      project: typeof item.project === 'string' ? item.project : null,
      priority: ['low', 'medium', 'high', 'urgent'].includes(String(item.priority)) ? (item.priority as TaskPriority) : 'medium',
      difficulty: ['easy', 'normal', 'hard', 'very_hard'].includes(String(item.difficulty)) ? (item.difficulty as TaskItemCreate['difficulty']) : 'normal',
      estimated_minutes: Number(item.estimated_minutes) || 45,
      status: 'backlog',
      parent_task_id: suggestion.task_id || null,
      is_splittable: true,
      is_ai_generated: true,
      source_type: 'ai_split',
      source_ref: { suggestion_id: suggestion.id, reason: item.reason },
    }))
}

export default function TasksPage() {
  const [filterForm] = Form.useForm<TaskFilterValues>()
  const [tasks, setTasks] = useState<TaskItem[]>([])
  const [suggestions, setSuggestions] = useState<TaskAiSuggestion[]>([])
  const [editingTask, setEditingTask] = useState<TaskItem | null>(null)
  const [filters, setFilters] = useState<TaskListParams>({})
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [organizing, setOrganizing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function refresh(nextFilters: TaskListParams = filters) {
    setLoading(true)
    setError(null)
    try {
      setTasks(await listTasks(nextFilters))
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载任务池失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void refresh({})
  }, [])

  const stats = useMemo(() => {
    const active = tasks.filter((task) => !['completed', 'archived', 'skipped'].includes(task.status)).length
    const urgent = tasks.filter((task) => task.priority === 'urgent' || task.priority === 'high').length
    const minutes = tasks.reduce((sum, task) => sum + (task.estimated_minutes || 0), 0)
    const splittable = tasks.filter((task) => task.is_splittable && (task.estimated_minutes || 0) >= 120).length
    return { active, urgent, minutes, splittable }
  }, [tasks])

  async function handleCreate(payload: TaskItemCreate) {
    setSubmitting(true)
    setError(null)
    try {
      await createTask({ ...payload, source_type: 'manual' })
      message.success('任务已加入任务池')
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : '创建任务失败')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleUpdate(payload: TaskItemCreate) {
    if (!editingTask) return
    setSubmitting(true)
    try {
      await updateTask(editingTask.id, payload)
      setEditingTask(null)
      message.success('任务已更新')
      await refresh()
    } catch (err) {
      message.error(err instanceof Error ? err.message : '更新任务失败')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleFilter(values: TaskFilterValues) {
    const nextFilters: TaskListParams = {
      status: values.status,
      category: values.category?.trim() || undefined,
      subject: values.subject?.trim() || undefined,
      priority: values.priority,
      deadline_before: values.deadline_before || undefined,
    }
    setFilters(nextFilters)
    await refresh(nextFilters)
  }

  async function handleResetFilters() {
    filterForm.resetFields()
    setFilters({})
    await refresh({})
  }

  async function handleSplit(taskId: number) {
    try {
      const result = await splitTask(taskId)
      setSuggestions((current) => [...result.suggestions, ...current])
      message.success(result.message)
    } catch (err) {
      message.error(err instanceof Error ? err.message : '生成拆分建议失败')
    }
  }

  async function handleArchive(taskId: number) {
    try {
      await archiveTask(taskId)
      message.success('任务已归档')
      await refresh()
    } catch (err) {
      message.error(err instanceof Error ? err.message : '归档任务失败')
    }
  }

  async function handleStatus(task: TaskItem, status: TaskItemStatus) {
    try {
      await updateTask(task.id, { status })
      message.success('任务状态已更新')
      await refresh()
    } catch (err) {
      message.error(err instanceof Error ? err.message : '更新任务状态失败')
    }
  }

  async function handleOrganize() {
    setOrganizing(true)
    try {
      const result = await organizeTasks({ limit: 50 })
      setSuggestions((current) => [...result.suggestions, ...current])
      message.success(result.message)
    } catch (err) {
      message.error(err instanceof Error ? err.message : 'AI 整理失败')
    } finally {
      setOrganizing(false)
    }
  }

  async function addSubtasks(suggestion: TaskAiSuggestion) {
    const subtasks = buildSubtasks(suggestion)
    if (subtasks.length === 0) {
      message.warning('该建议没有可加入的子任务')
      return
    }
    try {
      await bulkCreateTasks(subtasks)
      message.success(`已加入 ${subtasks.length} 个子任务`)
      await refresh()
    } catch (err) {
      message.error(err instanceof Error ? err.message : '加入子任务失败')
    }
  }

  const columns: ColumnsType<TaskItem> = [
    {
      title: '任务',
      dataIndex: 'title',
      render: (value: string, record) => (
        <div>
          <Typography.Text strong>{value}</Typography.Text>
          {record.description && <div className="muted-text">{record.description}</div>}
        </div>
      ),
    },
    { title: '分类', dataIndex: 'category', width: 110, render: (value?: string | null) => value || '-' },
    { title: '学科 / 项目', width: 160, render: (_, record) => record.subject || record.project || '-' },
    {
      title: '优先级',
      dataIndex: 'priority',
      width: 90,
      render: (value: TaskPriority) => <Tag color={value === 'urgent' ? 'volcano' : value === 'high' ? 'red' : 'blue'}>{PRIORITY_LABEL[value]}</Tag>,
    },
    { title: '难度', dataIndex: 'difficulty', width: 90, render: (value?: string | null) => value || '-' },
    { title: '预计', dataIndex: 'estimated_minutes', width: 90, render: (value: number) => `${value} 分钟` },
    { title: '截止日期', dataIndex: 'deadline', width: 130, render: (value?: string | null) => value || '-' },
    { title: '状态', dataIndex: 'status', width: 100, render: (status: TaskItemStatus) => <TaskStatusBadge status={status} /> },
    { title: '来源', dataIndex: 'source_type', width: 130 },
    {
      title: '操作',
      width: 280,
      render: (_, record) => (
        <Space wrap>
          <Button size="small" onClick={() => setEditingTask(record)}>编辑</Button>
          <Button size="small" onClick={() => handleSplit(record.id)}>AI 拆分</Button>
          <Button size="small" onClick={() => handleStatus(record, 'in_progress')}>进行中</Button>
          <Button size="small" onClick={() => handleStatus(record, 'completed')}>完成</Button>
          <Button size="small" onClick={() => handleStatus(record, 'pending')}>待办</Button>
          <Button size="small" danger onClick={() => handleArchive(record.id)}>归档</Button>
        </Space>
      ),
    },
  ]

  return (
    <div className="page">
      <div className="page-title-row">
        <div>
          <Typography.Title level={2}>任务池</Typography.Title>
          <Typography.Text type="secondary">先维护任务池，再由 AI 辅助整理和生成今日任务建议。</Typography.Text>
        </div>
        <Space>
          <Button onClick={() => refresh()} loading={loading}>刷新</Button>
          <Button type="primary" onClick={handleOrganize} loading={organizing}>AI 整理任务池</Button>
        </Space>
      </div>
      <ErrorMessage message={error} />

      <div className="stats-grid">
        <Card><Typography.Text type="secondary">活跃任务</Typography.Text><Typography.Title level={3}>{stats.active}</Typography.Title></Card>
        <Card><Typography.Text type="secondary">高优先级</Typography.Text><Typography.Title level={3}>{stats.urgent}</Typography.Title></Card>
        <Card><Typography.Text type="secondary">预计总时长</Typography.Text><Typography.Title level={3}>{stats.minutes} 分钟</Typography.Title></Card>
        <Card><Typography.Text type="secondary">建议拆分</Typography.Text><Typography.Title level={3}>{stats.splittable}</Typography.Title></Card>
      </div>

      <Card title="创建任务">
        <TaskForm loading={submitting} submitText="加入任务池" onSubmit={handleCreate} />
      </Card>

      <Card className="block-gap" title="筛选任务">
        <Form form={filterForm} layout="inline" onFinish={handleFilter}>
          <Form.Item name="status">
            <Select
              allowClear
              placeholder="状态"
              style={{ width: 140 }}
              options={[
                { value: 'backlog', label: '待整理' },
                { value: 'pending', label: '待完成' },
                { value: 'in_progress', label: '进行中' },
                { value: 'completed', label: '已完成' },
                { value: 'delayed', label: '已延期' },
                { value: 'skipped', label: '已跳过' },
                { value: 'archived', label: '已归档' },
              ]}
            />
          </Form.Item>
          <Form.Item name="priority">
            <Select
              allowClear
              placeholder="优先级"
              style={{ width: 140 }}
              options={[
                { value: 'low', label: '低' },
                { value: 'medium', label: '中' },
                { value: 'high', label: '高' },
                { value: 'urgent', label: '紧急' },
              ]}
            />
          </Form.Item>
          <Form.Item name="category">
            <Input placeholder="分类" />
          </Form.Item>
          <Form.Item name="subject">
            <Input placeholder="学科" />
          </Form.Item>
          <Form.Item name="deadline_before">
            <Input type="date" />
          </Form.Item>
          <Space>
            <Button type="primary" htmlType="submit">筛选</Button>
            <Button onClick={handleResetFilters}>重置</Button>
          </Space>
        </Form>
      </Card>

      <Card className="block-gap" title="任务列表">
        {loading ? (
          <Loading tip="正在加载任务池" />
        ) : tasks.length === 0 ? (
          <EmptyState description="任务池暂无任务。先创建任务，AI 才能根据优先级、截止日期和可用时间生成今日建议。" />
        ) : (
          <Table rowKey="id" columns={columns} dataSource={tasks} pagination={{ pageSize: 8 }} scroll={{ x: 1120 }} />
        )}
      </Card>

      <Card className="block-gap" title="AI 建议">
        {suggestions.length === 0 ? (
          <EmptyState description="暂无建议。可以点击“AI 整理任务池”，或对某个大任务生成拆分建议。" />
        ) : (
          <div className="suggestion-grid">
            {suggestions.map((item) => {
              const content = asObject(item.suggestion_content)
              const subtasks = buildSubtasks(item)
              return (
                <Card key={item.id} size="small" className="suggestion-card">
                  <Space wrap>
                    <Tag color="purple">{item.suggestion_type}</Tag>
                    {item.task_id && <Tag>task {item.task_id}</Tag>}
                  </Space>
                  {typeof content.summary === 'string' && <Typography.Paragraph>{content.summary}</Typography.Paragraph>}
                  <pre className="json-block compact">{JSON.stringify(item.suggestion_content, null, 2)}</pre>
                  {subtasks.length > 0 && (
                    <Button size="small" type="primary" onClick={() => addSubtasks(item)}>
                      将 {subtasks.length} 个子任务加入任务池
                    </Button>
                  )}
                </Card>
              )
            })}
          </div>
        )}
      </Card>

      <Modal
        title="编辑任务"
        open={Boolean(editingTask)}
        onCancel={() => setEditingTask(null)}
        footer={null}
        width={760}
        destroyOnHidden
      >
        <TaskForm initialTask={editingTask} loading={submitting} submitText="保存修改" onSubmit={handleUpdate} />
      </Modal>
    </div>
  )
}
