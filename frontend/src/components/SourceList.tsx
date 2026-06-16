import { List, Tag, Typography } from 'antd'
import type { RagSource } from '../api/rag'

type GenericSource = RagSource | Record<string, unknown>

interface SourceListProps {
  sources?: GenericSource[]
  emptyText?: string
}

function readString(source: GenericSource, key: string) {
  const value = source[key as keyof GenericSource]
  return typeof value === 'string' ? value : undefined
}

function readNumber(source: GenericSource, key: string) {
  const value = source[key as keyof GenericSource]
  return typeof value === 'number' ? value : undefined
}

export function SourceList({ sources = [], emptyText = '暂无来源' }: SourceListProps) {
  if (sources.length === 0) {
    return <Typography.Text type="secondary">{emptyText}</Typography.Text>
  }

  return (
    <List
      size="small"
      dataSource={sources}
      renderItem={(source, index) => {
        const title =
          readString(source, 'title') ||
          readString(source, 'original_filename') ||
          readString(source, 'filename') ||
          readString(source, 'file_name') ||
          readString(source, 'source') ||
          `来源 ${index + 1}`
        const score = readNumber(source, 'score')
        const chunkId = readNumber(source, 'chunk_id')
        const documentId = readNumber(source, 'document_id')
        const pageNumber = readNumber(source, 'page_number')
        const preview = readString(source, 'content_preview')

        return (
          <List.Item>
            <div className="list-item-body">
              <div className="inline-row">
                <Typography.Text strong>{title}</Typography.Text>
                {score !== undefined && <Tag color="blue">score {score.toFixed(4)}</Tag>}
                {documentId !== undefined && <Tag>doc {documentId}</Tag>}
                {chunkId !== undefined && <Tag>chunk {chunkId}</Tag>}
                {pageNumber !== undefined && <Tag>page {pageNumber}</Tag>}
                {readString(source, 'category') && <Tag>{readString(source, 'category')}</Tag>}
                {readString(source, 'domain') && <Tag color="blue">{readString(source, 'domain')}</Tag>}
              </div>
              {preview && <Typography.Paragraph className="source-preview">{preview}</Typography.Paragraph>}
            </div>
          </List.Item>
        )
      }}
    />
  )
}
