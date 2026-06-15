import { Button, Layout, Menu } from 'antd'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

const { Header, Sider, Content } = Layout

export function MainLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const logout = useAuthStore((s) => s.logout)
  const selectedKey = location.pathname === '/planner' || location.pathname === '/tasks/today'
    ? location.pathname === '/planner' ? '/tasks' : '/today'
    : location.pathname

  return (
    <Layout className="layout">
      <Sider theme="light" width={232} breakpoint="lg" collapsedWidth={0}>
        <div className="brand">kaoyan-guide</div>
        <Menu
          mode="inline"
          selectedKeys={[selectedKey]}
          items={[
            { key: '/', label: '工作台', onClick: () => navigate('/') },
            { key: '/knowledge-base', label: '知识库', onClick: () => navigate('/knowledge-base') },
            { key: '/rag-chat', label: 'RAG 问答', onClick: () => navigate('/rag-chat') },
            { key: '/tasks', label: '任务池', onClick: () => navigate('/tasks') },
            { key: '/today', label: '今日任务', onClick: () => navigate('/today') },
            { key: '/calendar', label: '任务日历', onClick: () => navigate('/calendar') },
            { key: '/rag-task-recommend', label: 'RAG 推荐任务', onClick: () => navigate('/rag-task-recommend') },
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
