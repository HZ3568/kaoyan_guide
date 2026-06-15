import { Button, Empty, Typography } from 'antd'
import type { ReactNode } from 'react'

interface EmptyStateProps {
  title?: string
  description: string
  actionText?: string
  onAction?: () => void
  extra?: ReactNode
}

export function EmptyState({ title, description, actionText, onAction, extra }: EmptyStateProps) {
  return (
    <div className="empty-state">
      <Empty
        description={
          <div>
            {title && <Typography.Text strong>{title}</Typography.Text>}
            <Typography.Paragraph className="compact-paragraph">{description}</Typography.Paragraph>
          </div>
        }
      >
        {actionText && onAction && (
          <Button type="primary" onClick={onAction}>
            {actionText}
          </Button>
        )}
        {extra}
      </Empty>
    </div>
  )
}
