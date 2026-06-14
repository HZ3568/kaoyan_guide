import type { ReactElement } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { MainLayout } from '../components/MainLayout'
import LoginPage from '../pages/LoginPage'
import DashboardPage from '../pages/DashboardPage'
import KnowledgeBasePage from '../pages/KnowledgeBasePage'
import RagChatPage from '../pages/RagChatPage'
import PlannerPage from '../pages/PlannerPage'
import TasksPage from '../pages/TasksPage'

function RequireAuth({ children }: { children: ReactElement }) {
  const token = useAuthStore((s) => s.token)
  if (!token) return <Navigate to="/login" replace />
  return children
}

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <RequireAuth>
            <MainLayout />
          </RequireAuth>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="knowledge" element={<KnowledgeBasePage />} />
        <Route path="rag" element={<RagChatPage />} />
        <Route path="planner" element={<PlannerPage />} />
        <Route path="tasks" element={<TasksPage />} />
      </Route>
    </Routes>
  )
}
