import { Button, Form, Input, InputNumber, Modal, Select } from 'antd'
import type { TaskFeedbackCreate } from '../api/dailyPlans'

interface FeedbackModalProps {
  open: boolean
  submitting?: boolean
  onCancel: () => void
  onSubmit: (payload: TaskFeedbackCreate) => Promise<void> | void
}

export function FeedbackModal({ open, submitting = false, onCancel, onSubmit }: FeedbackModalProps) {
  const [form] = Form.useForm<TaskFeedbackCreate>()

  async function submit() {
    const values = await form.validateFields()
    await onSubmit(values)
    form.resetFields()
  }

  return (
    <Modal
      title="提交任务反馈"
      open={open}
      onCancel={onCancel}
      footer={[
        <Button key="cancel" onClick={onCancel}>
          取消
        </Button>,
        <Button key="submit" type="primary" loading={submitting} onClick={submit}>
          提交反馈
        </Button>,
      ]}
    >
      <Form form={form} layout="vertical">
        <Form.Item label="实际用时（分钟）" name="actual_minutes">
          <InputNumber min={0} max={1440} style={{ width: '100%' }} />
        </Form.Item>
        <Form.Item label="难度反馈" name="difficulty_feedback">
          <Select
            allowClear
            options={[
              { value: 'easy', label: '简单' },
              { value: 'normal', label: '适中' },
              { value: 'hard', label: '偏难' },
              { value: 'very_hard', label: '过难' },
            ]}
          />
        </Form.Item>
        <Form.Item label="完成说明" name="completion_note">
          <Input.TextArea rows={4} maxLength={500} placeholder="记录完成情况、阻塞点或需要顺延的原因" />
        </Form.Item>
      </Form>
    </Modal>
  )
}
