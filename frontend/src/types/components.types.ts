// import type { Issue } from './notebook.types'

// ==================== Code Highlighter ====================
export interface CodeHighlighterProps {
  code: string
  language?: string
  issues?: Array<{
    line: number
    severity: 'high' | 'medium' | 'low'
    message: string
  }>
}

// ==================== Modal ====================
export interface ModalProps {
  show: boolean
  title?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
}

// ==================== Button ====================
export type ButtonVariant = 'primary' | 'secondary' | 'success' | 'danger' | 'outline'
export type ButtonSize = 'sm' | 'md' | 'lg'
