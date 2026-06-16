import { Button, Card, Form, Input, InputNumber, Modal, Popconfirm, Select, Space, Table, Tag, Typography, message } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useEffect, useState } from 'react'
import { activateGoal, archiveGoal, createGoal, listGoals, updateGoal } from '../api/goals'
import type { Goal, GoalPayload, GoalPriority, GoalStatus } from '../api/goals'
import { ErrorMessage } from '../components/ErrorMessage'
import { useGoalStore } from '../stores/goalStore'

const PRIORITY_OPTIONS: Array<{ value: GoalPriority; label: string }> = [
  { value: 'low', label: '低' },
  { value: 'medium', label: '中' },
  { value: 'high', label: '高' },
  { value: 'urgent', label: '紧急' },
]

const STATUS_OPTIONS: Array<{ value: GoalStatus; label: string }> = [
  { value: 'active', label: '活跃' },
  { value: 'paused', label: '暂停' },
  { value: 'completed', label: '完成' },
  { value: 'archived', label: '归档' },
]

export default function GoalsPage() {
  const [form] = Form.useForm<GoalPayload>()
  const currentGoalId = useGoalStore((state) => state.currentGoalId)
  const setCurrentGoalId = useGoalStore((state) => state.setCurrentGoalId)
  const [goals, setGoals] = useState<Goal[]>([])
  const [editingGoal, setEditingGoal] = useState<Goal | null>(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function refresh() {
    setLoading(true)
    setError(null)
    try {
      const items = await listGoals()
      setGoals(items)
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载目标失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void refresh()
  }, [])

  function openCreate() {
    setEditingGoal(null)
    form.setFieldsValue({ priority: 'medium', status: 'active', progress: 0 })
    setModalOpen(true)
  }

  function openEdit(goal: Goal) {
    setEditingGoal(goal)
    form.setFieldsValue({
      title: goal.title,
      goal_type: goal.goal_type || undefined,
      domain: goal.domain || undefined,
      target_result: goal.target_result || undefined,
      deadline: goal.deadline || undefined,
      priority: goal.priority,
      status: goal.status,
      progress: Number(goal.progress || 0),
    })
    setModalOpen(true)
  }

  async function saveGoal(values: GoalPayload) {
    setSaving(true)
    try {
      const saved = editingGoal
        ? await updateGoal(editingGoal.id, values)
        : await createGoal({ ...values, priority: values.priority || 'medium', status: values.status || 'active' })
      if (!currentGoalId && saved.status !== 'archived') {
        setCurrentGoalId(saved.id)
      }
      message.success(editingGoal ? '目标已更新' : '目标已创建')
      setModalOpen(false)
      form.resetFields()
      await refresh()
    } catch (err) {
      message.error(err instanceof Error ? err.message : '保存目标失败')
    } finally {
      setSaving(false)
    }
  }

  async function handleArchive(goal: Goal) {
    try {
      await archiveGoal(goal.id)
      if (currentGoalId === goal.id) setCurrentGoalId(null)
      message.success('目标已归档')
      await refresh()
    } catch (err) {
      message.error(err instanceof Error ? err.message : '归档目标失败')
    }
  }

  async function handleActivate(goal: Goal) {
    try {
      const active = await activateGoal(goal.id)
      setCurrentGoalId(active.id)
      message.success('已切换当前目标')
      await refresh()
    } catch (err) {
      message.error(err instanceof Error ? err.message : '激活目标失败')
    }
  }

  const columns: ColumnsType<Goal> = [
    {
      title: '目标',
      dataIndex: 'title',
      render: (value: string, record) => (
        <Space direction="vertical" size={2}>
          <Typography.Text strong>{value}</Typography.Text>
          <Typography.Text type="secondary">{record.target_result || '暂无目标结果描述'}</Typography.Text>
        </Space>
      ),
    },
    { title: '类型', dataIndex: 'goal_type', render: (value?: string | null) => value || '-' },
    { title: '领域', dataIndex: 'domain', render: (value?: string | null) => value || '-' },
    { title: '截止日期', dataIndex: 'deadline', render: (value?: string | null) => value || '-' },
    { title: '优先级', dataIndex: 'priority', render: (value: string) => <Tag>{value}</Tag> },
    {
      title: '状态',
      dataIndex: 'status',
      render: (value: string, record) => (
        <Space>
          <Tag color={value === 'active' ? 'green' : value === 'archived' ? 'default' : 'blue'}>{value}</Tag>
          {record.id === currentGoalId && <Tag color="gold">当前</Tag>}
        </Space>
      ),
    },
    { title: '进度', dataIndex: 'progress', render: (value: number) => `${Number(value || 0).toFixed(0)}%` },
    {
      title: '操作',
      width: 260,
      render: (_, record) => (
        <Space wrap>
          <Button size="small" type={record.id === currentGoalId ? 'primary' : 'default'} onClick={() => setCurrentGoalId(record.id)}>
            切换
          </Button>
          <Button size="small" onClick={() => openEdit(record)}>编辑</Button>
          <Button size="small" onClick={() => handleActivate(record)}>激活</Button>
          <Popconfirm title="确认归档该目标？" onConfirm={() => handleArchive(record)}>
            <Button size="small" danger>归档</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div className="page">
      <div className="page-title-row">
        <div>
          <Typography.Title level={2}>目标管理</Typography.Title>
          <Typography.Text type="secondary">目标决定知识库、RAG 问答、任务日历和每日复盘的默认上下文。</Typography.Text>
        </div>
        <Button type="primary" onClick={openCreate}>新建目标</Button>
      </div>
      <ErrorMessage message={error} />
      <Card>
        <Table rowKey="id" columns={columns} dataSource={goals} loading={loading} pagination={{ pageSize: 8 }} />
      </Card>

      <Modal
        title={editingGoal ? '编辑目标' : '新建目标'}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        footer={null}
        destroyOnHidden
      >
        <Form form={form} layout="vertical" onFinish={saveGoal}>
          <Form.Item label="目标标题" name="title" rules={[{ required: true, message: '请输入目标标题' }]}>
            <Input />
          </Form.Item>
          <div className="form-grid">
            <Form.Item label="目标类型" name="goal_type">
              <Input placeholder="project / exam / skill / paper" />
            </Form.Item>
            <Form.Item label="领域" name="domain">
              <Input placeholder="例如 AI 工程、写作、语言学习" />
            </Form.Item>
            <Form.Item label="截止日期" name="deadline">
              <Input type="date" />
            </Form.Item>
            <Form.Item label="优先级" name="priority">
              <Select options={PRIORITY_OPTIONS} />
            </Form.Item>
            <Form.Item label="状态" name="status">
              <Select options={STATUS_OPTIONS} />
            </Form.Item>
            <Form.Item label="进度" name="progress">
              <InputNumber min={0} max={100} addonAfter="%" style={{ width: '100%' }} />
            </Form.Item>
          </div>
          <Form.Item label="目标结果" name="target_result">
            <Input.TextArea rows={3} />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={saving}>
            保存
          </Button>
        </Form>
      </Modal>
    </div>
  )
}
