import {
  Button,
  Card,
  Divider,
  Form,
  Input,
  InputNumber,
  Modal,
  Progress,
  Select,
  Space,
  Statistic,
  Tag,
  Typography,
  message,
} from 'antd'
import { useEffect, useMemo, useState } from 'react'
import {
  acceptCalendarTaskSuggestion,
  getCalendarMonthSummary,
  getCalendarTasksByDate,
  supplementCalendarTasks,
} from '../api/calendarTasks'
import type { CalendarDaySummary, CalendarTaskSuggestion } from '../api/calendarTasks'
import {
  submitDailyPlanTaskFeedback,
  updateDailyPlanTaskStatus,
} from '../api/dailyPlans'
import type { DailyPlan, DailyPlanTask, DailyPlanTaskStatus, TaskFeedbackCreate } from '../api/dailyPlans'
import {
  createTask,
  deleteTask,
  optimizeTask,
  updateTask,
} from '../api/tasks'
import type { TaskDifficulty, TaskItemCreate, TaskItemStatus, TaskPriority, TaskSourceType } from '../api/tasks'
import { EmptyState } from '../components/EmptyState'
import { ErrorMessage } from '../components/ErrorMessage'
import { FeedbackModal } from '../components/FeedbackModal'
import { Loading } from '../components/Loading'
import { TaskStatusBadge } from '../components/TaskStatusBadge'

function toDateKey(date: Date) {
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${date.getFullYear()}-${month}-${day}`
}

function monthDays(monthCursor: Date) {
  const year = monthCursor.getFullYear()
  const month = monthCursor.getMonth()
  const first = new Date(year, month, 1)
  const last = new Date(year, month + 1, 0)
  const days: Date[] = []
  for (let day = 1; day <= last.getDate(); day += 1) {
    days.push(new Date(year, month, day))
  }
  const startPadding = first.getDay()
  const prefix = Array.from({ length: startPadding }, (_, index) => new Date(year, month, index - startPadding + 1))
  const suffixCount = (7 - ((prefix.length + days.length) % 7)) % 7
  const suffix = Array.from({ length: suffixCount }, (_, index) => new Date(year, month + 1, index + 1))
  return [...prefix, ...days, ...suffix]
}

interface TaskFormValues {
  title: string
  description?: string
  category?: string
  subject?: string
  project?: string
  priority: TaskPriority
  difficulty?: TaskDifficulty
  estimated_minutes: number
  deadline?: string
  status: TaskItemStatus
}

interface SupplementFormValues {
  available_minutes: number
  max_new_tasks: number
}

const DEFAULT_TASK_VALUES: TaskFormValues = {
  title: '',
  description: '',
  category: '',
  subject: '',
  project: '',
  priority: 'medium',
  difficulty: 'normal',
  estimated_minutes: 60,
  deadline: '',
  status: 'pending',
}

const STATUS_ACTIONS: Array<{ label: string; status: DailyPlanTaskStatus }> = [
  { label: '开始', status: 'in_progress' },
  { label: '完成', status: 'completed' },
  { label: '延期', status: 'delayed' },
  { label: '跳过', status: 'skipped' },
  { label: '恢复待完成', status: 'pending' },
]

function normalizeTaskPayload(values: TaskFormValues, date: string, sourceType: TaskSourceType): TaskItemCreate {
  return {
    title: values.title.trim(),
    description: values.description?.trim() || null,
    category: values.category?.trim() || null,
    subject: values.subject?.trim() || null,
    project: values.project?.trim() || null,
    priority: values.priority,
    difficulty: values.difficulty || 'normal',
    estimated_minutes: Number(values.estimated_minutes),
    deadline: values.deadline || null,
    status: values.status || 'pending',
    date,
    is_splittable: true,
    is_ai_generated: sourceType !== 'manual',
    source_type: sourceType,
  }
}

function planStats(plan: DailyPlan | null) {
  const tasks = plan?.tasks.filter((item) => item.status !== 'removed') || []
  const completed = tasks.filter((item) => item.status === 'completed')
  const totalMinutes = tasks.reduce((sum, item) => sum + (item.planned_minutes || item.task?.estimated_minutes || 0), 0)
  const completedMinutes = completed.reduce((sum, item) => sum + (item.planned_minutes || item.task?.estimated_minutes || 0), 0)
  return {
    total: tasks.length,
    completed: completed.length,
    unfinished: tasks.length - completed.length,
    totalMinutes,
    completedMinutes,
    completionRate: tasks.length ? Math.round((completed.length / tasks.length) * 100) : 0,
  }
}

export default function TaskCalendarPage() {
  const todayKey = toDateKey(new Date())
  const [taskForm] = Form.useForm<TaskFormValues>()
  const [supplementForm] = Form.useForm<SupplementFormValues>()
  const [monthCursor, setMonthCursor] = useState(() => new Date())
  const [selectedDate, setSelectedDate] = useState(todayKey)
  const [monthSummary, setMonthSummary] = useState<CalendarDaySummary[]>([])
  const [selectedPlan, setSelectedPlan] = useState<DailyPlan | null>(null)
  const [loadingMonth, setLoadingMonth] = useState(false)
  const [loadingSelected, setLoadingSelected] = useState(false)
  const [taskModalOpen, setTaskModalOpen] = useState(false)
  const [editingPlanTask, setEditingPlanTask] = useState<DailyPlanTask | null>(null)
  const [taskSourceType, setTaskSourceType] = useState<TaskSourceType>('manual')
  const [savingTask, setSavingTask] = useState(false)
  const [optimizing, setOptimizing] = useState(false)
  const [optimizeSuggestion, setOptimizeSuggestion] = useState<Awaited<ReturnType<typeof optimizeTask>> | null>(null)
  const [originalDraft, setOriginalDraft] = useState<TaskFormValues | null>(null)
  const [supplementOpen, setSupplementOpen] = useState(false)
  const [supplementing, setSupplementing] = useState(false)
  const [supplementSuggestions, setSupplementSuggestions] = useState<CalendarTaskSuggestion[]>([])
  const [feedbackTask, setFeedbackTask] = useState<DailyPlanTask | null>(null)
  const [submittingFeedback, setSubmittingFeedback] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const days = useMemo(() => monthDays(monthCursor), [monthCursor])
  const summariesByDate = useMemo(() => Object.fromEntries(monthSummary.map((item) => [item.date, item])), [monthSummary])
  const stats = useMemo(() => planStats(selectedPlan), [selectedPlan])

  async function loadMonth(cursor = monthCursor) {
    setLoadingMonth(true)
    setError(null)
    try {
      const result = await getCalendarMonthSummary(cursor.getFullYear(), cursor.getMonth() + 1)
      setMonthSummary(result.days)
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载月历统计失败')
    } finally {
      setLoadingMonth(false)
    }
  }

  async function loadSelected(dateKey = selectedDate) {
    setLoadingSelected(true)
    try {
      setSelectedPlan(await getCalendarTasksByDate(dateKey))
    } catch (err) {
      message.error(err instanceof Error ? err.message : '加载日期任务失败')
    } finally {
      setLoadingSelected(false)
    }
  }

  async function refresh(dateKey = selectedDate) {
    await Promise.all([loadSelected(dateKey), loadMonth(monthCursor)])
  }

  useEffect(() => {
    void loadMonth(monthCursor)
  }, [monthCursor])

  useEffect(() => {
    void loadSelected(selectedDate)
  }, [selectedDate])

  function shiftMonth(offset: number) {
    setMonthCursor((current) => new Date(current.getFullYear(), current.getMonth() + offset, 1))
  }

  function openCreateTask(sourceType: TaskSourceType = 'manual', suggestion?: CalendarTaskSuggestion) {
    setEditingPlanTask(null)
    setTaskSourceType(sourceType)
    setOptimizeSuggestion(null)
    setOriginalDraft(null)
    taskForm.setFieldsValue({
      ...DEFAULT_TASK_VALUES,
      title: suggestion?.title || '',
      description: suggestion?.description || '',
      category: suggestion?.category || '',
      subject: suggestion?.subject || '',
      priority: suggestion?.priority || 'medium',
      estimated_minutes: suggestion?.estimated_minutes || 60,
      status: 'pending',
    })
    setTaskModalOpen(true)
  }

  function openEditTask(planTask: DailyPlanTask) {
    const task = planTask.task
    if (!task) return
    setEditingPlanTask(planTask)
    setTaskSourceType(task.source_type)
    setOptimizeSuggestion(null)
    setOriginalDraft(null)
    taskForm.setFieldsValue({
      title: task.title,
      description: task.description || '',
      category: task.category || '',
      subject: task.subject || '',
      project: task.project || '',
      priority: task.priority,
      difficulty: task.difficulty || 'normal',
      estimated_minutes: task.estimated_minutes,
      deadline: task.deadline || '',
      status: task.status,
    })
    setTaskModalOpen(true)
  }

  async function saveTask(values: TaskFormValues) {
    setSavingTask(true)
    setError(null)
    try {
      const payload = normalizeTaskPayload(values, selectedDate, taskSourceType)
      if (editingPlanTask?.task) {
        await updateTask(editingPlanTask.task.id, payload)
        message.success('任务已更新')
      } else {
        await createTask(payload)
        message.success('任务已添加到选中日期')
      }
      setTaskModalOpen(false)
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存任务失败')
    } finally {
      setSavingTask(false)
    }
  }

  async function runOptimize() {
    const values = await taskForm.validateFields()
    setOptimizing(true)
    setOriginalDraft(values)
    try {
      const result = await optimizeTask({
        raw_title: values.title,
        raw_description: values.description || '',
        date: selectedDate,
        subject: values.subject || null,
        estimated_minutes: values.estimated_minutes,
        priority: values.priority,
      })
      setOptimizeSuggestion(result)
    } catch (err) {
      message.error(err instanceof Error ? err.message : 'AI 优化失败')
    } finally {
      setOptimizing(false)
    }
  }

  function applyOptimizeSuggestion() {
    if (!optimizeSuggestion) return
    taskForm.setFieldsValue({
      title: optimizeSuggestion.suggested_title,
      description: optimizeSuggestion.suggested_description || '',
      subject: optimizeSuggestion.suggested_subject || '',
      estimated_minutes: optimizeSuggestion.suggested_estimated_minutes,
      priority: optimizeSuggestion.suggested_priority,
    })
    setTaskSourceType('ai_optimized')
  }

  function revertOptimizeSuggestion() {
    if (!originalDraft) return
    taskForm.setFieldsValue(originalDraft)
    setTaskSourceType(editingPlanTask?.task?.source_type || 'manual')
  }

  async function updatePlanTaskStatus(planTask: DailyPlanTask, status: DailyPlanTaskStatus) {
    if (!selectedPlan) return
    try {
      await updateDailyPlanTaskStatus(selectedPlan.id, planTask.id, status)
      await refresh()
    } catch (err) {
      message.error(err instanceof Error ? err.message : '更新任务状态失败')
    }
  }

  async function removeTask(planTask: DailyPlanTask) {
    if (!planTask.task) return
    try {
      await deleteTask(planTask.task.id)
      message.success('任务已删除')
      await refresh()
    } catch (err) {
      message.error(err instanceof Error ? err.message : '删除任务失败')
    }
  }

  async function submitFeedback(payload: TaskFeedbackCreate) {
    if (!selectedPlan || !feedbackTask) return
    setSubmittingFeedback(true)
    try {
      await submitDailyPlanTaskFeedback(selectedPlan.id, feedbackTask.id, payload)
      message.success('反馈已提交')
      setFeedbackTask(null)
      await refresh()
    } catch (err) {
      message.error(err instanceof Error ? err.message : '提交反馈失败')
    } finally {
      setSubmittingFeedback(false)
    }
  }

  async function runSupplement(values: SupplementFormValues) {
    setSupplementing(true)
    setSupplementSuggestions([])
    try {
      const result = await supplementCalendarTasks({
        date: selectedDate,
        available_minutes: values.available_minutes,
        max_new_tasks: values.max_new_tasks,
      })
      setSupplementSuggestions(result.suggestions)
      message.success(result.message)
    } catch (err) {
      message.error(err instanceof Error ? err.message : 'AI 补充任务失败')
    } finally {
      setSupplementing(false)
    }
  }

  async function acceptSuggestion(suggestion: CalendarTaskSuggestion) {
    try {
      await acceptCalendarTaskSuggestion({
        title: suggestion.title,
        description: suggestion.description || suggestion.reason,
        category: suggestion.category || null,
        subject: suggestion.subject || null,
        priority: suggestion.priority,
        estimated_minutes: suggestion.estimated_minutes,
        status: 'pending',
        date: selectedDate,
        is_ai_generated: true,
        source_type: 'ai_supplement',
        source_ref: {
          reason: suggestion.reason,
          confidence: suggestion.confidence,
          risk_level: suggestion.risk_level,
        },
      })
      message.success('已采用 AI 补充任务')
      setSupplementSuggestions((current) => current.filter((item) => item !== suggestion))
      await refresh()
    } catch (err) {
      message.error(err instanceof Error ? err.message : '采用建议失败')
    }
  }

  return (
    <div className="page">
      <div className="page-title-row">
        <div>
          <Typography.Title level={2}>学习日历</Typography.Title>
          <Typography.Text type="secondary">RAG 只负责院校知识库问答；学习任务在日历中按日期维护，AI 只提供优化和补充建议。</Typography.Text>
        </div>
        <Space wrap>
          <Button onClick={() => refresh()} loading={loadingMonth || loadingSelected}>刷新</Button>
          <Button type="primary" onClick={() => openCreateTask()}>新增任务</Button>
          <Button onClick={() => setSupplementOpen(true)}>AI 补充任务</Button>
        </Space>
      </div>
      <ErrorMessage message={error} />

      <div className="two-column-layout calendar-layout">
        <Card
          title={`${monthCursor.getFullYear()} 年 ${monthCursor.getMonth() + 1} 月`}
          extra={
            <Space>
              {loadingMonth && <Typography.Text type="secondary">同步中</Typography.Text>}
              <Button onClick={() => shiftMonth(-1)}>上个月</Button>
              <Button onClick={() => setMonthCursor(new Date())}>本月</Button>
              <Button onClick={() => shiftMonth(1)}>下个月</Button>
            </Space>
          }
        >
          <div className="calendar-weekdays">
            {['日', '一', '二', '三', '四', '五', '六'].map((item) => <span key={item}>{item}</span>)}
          </div>
          <div className="calendar-grid">
            {days.map((date) => {
              const key = toDateKey(date)
              const isCurrentMonth = date.getMonth() === monthCursor.getMonth()
              const summary = summariesByDate[key]
              const isSelected = key === selectedDate
              const isToday = key === todayKey
              return (
                <button
                  key={key}
                  type="button"
                  className={`calendar-cell ${isCurrentMonth ? '' : 'muted'} ${isSelected ? 'selected' : ''} ${isToday ? 'today' : ''} ${summary?.has_delayed ? 'has-delayed' : ''}`}
                  onClick={() => setSelectedDate(key)}
                >
                  <span className="calendar-date">{date.getDate()}</span>
                  {summary?.task_count ? (
                    <>
                      <span className="calendar-count">
                        {summary.completed_count}/{summary.task_count} 完成 · {summary.estimated_minutes} 分钟
                      </span>
                      <Progress percent={summary.completion_rate} size="small" showInfo={false} />
                      {summary.has_delayed && <Tag className="calendar-tag" color="orange">有延期</Tag>}
                      {(summary.titles || []).map((title) => (
                        <span key={title} className="calendar-task-title">{title}</span>
                      ))}
                    </>
                  ) : (
                    <span className="calendar-count muted-text">暂无任务</span>
                  )}
                </button>
              )
            })}
          </div>
        </Card>

        <Card
          title={`${selectedDate} 任务`}
          extra={<Button size="small" type="primary" onClick={() => openCreateTask()}>新增</Button>}
        >
          {loadingSelected ? (
            <Loading tip="正在加载日期任务" />
          ) : (
            <Space direction="vertical" className="full-width" size="middle">
              <div className="stats-grid compact-stats">
                <Card size="small"><Statistic title="任务数" value={stats.total} /></Card>
                <Card size="small"><Statistic title="已完成" value={stats.completed} /></Card>
                <Card size="small"><Statistic title="预计时长" value={stats.totalMinutes} suffix="分钟" /></Card>
                <Card size="small">
                  <Typography.Text type="secondary">完成率</Typography.Text>
                  <Progress percent={stats.completionRate} size="small" />
                </Card>
              </div>
              {!selectedPlan || selectedPlan.tasks.length === 0 ? (
                <EmptyState
                  title="该日期暂无任务"
                  description="可以手动新增任务，也可以让 AI 根据历史完成情况给出少量补充建议。"
                  extra={
                    <Space>
                      <Button type="primary" onClick={() => openCreateTask()}>新增任务</Button>
                      <Button onClick={() => setSupplementOpen(true)}>AI 补充任务</Button>
                    </Space>
                  }
                />
              ) : (
                <div className="task-list">
                  {selectedPlan.tasks.filter((item) => item.status !== 'removed').map((planTask) => (
                    <Card key={planTask.id} size="small" className="task-card">
                      <div className="task-header">
                        <div>
                          <Space wrap>
                            <Typography.Text strong>{planTask.task?.title || `任务 #${planTask.task_id}`}</Typography.Text>
                            <TaskStatusBadge status={planTask.status} />
                            {planTask.task?.category && <Tag>{planTask.task.category}</Tag>}
                            {planTask.task?.subject && <Tag>{planTask.task.subject}</Tag>}
                            {planTask.task?.priority && <Tag color={planTask.task.priority === 'urgent' ? 'volcano' : planTask.task.priority === 'high' ? 'red' : 'blue'}>{planTask.task.priority}</Tag>}
                            {planTask.task?.source_type === 'ai_optimized' && <Tag color="purple">AI 优化</Tag>}
                            {planTask.task?.source_type === 'ai_supplement' && <Tag color="cyan">AI 补充</Tag>}
                          </Space>
                          <Typography.Paragraph className="task-desc">
                            {planTask.task?.description || planTask.reason || '暂无说明'}
                          </Typography.Paragraph>
                          {planTask.reason && <Typography.Text type="secondary">{planTask.reason}</Typography.Text>}
                        </div>
                        <Typography.Text type="secondary">{planTask.planned_minutes || planTask.task?.estimated_minutes || 0} 分钟</Typography.Text>
                      </div>
                      <Divider className="compact-divider" />
                      <Space wrap>
                        <Button size="small" onClick={() => openEditTask(planTask)}>编辑</Button>
                        {STATUS_ACTIONS.map((item) => (
                          <Button
                            key={item.status}
                            size="small"
                            type={item.status === 'completed' ? 'primary' : 'default'}
                            disabled={planTask.status === item.status}
                            onClick={() => updatePlanTaskStatus(planTask, item.status)}
                          >
                            {item.label}
                          </Button>
                        ))}
                        <Button size="small" onClick={() => setFeedbackTask(planTask)}>反馈</Button>
                        <Button size="small" danger onClick={() => removeTask(planTask)}>删除</Button>
                      </Space>
                    </Card>
                  ))}
                </div>
              )}
            </Space>
          )}
        </Card>
      </div>

      <Modal
        title={editingPlanTask ? '编辑日期任务' : '新增日期任务'}
        open={taskModalOpen}
        onCancel={() => setTaskModalOpen(false)}
        footer={null}
        width={920}
        destroyOnHidden
      >
        <Form form={taskForm} layout="vertical" onFinish={saveTask} initialValues={DEFAULT_TASK_VALUES}>
          <div className="form-grid">
            <Form.Item label="标题" name="title" rules={[{ required: true, message: '请输入任务标题' }]}>
              <Input placeholder="例如：完成高数极限专题 20 道选择题" />
            </Form.Item>
            <Form.Item label="分类" name="category">
              <Input placeholder="项目 / 论文 / 考试 / 课程" />
            </Form.Item>
            <Form.Item label="学科" name="subject">
              <Input placeholder="数学 / 英语 / 专业课" />
            </Form.Item>
            <Form.Item label="项目" name="project">
              <Input placeholder="可选" />
            </Form.Item>
            <Form.Item label="优先级" name="priority" rules={[{ required: true }]}>
              <Select
                options={[
                  { value: 'low', label: '低' },
                  { value: 'medium', label: '中' },
                  { value: 'high', label: '高' },
                  { value: 'urgent', label: '紧急' },
                ]}
              />
            </Form.Item>
            <Form.Item label="难度" name="difficulty">
              <Select
                options={[
                  { value: 'easy', label: '简单' },
                  { value: 'normal', label: '适中' },
                  { value: 'hard', label: '偏难' },
                  { value: 'very_hard', label: '过难' },
                ]}
              />
            </Form.Item>
            <Form.Item label="预计耗时（分钟）" name="estimated_minutes" rules={[{ required: true, type: 'number', min: 5 }]}>
              <InputNumber min={5} max={10000} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item label="截止日期" name="deadline">
              <Input type="date" />
            </Form.Item>
            <Form.Item label="状态" name="status">
              <Select
                options={[
                  { value: 'pending', label: '待完成' },
                  { value: 'scheduled', label: '已安排' },
                  { value: 'in_progress', label: '进行中' },
                  { value: 'completed', label: '已完成' },
                  { value: 'delayed', label: '已延期' },
                  { value: 'skipped', label: '已跳过' },
                  { value: 'cancelled', label: '已取消' },
                ]}
              />
            </Form.Item>
          </div>
          <Form.Item label="描述" name="description">
            <Input.TextArea rows={3} maxLength={1000} placeholder="说明任务背景、期望产出或约束" />
          </Form.Item>

          {optimizeSuggestion && (
            <Card size="small" className="block-gap" title="AI 优化建议">
              <div className="compare-grid">
                <Card size="small" title="原任务">
                  <Typography.Text strong>{originalDraft?.title}</Typography.Text>
                  <Typography.Paragraph>{originalDraft?.description || '无描述'}</Typography.Paragraph>
                  <Tag>{originalDraft?.estimated_minutes} 分钟</Tag>
                  <Tag>{originalDraft?.priority}</Tag>
                </Card>
                <Card size="small" title="优化建议">
                  <Typography.Text strong>{optimizeSuggestion.suggested_title}</Typography.Text>
                  <Typography.Paragraph>{optimizeSuggestion.suggested_description}</Typography.Paragraph>
                  <Tag>{optimizeSuggestion.suggested_estimated_minutes} 分钟</Tag>
                  <Tag>{optimizeSuggestion.suggested_priority}</Tag>
                  <Typography.Paragraph type="secondary">{optimizeSuggestion.reason}</Typography.Paragraph>
                </Card>
              </div>
              {optimizeSuggestion.warnings.length > 0 && (
                <Typography.Paragraph type="warning">{optimizeSuggestion.warnings.join('；')}</Typography.Paragraph>
              )}
              <Space>
                <Button type="primary" onClick={applyOptimizeSuggestion}>采用优化结果</Button>
                <Button onClick={revertOptimizeSuggestion}>退回原任务</Button>
              </Space>
            </Card>
          )}

          <Space className="block-gap">
            <Button onClick={runOptimize} loading={optimizing}>AI 优化任务</Button>
            <Button type="primary" htmlType="submit" loading={savingTask}>保存任务</Button>
          </Space>
        </Form>
      </Modal>

      <Modal
        title={`${selectedDate} AI 补充任务`}
        open={supplementOpen}
        onCancel={() => setSupplementOpen(false)}
        footer={null}
        width={860}
        destroyOnHidden
      >
        <Form
          form={supplementForm}
          layout="inline"
          onFinish={runSupplement}
          initialValues={{ available_minutes: Math.max(stats.totalMinutes, 240), max_new_tasks: 3 }}
        >
          <Form.Item label="可用时间" name="available_minutes" rules={[{ required: true, type: 'number', min: 15 }]}>
            <InputNumber min={15} max={1440} addonAfter="分钟" />
          </Form.Item>
          <Form.Item label="最多建议" name="max_new_tasks" rules={[{ required: true, type: 'number', min: 1, max: 5 }]}>
            <InputNumber min={1} max={5} />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={supplementing}>生成补充建议</Button>
        </Form>
        <Divider />
        {supplementSuggestions.length === 0 ? (
          <EmptyState description="暂无补充建议。AI 会基于当天任务、近期完成情况和反馈生成少量候选任务。" />
        ) : (
          <div className="suggestion-grid">
            {supplementSuggestions.map((suggestion) => (
              <Card key={`${suggestion.title}-${suggestion.estimated_minutes}`} size="small" className="suggestion-card">
                <Space wrap>
                  <Typography.Text strong>{suggestion.title}</Typography.Text>
                  <Tag color="cyan">AI 补充</Tag>
                  <Tag>{suggestion.estimated_minutes} 分钟</Tag>
                  <Tag>{suggestion.priority}</Tag>
                  {suggestion.subject && <Tag>{suggestion.subject}</Tag>}
                </Space>
                <Typography.Paragraph className="compact-paragraph">{suggestion.description}</Typography.Paragraph>
                <Typography.Paragraph type="secondary">{suggestion.reason}</Typography.Paragraph>
                <Space>
                  <Button size="small" type="primary" onClick={() => acceptSuggestion(suggestion)}>采用</Button>
                  <Button size="small" onClick={() => openCreateTask('ai_supplement', suggestion)}>编辑后采用</Button>
                  <Button size="small" onClick={() => setSupplementSuggestions((current) => current.filter((item) => item !== suggestion))}>忽略</Button>
                </Space>
              </Card>
            ))}
          </div>
        )}
      </Modal>

      <FeedbackModal
        open={Boolean(feedbackTask)}
        submitting={submittingFeedback}
        onCancel={() => setFeedbackTask(null)}
        onSubmit={submitFeedback}
      />
    </div>
  )
}
