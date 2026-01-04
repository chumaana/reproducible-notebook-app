import { describe, it, expect, vi } from 'vitest'
import { getErrorMessage, formatDateTime, debounce } from '@/utils/helpers'

describe('Utils - helpers', () => {
  describe('getErrorMessage', () => {
    it('extracts error from axios error with detail', () => {
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

    it('extracts error from Django field errors', () => {
      const error = {
        isAxiosError: true,
        response: {
          data: {
            username: ['This field is required.'],
            password: ['Too short.'],
          },
        },
      }
      // Expects joined string
      const msg = getErrorMessage(error)
      expect(msg).toContain('username: This field is required.')
      expect(msg).toContain('password: Too short.')
    })

    it('handles non-axios errors', () => {
      const error = new Error('Something went wrong')
      expect(getErrorMessage(error)).toBe('Something went wrong')
    })
  })

  describe('formatDateTime', () => {
    it('formats ISO date string with time', () => {
      const date = '2024-03-15T10:30:00Z'
      const formatted = formatDateTime(date)

      // Check for basics (locale implementation may vary slightly by node version)
      expect(formatted).not.toBe('Invalid Date')
      expect(formatted).not.toBe('Unknown')
      // Should likely contain the year
      expect(formatted).toContain('2024')
    })

    it('returns "Unknown" for undefined', () => {
      expect(formatDateTime(undefined)).toBe('Unknown')
    })

    it('returns "Invalid date" for bad strings', () => {
      expect(formatDateTime('not-a-date')).toBe('Invalid Date')
    })
  })

  describe('debounce', () => {
    it('delays execution of function', () => {
      vi.useFakeTimers()
      const func = vi.fn()
      const debouncedFunc = debounce(func, 100)

      // Call multiple times quickly
      debouncedFunc()
      debouncedFunc()
      debouncedFunc()

      // Should not have been called yet
      expect(func).not.toHaveBeenCalled()

      // Fast forward time
      vi.advanceTimersByTime(100)

      // Should be called exactly once
      expect(func).toHaveBeenCalledTimes(1)
      vi.useRealTimers()
    })
  })
})
