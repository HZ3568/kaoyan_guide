import type { ReactElement } from 'react'
import { useEffect, useState } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { ApiError } from '../api/client'
import { getMyProfile } from '../api/profiles'
import { MainLayout } from '../components/MainLayout'
import { Loading } from '../components/Loading'
import { useAuthStore } from '../stores/authStore'
import DashboardPage from '../pages/DashboardPage'
import GoalsPage from '../pages/GoalsPage'
import KnowledgeBasePage from '../pages/KnowledgeBasePage'
import LoginPage from '../pages/LoginPage'
import OnboardingPage from '../pages/OnboardingPage'
import RagChatPage from '../pages/RagChatPage'
import ReviewPage from '../pages/ReviewPage'
import SearchDebugPage from '../pages/SearchDebugPage'
import TaskCalendarPage from '../pages/TaskCalendarPage'

function RequireAuth({ children }: { children: ReactElement }) {
  const token = useAuthStore((state) => state.token)
  if (!token) return <Navigate to="/login" replace />
  return children
}

function RequireProfile({ children }: { children: ReactElement }) {
  const [checking, setChecking] = useState(true)
  const [needsOnboarding, setNeedsOnboarding] = useState(false)

  useEffect(() => {
    let cancelled = false
    getMyProfile()
      .then(() => {
        if (!cancelled) setNeedsOnboarding(false)
      })
      .catch((err) => {
        if (cancelled) return
        if (err instanceof ApiError && err.status === 404) {
          setNeedsOnboarding(true)
        } else {
          setNeedsOnboarding(false)
        }
      })
      .finally(() => {
        if (!cancelled) setChecking(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  if (checking) return <Loading tip="正在检查学习画像" />
  if (needsOnboarding) return <Navigate to="/onboarding" replace />
  return children
}

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/onboarding"
        element={
          <RequireAuth>
            <OnboardingPage />
          </RequireAuth>
        }
      />
      <Route
        path="/"
        element={
          <RequireAuth>
            <RequireProfile>
              <MainLayout />
            </RequireProfile>
          </RequireAuth>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="goals" element={<GoalsPage />} />
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
        <Route path="reviews" element={<ReviewPage />} />
      </Route>
    </Routes>
  )
}
