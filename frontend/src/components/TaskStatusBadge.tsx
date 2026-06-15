import { Tag } from 'antd'
import type { DailyPlanStatus, DailyPlanTaskStatus } from '../api/dailyPlans'
import type { TaskItemStatus } from '../api/tasks'

type Status = TaskItemStatus | DailyPlanTaskStatus | DailyPlanStatus

const STATUS_LABEL: Record<Status, string> = {
  backlog: '待整理',
  pending: '待完成',
  in_progress: '进行中',
  completed: '已完成',
  delayed: '已延期',
  skipped: '已跳过',
  archived: '已归档',
  suggested: '待确认',
  accepted: '已接受',
  removed: '已移除',
  confirmed: '已确认',
  finished: '已结束',
}

const STATUS_COLOR: Record<Status, string> = {
  backlog: 'default',
  pending: 'gold',
  in_progress: 'blue',
  completed: 'green',
  delayed: 'orange',
  skipped: 'default',
  archived: 'default',
  suggested: 'purple',
  accepted: 'cyan',
  removed: 'default',
  confirmed: 'green',
  finished: 'green',
}

export function TaskStatusBadge({ status }: { status: Status }) {
  return <Tag color={STATUS_COLOR[status] || 'default'}>{STATUS_LABEL[status] || status}</Tag>
}
