import { Button, Card, Input, Typography } from 'antd'
import { useState } from 'react'
import { ragChat } from '../api/rag'

export default function RagChatPage() {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')

  async function ask() {
    const res = await ragChat(question)
    setAnswer(res.answer)
  }

  return (
    <div className="page">
      <Typography.Title level={2}>RAG 问答</Typography.Title>
      <Card>
        <Input.TextArea rows={4} value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="请输入考研相关问题" />
        <Button type="primary" style={{ marginTop: 12 }} onClick={ask}>提问</Button>
      </Card>
      {answer && <Card style={{ marginTop: 16, whiteSpace: 'pre-wrap' }}>{answer}</Card>}
    </div>
  )
}
