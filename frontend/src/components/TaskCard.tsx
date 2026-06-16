import { Button, Card, Space, Tag, Typography } from 'antd'
import { useState } from 'react'
import type { DailyPlanTask, DailyPlanTaskStatus, TaskFeedbackCreate } from '../api/dailyPlans'
import type { TaskItem } from '../api/tasks'
import { FeedbackModal } from './FeedbackModal'
import { TaskStatusBadge } from './TaskStatusBadge'

const PRIORITY_COLOR: Record<string, string> = {
  urgent: 'volcano',
  high: 'red',
  medium: 'blue',
  low: 'default',
}

const SOURCE_LABEL: Record<string, string> = {
  manual: '手动',
  ai_optimized: 'AI 优化',
  ai_supplement: 'AI 补充',
  ai_split: 'AI 拆分',
  imported: '导入',
  planner: '日历',
}

interface TaskCardProps {
  planTask?: DailyPlanTask
  task?: TaskItem
  onStatusChange?: (dailyPlanTaskId: number, status: DailyPlanTaskStatus) => Promise<void> | void
  onSubmitFeedback?: (dailyPlanTaskId: number, payload: TaskFeedbackCreate) => Promise<void> | void
}

export function TaskCard({ planTask, task: taskProp, onStatusChange, onSubmitFeedback }: TaskCardProps) {
  const [feedbackOpen, setFeedbackOpen] = useState(false)
  const [submittingFeedback, setSubmittingFeedback] = useState(false)
  const task = taskProp || planTask?.task

  async function submitFeedback(payload: TaskFeedbackCreate) {
    if (!planTask) return
    setSubmittingFeedback(true)
    await onSubmitFeedback?.(planTask.id, payload)
    setSubmittingFeedback(false)
    setFeedbackOpen(false)
  }

  return (
    <Card className="task-card" size="small">
      <div className="task-header">
        <div>
          <Space wrap>
            <Typography.Text strong>{task?.title || (planTask ? `任务 #${planTask.task_id}` : '未命名任务')}</Typography.Text>
            {planTask && <TaskStatusBadge status={planTask.status} />}
            {!planTask && task?.status && <TaskStatusBadge status={task.status} />}
            {task?.category && <Tag>{task.category}</Tag>}
            {task?.project && <Tag>{task.project}</Tag>}
            {task?.priority && <Tag color={PRIORITY_COLOR[task.priority]}>{task.priority}</Tag>}
            {task?.source_type && <Tag>{SOURCE_LABEL[task.source_type] || task.source_type}</Tag>}
          </Space>
          <Typography.Paragraph className="task-desc">
            {task?.description || planTask?.reason || '暂无说明'}
          </Typography.Paragraph>
          {planTask?.reason && <Typography.Paragraph type="secondary">{planTask.reason}</Typography.Paragraph>}
        </div>
        <Typography.Text type="secondary">{planTask?.planned_minutes || task?.estimated_minutes || 0} 分钟</Typography.Text>
      </div>

      {planTask && (onStatusChange || onSubmitFeedback) && (
        <Space wrap>
          {onStatusChange && (
            <>
              <Button size="small" disabled={planTask.status === 'in_progress'} onClick={() => onStatusChange(planTask.id, 'in_progress')}>
                开始
              </Button>
              <Button size="small" type="primary" disabled={planTask.status === 'completed'} onClick={() => onStatusChange(planTask.id, 'completed')}>
                完成
              </Button>
              <Button size="small" disabled={planTask.status === 'delayed'} onClick={() => onStatusChange(planTask.id, 'delayed')}>
                延期
              </Button>
              <Button size="small" disabled={planTask.status === 'skipped'} onClick={() => onStatusChange(planTask.id, 'skipped')}>
                跳过
              </Button>
              <Button size="small" disabled={planTask.status === 'pending'} onClick={() => onStatusChange(planTask.id, 'pending')}>
                恢复待完成
              </Button>
            </>
          )}
          {onSubmitFeedback && (
            <Button size="small" onClick={() => setFeedbackOpen((value) => !value)}>
              反馈
            </Button>
          )}
        </Space>
      )}

      <FeedbackModal
        open={feedbackOpen}
        submitting={submittingFeedback}
        onCancel={() => setFeedbackOpen(false)}
        onSubmit={submitFeedback}
      />
    </Card>
  )
}
