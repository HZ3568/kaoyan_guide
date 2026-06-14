import { Button, Card, Form, Input, Typography, message, Space } from 'antd'
import { useNavigate } from 'react-router-dom'
import { login, register } from '../api/auth'
import { useAuthStore } from '../stores/authStore'

export default function LoginPage() {
  const [form] = Form.useForm()
  const navigate = useNavigate()
  const setToken = useAuthStore((s) => s.setToken)

  async function handleLogin() {
    const values = await form.validateFields()
    try {
      const res = await login(values)
      setToken(res.access_token)
      navigate('/')
    } catch {
      message.error('登录失败，请先注册或检查账号密码')
    }
  }

  async function handleRegister() {
    const values = await form.validateFields()
    await register(values)
    message.success('注册成功，请登录')
  }

  return (
    <div style={{ minHeight: '100vh', display: 'grid', placeItems: 'center' }}>
      <Card style={{ width: 400 }}>
        <Typography.Title level={3}>考研 RAG 学习系统</Typography.Title>
        <Form form={form} layout="vertical">
          <Form.Item label="用户名" name="username" rules={[{ required: true, min: 3 }]}> <Input /> </Form.Item>
          <Form.Item label="密码" name="password" rules={[{ required: true, min: 6 }]}> <Input.Password /> </Form.Item>
          <Space style={{ width: '100%' }} direction="vertical">
            <Button type="primary" block onClick={handleLogin}>登录</Button>
            <Button block onClick={handleRegister}>注册</Button>
          </Space>
        </Form>
      </Card>
    </div>
  )
}
