import { Input, InputNumber, Select, Typography, message } from 'antd'
import type { ReactNode } from 'react'
import { useEffect, useState } from 'react'

interface SelectOption {
  value: string
  label: string
}

interface EditableTextProps {
  value: string
  className?: string
  placeholder?: string
  multiline?: boolean
  strong?: boolean
  onSave: (value: string) => Promise<void> | void
}

export function EditableText({
  value,
  className,
  placeholder = '点击编辑',
  multiline = false,
  strong = true,
  onSave,
}: EditableTextProps) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(value)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!editing) setDraft(value)
  }, [editing, value])

  async function commit() {
    const nextValue = draft.trim()
    if (!nextValue) {
      message.error('内容不能为空')
      setDraft(value)
      setEditing(false)
      return
    }
    if (nextValue === value) {
      setEditing(false)
      return
    }
    setSaving(true)
    try {
      await onSave(nextValue)
      setEditing(false)
    } catch (err) {
      setDraft(value)
      message.error(err instanceof Error ? err.message : '保存失败')
    } finally {
      setSaving(false)
    }
  }

  if (editing) {
    if (multiline) {
      return (
        <Input.TextArea
          autoFocus
          className={className}
          disabled={saving}
          value={draft}
          autoSize={{ minRows: 2, maxRows: 5 }}
          onBlur={() => void commit()}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && (event.metaKey || event.ctrlKey)) {
              event.preventDefault()
              void commit()
            }
            if (event.key === 'Escape') {
              event.preventDefault()
              setDraft(value)
              setEditing(false)
            }
          }}
        />
      )
    }

    return (
      <Input
        autoFocus
        className={className}
        disabled={saving}
        value={draft}
        onBlur={() => void commit()}
        onChange={(event) => setDraft(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === 'Enter') {
            event.preventDefault()
            void commit()
          }
          if (event.key === 'Escape') {
            event.preventDefault()
            setDraft(value)
            setEditing(false)
          }
        }}
      />
    )
  }

  return (
    <Typography.Text
      strong={strong}
      className={`editable-value ${className || ''}`}
      title="点击编辑"
      onClick={() => setEditing(true)}
    >
      {value || placeholder}
    </Typography.Text>
  )
}

interface EditableSelectProps {
  value?: string | null
  options: SelectOption[]
  placeholder?: string
  className?: string
  children: ReactNode
  onSave: (value: string) => Promise<void> | void
}

export function EditableSelect({ value, options, placeholder = '选择', className, children, onSave }: EditableSelectProps) {
  const [editing, setEditing] = useState(false)
  const [saving, setSaving] = useState(false)

  async function commit(nextValue: string) {
    if (nextValue === value) {
      setEditing(false)
      return
    }
    setSaving(true)
    try {
      await onSave(nextValue)
      setEditing(false)
    } catch (err) {
      message.error(err instanceof Error ? err.message : '保存失败')
    } finally {
      setSaving(false)
    }
  }

  if (editing) {
    return (
      <Select
        autoFocus
        className={className || 'editable-select'}
        disabled={saving}
        value={value || undefined}
        placeholder={placeholder}
        options={options}
        onBlur={() => setEditing(false)}
        onChange={(nextValue) => void commit(nextValue)}
      />
    )
  }

  return (
    <span className="editable-trigger" title="点击编辑" onClick={() => setEditing(true)}>
      {children}
    </span>
  )
}

interface EditableNumberProps {
  value?: number | null
  min?: number
  max?: number
  suffix?: string
  children: ReactNode
  onSave: (value: number) => Promise<void> | void
}

export function EditableNumber({ value, min = 5, max = 10000, suffix, children, onSave }: EditableNumberProps) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState<number | null>(value ?? null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!editing) setDraft(value ?? null)
  }, [editing, value])

  async function commit() {
    if (draft === null || draft === undefined || Number.isNaN(draft)) {
      message.error('请输入预计耗时')
      setDraft(value ?? null)
      setEditing(false)
      return
    }
    const nextValue = Math.min(Math.max(Number(draft), min), max)
    if (nextValue === value) {
      setEditing(false)
      return
    }
    setSaving(true)
    try {
      await onSave(nextValue)
      setEditing(false)
    } catch (err) {
      setDraft(value ?? null)
      message.error(err instanceof Error ? err.message : '保存失败')
    } finally {
      setSaving(false)
    }
  }

  if (editing) {
    return (
      <InputNumber
        autoFocus
        disabled={saving}
        min={min}
        max={max}
        value={draft}
        addonAfter={suffix}
        className="editable-number"
        onBlur={() => void commit()}
        onChange={(nextValue) => setDraft(typeof nextValue === 'number' ? nextValue : null)}
        onKeyDown={(event) => {
          if (event.key === 'Enter') {
            event.preventDefault()
            void commit()
          }
          if (event.key === 'Escape') {
            event.preventDefault()
            setDraft(value ?? null)
            setEditing(false)
          }
        }}
      />
    )
  }

  return (
    <span className="editable-trigger" title="点击编辑" onClick={() => setEditing(true)}>
      {children}
    </span>
  )
}
