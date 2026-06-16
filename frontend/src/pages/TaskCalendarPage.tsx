import {
  Button,
  Card,
  Divider,
  Form,
  Input,
  InputNumber,
  Modal,
  Popconfirm,
  Progress,
  Select,
  Space,
  Tag,
  Typography,
  message,
} from 'antd'
import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  completeTask,
  createTask,
  deleteTask,
  getTaskMonthSummary,
  listTasks,
  optimizeTask,
  postponeTask,
  startTask,
  supplementTasks,
  updateTask,
} from '../api/taskCalendar'
import type { CalendarDaySummary, TaskItem, TaskPriority, TaskSourceType, TaskSuggestion } from '../api/taskCalendar'
import { EditableNumber, EditableSelect, EditableText } from '../components/EditableFields'
import { EmptyState } from '../components/EmptyState'
import { ErrorMessage } from '../components/ErrorMessage'
import { Loading } from '../components/Loading'
import { TaskStatusBadge } from '../components/TaskStatusBadge'
import { useCurrentGoal } from '../hooks/useCurrentGoal'

const TIMER_STORAGE_KEY = 'learning_growth_active_task_timer'

const CATEGORY_OPTIONS = ['阅读', '练习', '项目', '写作', '复盘', '实验', '其他'].map((value) => ({ value, label: value }))
const PRIORITY_OPTIONS: Array<{ value: TaskPriority; label: string }> = [
  { value: 'low', label: '低' },
  { value: 'medium', label: '中' },
  { value: 'high', label: '高' },
  { value: 'urgent', label: '紧急' },
]
const PRIORITY_LABELS: Record<TaskPriority, string> = {
  low: '低',
  medium: '中',
  high: '高',
  urgent: '紧急',
}
const SOURCE_LABELS: Partial<Record<TaskSourceType, string>> = {
  manual: '手动',
  ai_optimized: 'AI 优化',
  ai_supplement: 'AI 补充',
  imported: '导入',
  planner: '系统',
}

interface TaskFormValues {
  content: string
  category: string
  priority: TaskPriority
  estimated_minutes: number
}

interface SupplementFormValues {
  available_minutes: number
  max_new_tasks: number
}

interface ActiveTimer {
  taskId: number
  content: string
  category?: string | null
  startedAt: string
}

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
  const days = Array.from({ length: last.getDate() }, (_, index) => new Date(year, month, index + 1))
  const prefix = Array.from({ length: first.getDay() }, (_, index) => new Date(year, month, index - first.getDay() + 1))
  const suffixCount = (7 - ((prefix.length + days.length) % 7)) % 7
  const suffix = Array.from({ length: suffixCount }, (_, index) => new Date(year, month + 1, index + 1))
  return [...prefix, ...days, ...suffix]
}

function readStoredTimer(): ActiveTimer | null {
  const raw = localStorage.getItem(TIMER_STORAGE_KEY)
  if (!raw) return null
  try {
    const parsed = JSON.parse(raw) as ActiveTimer
    if (!parsed.taskId || !parsed.startedAt) return null
    return parsed
  } catch {
    localStorage.removeItem(TIMER_STORAGE_KEY)
    return null
  }
}

function formatDuration(seconds: number) {
  const safe = Math.max(0, Math.floor(seconds))
  const hours = Math.floor(safe / 3600)
  const minutes = Math.floor((safe % 3600) / 60)
  const rest = safe % 60
  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(rest).padStart(2, '0')}`
}

function priorityColor(priority?: string | null) {
  if (priority === 'urgent') return 'volcano'
  if (priority === 'high') return 'red'
  if (priority === 'medium') return 'blue'
  return 'default'
}

function computeStats(tasks: TaskItem[]) {
  const visible = tasks.filter((task) => task.status !== 'archived' && task.status !== 'cancelled')
  const completed = visible.filter((task) => task.status === 'completed')
  const estimated = visible.reduce((sum, task) => sum + (task.estimated_minutes || 0), 0)
  const actual = completed.reduce((sum, task) => sum + (task.actual_minutes || 0), 0)
  return {
    total: visible.length,
    completed: completed.length,
    unfinished: visible.length - completed.length,
    estimated,
    actual,
    completionRate: visible.length ? Math.round((completed.length / visible.length) * 100) : 0,
  }
}

export default function TaskCalendarPage() {
  const todayKey = toDateKey(new Date())
  const [taskForm] = Form.useForm<TaskFormValues>()
  const [supplementForm] = Form.useForm<SupplementFormValues>()
  const { currentGoal, currentGoalId } = useCurrentGoal()
  const [monthCursor, setMonthCursor] = useState(() => new Date())
  const [selectedDate, setSelectedDate] = useState(todayKey)
  const [monthSummary, setMonthSummary] = useState<CalendarDaySummary[]>([])
  const [tasks, setTasks] = useState<TaskItem[]>([])
  const [loadingMonth, setLoadingMonth] = useState(false)
  const [loadingTasks, setLoadingTasks] = useState(false)
  const [taskModalOpen, setTaskModalOpen] = useState(false)
  const [taskSourceType, setTaskSourceType] = useState<TaskSourceType>('manual')
  const [savingTask, setSavingTask] = useState(false)
  const [optimizing, setOptimizing] = useState(false)
  const [optimizeSuggestion, setOptimizeSuggestion] = useState<Awaited<ReturnType<typeof optimizeTask>> | null>(null)
  const [originalDraft, setOriginalDraft] = useState<TaskFormValues | null>(null)
  const [supplementOpen, setSupplementOpen] = useState(false)
  const [supplementing, setSupplementing] = useState(false)
  const [supplementSuggestions, setSupplementSuggestions] = useState<TaskSuggestion[]>([])
  const [activeTimer, setActiveTimer] = useState<ActiveTimer | null>(() => readStoredTimer())
  const [timerTick, setTimerTick] = useState(() => Date.now())
  const [error, setError] = useState<string | null>(null)

  const days = useMemo(() => monthDays(monthCursor), [monthCursor])
  const summariesByDate = useMemo(() => Object.fromEntries(monthSummary.map((item) => [item.date, item])), [monthSummary])
  const stats = useMemo(() => computeStats(tasks), [tasks])
  const activeElapsedSeconds = activeTimer ? Math.max(Math.floor((timerTick - Date.parse(activeTimer.startedAt)) / 1000), 0) : 0

  async function loadMonth(cursor = monthCursor) {
    if (!currentGoalId) {
      setMonthSummary([])
      return
    }
    setLoadingMonth(true)
    setError(null)
    try {
      const result = await getTaskMonthSummary(cursor.getFullYear(), cursor.getMonth() + 1, currentGoalId)
      setMonthSummary(result.days)
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载月历统计失败')
    } finally {
      setLoadingMonth(false)
    }
  }

  async function loadTasks(dateKey = selectedDate) {
    if (!currentGoalId) {
      setTasks([])
      return
    }
    setLoadingTasks(true)
    try {
      setTasks(await listTasks({ goal_id: currentGoalId, date: dateKey }))
    } catch (err) {
      message.error(err instanceof Error ? err.message : '加载日期任务失败')
    } finally {
      setLoadingTasks(false)
    }
  }

  async function refresh(dateKey = selectedDate) {
    await Promise.all([loadTasks(dateKey), loadMonth(monthCursor)])
  }

  useEffect(() => {
    void loadMonth(monthCursor)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [monthCursor, currentGoalId])

  useEffect(() => {
    void loadTasks(selectedDate)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedDate, currentGoalId])

  useEffect(() => {
    if (activeTimer) {
      localStorage.setItem(TIMER_STORAGE_KEY, JSON.stringify(activeTimer))
    } else {
      localStorage.removeItem(TIMER_STORAGE_KEY)
    }
  }, [activeTimer])

  useEffect(() => {
    if (!activeTimer) return
    setTimerTick(Date.now())
    const timer = window.setInterval(() => setTimerTick(Date.now()), 1000)
    return () => window.clearInterval(timer)
  }, [activeTimer])

  useEffect(() => {
    if (!activeTimer) return
    const current = tasks.find((task) => task.id === activeTimer.taskId)
    if (current && ['completed', 'archived', 'cancelled', 'delayed'].includes(current.status)) {
      setActiveTimer(null)
    }
  }, [activeTimer, tasks])

  function shiftMonth(offset: number) {
    setMonthCursor((current) => new Date(current.getFullYear(), current.getMonth() + offset, 1))
  }

  function openCreateTask(sourceType: TaskSourceType = 'manual', suggestion?: TaskSuggestion) {
    setTaskSourceType(sourceType)
    setOptimizeSuggestion(null)
    setOriginalDraft(null)
    taskForm.setFieldsValue({
      content: suggestion?.content || '',
      category: suggestion?.category || '其他',
      priority: suggestion?.priority || 'medium',
      estimated_minutes: suggestion?.estimated_minutes || 60,
    })
    setTaskModalOpen(true)
  }

  async function saveTask(values: TaskFormValues) {
    if (!currentGoalId) {
      message.warning('请先选择当前目标')
      return
    }
    setSavingTask(true)
    try {
      await createTask({
        content: values.content.trim(),
        category: values.category || '其他',
        priority: values.priority,
        estimated_minutes: values.estimated_minutes,
        planned_date: selectedDate,
        goal_id: currentGoalId,
        domain: currentGoal?.domain || null,
        status: 'pending',
        source_type: taskSourceType,
        ai_reason: optimizeSuggestion?.reason || null,
      })
      message.success('任务已添加到选中日期')
      setTaskModalOpen(false)
      taskForm.resetFields()
      await refresh()
    } catch (err) {
      message.error(err instanceof Error ? err.message : '保存任务失败')
    } finally {
      setSavingTask(false)
    }
  }

  async function runOptimize() {
    const values = await taskForm.validateFields()
    setOptimizing(true)
    setOriginalDraft(values)
    try {
      setOptimizeSuggestion(await optimizeTask({
        raw_content: values.content,
        date: selectedDate,
        category: values.category,
        estimated_minutes: values.estimated_minutes,
        priority: values.priority,
      }))
    } catch (err) {
      message.error(err instanceof Error ? err.message : 'AI 优化失败')
    } finally {
      setOptimizing(false)
    }
  }

  function applyOptimizeSuggestion() {
    if (!optimizeSuggestion) return
    taskForm.setFieldsValue({
      content: optimizeSuggestion.suggested_content,
      category: optimizeSuggestion.suggested_category || taskForm.getFieldValue('category') || '其他',
      estimated_minutes: optimizeSuggestion.suggested_estimated_minutes,
      priority: optimizeSuggestion.suggested_priority,
    })
    setTaskSourceType('ai_optimized')
  }

  function revertOptimizeSuggestion() {
    if (!originalDraft) return
    taskForm.setFieldsValue(originalDraft)
    setTaskSourceType('manual')
  }

  async function updateInlineTask(task: TaskItem, payload: Partial<TaskItem>) {
    await updateTask(task.id, payload)
    await loadTasks(selectedDate)
    void loadMonth(monthCursor)
  }

  async function handleStart(task: TaskItem) {
    if (activeTimer && activeTimer.taskId !== task.id) {
      message.warning('当前已有任务正在计时，请先完成当前任务')
      return
    }
    try {
      const session = await startTask(task.id)
      setActiveTimer({
        taskId: task.id,
        content: task.content,
        category: task.category,
        startedAt: session.started_at || new Date().toISOString(),
      })
      message.success('已开始计时')
      await refresh()
    } catch (err) {
      message.error(err instanceof Error ? err.message : '开始计时失败')
    }
  }

  async function handleComplete(task: TaskItem) {
    const isActive = activeTimer?.taskId === task.id
    const actualMinutes = isActive ? Math.max(0, Math.ceil(activeElapsedSeconds / 60)) : undefined
    try {
      const completed = await completeTask(task.id, actualMinutes === undefined ? {} : { actual_minutes: actualMinutes })
      if (isActive) setActiveTimer(null)
      message.success(`任务已完成，实际用时 ${completed.actual_minutes ?? 0} 分钟`)
      await refresh()
    } catch (err) {
      message.error(err instanceof Error ? err.message : '完成任务失败')
    }
  }

  async function handlePostpone(task: TaskItem) {
    if (activeTimer?.taskId === task.id) {
      message.warning('当前任务正在计时，请先完成后再延期')
      return
    }
    try {
      await postponeTask(task.id)
      message.success('任务已延期到下一天')
      await refresh()
    } catch (err) {
      message.error(err instanceof Error ? err.message : '延期任务失败')
    }
  }

  async function handleDelete(task: TaskItem) {
    try {
      await deleteTask(task.id)
      if (activeTimer?.taskId === task.id) setActiveTimer(null)
      message.success('任务已删除')
      await refresh()
    } catch (err) {
      message.error(err instanceof Error ? err.message : '删除任务失败')
    }
  }

  async function runSupplement(values: SupplementFormValues) {
    if (!currentGoalId) {
      message.warning('请先选择当前目标')
      return
    }
    setSupplementing(true)
    setSupplementSuggestions([])
    try {
      const result = await supplementTasks({
        planned_date: selectedDate,
        goal_id: currentGoalId,
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

  async function acceptSuggestion(suggestion: TaskSuggestion) {
    if (!currentGoalId) return
    try {
      await createTask({
        content: suggestion.content,
        category: suggestion.category || '其他',
        task_type: suggestion.task_type || null,
        priority: suggestion.priority,
        estimated_minutes: suggestion.estimated_minutes,
        planned_date: selectedDate,
        goal_id: currentGoalId,
        domain: currentGoal?.domain || null,
        source_type: 'ai_supplement',
        ai_reason: suggestion.reason,
        context_json: {
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
    <div className="page study-calendar-page">
      <div className="page-title-row study-calendar-title-row">
        <div>
          <Typography.Title level={2}>学习日历</Typography.Title>
          <Typography.Text type="secondary">
            当前目标：{currentGoal?.title || '未选择目标'}。按日期管理任务，AI 只提供优化和补充建议。
          </Typography.Text>
        </div>
        <Space wrap align="center">
          <div className={`timer-panel ${activeTimer ? 'active' : ''}`}>
            {activeTimer ? (
              <>
                <span className="timer-label">正在计时：{activeTimer.category || '未分类'} - {activeTimer.content}</span>
                <span className="timer-value">{formatDuration(activeElapsedSeconds)}</span>
              </>
            ) : (
              <>
                <span className="timer-label">暂无任务计时</span>
                <span className="timer-value muted">00:00:00</span>
              </>
            )}
          </div>
          <Button onClick={() => refresh()} loading={loadingMonth || loadingTasks}>刷新</Button>
          <Button type="primary" className="soft-primary-button" onClick={() => openCreateTask()} disabled={!currentGoalId}>+ 新增</Button>
          <Button onClick={() => setSupplementOpen(true)} disabled={!currentGoalId}>AI 补充任务</Button>
        </Space>
      </div>
      <ErrorMessage message={error} />

      {!currentGoalId ? (
        <Card>
          <EmptyState
            title="请先选择或创建目标"
            description="任务日历需要绑定到目标，便于统计和复盘。"
            extra={<Link to="/goals">前往目标管理</Link>}
          />
        </Card>
      ) : (
        <div className="two-column-layout calendar-layout">
          <Card
            className="calendar-shell"
            title={<Typography.Title level={3} className="calendar-month-title">{monthCursor.getFullYear()} 年 {monthCursor.getMonth() + 1} 月</Typography.Title>}
            extra={
              <Space className="calendar-nav">
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
            className="selected-day-panel"
            title={
              <div className="selected-day-title">
                <span className="selected-day-icon" aria-hidden="true" />
                <Typography.Title level={3}>{selectedDate} 任务</Typography.Title>
              </div>
            }
            extra={<Button size="small" type="primary" className="soft-primary-button" onClick={() => openCreateTask()}>+ 新增</Button>}
          >
            {loadingTasks ? (
              <Loading tip="正在加载日期任务" />
            ) : (
              <Space direction="vertical" className="full-width" size="middle">
                <div className="panel-stats-grid">
                  <div className="panel-stat-card">
                    <span>任务数</span>
                    <strong>{stats.total}</strong>
                  </div>
                  <div className="panel-stat-card">
                    <span>已完成</span>
                    <strong>{stats.completed}</strong>
                  </div>
                  <div className="panel-stat-card">
                    <span>预计时长</span>
                    <strong>{stats.estimated} <small>分钟</small></strong>
                  </div>
                  <div className="panel-stat-card completion-card">
                    <span>完成率</span>
                    <Progress type="circle" percent={stats.completionRate} size={64} strokeColor="#12b886" />
                  </div>
                </div>
                <div className="actual-time-bar">今日已记录实际用时：<strong>{stats.actual} 分钟</strong></div>
                {tasks.filter((item) => item.status !== 'archived').length === 0 ? (
                  <EmptyState
                    title="该日期暂无任务"
                    description="可以手动新增任务，也可以让 AI 根据近期完成情况给出少量补充建议。"
                    extra={
                      <Space>
                        <Button type="primary" onClick={() => openCreateTask()}>新增任务</Button>
                        <Button onClick={() => setSupplementOpen(true)}>AI 补充任务</Button>
                      </Space>
                    }
                  />
                ) : (
                  <div className="task-list">
                    {tasks.filter((task) => task.status !== 'archived').map((task) => (
                      <Card key={task.id} size="small" className={`task-card study-task-card ${activeTimer?.taskId === task.id ? 'timing' : ''}`}>
                        <div className="task-header">
                          <div className="task-main">
                            <div className="task-title-line">
                              <EditableText
                                value={task.content}
                                className="task-title-editable"
                                onSave={(value) => updateInlineTask(task, { content: value })}
                              />
                              <TaskStatusBadge status={task.status} />
                            </div>
                            <Space wrap className="task-tags">
                              <EditableSelect
                                value={task.category || '其他'}
                                options={CATEGORY_OPTIONS}
                                onSave={(value) => updateInlineTask(task, { category: value })}
                              >
                                <Tag color="processing">{task.category || '其他'}</Tag>
                              </EditableSelect>
                              <EditableSelect
                                value={task.priority}
                                options={PRIORITY_OPTIONS}
                                onSave={(value) => updateInlineTask(task, { priority: value as TaskPriority })}
                              >
                                <Tag color={priorityColor(task.priority)}>{PRIORITY_LABELS[task.priority]}</Tag>
                              </EditableSelect>
                              {task.source_type !== 'manual' && (
                                <Tag color={task.source_type === 'ai_optimized' ? 'purple' : 'cyan'}>
                                  {SOURCE_LABELS[task.source_type] || task.source_type}
                                </Tag>
                              )}
                            </Space>
                            {task.ai_reason && (
                              <Typography.Paragraph className="task-detail-editable">{task.ai_reason}</Typography.Paragraph>
                            )}
                          </div>
                          <div className="task-time-box">
                            <EditableNumber
                              value={task.estimated_minutes}
                              suffix="分钟"
                              onSave={(value) => updateInlineTask(task, { estimated_minutes: value })}
                            >
                              <Tag>预计 {task.estimated_minutes} 分钟</Tag>
                            </EditableNumber>
                            {task.actual_minutes !== null && task.actual_minutes !== undefined && (
                              <Tag color="green">实际 {task.actual_minutes} 分钟</Tag>
                            )}
                          </div>
                        </div>
                        <Divider className="compact-divider" />
                        <Space wrap className="task-actions">
                          <Button size="small" onClick={() => handleStart(task)} disabled={task.status === 'completed'}>
                            {activeTimer?.taskId === task.id ? '计时中' : '开始'}
                          </Button>
                          <Button size="small" type="primary" onClick={() => handleComplete(task)} disabled={task.status === 'completed'}>
                            {task.status === 'completed' ? '已完成' : '完成'}
                          </Button>
                          <Popconfirm title="确认延期该任务？" onConfirm={() => handlePostpone(task)}>
                            <Button size="small" disabled={task.status === 'completed'}>延期</Button>
                          </Popconfirm>
                          <Popconfirm title="确认删除该任务？" onConfirm={() => handleDelete(task)}>
                            <Button size="small" danger>删除</Button>
                          </Popconfirm>
                        </Space>
                      </Card>
                    ))}
                  </div>
                )}
              </Space>
            )}
          </Card>
        </div>
      )}

      <Modal
        title="添加任务"
        open={taskModalOpen}
        onCancel={() => setTaskModalOpen(false)}
        footer={null}
        width={720}
        destroyOnHidden
      >
        <Form
          form={taskForm}
          layout="vertical"
          onFinish={saveTask}
          initialValues={{ category: '其他', priority: 'medium', estimated_minutes: 60 }}
        >
          <Form.Item label="任务内容" name="content" rules={[{ required: true, message: '请输入任务内容' }]}>
            <Input.TextArea rows={3} placeholder="例如：完成第 3 章核心概念整理，并输出 10 条可复用笔记" />
          </Form.Item>
          <div className="form-grid">
            <Form.Item label="分类" name="category" rules={[{ required: true, message: '请选择分类' }]}>
              <Select options={CATEGORY_OPTIONS} />
            </Form.Item>
            <Form.Item label="优先级" name="priority" rules={[{ required: true }]}>
              <Select options={PRIORITY_OPTIONS} />
            </Form.Item>
            <Form.Item label="预计耗时" name="estimated_minutes" rules={[{ required: true, type: 'number', min: 5 }]}>
              <InputNumber min={5} max={10000} addonAfter="分钟" style={{ width: '100%' }} />
            </Form.Item>
          </div>
          {optimizeSuggestion && (
            <Card size="small" className="block-gap" title="AI 优化建议">
              <div className="compare-grid">
                <Card size="small" title="原任务">
                  <Typography.Paragraph>{originalDraft?.content}</Typography.Paragraph>
                  <Space wrap>
                    <Tag>{originalDraft?.category}</Tag>
                    <Tag>{originalDraft?.estimated_minutes} 分钟</Tag>
                    <Tag>{originalDraft?.priority && PRIORITY_LABELS[originalDraft.priority]}</Tag>
                  </Space>
                </Card>
                <Card size="small" title="优化建议">
                  <Typography.Paragraph>{optimizeSuggestion.suggested_content}</Typography.Paragraph>
                  <Space wrap>
                    <Tag>{optimizeSuggestion.suggested_category || '其他'}</Tag>
                    <Tag>{optimizeSuggestion.suggested_estimated_minutes} 分钟</Tag>
                    <Tag>{PRIORITY_LABELS[optimizeSuggestion.suggested_priority]}</Tag>
                  </Space>
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
          initialValues={{ available_minutes: Math.max(stats.estimated, 120), max_new_tasks: 3 }}
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
          <EmptyState description="暂无补充建议。AI 会基于当前目标、当天任务和近期完成情况生成少量候选任务。" />
        ) : (
          <div className="suggestion-grid">
            {supplementSuggestions.map((suggestion) => (
              <Card key={`${suggestion.content}-${suggestion.estimated_minutes}`} size="small" className="suggestion-card">
                <Space wrap>
                  <Typography.Text strong>{suggestion.content}</Typography.Text>
                  <Tag color="cyan">AI 补充</Tag>
                  <Tag>{suggestion.estimated_minutes} 分钟</Tag>
                  <Tag>{PRIORITY_LABELS[suggestion.priority]}</Tag>
                  <Tag>{suggestion.category || '其他'}</Tag>
                </Space>
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
    </div>
  )
}
