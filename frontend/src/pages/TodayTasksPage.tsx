import { Button, Card, Checkbox, Form, Input, InputNumber, Space, Typography, message } from 'antd'
import { useEffect, useState } from 'react'
import {
  adjustDailyPlans,
  confirmDailyPlan,
  generateDailyPlan,
  getTodayPlan,
  submitDailyPlanTaskFeedback,
  updateDailyPlanTaskStatus,
} from '../api/dailyPlans'
import type { DailyPlan, DailyPlanTaskStatus, TaskFeedbackCreate } from '../api/dailyPlans'
import { DailyPlanCard } from '../components/DailyPlanCard'
import { ErrorMessage } from '../components/ErrorMessage'
import { Loading } from '../components/Loading'

function todayString() {
  const now = new Date()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${now.getFullYear()}-${month}-${day}`
}

interface GenerateFormValues {
  date: string
  available_minutes: number
  max_tasks: number
  include_overdue: boolean
  prefer_mixed_categories: boolean
}

export default function TodayTasksPage() {
  const [form] = Form.useForm<GenerateFormValues>()
  const [plan, setPlan] = useState<DailyPlan | null>(null)
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [adjusting, setAdjusting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function refresh() {
    setLoading(true)
    setError(null)
    try {
      setPlan(await getTodayPlan())
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载今日计划失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void refresh()
  }, [])

  async function handleGenerate(values: GenerateFormValues) {
    setGenerating(true)
    setError(null)
    try {
      await generateDailyPlan({
        date: values.date || todayString(),
        available_minutes: Number(values.available_minutes),
        preferences: {
          max_tasks: Number(values.max_tasks),
          prefer_mixed_categories: Boolean(values.prefer_mixed_categories),
          include_overdue: Boolean(values.include_overdue),
        },
      })
      message.success('已生成今日任务建议')
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : '生成今日任务建议失败')
    } finally {
      setGenerating(false)
    }
  }

  async function handleConfirm() {
    if (!plan) return
    try {
      setPlan(await confirmDailyPlan(plan.id))
      message.success('今日计划已确认')
    } catch (err) {
      message.error(err instanceof Error ? err.message : '确认今日计划失败')
    }
  }

  async function handleStatusChange(dailyPlanTaskId: number, status: DailyPlanTaskStatus) {
    if (!plan) return
    try {
      const updated = await updateDailyPlanTaskStatus(plan.id, dailyPlanTaskId, status)
      setPlan((current) => current ? {
        ...current,
        tasks: current.tasks.map((task) => (task.id === updated.id ? updated : task)),
        status: current.tasks.every((task) => (task.id === updated.id ? updated.status : task.status) === 'completed') ? 'finished' : current.status,
      } : current)
    } catch (err) {
      message.error(err instanceof Error ? err.message : '更新任务状态失败')
    }
  }

  async function handleFeedback(dailyPlanTaskId: number, payload: TaskFeedbackCreate) {
    if (!plan) return
    try {
      await submitDailyPlanTaskFeedback(plan.id, dailyPlanTaskId, payload)
      message.success('反馈已提交')
    } catch (err) {
      message.error(err instanceof Error ? err.message : '提交反馈失败')
    }
  }

  async function handleAdjust() {
    setAdjusting(true)
    try {
      const result = await adjustDailyPlans({ from_date: todayString(), days: 7 })
      message.success(result.message)
      await refresh()
    } catch (err) {
      message.error(err instanceof Error ? err.message : '调整任务失败')
    } finally {
      setAdjusting(false)
    }
  }

  return (
    <div className="page">
      <div className="page-title-row">
        <div>
          <Typography.Title level={2}>今日任务</Typography.Title>
          <Typography.Text type="secondary">先生成 suggested 计划，确认后再作为今日正式任务执行。</Typography.Text>
        </div>
        <Space>
          <Button onClick={refresh} loading={loading}>刷新</Button>
          <Button onClick={handleAdjust} loading={adjusting}>调整后续任务</Button>
          {plan?.status === 'suggested' && <Button type="primary" onClick={handleConfirm}>确认今日计划</Button>}
        </Space>
      </div>
      <ErrorMessage message={error} />

      <Card title="生成今日任务建议">
        <Form
          form={form}
          layout="vertical"
          onFinish={handleGenerate}
          initialValues={{
            date: todayString(),
            available_minutes: 240,
            max_tasks: 5,
            include_overdue: true,
            prefer_mixed_categories: true,
          }}
        >
          <div className="form-grid compact-form-grid">
            <Form.Item label="计划日期" name="date" rules={[{ required: true, message: '请选择日期' }]}>
              <Input type="date" />
            </Form.Item>
            <Form.Item label="可用时间" name="available_minutes" rules={[{ required: true, type: 'number', min: 15 }]}>
              <InputNumber min={15} max={1440} addonAfter="分钟" style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item label="最多任务数" name="max_tasks" rules={[{ required: true, type: 'number', min: 1, max: 20 }]}>
              <InputNumber min={1} max={20} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item name="include_overdue" valuePropName="checked">
              <Checkbox>优先处理过期任务</Checkbox>
            </Form.Item>
            <Form.Item name="prefer_mixed_categories" valuePropName="checked">
              <Checkbox>混合不同分类</Checkbox>
            </Form.Item>
          </div>
          <Button type="primary" htmlType="submit" loading={generating}>生成今日任务建议</Button>
        </Form>
      </Card>

      {loading ? (
        <Loading tip="正在加载今日计划" />
      ) : (
        <DailyPlanCard
          plan={plan}
          title={plan ? `${plan.plan_date} 今日计划` : '今日计划'}
          onStatusChange={handleStatusChange}
          onSubmitFeedback={handleFeedback}
        />
      )}
    </div>
  )
}
