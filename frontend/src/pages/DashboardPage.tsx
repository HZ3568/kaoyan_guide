import { Button, Card, Col, Row, Statistic, Typography } from 'antd'
import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { getTodayPlan } from '../api/dailyPlans'
import type { DailyPlan } from '../api/dailyPlans'
import { EmptyState } from '../components/EmptyState'
import { ErrorMessage } from '../components/ErrorMessage'

export default function DashboardPage() {
  const navigate = useNavigate()
  const [todayPlan, setTodayPlan] = useState<DailyPlan | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getTodayPlan()
      .then(setTodayPlan)
      .catch((err) => setError(err instanceof Error ? err.message : '加载今日概况失败'))
  }, [])

  const stats = useMemo(() => {
    const tasks = todayPlan?.tasks || []
    return {
      total: tasks.length,
      completed: tasks.filter((task) => task.status === 'completed').length,
      unfinished: tasks.filter((task) => !['completed', 'skipped', 'removed'].includes(task.status)).length,
      minutes: tasks.reduce((sum, task) => sum + task.planned_minutes, 0),
    }
  }, [todayPlan])

  return (
    <div className="page">
      <div className="page-title-row">
        <div>
          <Typography.Title level={2}>工作台</Typography.Title>
          <Typography.Text type="secondary">RAG 知识库和 AI 每日任务清单的操作入口。</Typography.Text>
        </div>
      </div>
      <ErrorMessage message={error} />

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}><Card><Statistic title="今日任务" value={stats.total} /></Card></Col>
        <Col xs={24} sm={12} lg={6}><Card><Statistic title="已完成" value={stats.completed} /></Card></Col>
        <Col xs={24} sm={12} lg={6}><Card><Statistic title="未完成" value={stats.unfinished} /></Card></Col>
        <Col xs={24} sm={12} lg={6}><Card><Statistic title="预计学习时长" value={stats.minutes} suffix="分钟" /></Card></Col>
      </Row>

      {!todayPlan && (
        <Card className="block-gap">
          <EmptyState
            title="今日暂无计划"
            description="可以先去任务池添加任务，也可以直接生成今日任务建议。"
            extra={
              <div className="inline-row">
                <Button type="primary" onClick={() => navigate('/today')}>生成今日任务建议</Button>
                <Button onClick={() => navigate('/tasks')}>去任务池添加任务</Button>
              </div>
            }
          />
        </Card>
      )}

      <Card className="block-gap" title="核心流程">
        <Typography.Paragraph>
          推荐演示路径：上传资料并向量化，使用 RAG 问答和检索调试确认来源，再维护任务池并生成今日任务建议。
        </Typography.Paragraph>
        <SpaceLinks />
      </Card>

      <Row gutter={[16, 16]} className="block-gap">
        <Col xs={24} md={12} xl={8}>
          <QuickCard title="知识库管理" description="上传 txt、md、pdf、json，查看 chunk，并触发 Redis Vector 向量化。" to="/knowledge-base" />
        </Col>
        <Col xs={24} md={12} xl={8}>
          <QuickCard title="RAG 问答" description="基于知识库回答考研资料问题，并展示引用来源。" to="/rag-chat" />
        </Col>
        <Col xs={24} md={12} xl={8}>
          <QuickCard title="任务池" description="手动创建任务，使用 AI 整理或拆分大任务。" to="/tasks" />
        </Col>
        <Col xs={24} md={12} xl={8}>
          <QuickCard title="今日任务" description="根据可用时间生成 suggested 计划，确认后执行和反馈。" to="/today" />
        </Col>
        <Col xs={24} md={12} xl={8}>
          <QuickCard title="任务日历" description="按日期查看每日任务安排和完成状态。" to="/calendar" />
        </Col>
        <Col xs={24} md={12} xl={8}>
          <QuickCard title="RAG 推荐任务" description="从知识库依据中提炼候选任务，确认后加入任务池。" to="/rag-task-recommend" />
        </Col>
      </Row>
    </div>
  )
}

function SpaceLinks() {
  return (
    <div className="inline-row">
      <Link to="/knowledge-base">知识库管理</Link>
      <Link to="/rag-chat">RAG 问答</Link>
      <Link to="/tasks">任务池</Link>
      <Link to="/today">今日任务</Link>
      <Link to="/calendar">任务日历</Link>
      <Link to="/rag-task-recommend">RAG 推荐任务</Link>
      <Link to="/rag-debug">检索调试</Link>
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
