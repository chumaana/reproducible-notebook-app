import axios from 'axios'

/**
 * Extracts a user-friendly error message from various error types.
 * Handles Axios errors, Django REST framework responses, and generic errors.
 *
 * @param err - The error object to extract a message from
 * @returns A formatted error message string
 */
export function getErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const data = err.response?.data

    if (typeof data === 'string') {
      return data
    }

    if (data && typeof data === 'object') {
      if ('detail' in data && typeof data.detail === 'string') {
        return data.detail
      }

      if ('error' in data && typeof data.error === 'string') {
        return data.error
      }

      if ('title' in data) {
        const msg = Array.isArray(data.title) ? data.title[0] : data.title
        return `Title: ${msg}`
      }

      if ('content' in data) {
        const msg = Array.isArray(data.content) ? data.content[0] : data.content
        return `Content: ${msg}`
      }

      if ('is_public' in data) {
        const msg = Array.isArray(data.is_public) ? data.is_public[0] : data.is_public
        return `Visibility: ${msg}`
      }

      if ('username' in data) {
        const msg = Array.isArray(data.username) ? data.username[0] : data.username
        return `Username: ${msg}`
      }

      if ('email' in data) {
        const msg = Array.isArray(data.email) ? data.email[0] : data.email
        return `Email: ${msg}`
      }

      if ('password' in data) {
        const msg = Array.isArray(data.password) ? data.password[0] : data.password
        return `Password: ${msg}`
      }

      if ('non_field_errors' in data) {
        const msg = Array.isArray(data.non_field_errors)
          ? data.non_field_errors[0]
          : data.non_field_errors
        return String(msg)
      }

      const errors = Object.entries(data)
        .filter(([key]) => key !== 'detail' && key !== 'error')
        .map(([field, messages]) => {
          if (Array.isArray(messages)) {
            return `${field}: ${messages.join(', ')}`
          }
          return `${field}: ${String(messages)}`
        })
        .filter(Boolean)

      if (errors.length > 0) {
        return errors.join('; ')
      }
    }

    if (err.response?.statusText) {
      return `${err.response.status}: ${err.response.statusText}`
    }

    return err.message
  }

  if (err instanceof Error) {
    return err.message
  }

  return String(err)
}

/**
 * Formats an ISO date string into a human-readable format.
 *
 * @param dateString - ISO date string to format
 * @returns Formatted date string (e.g., "Jan 15, 2024")
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
 * Formats an ISO date string with time included.
 *
 * @param dateString - ISO date string to format
 * @returns Formatted date-time string (e.g., "Jan 15, 2024, 02:30 PM")
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
 * Creates a debounced function that delays execution until after
 * the specified delay has elapsed since the last call.
 *
 * @param fn - The function to debounce
 * @param delay - Delay in milliseconds
 * @returns Debounced function
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number,
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>

  return function (this: unknown, ...args: Parameters<T>) {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn.apply(this, args), delay)
  }
}

/**
 * Truncates text to a specified maximum length with ellipsis.
 *
 * @param text - The text to truncate
 * @param maxLength - Maximum length before truncation
 * @returns Truncated text with ellipsis if necessary
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

/**
 * Generates a unique identifier for client-side use.
 * Format: "timestamp-randomstring"
 *
 * @returns Unique ID string
 */
export function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

/**
 * Downloads text content as a file to the user's device.
 *
 * @param content - The text content to download
 * @param filename - The name for the downloaded file
 */
export function downloadTextFile(content: string, filename: string): void {
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')

  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()

  // Cleanup
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
