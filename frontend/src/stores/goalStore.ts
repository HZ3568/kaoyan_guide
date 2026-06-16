import { create } from 'zustand'

interface GoalState {
  currentGoalId: number | null
  setCurrentGoalId: (goalId: number | null) => void
  clearCurrentGoal: () => void
}

const STORAGE_KEY = 'learning_growth_current_goal_id'

function readStoredGoalId() {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return null
  const parsed = Number(raw)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null
}

export const useGoalStore = create<GoalState>((set) => ({
  currentGoalId: readStoredGoalId(),
  setCurrentGoalId: (goalId) => {
    if (goalId) {
      localStorage.setItem(STORAGE_KEY, String(goalId))
    } else {
      localStorage.removeItem(STORAGE_KEY)
    }
    set({ currentGoalId: goalId })
  },
  clearCurrentGoal: () => {
    localStorage.removeItem(STORAGE_KEY)
    set({ currentGoalId: null })
  },
}))
