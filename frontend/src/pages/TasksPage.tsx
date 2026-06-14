import { Card, Typography } from 'antd'

export default function TasksPage() {
  return (
    <div className="page">
      <Typography.Title level={2}>今日任务</Typography.Title>
      <Card>今日任务列表占位。后续接入 /api/v1/tasks/today。</Card>
    </div>
  )
}
