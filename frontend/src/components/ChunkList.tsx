import { Collapse, Empty, Tag, Typography } from 'antd'
import type { DocumentChunk } from '../api/documents'

interface ChunkListProps {
  chunks: DocumentChunk[]
}

export function ChunkList({ chunks }: ChunkListProps) {
  if (chunks.length === 0) return <Empty description="暂无 chunk" />

  return (
    <Collapse
      items={chunks.map((chunk) => ({
        key: chunk.id,
        label: (
          <div className="inline-row">
            <Typography.Text>#{chunk.chunk_index}</Typography.Text>
            <Tag>{chunk.chunk_type}</Tag>
            <Tag>{chunk.token_count} tokens</Tag>
            <Tag color={chunk.is_vectorized ? 'green' : 'orange'}>{chunk.is_vectorized ? '已向量化' : '未向量化'}</Tag>
            {chunk.page_number && <Tag>page {chunk.page_number}</Tag>}
          </div>
        ),
        children: (
          <div>
            <Typography.Paragraph className="chunk-content">{chunk.content}</Typography.Paragraph>
            <Typography.Text type="secondary">document_id: {chunk.document_id}，chunk_id: {chunk.id}</Typography.Text>
            {chunk.metadata_json && (
              <pre className="json-block">{JSON.stringify(chunk.metadata_json, null, 2)}</pre>
            )}
          </div>
        ),
      }))}
    />
  )
}

