import { Button, Card, Form, Input, Typography, message } from 'antd'
import { http } from '../api/http'

export default function PlannerPage() {
  async function onFinish(values: any) {
    const profile = await http.post('/planner/profiles', {
      ...values,
      weak_subjects: values.weak_subjects ? values.weak_subjects.split(',') : [],
      daily_available_hours: Number(values.daily_available_hours || 3),
      weekly_available_days: Number(values.weekly_available_days || 6),
    })
    await http.post('/planner/generate', { profile_id: profile.data.id })
    message.success('学习计划已生成')
  }

  return (
    <div className="page">
      <Typography.Title level={2}>智能学习规划</Typography.Title>
      <Card>
        <Form layout="vertical" onFinish={onFinish}>
          <Form.Item label="目标院校" name="target_school"><Input /></Form.Item>
          <Form.Item label="目标专业" name="target_major"><Input /></Form.Item>
          <Form.Item label="当前水平" name="current_level"><Input /></Form.Item>
          <Form.Item label="薄弱科目，用逗号分隔" name="weak_subjects"><Input /></Form.Item>
          <Form.Item label="每日可学习小时数" name="daily_available_hours"><Input /></Form.Item>
          <Form.Item label="每周可学习天数" name="weekly_available_days"><Input /></Form.Item>
          <Button type="primary" htmlType="submit">生成计划</Button>
        </Form>
      </Card>
    </div>
  )
}
