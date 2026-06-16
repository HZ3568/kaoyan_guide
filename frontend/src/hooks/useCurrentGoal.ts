import { useEffect, useMemo, useState } from 'react'
import { listGoals } from '../api/goals'
import type { Goal } from '../api/goals'
import { useGoalStore } from '../stores/goalStore'

export function useCurrentGoal() {
  const currentGoalId = useGoalStore((state) => state.currentGoalId)
  const setCurrentGoalId = useGoalStore((state) => state.setCurrentGoalId)
  const [goals, setGoals] = useState<Goal[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function refreshGoals() {
    setLoading(true)
    setError(null)
    try {
      const items = await listGoals()
      setGoals(items)
      const activeGoals = items.filter((goal) => goal.status !== 'archived')
      const currentStillExists = activeGoals.some((goal) => goal.id === currentGoalId)
      if (!currentStillExists) {
        const preferred = activeGoals.find((goal) => goal.status === 'active') || activeGoals[0] || null
        setCurrentGoalId(preferred?.id ?? null)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载目标失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void refreshGoals()
    // currentGoalId intentionally stays out to avoid refetching after local selection.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const currentGoal = useMemo(
    () => goals.find((goal) => goal.id === currentGoalId) || null,
    [currentGoalId, goals],
  )

  return {
    goals,
    activeGoals: goals.filter((goal) => goal.status !== 'archived'),
    currentGoal,
    currentGoalId,
    setCurrentGoalId,
    loading,
    error,
    refreshGoals,
  }
}
