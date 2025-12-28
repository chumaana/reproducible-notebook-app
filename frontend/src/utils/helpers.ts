import axios from 'axios'

/**
 * Extract error message from unknown error types
 * This is a best practice for error handling in TypeScript
 */
export function getErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    // Check for specific error response formats
    const data = err.response?.data

    if (typeof data === 'string') {
      return data
    }

    if (data && typeof data === 'object') {
      // Handle Django REST framework error format
      if (data.detail) {
        return data.detail
      }

      if (data.error) {
        return data.error
      }

      // Handle validation errors (field-specific errors)
      const errors = Object.entries(data)
        .map(([field, messages]) => {
          const messageArray = Array.isArray(messages) ? messages : [messages]
          return `${field}: ${messageArray.join(', ')}`
        })
        .join('; ')

      if (errors) return errors
    }

    return err.message
  }

  if (err instanceof Error) {
    return err.message
  }

  return String(err)
}

/**
 * Format date to readable string
 */
export function formatDate(dateString?: string): string {
  if (!dateString) return 'Unknown'

  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  } catch {
    return 'Invalid date'
  }
}

/**
 * Format date with time
 */
export function formatDateTime(dateString?: string): string {
  if (!dateString) return 'Unknown'

  try {
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return 'Invalid date'
  }
}

/**
 * Debounce function for input handlers
 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number,
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>

  return function (this: any, ...args: Parameters<T>) {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn.apply(this, args), delay)
  }
}

/**
 * Truncate text to specified length
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

/**
 * Generate unique ID
 */
export function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

/**
 * Download text file
 */
export function downloadTextFile(content: string, filename: string): void {
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
