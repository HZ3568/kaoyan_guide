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
import {
  acceptCalendarTaskSuggestion,
  getCalendarMonthSummary,
  getCalendarTasksByDate,
  supplementCalendarTasks,
} from '../api/calendarTasks'
import type { CalendarDaySummary, CalendarTaskSuggestion } from '../api/calendarTasks'
import {
  completeDailyPlanTask,
  postponeDailyPlanTask,
  startDailyPlanTask,
} from '../api/dailyPlans'
import type { DailyPlan, DailyPlanTask } from '../api/dailyPlans'
import {
  createTask,
  deleteTask,
  optimizeTask,
  updateTask,
} from '../api/tasks'
import type { TaskDifficulty, TaskItemCreate, TaskPriority, TaskSourceType } from '../api/tasks'
import { EditableNumber, EditableSelect, EditableText } from '../components/EditableFields'
import { EmptyState } from '../components/EmptyState'
import { ErrorMessage } from '../components/ErrorMessage'
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

const TIMER_STORAGE_KEY = 'learning_growth_active_task_timer'
const CATEGORY_OPTIONS = ['阅读', '练习', '项目', '复盘', '写作', '其他'].map((value) => ({ value, label: value }))
const PRIORITY_OPTIONS: Array<{ value: TaskPriority; label: string }> = [
  { value: 'low', label: '低' },
  { value: 'medium', label: '中' },
  { value: 'high', label: '高' },
  { value: 'urgent', label: '紧急' },
]
const DIFFICULTY_OPTIONS: Array<{ value: TaskDifficulty; label: string }> = [
  { value: 'easy', label: '简单' },
  { value: 'normal', label: '适中' },
  { value: 'hard', label: '困难' },
  { value: 'very_hard', label: '很难' },
]
const PRIORITY_LABELS: Record<TaskPriority, string> = {
  low: '低',
  medium: '中',
  high: '高',
  urgent: '紧急',
}
const DIFFICULTY_LABELS: Record<TaskDifficulty, string> = {
  easy: '简单',
  normal: '适中',
  hard: '困难',
  very_hard: '很难',
}
const SOURCE_LABELS: Partial<Record<TaskSourceType, string>> = {
  manual: '手动',
  ai_optimized: 'AI 优化',
  ai_supplement: 'AI 补充',
}

interface TaskFormValues {
  title: string
  description: string
  category: string
  priority: TaskPriority
  difficulty: TaskDifficulty
  estimated_minutes: number
}

interface SupplementFormValues {
  available_minutes: number
  max_new_tasks: number
}

interface ActiveTimer {
  dailyPlanId: number
  dailyPlanTaskId: number
  taskId: number
  title: string
  category?: string | null
  startedAt: string
}

const DEFAULT_TASK_VALUES: TaskFormValues = {
  title: '',
  description: '',
  category: '其他',
  priority: 'medium',
  difficulty: 'normal',
  estimated_minutes: 60,
}

function normalizeCategory(value?: string | null) {
  if (!value) return '其他'
  return CATEGORY_OPTIONS.some((item) => item.value === value) ? value : '其他'
}

function normalizeTaskPayload(values: TaskFormValues, date: string, sourceType: TaskSourceType): TaskItemCreate {
  return {
    title: values.title.trim(),
    description: values.description.trim(),
    category: normalizeCategory(values.category),
    priority: values.priority,
    difficulty: values.difficulty,
    estimated_minutes: Number(values.estimated_minutes),
    status: 'pending',
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
  const actualSeconds = completed.reduce((sum, item) => sum + (item.actual_seconds || 0), 0)
  return {
    total: tasks.length,
    completed: completed.length,
    unfinished: tasks.length - completed.length,
    totalMinutes,
    actualSeconds,
    completionRate: tasks.length ? Math.round((completed.length / tasks.length) * 100) : 0,
  }
}

function readStoredTimer(): ActiveTimer | null {
  if (typeof window === 'undefined') return null
  const raw = window.localStorage.getItem(TIMER_STORAGE_KEY)
  if (!raw) return null
  try {
    const parsed = JSON.parse(raw) as ActiveTimer
    if (!parsed.dailyPlanId || !parsed.dailyPlanTaskId || !parsed.taskId || !parsed.startedAt) return null
    return parsed
  } catch {
    window.localStorage.removeItem(TIMER_STORAGE_KEY)
    return null
  }
}

function formatDuration(seconds?: number | null) {
  const safeSeconds = Math.max(Math.floor(seconds || 0), 0)
  const hours = Math.floor(safeSeconds / 3600)
  const minutes = Math.floor((safeSeconds % 3600) / 60)
  const rest = safeSeconds % 60
  if (hours > 0) {
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(rest).padStart(2, '0')}`
  }
  return `${String(minutes).padStart(2, '0')}:${String(rest).padStart(2, '0')}`
}

function priorityColor(priority?: string | null) {
  if (priority === 'urgent') return 'volcano'
  if (priority === 'high') return 'red'
  if (priority === 'medium') return 'blue'
  return 'default'
}

function difficultyColor(difficulty?: string | null) {
  if (difficulty === 'very_hard') return 'volcano'
  if (difficulty === 'hard') return 'orange'
  if (difficulty === 'easy') return 'green'
  return 'geekblue'
}

function taskDetail(description?: string | null, reason?: string | null) {
  const detail = (description || '').trim()
  if (detail) return detail
  const fallback = (reason || '').trim()
  const isGenericManualReason = fallback.includes('手动添加') && fallback.includes('日期')
  return fallback && !isGenericManualReason ? fallback : ''
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
  const [taskSourceType, setTaskSourceType] = useState<TaskSourceType>('manual')
  const [savingTask, setSavingTask] = useState(false)
  const [optimizing, setOptimizing] = useState(false)
  const [optimizeSuggestion, setOptimizeSuggestion] = useState<Awaited<ReturnType<typeof optimizeTask>> | null>(null)
  const [originalDraft, setOriginalDraft] = useState<TaskFormValues | null>(null)
  const [supplementOpen, setSupplementOpen] = useState(false)
  const [supplementing, setSupplementing] = useState(false)
  const [supplementSuggestions, setSupplementSuggestions] = useState<CalendarTaskSuggestion[]>([])
  const [activeTimer, setActiveTimer] = useState<ActiveTimer | null>(() => readStoredTimer())
  const [timerTick, setTimerTick] = useState(() => Date.now())
  const [error, setError] = useState<string | null>(null)

  const days = useMemo(() => monthDays(monthCursor), [monthCursor])
  const summariesByDate = useMemo(() => Object.fromEntries(monthSummary.map((item) => [item.date, item])), [monthSummary])
  const stats = useMemo(() => planStats(selectedPlan), [selectedPlan])
  const activeElapsedSeconds = activeTimer ? Math.max(Math.floor((timerTick - Date.parse(activeTimer.startedAt)) / 1000), 0) : 0

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

  useEffect(() => {
    if (typeof window === 'undefined') return
    if (activeTimer) {
      window.localStorage.setItem(TIMER_STORAGE_KEY, JSON.stringify(activeTimer))
    } else {
      window.localStorage.removeItem(TIMER_STORAGE_KEY)
    }
  }, [activeTimer])

  useEffect(() => {
    if (!activeTimer) return
    setTimerTick(Date.now())
    const timer = window.setInterval(() => setTimerTick(Date.now()), 1000)
    return () => window.clearInterval(timer)
  }, [activeTimer])

  useEffect(() => {
    if (!activeTimer || !selectedPlan) return
    const current = selectedPlan.tasks.find((item) => item.id === activeTimer.dailyPlanTaskId)
    if (current && ['completed', 'removed', 'delayed'].includes(current.status)) {
      setActiveTimer(null)
    }
  }, [activeTimer, selectedPlan])

  function shiftMonth(offset: number) {
    setMonthCursor((current) => new Date(current.getFullYear(), current.getMonth() + offset, 1))
  }

  function isActivePlanTask(planTask: DailyPlanTask) {
    return Boolean(activeTimer && activeTimer.dailyPlanTaskId === planTask.id)
  }

  function openCreateTask(sourceType: TaskSourceType = 'manual', suggestion?: CalendarTaskSuggestion) {
    setTaskSourceType(sourceType)
    setOptimizeSuggestion(null)
    setOriginalDraft(null)
    taskForm.setFieldsValue({
      ...DEFAULT_TASK_VALUES,
      title: suggestion?.title || '',
      description: suggestion?.description || '',
      category: normalizeCategory(suggestion?.category),
      priority: suggestion?.priority || 'medium',
      estimated_minutes: suggestion?.estimated_minutes || 60,
    })
    setTaskModalOpen(true)
  }

  async function saveTask(values: TaskFormValues) {
    setSavingTask(true)
    setError(null)
    try {
      const payload = normalizeTaskPayload(values, selectedDate, taskSourceType)
      await createTask(payload)
      message.success('任务已添加到选中日期')
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
        raw_description: values.description,
        date: selectedDate,
        category: values.category || null,
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
      description: optimizeSuggestion.suggested_description || taskForm.getFieldValue('description'),
      category: normalizeCategory(optimizeSuggestion.suggested_category),
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

  async function updateInlineTask(planTask: DailyPlanTask, payload: Partial<TaskItemCreate>) {
    if (!planTask.task) throw new Error('任务数据不完整')
    await updateTask(planTask.task.id, payload)
    await loadSelected(selectedDate)
    void loadMonth(monthCursor)
  }

  async function startTimer(planTask: DailyPlanTask) {
    if (!selectedPlan || !planTask.task) return
    if (activeTimer && !isActivePlanTask(planTask)) {
      message.warning('当前已有任务正在计时，请先完成当前任务')
      return
    }
    try {
      const result = await startDailyPlanTask(selectedPlan.id, planTask.id)
      const startedAt = result.started_at || new Date().toISOString()
      setActiveTimer({
        dailyPlanId: selectedPlan.id,
        dailyPlanTaskId: planTask.id,
        taskId: planTask.task.id,
        title: planTask.task.title,
        category: planTask.task.category,
        startedAt,
      })
      message.success('已开始计时')
      await refresh()
    } catch (err) {
      message.error(err instanceof Error ? err.message : '开始计时失败')
    }
  }

  async function completeTask(planTask: DailyPlanTask) {
    if (!selectedPlan || !planTask.task) return
    const active = isActivePlanTask(planTask)
    const actualSeconds = activeTimer && active
      ? Math.max(Math.floor((Date.now() - Date.parse(activeTimer.startedAt)) / 1000), 0)
      : undefined
    try {
      const result = await completeDailyPlanTask(
        selectedPlan.id,
        planTask.id,
        actualSeconds === undefined ? {} : { actual_seconds: actualSeconds },
      )
      if (active) setActiveTimer(null)
      const seconds = result.actual_seconds ?? actualSeconds
      message.success(seconds ? `任务已完成，实际用时 ${formatDuration(seconds)}` : '任务已完成')
      await refresh()
    } catch (err) {
      message.error(err instanceof Error ? err.message : '完成任务失败')
    }
  }

  async function postponeTask(planTask: DailyPlanTask) {
    if (!selectedPlan) return
    if (isActivePlanTask(planTask)) {
      message.warning('当前任务正在计时，请先完成后再延期')
      return
    }
    try {
      await postponeDailyPlanTask(selectedPlan.id, planTask.id)
      message.success('任务已延期到下一天')
      await refresh()
    } catch (err) {
      message.error(err instanceof Error ? err.message : '延期任务失败')
    }
  }

  async function removeTask(planTask: DailyPlanTask) {
    if (!planTask.task) return
    try {
      await deleteTask(planTask.task.id)
      if (isActivePlanTask(planTask)) setActiveTimer(null)
      message.success('任务已删除')
      await refresh()
    } catch (err) {
      message.error(err instanceof Error ? err.message : '删除任务失败')
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
        description: suggestion.description || null,
        category: normalizeCategory(suggestion.category),
        priority: suggestion.priority,
        estimated_minutes: suggestion.estimated_minutes,
        status: 'pending',
        date: selectedDate,
        is_ai_generated: true,
        source_type: 'ai_supplement',
        source_ref: {
          description: suggestion.description,
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
    <div className="page study-calendar-page">
      <div className="page-title-row study-calendar-title-row">
        <div>
          <Typography.Title level={2}>学习日历</Typography.Title>
          <Typography.Text type="secondary">按日期维护学习任务，AI 只辅助优化表达和补充少量候选任务。</Typography.Text>
        </div>
        <Space wrap align="center">
          <Button onClick={() => refresh()} loading={loadingMonth || loadingSelected}>刷新</Button>
          <Button type="primary" className="soft-primary-button" onClick={() => openCreateTask()}>+ 新增</Button>
          <Button onClick={() => setSupplementOpen(true)}>AI 补充任务</Button>
        </Space>
      </div>
      <ErrorMessage message={error} />

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
          {loadingSelected ? (
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
                  <strong>{stats.totalMinutes} <small>分钟</small></strong>
                </div>
                <div className="panel-stat-card completion-card">
                  <span>完成率</span>
                  <Progress type="circle" percent={stats.completionRate} size={64} strokeColor="#12b886" />
                </div>
              </div>
              <div className="actual-time-bar">已记录实际用时：<strong>{formatDuration(stats.actualSeconds)}</strong></div>
              {!selectedPlan || selectedPlan.tasks.filter((item) => item.status !== 'removed').length === 0 ? (
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
                  {selectedPlan.tasks.filter((item) => item.status !== 'removed').map((planTask) => {
                    const task = planTask.task
                    const priority = (task?.priority || 'medium') as TaskPriority
                    const difficulty = (task?.difficulty || 'normal') as TaskDifficulty
                    const estimatedMinutes = task?.estimated_minutes || planTask.planned_minutes || 0
                    const isCompleted = planTask.status === 'completed'
                    const detail = taskDetail(task?.description, planTask.reason)
                    return (
                      <Card key={planTask.id} size="small" className={`task-card study-task-card ${isActivePlanTask(planTask) ? 'timing' : ''}`}>
                        <div className="task-header">
                          <div className="task-main">
                            <div className="task-title-line">
                              <EditableText
                                value={task?.title || `任务 #${planTask.task_id}`}
                                className="task-title-editable"
                                onSave={(value) => updateInlineTask(planTask, { title: value })}
                              />
                              <TaskStatusBadge status={planTask.status} />
                            </div>
                            <Space wrap className="task-tags">
                              <EditableSelect
                                value={normalizeCategory(task?.category)}
                                options={CATEGORY_OPTIONS}
                                onSave={(value) => updateInlineTask(planTask, { category: value })}
                              >
                                <Tag color="processing">{normalizeCategory(task?.category)}</Tag>
                              </EditableSelect>
                              <EditableSelect
                                value={priority}
                                options={PRIORITY_OPTIONS}
                                onSave={(value) => updateInlineTask(planTask, { priority: value as TaskPriority })}
                              >
                                <Tag color={priorityColor(priority)}>{PRIORITY_LABELS[priority]}</Tag>
                              </EditableSelect>
                              <EditableSelect
                                value={difficulty}
                                options={DIFFICULTY_OPTIONS}
                                onSave={(value) => updateInlineTask(planTask, { difficulty: value as TaskDifficulty })}
                              >
                                <Tag color={difficultyColor(difficulty)}>{DIFFICULTY_LABELS[difficulty]}</Tag>
                              </EditableSelect>
                              {task?.source_type && task.source_type !== 'manual' && (
                                <Tag color={task.source_type === 'ai_optimized' ? 'purple' : 'cyan'}>
                                  {SOURCE_LABELS[task.source_type] || task.source_type}
                                </Tag>
                              )}
                            </Space>
                            <EditableText
                              value={detail}
                              multiline
                              strong={false}
                              className="task-detail-editable"
                              placeholder="点击补充具体任务内容"
                              onSave={(value) => updateInlineTask(planTask, { description: value })}
                            />
                          </div>
                          <div className="task-time-box">
                            <EditableNumber
                              value={estimatedMinutes}
                              suffix="分钟"
                              onSave={(value) => updateInlineTask(planTask, { estimated_minutes: value })}
                            >
                              <Tag color="default">预计 {estimatedMinutes} 分钟</Tag>
                            </EditableNumber>
                            {planTask.actual_seconds !== null && planTask.actual_seconds !== undefined && (
                              <Tag color="green">实际 {formatDuration(planTask.actual_seconds)}</Tag>
                            )}
                          </div>
                        </div>
                        <Divider className="compact-divider" />
                        <Space wrap className="task-actions">
                          <Button
                            size="small"
                            onClick={() => startTimer(planTask)}
                            disabled={isCompleted || planTask.status === 'removed'}
                          >
                            {isActivePlanTask(planTask) ? '计时中' : '开始'}
                          </Button>
                          <Button
                            size="small"
                            type="primary"
                            onClick={() => completeTask(planTask)}
                            disabled={isCompleted || planTask.status === 'removed'}
                          >
                            {isCompleted ? '已完成' : '完成'}
                          </Button>
                          <Popconfirm
                            title="确认延期该任务？"
                            description="延期后该任务会从当前日期移除，并安排到下一天。"
                            onConfirm={() => postponeTask(planTask)}
                          >
                            <Button size="small" disabled={isCompleted || planTask.status === 'removed'}>延期</Button>
                          </Popconfirm>
                          <Popconfirm
                            title="确认删除该任务？"
                            description="删除会归档任务，并从日期任务中移除。"
                            onConfirm={() => removeTask(planTask)}
                          >
                            <Button size="small" danger>删除</Button>
                          </Popconfirm>
                        </Space>
                      </Card>
                    )
                  })}
                </div>
              )}
            </Space>
          )}
        </Card>
      </div>

      <Modal
        title="添加任务"
        open={taskModalOpen}
        onCancel={() => setTaskModalOpen(false)}
        footer={null}
        width={720}
        destroyOnHidden
      >
        <Form form={taskForm} layout="vertical" onFinish={saveTask} initialValues={DEFAULT_TASK_VALUES}>
          <div className="form-grid compact-task-form">
            <Form.Item label="标题" name="title" rules={[{ required: true, message: '请输入任务标题' }]}>
              <Input placeholder="例如：学习函数第一章" />
            </Form.Item>
            <Form.Item
              className="full-row"
              label="内容"
              name="description"
              rules={[{ required: true, message: '请输入具体任务内容' }]}
            >
              <Input.TextArea
                rows={3}
                placeholder="例如：完成高数极限与连续专题 20 道选择题，记录错题并总结 3 个易错点。"
              />
            </Form.Item>
            <Form.Item label="分类" name="category" rules={[{ required: true, message: '请选择分类' }]}>
              <Select options={CATEGORY_OPTIONS} />
            </Form.Item>
            <Form.Item label="优先级" name="priority" rules={[{ required: true }]}>
              <Select options={PRIORITY_OPTIONS} />
            </Form.Item>
            <Form.Item label="难度" name="difficulty" rules={[{ required: true }]}>
              <Select options={DIFFICULTY_OPTIONS} />
            </Form.Item>
            <Form.Item label="预计耗时（分钟）" name="estimated_minutes" rules={[{ required: true, type: 'number', min: 5 }]}>
              <InputNumber min={5} max={10000} style={{ width: '100%' }} />
            </Form.Item>
          </div>

          {optimizeSuggestion && (
            <Card size="small" className="block-gap" title="AI 优化建议">
              <div className="compare-grid">
                <Card size="small" title="原任务">
                  <Typography.Text strong>{originalDraft?.title}</Typography.Text>
                  <Typography.Paragraph className="compact-paragraph">
                    {originalDraft?.description}
                  </Typography.Paragraph>
                  <div className="tag-row">
                    <Tag>{originalDraft?.category}</Tag>
                    <Tag>{originalDraft?.estimated_minutes} 分钟</Tag>
                    <Tag>{originalDraft?.priority && PRIORITY_LABELS[originalDraft.priority]}</Tag>
                  </div>
                </Card>
                <Card size="small" title="优化建议">
                  <Typography.Text strong>{optimizeSuggestion.suggested_title}</Typography.Text>
                  {optimizeSuggestion.suggested_description && (
                    <Typography.Paragraph className="compact-paragraph">
                      {optimizeSuggestion.suggested_description}
                    </Typography.Paragraph>
                  )}
                  <div className="tag-row">
                    <Tag>{normalizeCategory(optimizeSuggestion.suggested_category)}</Tag>
                    <Tag>{optimizeSuggestion.suggested_estimated_minutes} 分钟</Tag>
                    <Tag>{PRIORITY_LABELS[optimizeSuggestion.suggested_priority]}</Tag>
                  </div>
                  <Typography.Paragraph type="secondary">{optimizeSuggestion.reason}</Typography.Paragraph>
                </Card>
              </div>
              {optimizeSuggestion.warnings?.length > 0 && (
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
                  <Tag>{PRIORITY_LABELS[suggestion.priority]}</Tag>
                  <Tag>{normalizeCategory(suggestion.category)}</Tag>
                </Space>
                {suggestion.description && (
                  <Typography.Paragraph className="compact-paragraph">{suggestion.description}</Typography.Paragraph>
                )}
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
