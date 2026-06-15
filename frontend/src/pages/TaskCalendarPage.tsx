import { Button, Card, Space, Typography, message } from 'antd'
import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getDailyPlanByDate } from '../api/dailyPlans'
import type { DailyPlan } from '../api/dailyPlans'
import { DailyPlanCard } from '../components/DailyPlanCard'
import { ErrorMessage } from '../components/ErrorMessage'
import { Loading } from '../components/Loading'

function toDateKey(date: Date) {
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${date.getFullYear()}-${month}-${day}`
}

function monthDays(monthCursor: Date) {
  const year = monthCursor.getFullYear()
  const month = monthCursor.getMonth()
  const first = new Date(year, month, 1)
  const last = new Date(year, month + 1, 0)
  const days: Date[] = []
  for (let day = 1; day <= last.getDate(); day += 1) {
    days.push(new Date(year, month, day))
  }
  const startPadding = first.getDay()
  const prefix = Array.from({ length: startPadding }, (_, index) => new Date(year, month, index - startPadding + 1))
  const suffixCount = (7 - ((prefix.length + days.length) % 7)) % 7
  const suffix = Array.from({ length: suffixCount }, (_, index) => new Date(year, month + 1, index + 1))
  return [...prefix, ...days, ...suffix]
}

function planStats(plan?: DailyPlan | null) {
  const tasks = plan?.tasks || []
  return {
    count: tasks.length,
    completed: tasks.filter((task) => task.status === 'completed').length,
    titles: tasks.slice(0, 2).map((task) => task.task?.title || `任务 #${task.task_id}`),
  }
}

export default function TaskCalendarPage() {
  const navigate = useNavigate()
  const todayKey = toDateKey(new Date())
  const [monthCursor, setMonthCursor] = useState(() => new Date())
  const [selectedDate, setSelectedDate] = useState(todayKey)
  const [plansByDate, setPlansByDate] = useState<Record<string, DailyPlan | null>>({})
  const [loadingMonth, setLoadingMonth] = useState(false)
  const [loadingSelected, setLoadingSelected] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const days = useMemo(() => monthDays(monthCursor), [monthCursor])
  const selectedPlan = plansByDate[selectedDate] || null

  async function loadMonth(cursor: Date) {
    setLoadingMonth(true)
    setError(null)
    try {
      const currentMonthDays = monthDays(cursor).filter((date) => date.getMonth() === cursor.getMonth())
      const pairs = await Promise.all(
        currentMonthDays.map(async (date) => {
          const key = toDateKey(date)
          try {
            return [key, await getDailyPlanByDate(key)] as const
          } catch {
            return [key, null] as const
          }
        }),
      )
      setPlansByDate((current) => ({ ...current, ...Object.fromEntries(pairs) }))
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载日历任务失败')
    } finally {
      setLoadingMonth(false)
    }
  }

  async function loadSelected(dateKey: string) {
    if (dateKey in plansByDate) return
    setLoadingSelected(true)
    try {
      const plan = await getDailyPlanByDate(dateKey)
      setPlansByDate((current) => ({ ...current, [dateKey]: plan }))
    } catch (err) {
      message.error(err instanceof Error ? err.message : '加载日期计划失败')
    } finally {
      setLoadingSelected(false)
    }
  }

  useEffect(() => {
    void loadMonth(monthCursor)
  }, [monthCursor])

  useEffect(() => {
    void loadSelected(selectedDate)
  }, [selectedDate])

  function shiftMonth(offset: number) {
    setMonthCursor((current) => new Date(current.getFullYear(), current.getMonth() + offset, 1))
  }

  return (
    <div className="page">
      <div className="page-title-row">
        <div>
          <Typography.Title level={2}>任务日历</Typography.Title>
          <Typography.Text type="secondary">按日期查看每日计划，适合回顾延期、完成和待处理任务。</Typography.Text>
        </div>
        <Space>
          <Button onClick={() => shiftMonth(-1)}>上个月</Button>
          <Button onClick={() => setMonthCursor(new Date())}>回到本月</Button>
          <Button onClick={() => shiftMonth(1)}>下个月</Button>
        </Space>
      </div>
      <ErrorMessage message={error} />

      <div className="two-column-layout">
        <Card
          title={`${monthCursor.getFullYear()} 年 ${monthCursor.getMonth() + 1} 月`}
          extra={loadingMonth ? <Typography.Text type="secondary">同步中</Typography.Text> : null}
        >
          <div className="calendar-weekdays">
            {['日', '一', '二', '三', '四', '五', '六'].map((item) => <span key={item}>{item}</span>)}
          </div>
          <div className="calendar-grid">
            {days.map((date) => {
              const key = toDateKey(date)
              const isCurrentMonth = date.getMonth() === monthCursor.getMonth()
              const stats = planStats(plansByDate[key])
              const isSelected = key === selectedDate
              const isToday = key === todayKey
              return (
                <button
                  key={key}
                  type="button"
                  className={`calendar-cell ${isCurrentMonth ? '' : 'muted'} ${isSelected ? 'selected' : ''} ${isToday ? 'today' : ''}`}
                  onClick={() => setSelectedDate(key)}
                >
                  <span className="calendar-date">{date.getDate()}</span>
                  {stats.count > 0 ? (
                    <span className="calendar-count">{stats.completed}/{stats.count} 完成</span>
                  ) : (
                    <span className="calendar-count muted-text">暂无任务</span>
                  )}
                  {stats.titles.map((title) => (
                    <span key={title} className="calendar-task-title">{title}</span>
                  ))}
                </button>
              )
            })}
          </div>
        </Card>

        <div>
          {loadingSelected ? (
            <Loading tip="正在加载日期任务" />
          ) : (
            <DailyPlanCard
              plan={selectedPlan}
              title={`${selectedDate} 任务详情`}
              onEmptyAction={() => navigate(selectedDate === todayKey ? '/today' : '/tasks')}
            />
          )}
        </div>
      </div>
    </div>
  )
}
