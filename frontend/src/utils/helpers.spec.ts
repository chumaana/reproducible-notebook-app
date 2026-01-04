import { describe, it, expect, vi } from 'vitest'
import { getErrorMessage, formatDateTime, debounce } from '@/utils/helpers'

describe('Utils - helpers', () => {
  describe('getErrorMessage', () => {
    it('extracts error from axios error with detail field', () => {
      const error = {
        isAxiosError: true,
        response: {
          data: { detail: 'Authentication failed' },
        },
      }
      expect(getErrorMessage(error)).toBe('Authentication failed')
    })

    it('extracts error from axios error with error field', () => {
      const error = {
        isAxiosError: true,
        response: {
          data: { error: 'Invalid input' },
        },
      }
      expect(getErrorMessage(error)).toBe('Invalid input')
    })

    it('extracts and joins multiple Django field errors', () => {
      const error = {
        isAxiosError: true,
        response: {
          data: {
            username: ['This field is required.'],
            password: ['Too short.'],
          },
        },
      }

      const msg = getErrorMessage(error)

      expect(msg).toContain('username: This field is required.')
      expect(msg).toContain('password: Too short.')
    })

    it('handles generic JS errors (non-axios)', () => {
      const error = new Error('Something went wrong')
      expect(getErrorMessage(error)).toBe('Something went wrong')
    })
  })

  describe('formatDateTime', () => {
    it('formats ISO date string into readable text', () => {
      const date = '2024-03-15T10:30:00Z'
      const formatted = formatDateTime(date)

      expect(formatted).not.toBe('Invalid Date')
      expect(formatted).not.toBe('Unknown')
      expect(formatted).toContain('2024')
    })

    it('handles undefined input gracefully', () => {
      expect(formatDateTime(undefined)).toBe('Unknown')
    })

    it('handles malformed date strings', () => {
      expect(formatDateTime('not-a-date')).toBe('Invalid Date')
    })
  })

  describe('debounce', () => {
    it('delays execution and coalesces multiple calls', () => {
      vi.useFakeTimers()
      const func = vi.fn()
      const debouncedFunc = debounce(func, 100)

      // Call multiple times rapidly
      debouncedFunc()
      debouncedFunc()
      debouncedFunc()

      // Should not be called yet due to delay
      expect(func).not.toHaveBeenCalled()

      // Fast-forward time
      vi.advanceTimersByTime(100)

      // Should execute exactly once
      expect(func).toHaveBeenCalledTimes(1)

      vi.useRealTimers()
    })
  })
})
