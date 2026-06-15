import { Button, Card, Form, Input, InputNumber, Space, Table, Typography, message } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useState } from 'react'
import { searchRag } from '../api/rag'
import type { RagSearchResult } from '../api/rag'
import { ErrorMessage } from '../components/ErrorMessage'

interface SearchFormValues {
  query: string
  top_k: number
}

export default function SearchDebugPage() {
  const [form] = Form.useForm<SearchFormValues>()
  const [results, setResults] = useState<RagSearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function search(values: SearchFormValues) {
    setLoading(true)
    setError(null)
    try {
      setResults(await searchRag({ query: values.query.trim(), top_k: values.top_k || 5 }))
    } catch (err) {
      setError(err instanceof Error ? err.message : '检索失败')
    } finally {
      setLoading(false)
    }
  }

  async function copy(text: string) {
    await navigator.clipboard.writeText(text)
    message.success('已复制')
  }

  const columns: ColumnsType<RagSearchResult> = [
    { title: 'Rank', render: (_, __, index) => index + 1, width: 70 },
    { title: 'Score', dataIndex: 'score', width: 110, render: (value: number) => value.toFixed(4) },
    {
      title: 'ID',
      width: 180,
      render: (_, record) => (
        <Space direction="vertical" size={2}>
          <Button size="small" onClick={() => copy(String(record.document_id))}>doc {record.document_id}</Button>
          <Button size="small" onClick={() => copy(String(record.chunk_id))}>chunk {record.chunk_id}</Button>
        </Space>
      ),
    },
    {
      title: '来源',
      width: 220,
      render: (_, record) => (
        <div>
          <Typography.Text>{String(record.source.title || record.source.file_name || record.source.source || '-')}</Typography.Text>
          <div className="muted-text">page: {record.page_number || '-'}</div>
        </div>
      ),
    },
    {
      title: '内容',
      dataIndex: 'content',
      render: (value: string) => <Typography.Paragraph className="chunk-content">{value}</Typography.Paragraph>,
    },
    {
      title: 'metadata',
      width: 240,
      render: (_, record) => <pre className="json-block compact">{JSON.stringify(record.metadata, null, 2)}</pre>,
    },
  ]

  return (
    <div className="page">
      <Typography.Title level={2}>检索调试</Typography.Title>
      <ErrorMessage message={error} />

      <Card>
        <Form form={form} layout="inline" onFinish={search} initialValues={{ top_k: 5 }}>
          <Form.Item name="query" rules={[{ required: true, message: '请输入检索 query' }]} className="flex-form-item">
            <Input placeholder="输入 query" />
          </Form.Item>
          <Form.Item name="top_k" rules={[{ required: true, type: 'number', min: 1, max: 20 }]}>
            <InputNumber min={1} max={20} />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={loading}>检索</Button>
        </Form>
      </Card>

      <Card className="block-gap" title="TopK 结果">
        <Table
          rowKey="chunk_id"
          columns={columns}
          dataSource={results}
          loading={loading}
          locale={{ emptyText: '暂无检索结果' }}
          pagination={{ pageSize: 5 }}
        />
      </Card>
    </div>
  )
}

