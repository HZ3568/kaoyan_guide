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
          <Typography.Text type="secondary">院校信息 RAG 查询与 AI 学习任务日历的操作入口。</Typography.Text>
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
            description="可以在学习日历中按日期添加任务，也可以让 AI 根据历史完成情况补充少量建议。"
            extra={
              <div className="inline-row">
                <Button type="primary" onClick={() => navigate('/calendar')}>打开学习日历</Button>
              </div>
            }
          />
        </Card>
      )}

      <Card className="block-gap" title="核心流程">
        <Typography.Paragraph>
          推荐演示路径：上传资料并向量化，使用 RAG 问答和检索调试确认来源；学习任务则在日历中按日期维护，并由 AI 优化表达或补充当天任务。
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
          <QuickCard title="学习日历" description="按日期新增、编辑和反馈任务，AI 只提供优化与补充建议。" to="/calendar" />
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
      <Link to="/calendar">学习日历</Link>
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
