import axios from 'axios'

/**
 * Extracts a human-readable error message from an error object.
 * Handles Axios responses, Django REST Framework field errors, and native Error objects.
 *
 * @param err - The error object to parse (unknown type)
 * @returns A formatted error message string
 */
export function getErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const data = err.response?.data

    if (typeof data === 'string') return data

    if (data && typeof data === 'object') {
      // Standard DRF 'detail' field
      if ('detail' in data && typeof data.detail === 'string') {
        return data.detail
      }

      // Generic 'error' field
      if ('error' in data && typeof data.error === 'string') {
        return data.error
      }

      // Handle validation errors (fields often return arrays of strings)
      const errors = Object.entries(data)
        .filter(([key]) => key !== 'detail' && key !== 'error')
        .map(([field, messages]) => {
          if (Array.isArray(messages)) {
            return `${field}: ${messages.join(', ')}`
          }
          return `${field}: ${String(messages)}`
        })
        .filter(Boolean)

      if (errors.length > 0) return errors.join('; ')
    }

    if (err.response?.statusText) {
      return `${err.response.status}: ${err.response.statusText}`
    }
    return err.message
  }

  if (err instanceof Error) return err.message
  return String(err)
}

/**
 * Formats an ISO date string into a localized date and time string.
 *
 * @param dateString - The ISO date string (e.g., "2024-03-15T10:30:00Z")
 * @returns The formatted date string, "Invalid Date" if malformed, or "Unknown" if undefined
 */
export function formatDateTime(dateString?: string): string {
  if (!dateString) return 'Unknown'

  const date = new Date(dateString)

  if (isNaN(date.getTime())) {
    return 'Invalid Date'
  }

  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Creates a debounced function that delays invoking the provided function
 * until after the specified wait time has elapsed since the last invocation.
 *
 * @param fn - The function to debounce
 * @param delay - The delay in milliseconds
 * @returns A new debounced function
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
