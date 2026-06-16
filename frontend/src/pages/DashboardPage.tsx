import { Button, Card, Col, Progress, Row, Space, Statistic, Tag, Typography } from 'antd'
import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { listTasks } from '../api/tasks'
import type { TaskItem } from '../api/tasks'
import { EmptyState } from '../components/EmptyState'
import { ErrorMessage } from '../components/ErrorMessage'
import { TaskStatusBadge } from '../components/TaskStatusBadge'
import { useCurrentGoal } from '../hooks/useCurrentGoal'

function todayKey() {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
}

function taskStats(tasks: TaskItem[]) {
  const visible = tasks.filter((task) => task.status !== 'archived' && task.status !== 'cancelled')
  const completed = visible.filter((task) => task.status === 'completed')
  return {
    total: visible.length,
    completed: completed.length,
    unfinished: visible.length - completed.length,
    minutes: visible.reduce((sum, task) => sum + (task.estimated_minutes || 0), 0),
    rate: visible.length ? Math.round((completed.length / visible.length) * 100) : 0,
  }
}

export default function DashboardPage() {
  const navigate = useNavigate()
  const { currentGoal, currentGoalId, loading: loadingGoals, error: goalError } = useCurrentGoal()
  const [todayTasks, setTodayTasks] = useState<TaskItem[]>([])
  const [runningTasks, setRunningTasks] = useState<TaskItem[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!currentGoalId) {
      setTodayTasks([])
      setRunningTasks([])
      return
    }
    Promise.all([
      listTasks({ goal_id: currentGoalId, date: todayKey() }),
      listTasks({ goal_id: currentGoalId, status: 'in_progress' }),
    ])
      .then(([today, running]) => {
        setTodayTasks(today)
        setRunningTasks(running)
      })
      .catch((err) => setError(err instanceof Error ? err.message : '加载工作台失败'))
  }, [currentGoalId])

  const stats = useMemo(() => taskStats(todayTasks), [todayTasks])
  const runningTask = runningTasks[0]

  return (
    <div className="page">
      <div className="page-title-row">
        <div>
          <Typography.Title level={2}>工作台</Typography.Title>
          <Typography.Text type="secondary">围绕当前目标组织知识库、RAG 问答、任务日历和每日复盘。</Typography.Text>
        </div>
        <Space wrap>
          <Button onClick={() => navigate('/goals')}>目标管理</Button>
          <Button type="primary" onClick={() => navigate('/calendar')}>打开学习日历</Button>
        </Space>
      </div>
      <ErrorMessage message={goalError || error} />

      {!currentGoalId && !loadingGoals ? (
        <Card>
          <EmptyState
            title="还没有当前目标"
            description="先创建或切换一个目标，系统会用它关联知识库、任务和复盘。"
            extra={<Button type="primary" onClick={() => navigate('/goals')}>创建目标</Button>}
          />
        </Card>
      ) : (
        <>
          <Card className="goal-hero-card">
            <Row gutter={[24, 16]} align="middle">
              <Col xs={24} md={16}>
                <Space direction="vertical" size={6}>
                  <Space wrap>
                    <Typography.Title level={3} style={{ margin: 0 }}>{currentGoal?.title || '当前目标'}</Typography.Title>
                    {currentGoal?.goal_type && <Tag>{currentGoal.goal_type}</Tag>}
                    {currentGoal?.domain && <Tag color="blue">{currentGoal.domain}</Tag>}
                  </Space>
                  <Typography.Text type="secondary">{currentGoal?.target_result || '暂无目标结果描述'}</Typography.Text>
                  <Typography.Text type="secondary">截止日期：{currentGoal?.deadline || '未设置'}</Typography.Text>
                </Space>
              </Col>
              <Col xs={24} md={8}>
                <Progress percent={Number(currentGoal?.progress || 0)} strokeColor="#12b886" />
              </Col>
            </Row>
          </Card>

          <Row gutter={[16, 16]} className="block-gap">
            <Col xs={24} sm={12} lg={6}><Card><Statistic title="今日任务" value={stats.total} /></Card></Col>
            <Col xs={24} sm={12} lg={6}><Card><Statistic title="已完成" value={stats.completed} /></Card></Col>
            <Col xs={24} sm={12} lg={6}><Card><Statistic title="未完成" value={stats.unfinished} /></Card></Col>
            <Col xs={24} sm={12} lg={6}><Card><Statistic title="预计学习时长" value={stats.minutes} suffix="分钟" /></Card></Col>
          </Row>

          <Card className="block-gap" title="正在进行">
            {runningTask ? (
              <Space direction="vertical">
                <Space wrap>
                  <Typography.Text strong>{runningTask.content}</Typography.Text>
                  <TaskStatusBadge status={runningTask.status} />
                  {runningTask.category && <Tag>{runningTask.category}</Tag>}
                  <Tag>{runningTask.estimated_minutes} 分钟</Tag>
                </Space>
                <Button type="primary" onClick={() => navigate('/calendar')}>回到学习日历处理</Button>
              </Space>
            ) : (
              <Typography.Text type="secondary">当前没有正在计时的任务。</Typography.Text>
            )}
          </Card>

          <Card className="block-gap" title="核心入口">
            <Row gutter={[16, 16]}>
              <Col xs={24} md={12} xl={6}><QuickCard title="目标管理" description="创建、归档、切换当前目标。" to="/goals" /></Col>
              <Col xs={24} md={12} xl={6}><QuickCard title="知识库" description="为目标创建知识库并上传文档。" to="/knowledge-base" /></Col>
              <Col xs={24} md={12} xl={6}><QuickCard title="RAG 问答" description="基于选中知识库回答问题并展示来源。" to="/rag-chat" /></Col>
              <Col xs={24} md={12} xl={6}><QuickCard title="每日复盘" description="查看完成率和实际用时偏差。" to="/reviews" /></Col>
            </Row>
          </Card>
        </>
      )}
    </div>
  )
}

function QuickCard({ title, description, to }: { title: string; description: string; to: string }) {
  return (
    <Link to={to} className="quick-card-link">
      <Card className="quick-card">
        <Typography.Title level={4}>{title}</Typography.Title>
        <Typography.Paragraph type="secondary">{description}</Typography.Paragraph>
      </Card>
    </Link>
  )
}
