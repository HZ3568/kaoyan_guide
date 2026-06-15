import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import App from './App'
import { AppErrorBoundary } from './components/AppErrorBoundary'
import './styles.css'

const queryClient = new QueryClient()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <ConfigProvider locale={zhCN}>
        <AppErrorBoundary>
          <App />
        </AppErrorBoundary>
      </ConfigProvider>
    </QueryClientProvider>
  </React.StrictMode>,
)
