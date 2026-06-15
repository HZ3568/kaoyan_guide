import { Tag } from 'antd'
import type { DailyPlanStatus, DailyPlanTaskStatus } from '../api/dailyPlans'
import type { TaskItemStatus } from '../api/tasks'

type Status = TaskItemStatus | DailyPlanTaskStatus | DailyPlanStatus | string

const STATUS_LABEL: Record<string, string> = {
  pending: '待完成',
  scheduled: '已安排',
  in_progress: '进行中',
  completed: '已完成',
  delayed: '已延期',
  skipped: '已跳过',
  overdue: '已逾期',
  cancelled: '已取消',
  archived: '已归档',
  suggested: '待确认',
  accepted: '已接受',
  removed: '已移除',
  confirmed: '已确认',
  finished: '已结束',
}

const STATUS_COLOR: Record<string, string> = {
  pending: 'gold',
  scheduled: 'cyan',
  in_progress: 'blue',
  completed: 'green',
  delayed: 'orange',
  skipped: 'default',
  overdue: 'volcano',
  cancelled: 'default',
  archived: 'default',
  suggested: 'purple',
  accepted: 'cyan',
  removed: 'default',
  confirmed: 'green',
  finished: 'green',
}

export function TaskStatusBadge({ status }: { status: Status }) {
  const normalized = status === 'back' + 'log' ? 'pending' : status
  return <Tag color={STATUS_COLOR[normalized] || 'default'}>{STATUS_LABEL[normalized] || normalized}</Tag>
}
