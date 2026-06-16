import { Button, Card, Collapse, Form, Input, InputNumber, Space, Typography } from 'antd'
import type { KeyboardEvent } from 'react'
import { useState } from 'react'
import { askRag } from '../api/rag'
import type { RagAskResponse } from '../api/rag'
import { ErrorMessage } from '../components/ErrorMessage'
import { SourceList } from '../components/SourceList'

interface AskFormValues {
  question: string
  top_k: number
}

export default function RagChatPage() {
  const [form] = Form.useForm<AskFormValues>()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [records, setRecords] = useState<Array<{ id: number; question: string; response: RagAskResponse }>>([])

  async function ask(values: AskFormValues) {
    const question = values.question.trim()
    setLoading(true)
    setError(null)
    try {
      const response = await askRag({ question, top_k: values.top_k || 5 })
      setRecords((current) => [{ id: Date.now(), question, response }, ...current])
      form.setFieldValue('question', '')
    } catch (err) {
      setError(err instanceof Error ? err.message : '问答失败')
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      form.submit()
    }
  }

  return (
    <div className="page">
      <Typography.Title level={2}>RAG 问答</Typography.Title>
      <ErrorMessage message={error} />

      <Card>
        <Form form={form} layout="vertical" onFinish={ask} initialValues={{ top_k: 5 }}>
          <Form.Item
            label="问题"
            name="question"
            rules={[{ required: true, message: '请输入问题' }]}
          >
            <Input.TextArea
              rows={5}
              onKeyDown={handleKeyDown}
              placeholder="例如：这份资料建议我优先实践哪些步骤？"
            />
          </Form.Item>
          <Form.Item label="TopK" name="top_k" rules={[{ required: true, type: 'number', min: 1, max: 20 }]}>
            <InputNumber min={1} max={20} style={{ width: 160 }} />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={loading}>
            {loading ? '正在检索知识库并生成回答' : '提问'}
          </Button>
        </Form>
      </Card>

      <div className="chat-records">
        {records.length === 0 ? (
          <Card className="block-gap">
            <Typography.Text type="secondary">暂无问答记录。输入问题后会在这里展示回答、来源和检索调试信息。</Typography.Text>
          </Card>
        ) : (
          records.map(({ id, question, response }) => (
            <Card key={id} className="block-gap" title={question}>
              <Typography.Paragraph className="answer-text">{response.answer}</Typography.Paragraph>
              <Space wrap>
                <Typography.Text type="secondary">命中来源：{response.hit_source ? '是' : '否'}</Typography.Text>
                {response.model_provider && <Typography.Text type="secondary">模型：{response.model_provider}/{response.model_name}</Typography.Text>}
                {response.log_id && <Typography.Text type="secondary">日志 ID：{response.log_id}</Typography.Text>}
              </Space>
              <Card className="block-gap" size="small" title="引用来源">
                <SourceList sources={response.sources} emptyText="当前回答没有引用来源" />
              </Card>
              <Collapse
                className="block-gap"
                items={[
                  {
                    key: 'debug',
                    label: 'retrieval_debug',
                    children: <pre className="json-block">{JSON.stringify(response.retrieval_debug, null, 2)}</pre>,
                  },
                  {
                    key: 'chunks',
                    label: '检索到的 chunks',
                    children: <SourceList sources={response.sources} emptyText="暂无 chunks" />,
                  },
                ]}
              />
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
