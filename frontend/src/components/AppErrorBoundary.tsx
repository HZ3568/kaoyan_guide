import { Component, type ErrorInfo, type ReactNode } from 'react'
import { Alert, Button, Card, Typography } from 'antd'

interface AppErrorBoundaryProps {
  children: ReactNode
}

interface AppErrorBoundaryState {
  error: Error | null
}

export class AppErrorBoundary extends Component<AppErrorBoundaryProps, AppErrorBoundaryState> {
  state: AppErrorBoundaryState = { error: null }

  static getDerivedStateFromError(error: Error): AppErrorBoundaryState {
    return { error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Frontend render error', error, info)
  }

  render() {
    if (!this.state.error) return this.props.children

    return (
      <div className="login-page">
        <Card className="login-card">
          <Typography.Title level={3}>页面加载失败</Typography.Title>
          <Alert
            type="error"
            showIcon
            message={this.state.error.message || '前端渲染时发生错误'}
            description="请刷新页面。如果仍然出现该提示，请查看浏览器控制台错误。"
          />
          <Button className="block-gap" type="primary" onClick={() => window.location.reload()}>
            刷新页面
          </Button>
        </Card>
      </div>
    )
  }
}
