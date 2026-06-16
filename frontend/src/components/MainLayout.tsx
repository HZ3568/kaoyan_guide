import { Button, Layout, Menu, Select, Space, Typography } from 'antd'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useCurrentGoal } from '../hooks/useCurrentGoal'
import { useAuthStore } from '../stores/authStore'
import { useGoalStore } from '../stores/goalStore'

const { Header, Sider, Content } = Layout

export function MainLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const logout = useAuthStore((state) => state.logout)
  const clearCurrentGoal = useGoalStore((state) => state.clearCurrentGoal)
  const { activeGoals, currentGoalId, setCurrentGoalId, loading } = useCurrentGoal()
  const selectedKey = ['/planner', '/tasks', '/tasks/today', '/today'].includes(location.pathname)
    ? '/calendar'
    : location.pathname

  function handleLogout() {
    clearCurrentGoal()
    logout()
    navigate('/login')
  }

  return (
    <Layout className="layout">
      <Sider theme="light" width={236} breakpoint="lg" collapsedWidth={0}>
        <div className="brand">
          <span className="brand-mark">LG</span>
          <span>Learning Growth</span>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[selectedKey]}
          items={[
            { key: '/', label: '工作台', onClick: () => navigate('/') },
            { key: '/goals', label: '目标管理', onClick: () => navigate('/goals') },
            { key: '/knowledge-base', label: '知识库', onClick: () => navigate('/knowledge-base') },
            { key: '/rag-chat', label: 'RAG 问答', onClick: () => navigate('/rag-chat') },
            { key: '/calendar', label: '学习日历', onClick: () => navigate('/calendar') },
            { key: '/reviews', label: '每日复盘', onClick: () => navigate('/reviews') },
            { key: '/rag-debug', label: '检索调试', onClick: () => navigate('/rag-debug') },
          ]}
        />
      </Sider>
      <Layout>
        <Header className="topbar">
          <Space wrap>
            <Typography.Text type="secondary">当前目标</Typography.Text>
            <Select
              loading={loading}
              value={currentGoalId ?? undefined}
              placeholder="选择目标"
              style={{ minWidth: 220 }}
              options={activeGoals.map((goal) => ({ value: goal.id, label: goal.title }))}
              onChange={(goalId) => setCurrentGoalId(goalId)}
              onFocus={() => {
                if (!activeGoals.length) navigate('/goals')
              }}
            />
            <Button onClick={() => navigate('/goals')}>管理目标</Button>
            <Button onClick={handleLogout}>退出登录</Button>
          </Space>
        </Header>
        <Content>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
