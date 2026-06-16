import { Button, Card, Form, Input, InputNumber, Select, Typography, message } from 'antd'
import { useNavigate } from 'react-router-dom'
import { submitOnboarding } from '../api/profiles'
import { useGoalStore } from '../stores/goalStore'

interface OnboardingValues {
  persona_type?: string
  current_stage?: string
  domain?: string
  ability_level?: string
  daily_available_minutes?: number
  goal_title: string
  goal_type?: string
  goal_domain?: string
  deadline?: string
  target_result?: string
}

export default function OnboardingPage() {
  const [form] = Form.useForm<OnboardingValues>()
  const navigate = useNavigate()
  const setCurrentGoalId = useGoalStore((state) => state.setCurrentGoalId)

  async function handleSubmit(values: OnboardingValues) {
    try {
      const response = await submitOnboarding({
        profile: {
          persona_type: values.persona_type || null,
          current_stage: values.current_stage || null,
          domain: values.domain || values.goal_domain || null,
          ability_level: values.ability_level || null,
          daily_available_minutes: values.daily_available_minutes ?? null,
        },
        goal: {
          title: values.goal_title,
          goal_type: values.goal_type || null,
          domain: values.goal_domain || values.domain || null,
          deadline: values.deadline || null,
          target_result: values.target_result || null,
          priority: 'medium',
          status: 'active',
          progress: 0,
        },
      })
      if (response.goal?.id) {
        setCurrentGoalId(response.goal.id)
      }
      message.success('初始化完成')
      navigate('/')
    } catch (error) {
      message.error(error instanceof Error ? error.message : '初始化失败')
    }
  }

  return (
    <div className="onboarding-page">
      <Card className="onboarding-card">
        <Typography.Title level={2}>建立学习画像</Typography.Title>
        <Typography.Paragraph type="secondary">
          先创建一个当前目标。之后知识库、RAG 问答、任务日历和复盘都会围绕该目标组织。
        </Typography.Paragraph>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            persona_type: 'learner',
            goal_type: 'project',
            daily_available_minutes: 120,
          }}
        >
          <div className="form-grid">
            <Form.Item label="身份类型" name="persona_type">
              <Input placeholder="例如：学生、开发者、研究者、职场学习者" />
            </Form.Item>
            <Form.Item label="当前阶段" name="current_stage">
              <Input placeholder="例如：入门、强化、冲刺、转型期" />
            </Form.Item>
            <Form.Item label="学习领域" name="domain">
              <Input placeholder="例如：AI 工程、写作、语言学习、职业技能" />
            </Form.Item>
            <Form.Item label="能力水平" name="ability_level">
              <Select
                allowClear
                options={[
                  { value: 'beginner', label: '入门' },
                  { value: 'intermediate', label: '进阶' },
                  { value: 'advanced', label: '熟练' },
                ]}
              />
            </Form.Item>
            <Form.Item
              label="每日可用时间"
              name="daily_available_minutes"
              rules={[{ type: 'number', min: 0, max: 1440, message: '请输入 0-1440 分钟' }]}
            >
              <InputNumber addonAfter="分钟" min={0} max={1440} style={{ width: '100%' }} />
            </Form.Item>
          </div>

          <Typography.Title level={4}>初始目标</Typography.Title>
          <div className="form-grid">
            <Form.Item
              label="目标标题"
              name="goal_title"
              rules={[{ required: true, message: '请输入目标标题' }]}
            >
              <Input placeholder="例如：完成 RAG 项目 Demo" />
            </Form.Item>
            <Form.Item label="目标类型" name="goal_type">
              <Input placeholder="例如：project、exam、skill、paper" />
            </Form.Item>
            <Form.Item label="目标领域" name="goal_domain">
              <Input placeholder="默认继承学习领域" />
            </Form.Item>
            <Form.Item label="截止日期" name="deadline">
              <Input type="date" />
            </Form.Item>
          </div>
          <Form.Item label="目标结果" name="target_result">
            <Input.TextArea rows={3} placeholder="描述你希望达成的具体结果" />
          </Form.Item>
          <Button type="primary" htmlType="submit">
            完成初始化
          </Button>
        </Form>
      </Card>
    </div>
  )
}
