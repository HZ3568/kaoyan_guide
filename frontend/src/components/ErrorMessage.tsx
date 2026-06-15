import { Alert } from 'antd'

interface ErrorMessageProps {
  message?: string | null
}

export function ErrorMessage({ message }: ErrorMessageProps) {
  if (!message) return null
  return <Alert className="block-gap" type="error" showIcon message={message} />
}

