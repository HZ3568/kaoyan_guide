import { Card, Spin } from 'antd'

interface LoadingProps {
  tip?: string
}

export function Loading({ tip = '加载中' }: LoadingProps) {
  return (
    <Card>
      <div className="center-state">
        <Spin />
        <span>{tip}</span>
      </div>
    </Card>
  )
}

