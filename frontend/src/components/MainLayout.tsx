import { Layout, Menu, Button } from 'antd'
import { Outlet, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

const { Header, Sider, Content } = Layout

export function MainLayout() {
  const navigate = useNavigate()
  const logout = useAuthStore((s) => s.logout)

  return (
    <Layout className="layout">
      <Sider theme="light">
        <div style={{ padding: 20, fontWeight: 700 }}>kaoyan-guide</div>
        <Menu
          mode="inline"
          defaultSelectedKeys={[location.pathname]}
          items={[
            { key: '/', label: '首页仪表盘', onClick: () => navigate('/') },
            { key: '/knowledge', label: '知识库管理', onClick: () => navigate('/knowledge') },
            { key: '/rag', label: 'RAG 问答', onClick: () => navigate('/rag') },
            { key: '/planner', label: '学习规划', onClick: () => navigate('/planner') },
            { key: '/tasks', label: '今日任务', onClick: () => navigate('/tasks') },
          ]}
        />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', display: 'flex', justifyContent: 'flex-end' }}>
          <Button onClick={() => { logout(); navigate('/login') }}>退出登录</Button>
        </Header>
        <Content>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
