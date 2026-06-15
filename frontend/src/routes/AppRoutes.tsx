import type { ReactElement } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { MainLayout } from '../components/MainLayout'
import LoginPage from '../pages/LoginPage'
import DashboardPage from '../pages/DashboardPage'
import KnowledgeBasePage from '../pages/KnowledgeBasePage'
import RagChatPage from '../pages/RagChatPage'
import SearchDebugPage from '../pages/SearchDebugPage'
import TaskCalendarPage from '../pages/TaskCalendarPage'

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
        <Route path="knowledge" element={<Navigate to="/knowledge-base" replace />} />
        <Route path="knowledge-base" element={<KnowledgeBasePage />} />
        <Route path="rag" element={<Navigate to="/rag-chat" replace />} />
        <Route path="rag-chat" element={<RagChatPage />} />
        <Route path="rag-debug" element={<SearchDebugPage />} />
        <Route path="planner" element={<Navigate to="/calendar" replace />} />
        <Route path="tasks" element={<Navigate to="/calendar" replace />} />
        <Route path="tasks/today" element={<Navigate to="/calendar" replace />} />
        <Route path="today" element={<Navigate to="/calendar" replace />} />
        <Route path="calendar" element={<TaskCalendarPage />} />
      </Route>
    </Routes>
  )
}
