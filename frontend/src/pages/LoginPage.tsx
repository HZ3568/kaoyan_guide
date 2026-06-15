import { Button, Card, Form, Input, Space, Typography, message } from 'antd'
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
    } catch (error) {
      message.error(error instanceof Error ? error.message : '登录失败，请先注册或检查账号密码')
    }
  }

  async function handleRegister() {
    const values = await form.validateFields()
    try {
      await register(values)
      message.success('注册成功，请登录')
    } catch (error) {
      message.error(error instanceof Error ? error.message : '注册失败')
    }
  }

  return (
    <div className="login-page">
      <Card className="login-card">
        <Typography.Title level={3}>考研 RAG 学习系统</Typography.Title>
        <Form form={form} layout="vertical">
          <Form.Item label="用户名" name="username" rules={[{ required: true, min: 3, message: '请输入至少 3 位用户名' }]}>
            <Input />
          </Form.Item>
          <Form.Item label="密码" name="password" rules={[{ required: true, min: 6, message: '请输入至少 6 位密码' }]}>
            <Input.Password />
          </Form.Item>
          <Space className="full-width" direction="vertical">
            <Button type="primary" block onClick={handleLogin}>登录</Button>
            <Button block onClick={handleRegister}>注册</Button>
          </Space>
        </Form>
      </Card>
    </div>
  )
}

