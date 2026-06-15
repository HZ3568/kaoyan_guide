import { Card, Progress, Space, Statistic, Typography } from 'antd'
import type { DailyPlan, DailyPlanTaskStatus, TaskFeedbackCreate } from '../api/dailyPlans'
import { EmptyState } from './EmptyState'
import { TaskCard } from './TaskCard'
import { TaskStatusBadge } from './TaskStatusBadge'

interface DailyPlanCardProps {
  plan: DailyPlan | null
  title?: string
  onStatusChange?: (dailyPlanTaskId: number, status: DailyPlanTaskStatus) => Promise<void> | void
  onSubmitFeedback?: (dailyPlanTaskId: number, payload: TaskFeedbackCreate) => Promise<void> | void
  onEmptyAction?: () => void
}

function computeStats(plan: DailyPlan | null) {
  const tasks = plan?.tasks || []
  const totalMinutes = tasks.reduce((sum, task) => sum + task.planned_minutes, 0)
  const completedTasks = tasks.filter((task) => task.status === 'completed')
  const completedMinutes = completedTasks.reduce((sum, task) => sum + task.planned_minutes, 0)
  const active = tasks.filter((task) => !['completed', 'skipped', 'removed'].includes(task.status)).length
  const completionRate = tasks.length > 0 ? Math.round((completedTasks.length / tasks.length) * 100) : 0
  return { totalMinutes, completedMinutes, completed: completedTasks.length, active, completionRate }
}

export function DailyPlanCard({ plan, title, onStatusChange, onSubmitFeedback, onEmptyAction }: DailyPlanCardProps) {
  const stats = computeStats(plan)

  return (
    <Card
      className="block-gap"
      title={
        <Space wrap>
          <span>{title || plan?.plan_date || '每日计划'}</span>
          {plan && <TaskStatusBadge status={plan.status} />}
        </Space>
      }
    >
      {!plan || plan.tasks.length === 0 ? (
        <EmptyState
          title="暂无任务"
          description="当前日期还没有任务。可以在学习日历中手动添加，或使用 AI 补充任务建议。"
          actionText={onEmptyAction ? '去添加任务' : undefined}
          onAction={onEmptyAction}
        />
      ) : (
        <Space direction="vertical" className="full-width" size="middle">
          <div className="stats-grid compact-stats">
            <Card size="small"><Statistic title="计划总时长" value={stats.totalMinutes} suffix="分钟" /></Card>
            <Card size="small"><Statistic title="已完成时长" value={stats.completedMinutes} suffix="分钟" /></Card>
            <Card size="small"><Statistic title="已完成任务" value={stats.completed} /></Card>
            <Card size="small">
              <Typography.Text type="secondary">完成率</Typography.Text>
              <Progress percent={stats.completionRate} size="small" />
            </Card>
          </div>
          {plan.summary && <Typography.Paragraph className="plan-summary">{plan.summary}</Typography.Paragraph>}
          <div className="task-list">
            {plan.tasks.map((task) => (
              <TaskCard
                key={task.id}
                planTask={task}
                onStatusChange={onStatusChange}
                onSubmitFeedback={onSubmitFeedback}
              />
            ))}
          </div>
        </Space>
      )}
    </Card>
  )
}
