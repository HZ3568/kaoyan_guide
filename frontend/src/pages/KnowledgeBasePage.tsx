import { Button, Card, Upload, message, Typography } from 'antd'
import type { UploadProps } from 'antd'
import { uploadDocument } from '../api/rag'

export default function KnowledgeBasePage() {
  const props: UploadProps = {
    beforeUpload: async (file) => {
      await uploadDocument(file)
      message.success('上传并解析完成')
      return false
    },
  }

  return (
    <div className="page">
      <Typography.Title level={2}>知识库管理</Typography.Title>
      <Card>
        <Upload {...props} maxCount={1}>
          <Button type="primary">上传文档</Button>
        </Upload>
        <p>支持 TXT/Markdown 直接解析；PDF、Word、图片 OCR 当前为占位逻辑，后续在 IngestionService 中扩展。</p>
      </Card>
    </div>
  )
}
