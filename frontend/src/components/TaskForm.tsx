import { Button, Form, Input, InputNumber, Select, Switch } from 'antd'
import { useEffect } from 'react'
import type { TaskDifficulty, TaskItem, TaskItemCreate, TaskItemStatus, TaskPriority } from '../api/tasks'

export interface TaskFormValues {
  title: string
  description?: string
  category?: string
  project?: string
  priority: TaskPriority
  difficulty?: TaskDifficulty
  estimated_minutes: number
  deadline?: string
  status: TaskItemStatus
  is_splittable: boolean
}

interface TaskFormProps {
  initialTask?: TaskItem | null
  loading?: boolean
  submitText?: string
  onSubmit: (payload: TaskItemCreate) => Promise<void> | void
}

const DEFAULT_VALUES: TaskFormValues = {
  title: '',
  priority: 'medium',
  difficulty: 'normal',
  estimated_minutes: 60,
  status: 'pending',
  is_splittable: true,
}

function normalizeValues(values: TaskFormValues): TaskItemCreate {
  return {
    title: values.title.trim(),
    description: values.description?.trim() || null,
    category: values.category?.trim() || null,
    project: values.project?.trim() || null,
    priority: values.priority,
    difficulty: values.difficulty || 'normal',
    estimated_minutes: Number(values.estimated_minutes),
    deadline: values.deadline || null,
    status: values.status,
    is_splittable: values.is_splittable,
    source_type: 'manual',
  }
}

export function TaskForm({ initialTask, loading = false, submitText = '保存任务', onSubmit }: TaskFormProps) {
  const [form] = Form.useForm<TaskFormValues>()

  useEffect(() => {
    if (initialTask) {
      form.setFieldsValue({
        title: initialTask.title,
        description: initialTask.description || undefined,
        category: initialTask.category || undefined,
        project: initialTask.project || undefined,
        priority: initialTask.priority,
        difficulty: initialTask.difficulty || 'normal',
        estimated_minutes: initialTask.estimated_minutes,
        deadline: initialTask.deadline || undefined,
        status: initialTask.status,
        is_splittable: initialTask.is_splittable,
      })
    } else {
      form.setFieldsValue(DEFAULT_VALUES)
    }
  }, [form, initialTask])

  async function handleFinish(values: TaskFormValues) {
    await onSubmit(normalizeValues(values))
    if (!initialTask) form.resetFields()
  }

  return (
    <Form form={form} layout="vertical" onFinish={handleFinish} initialValues={DEFAULT_VALUES}>
      <div className="form-grid">
        <Form.Item label="标题" name="title" rules={[{ required: true, message: '请输入任务标题' }]}>
          <Input placeholder="例如：黑马 RAG 和 Agent 项目" />
        </Form.Item>
        <Form.Item label="分类" name="category">
          <Input placeholder="项目 / 论文 / 考试 / 课程" />
        </Form.Item>
        <Form.Item label="项目" name="project">
          <Input placeholder="可选" />
        </Form.Item>
        <Form.Item label="优先级" name="priority" rules={[{ required: true }]}>
          <Select
            options={[
              { value: 'low', label: '低' },
              { value: 'medium', label: '中' },
              { value: 'high', label: '高' },
              { value: 'urgent', label: '紧急' },
            ]}
          />
        </Form.Item>
        <Form.Item label="难度" name="difficulty">
          <Select
            options={[
              { value: 'easy', label: '简单' },
              { value: 'normal', label: '适中' },
              { value: 'hard', label: '偏难' },
              { value: 'very_hard', label: '过难' },
            ]}
          />
        </Form.Item>
        <Form.Item label="预计耗时（分钟）" name="estimated_minutes" rules={[{ required: true, type: 'number', min: 5 }]}>
          <InputNumber min={5} max={10000} style={{ width: '100%' }} />
        </Form.Item>
        <Form.Item label="截止日期" name="deadline">
          <Input type="date" />
        </Form.Item>
        <Form.Item label="状态" name="status">
          <Select
            options={[
              { value: 'pending', label: '待完成' },
              { value: 'scheduled', label: '已安排' },
              { value: 'in_progress', label: '进行中' },
              { value: 'completed', label: '已完成' },
              { value: 'delayed', label: '已延期' },
              { value: 'skipped', label: '已跳过' },
              { value: 'cancelled', label: '已取消' },
            ]}
          />
        </Form.Item>
        <Form.Item label="可拆分" name="is_splittable" valuePropName="checked">
          <Switch />
        </Form.Item>
      </div>
      <Form.Item label="描述" name="description">
        <Input.TextArea rows={3} maxLength={1000} placeholder="说明任务背景、期望产出或约束" />
      </Form.Item>
      <Button type="primary" htmlType="submit" loading={loading}>
        {submitText}
      </Button>
    </Form>
  )
}
