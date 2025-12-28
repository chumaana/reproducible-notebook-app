import axios from 'axios'

/**
 * Extracts a user-friendly error message from various error types.
 * Handles Axios errors, Django REST framework responses, and generic errors.
 *
 * @param err - The error object to extract a message from
 * @returns A formatted error message string
 */
export function getErrorMessage(err: unknown): string {
  // Handle Axios API errors
  if (axios.isAxiosError(err)) {
    const data = err.response?.data

    // Simple string response
    if (typeof data === 'string') {
      return data
    }

    if (data && typeof data === 'object') {
      // Django REST framework 'detail' field
      if ('detail' in data && typeof data.detail === 'string') {
        return data.detail
      }

      // Generic 'error' field
      if ('error' in data && typeof data.error === 'string') {
        return data.error
      }

      // Field-level validation errors (e.g., form validation)
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

  // Handle standard JavaScript errors
  if (err instanceof Error) {
    return err.message
  }

  // Fallback for unknown error types
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
 * Useful for search inputs, auto-save, and other rapid events.
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
 * Used for exporting notebooks, R scripts, etc.
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
