import { Button, Card, Form, Input, InputNumber, Progress, Space, Statistic, Table, Typography, message } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useEffect, useMemo, useState } from 'react'
import { createReview, getReviewStats, listReviews } from '../api/reviews'
import type { DailyReview, DailyReviewPayload, ReviewStats } from '../api/reviews'
import { listTasks } from '../api/tasks'
import type { TaskItem } from '../api/tasks'
import { EmptyState } from '../components/EmptyState'
import { ErrorMessage } from '../components/ErrorMessage'
import { useCurrentGoal } from '../hooks/useCurrentGoal'

function todayKey() {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
}

function statsFromTasks(tasks: TaskItem[]) {
  const visible = tasks.filter((task) => task.status !== 'archived' && task.status !== 'cancelled')
  const completed = visible.filter((task) => task.status === 'completed')
  const estimated = visible.reduce((sum, task) => sum + (task.estimated_minutes || 0), 0)
  const actual = completed.reduce((sum, task) => sum + (task.actual_minutes || 0), 0)
  return {
    completion_rate: visible.length ? Math.round((completed.length / visible.length) * 100) : 0,
    total_estimated_minutes: estimated,
    total_actual_minutes: actual,
  }
}

function isCurrentWeek(dateString?: string | null) {
  if (!dateString) return false
  const today = new Date()
  const target = new Date(`${dateString}T00:00:00`)
  const start = new Date(today)
  const day = start.getDay() || 7
  start.setDate(start.getDate() - day + 1)
  start.setHours(0, 0, 0, 0)
  const end = new Date(start)
  end.setDate(start.getDate() + 7)
  return target >= start && target < end
}

export default function ReviewPage() {
  const [form] = Form.useForm<DailyReviewPayload>()
  const { currentGoal, currentGoalId } = useCurrentGoal()
  const [reviews, setReviews] = useState<DailyReview[]>([])
  const [stats, setStats] = useState<ReviewStats | null>(null)
  const [todayTasks, setTodayTasks] = useState<TaskItem[]>([])
  const [allTasks, setAllTasks] = useState<TaskItem[]>([])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const todayTaskStats = useMemo(() => statsFromTasks(todayTasks), [todayTasks])
  const weekTaskStats = useMemo(() => statsFromTasks(allTasks.filter((task) => isCurrentWeek(task.planned_date))), [allTasks])

  async function refresh() {
    if (!currentGoalId) {
      setReviews([])
      setStats(null)
      setTodayTasks([])
      setAllTasks([])
      return
    }
    setLoading(true)
    setError(null)
    try {
      const [reviewItems, statsResult, todayRows, allRows] = await Promise.all([
        listReviews({ goal_id: currentGoalId }),
        getReviewStats(currentGoalId),
        listTasks({ goal_id: currentGoalId, date: todayKey() }),
        listTasks({ goal_id: currentGoalId }),
      ])
      setReviews(reviewItems)
      setStats(statsResult)
      setTodayTasks(todayRows)
      setAllTasks(allRows)
      form.setFieldsValue({
        goal_id: currentGoalId,
        review_date: todayKey(),
        ...statsFromTasks(todayRows),
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载复盘数据失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void refresh()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentGoalId])

  async function submitReview(values: DailyReviewPayload) {
    if (!currentGoalId) {
      message.warning('请先选择当前目标')
      return
    }
    setSaving(true)
    try {
      await createReview({
        ...values,
        goal_id: currentGoalId,
        review_date: values.review_date || todayKey(),
        completion_rate: values.completion_rate ?? todayTaskStats.completion_rate,
        total_estimated_minutes: values.total_estimated_minutes ?? todayTaskStats.total_estimated_minutes,
        total_actual_minutes: values.total_actual_minutes ?? todayTaskStats.total_actual_minutes,
      })
      message.success('复盘已保存')
      form.resetFields()
      await refresh()
    } catch (err) {
      message.error(err instanceof Error ? err.message : '保存复盘失败')
    } finally {
      setSaving(false)
    }
  }

  const columns: ColumnsType<DailyReview> = [
    { title: '日期', dataIndex: 'review_date', width: 120 },
    { title: '完成率', dataIndex: 'completion_rate', width: 120, render: (value: number) => `${value}%` },
    { title: '预计用时', dataIndex: 'total_estimated_minutes', width: 120, render: (value: number) => `${value} 分钟` },
    { title: '实际用时', dataIndex: 'total_actual_minutes', width: 120, render: (value: number) => `${value} 分钟` },
    {
      title: '总结',
      dataIndex: 'summary',
      render: (value: string | null | undefined, record) => (
        <Space direction="vertical" size={2}>
          <Typography.Text>{value || '-'}</Typography.Text>
          {record.problems && <Typography.Text type="secondary">问题：{record.problems}</Typography.Text>}
          {record.adjustment_suggestion && <Typography.Text type="secondary">调整：{record.adjustment_suggestion}</Typography.Text>}
        </Space>
      ),
    },
  ]

  return (
    <div className="page">
      <div className="page-title-row">
        <div>
          <Typography.Title level={2}>每日复盘</Typography.Title>
          <Typography.Text type="secondary">
            当前目标：{currentGoal?.title || '未选择目标'}。复盘基于目标下的任务完成情况。
          </Typography.Text>
        </div>
        <Button onClick={() => void refresh()} loading={loading}>刷新</Button>
      </div>
      <ErrorMessage message={error} />

      {!currentGoalId ? (
        <Card>
          <EmptyState title="请先选择目标" description="复盘需要绑定到目标。" />
        </Card>
      ) : (
        <>
          <div className="stats-grid">
            <Card><Statistic title="今日完成率" value={todayTaskStats.completion_rate} suffix="%" /></Card>
            <Card><Statistic title="本周完成率" value={weekTaskStats.completion_rate} suffix="%" /></Card>
            <Card><Statistic title="延期率" value={stats?.delay_rate ?? 0} suffix="%" /></Card>
            <Card><Statistic title="实际偏差" value={stats?.actual_estimated_delta_minutes ?? 0} suffix="分钟" /></Card>
          </div>

          <Card title="今日任务概况">
            <Space wrap>
              <Progress type="circle" percent={todayTaskStats.completion_rate} size={72} />
              <Typography.Text>预计 {todayTaskStats.total_estimated_minutes} 分钟</Typography.Text>
              <Typography.Text>实际 {todayTaskStats.total_actual_minutes} 分钟</Typography.Text>
            </Space>
          </Card>

          <Card className="block-gap" title="创建每日复盘">
            <Form form={form} layout="vertical" onFinish={submitReview}>
              <div className="form-grid">
                <Form.Item label="复盘日期" name="review_date" rules={[{ required: true, message: '请选择复盘日期' }]}>
                  <Input type="date" />
                </Form.Item>
                <Form.Item label="完成率" name="completion_rate">
                  <InputNumber min={0} max={100} addonAfter="%" style={{ width: '100%' }} />
                </Form.Item>
                <Form.Item label="预计用时" name="total_estimated_minutes">
                  <InputNumber min={0} addonAfter="分钟" style={{ width: '100%' }} />
                </Form.Item>
                <Form.Item label="实际用时" name="total_actual_minutes">
                  <InputNumber min={0} addonAfter="分钟" style={{ width: '100%' }} />
                </Form.Item>
              </div>
              <Form.Item label="总结" name="summary">
                <Input.TextArea rows={3} />
              </Form.Item>
              <Form.Item label="问题" name="problems">
                <Input.TextArea rows={3} />
              </Form.Item>
              <Form.Item label="调整建议" name="adjustment_suggestion">
                <Input.TextArea rows={3} />
              </Form.Item>
              <Button type="primary" htmlType="submit" loading={saving}>保存复盘</Button>
            </Form>
          </Card>

          <Card className="block-gap" title="历史复盘">
            <Table rowKey="id" columns={columns} dataSource={reviews} loading={loading} pagination={{ pageSize: 8 }} />
          </Card>
        </>
      )}
    </div>
  )
}
