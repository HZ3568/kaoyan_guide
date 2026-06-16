import { Tag } from 'antd'
import type { TaskItemStatus } from '../api/tasks'

type Status = TaskItemStatus | string

const STATUS_LABEL: Record<string, string> = {
  pending: '待处理',
  scheduled: '已安排',
  in_progress: '进行中',
  completed: '已完成',
  delayed: '已延期',
  overdue: '已逾期',
  cancelled: '已取消',
  archived: '已归档',
}

const STATUS_COLOR: Record<string, string> = {
  pending: 'gold',
  scheduled: 'cyan',
  in_progress: 'blue',
  completed: 'green',
  delayed: 'orange',
  overdue: 'volcano',
  cancelled: 'default',
  archived: 'default',
}

export function TaskStatusBadge({ status }: { status: Status }) {
  return <Tag color={STATUS_COLOR[status] || 'default'}>{STATUS_LABEL[status] || status}</Tag>
}
