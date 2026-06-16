import { Button, Layout, Menu } from 'antd'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

const { Header, Sider, Content } = Layout

export function MainLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const logout = useAuthStore((s) => s.logout)
  const selectedKey = ['/planner', '/tasks', '/tasks/today', '/today'].includes(location.pathname)
    ? '/calendar'
    : location.pathname

  return (
    <Layout className="layout">
      <Sider theme="light" width={232} breakpoint="lg" collapsedWidth={0}>
        <div className="brand">Learning Growth</div>
        <Menu
          mode="inline"
          selectedKeys={[selectedKey]}
          items={[
            { key: '/', label: '工作台', onClick: () => navigate('/') },
            { key: '/knowledge-base', label: '知识库', onClick: () => navigate('/knowledge-base') },
            { key: '/rag-chat', label: 'RAG 问答', onClick: () => navigate('/rag-chat') },
            { key: '/calendar', label: '学习日历', onClick: () => navigate('/calendar') },
            { key: '/rag-debug', label: '检索调试', onClick: () => navigate('/rag-debug') },
          ]}
        />
      </Sider>
      <Layout>
        <Header className="topbar">
          <Button onClick={() => { logout(); navigate('/login') }}>退出登录</Button>
        </Header>
        <Content>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
