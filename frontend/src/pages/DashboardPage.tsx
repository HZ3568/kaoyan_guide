import { Card, Col, Row, Statistic, Typography } from 'antd'

export default function DashboardPage() {
  return (
    <div className="page">
      <Typography.Title level={2}>首页仪表盘</Typography.Title>
      <Row gutter={16}>
        <Col span={6}><Card><Statistic title="知识库文档" value={0} /></Card></Col>
        <Col span={6}><Card><Statistic title="今日任务" value={0} /></Card></Col>
        <Col span={6}><Card><Statistic title="学习计划" value={0} /></Card></Col>
        <Col span={6}><Card><Statistic title="RAG 问答" value={0} /></Card></Col>
      </Row>
      <Card style={{ marginTop: 16 }}>
        当前骨架已预留：知识库管理、RAG 问答、学习规划、任务反馈与评估模块。
      </Card>
    </div>
  )
}
